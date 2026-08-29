import urllib.error
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from profit_engine_runtime.config import SiteConfig
from profit_engine_runtime.day10_public import (
    GovernorDecision,
    GovernorState,
    ProposalKind,
    build_action_proposal,
)
from profit_engine_runtime.day12_launch_gate import build_live_candidate_selection
from profit_engine_runtime.day12_readiness import build_day12_launch_readiness
from profit_engine_runtime.direct_controller import (
    ExecutionLockRegistry,
    ProviderIdentityRegistry,
    ProviderTarget,
    build_controller_plan,
    build_preflight,
    bind_governor,
)
from profit_engine_runtime.direct_production_writer import (
    LIVE_WRITE_METHODS,
    PRODUCTION_WRITER_DEFAULT_ENABLED,
    SingleAttemptDirectWriteTransport,
    YandexDirectProductionWriter,
    build_production_writer_arm,
)
from profit_engine_runtime.models import DiagnosticResult, DoctorStatus, HttpRequest, HttpResponse
from profit_engine_runtime.transport import TransportError, UrllibTransport


NOW = datetime(2026, 8, 29, 10, 0, tzinfo=timezone.utc)
TOKEN = "fixture-oauth-token"


class FakeTransport:
    def __init__(self, responses):
        self.responses = list(responses)
        self.requests = []

    def send(self, request):
        self.requests.append(request)
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response


def ok(body, **headers):
    return HttpResponse(200, headers, body, headers.get("RequestId"))


class WriterFixtures(unittest.TestCase):
    def setUp(self):
        self.config = SiteConfig(
            direct_operator_login="reklamadymova",
            direct_client_login="owner-advertiser-fixture",
            direct_endpoint="https://api.direct.yandex.com/json/v501",
        )
        self.target = ProviderTarget(
            "target-fixture",
            "dilivox",
            "yandex_direct",
            "advertiser-fixture",
            "campaign",
            "101",
        )
        self.registry = ProviderIdentityRegistry()
        self.registry.register(self.target)

    def plan(self, *, method="campaign.suspend", state="ACTIVE"):
        proposal = build_action_proposal(
            proposal_id="proposal-fixture",
            site_id="dilivox",
            kind=ProposalKind.STOP,
            target_refs={"provider_target": self.target.target_ref},
            strategy_evidence_digest="a" * 64,
            measurement_refs=("measurement-fixture",),
            provenance_refs=("provenance-fixture",),
            current_weekly_budget=None,
            proposed_weekly_budget=None,
            private_decision_ref="private-fixture",
            private_decision_digest="b" * 64,
            audit_metadata={"fixture": "true"},
        )
        governor = bind_governor(
            proposal,
            GovernorDecision(GovernorState.GOVERNOR_READY_FOR_DAY11_CONTROLLER, (), None),
        )
        preflight = build_preflight(
            target=self.target,
            normalized_state=state,
            status="ACCEPTED",
            current_provider_daily_budget=None,
            currency=None,
            strategy_subtype="not-required-for-suspend-resume",
            fetched_at=NOW,
            ttl=timedelta(minutes=5),
            source_ref="direct-live-fixture",
        )
        request = ({
            "provider_entity_id": self.target.provider_entity_id,
            "desired_state": "SUSPENDED" if method.endswith(".suspend") else "ACTIVE",
        },)
        plan, _ = build_controller_plan(
            proposal=proposal,
            governor=governor,
            registry=self.registry,
            target_ref=self.target.target_ref,
            preflight=preflight,
            method=method,
            request_objects=request,
            now=NOW,
            locks=ExecutionLockRegistry(),
        )
        self.assertEqual("READY_FOR_DAY12_EXECUTION", plan.state.value)
        return plan

    def readiness_and_selection(self, plan):
        diagnostics = (
            DiagnosticResult("direct", DoctorStatus.PASS, ("direct.permission=EDITING",), 200),
            DiagnosticResult("metrica", DoctorStatus.PASS, (), 200),
            DiagnosticResult("yan_statistics", DoctorStatus.PASS, (), 200),
        )
        readiness = build_day12_launch_readiness(diagnostics=diagnostics)
        self.assertEqual("READY_FOR_LIVE_CANDIDATE_SELECTION", readiness.state.value)
        selection = build_live_candidate_selection(
            readiness=readiness,
            plan=plan,
            private_decision_ref="private-fixture",
            private_decision_digest="c" * 64,
            measurement_refs=("measurement-fixture",),
            provenance_refs=("provenance-fixture",),
        )
        return readiness, selection

    def arm(self, plan):
        readiness, selection = self.readiness_and_selection(plan)
        return build_production_writer_arm(
            readiness=readiness,
            selection=selection,
            plan=plan,
            prepared_at=NOW,
            expires_at=NOW + timedelta(minutes=2),
            explicit_enable=True,
        )


class TestProductionWriter(WriterFixtures):
    def test_writer_is_disabled_by_default_and_budget_not_live_allowlisted(self):
        self.assertFalse(PRODUCTION_WRITER_DEFAULT_ENABLED)
        self.assertNotIn("campaign.update_budget", LIVE_WRITE_METHODS)
        plan = self.plan()
        writer = YandexDirectProductionWriter(transport=FakeTransport([]), config=self.config)
        with self.assertRaises(RuntimeError):
            writer.dispatch_once(arm=self.arm(plan), plan=plan, token=TOKEN, now=NOW)

    def test_explicit_arm_is_required(self):
        plan = self.plan()
        readiness, selection = self.readiness_and_selection(plan)
        with self.assertRaises(ValueError):
            build_production_writer_arm(
                readiness=readiness,
                selection=selection,
                plan=plan,
                prepared_at=NOW,
                expires_at=NOW + timedelta(minutes=2),
            )

    def test_arm_requires_timezone_aware_timestamps_and_max_five_minute_ttl(self):
        plan = self.plan()
        readiness, selection = self.readiness_and_selection(plan)
        for prepared, expires in (
            (datetime(2026, 8, 29, 10, 0), datetime(2026, 8, 29, 10, 2)),
            (NOW, NOW + timedelta(minutes=5, seconds=1)),
        ):
            with self.subTest(prepared=prepared, expires=expires), self.assertRaises(ValueError):
                build_production_writer_arm(
                    readiness=readiness,
                    selection=selection,
                    plan=plan,
                    prepared_at=prepared,
                    expires_at=expires,
                    explicit_enable=True,
                )

    def test_campaign_suspend_request_is_exact_one_object(self):
        plan = self.plan()
        transport = FakeTransport([
            ok({"result": {"SuspendResults": [{"Id": 101}]}}, RequestId="req-1", Units="1/100/1000")
        ])
        writer = YandexDirectProductionWriter(transport=transport, config=self.config, enabled=True)
        result = writer.dispatch_once(arm=self.arm(plan), plan=plan, token=TOKEN, now=NOW)
        self.assertTrue(result.object_success)
        self.assertEqual(1, writer.dispatch_count)
        self.assertEqual(1, len(transport.requests))
        request = transport.requests[0]
        self.assertEqual("https://api.direct.yandex.com/json/v501/campaigns", request.url)
        self.assertEqual("Bearer " + TOKEN, request.headers["Authorization"])
        self.assertEqual("owner-advertiser-fixture", request.headers["Client-Login"])
        self.assertEqual("suspend", request.json_body["method"])
        self.assertEqual({"Ids": [101]}, request.json_body["params"]["SelectionCriteria"])
        self.assertEqual("req-1", result.request_id)
        self.assertEqual("1/100/1000", result.units)
        with self.assertRaises(RuntimeError):
            writer.dispatch_once(arm=self.arm(plan), plan=plan, token=TOKEN, now=NOW)

    def test_object_error_is_not_success_and_idless_single_result_keeps_code(self):
        plan = self.plan()
        for item in (
            {"Id": 101, "Errors": [{"Code": 9999}]},
            {"Errors": [{"Code": 8800}]},
        ):
            with self.subTest(item=item):
                transport = FakeTransport([ok({"result": {"SuspendResults": [item]}})])
                writer = YandexDirectProductionWriter(transport=transport, config=self.config, enabled=True)
                result = writer.dispatch_once(arm=self.arm(plan), plan=plan, token=TOKEN, now=NOW)
                self.assertFalse(result.object_success)
                self.assertEqual((str(item["Errors"][0]["Code"]),), result.errors)

    def test_exact_readback_normalizes_provider_on_to_active(self):
        plan = self.plan(method="campaign.resume", state="SUSPENDED")
        transport = FakeTransport([
            ok({"result": {"Campaigns": [{"Id": 101, "State": "ON", "Status": "ACCEPTED"}]}})
        ])
        writer = YandexDirectProductionWriter(transport=FakeTransport([]), config=self.config, enabled=True)
        value = writer.read_back(plan=plan, token=TOKEN, transport=transport)
        self.assertEqual({
            "provider_entity_id": "101",
            "normalized_state": "ACTIVE",
            "status": "ACCEPTED",
        }, value)
        request = transport.requests[0]
        self.assertEqual("get", request.json_body["method"])
        self.assertEqual({"Ids": [101]}, request.json_body["params"]["SelectionCriteria"])

    def test_single_attempt_transport_never_retries_mutation(self):
        request = HttpRequest(
            "POST",
            "https://api.direct.yandex.com/json/v501/campaigns",
            {"Authorization": "Bearer fixture"},
            json_body={"method": "suspend", "params": {"SelectionCriteria": {"Ids": [101]}}},
        )
        error = urllib.error.HTTPError(request.url, 503, "unavailable", {}, None)
        tx = SingleAttemptDirectWriteTransport(UrllibTransport(max_attempts=1, backoff_seconds=0))
        with patch("urllib.request.urlopen", side_effect=error) as mocked:
            with self.assertRaises(TransportError):
                tx.send(request)
        self.assertEqual(1, mocked.call_count)

    def test_noncanonical_endpoint_is_rejected_before_network(self):
        tx = SingleAttemptDirectWriteTransport()
        with self.assertRaises(TransportError):
            tx.send(HttpRequest("POST", "https://example.invalid/campaigns"))


if __name__ == "__main__":
    unittest.main()
