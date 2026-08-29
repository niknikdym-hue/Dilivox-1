import unittest
from datetime import datetime, timedelta, timezone

from profit_engine_runtime.config import SiteConfig
from profit_engine_runtime.day10_public import GovernorDecision, GovernorState, ProposalKind, build_action_proposal
from profit_engine_runtime.day12_launch_gate import build_live_candidate_selection
from profit_engine_runtime.day12_readiness import build_day12_launch_readiness
from profit_engine_runtime.direct_controller import (
    ExecutionLockRegistry,
    KillSwitch,
    ProviderIdentityRegistry,
    ProviderTarget,
    build_controller_plan,
    build_preflight,
    bind_governor,
)
from profit_engine_runtime.direct_production_execution import (
    ProductionTerminalState,
    YandexDirectLiveStateReader,
    execute_guarded_production_once,
)
from profit_engine_runtime.direct_production_writer import YandexDirectProductionWriter, build_production_writer_arm
from profit_engine_runtime.models import DiagnosticResult, DoctorStatus, HttpResponse
from profit_engine_runtime.transport import TransportError


NOW = datetime(2026, 8, 29, 12, tzinfo=timezone.utc)
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


class ExecutionFixtures(unittest.TestCase):
    def setUp(self):
        self.config = SiteConfig(
            direct_operator_login="reklamadymova",
            direct_client_login="owner-advertiser-fixture",
            direct_endpoint="https://api.direct.yandex.com/json/v501",
        )
        self.target = ProviderTarget(
            "target-fixture", "dilivox", "yandex_direct", "advertiser-fixture", "campaign", "101"
        )
        registry = ProviderIdentityRegistry()
        registry.register(self.target)
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
        self.expected_preflight = build_preflight(
            target=self.target,
            normalized_state="ACTIVE",
            status="ACCEPTED",
            current_provider_daily_budget=None,
            currency=None,
            strategy_subtype="not-required-for-suspend-resume",
            fetched_at=NOW,
            ttl=timedelta(minutes=5),
            source_ref="accepted-live-preflight",
        )
        self.locks = ExecutionLockRegistry()
        self.plan, self.audit = build_controller_plan(
            proposal=proposal,
            governor=governor,
            registry=registry,
            target_ref=self.target.target_ref,
            preflight=self.expected_preflight,
            method="campaign.suspend",
            request_objects=({"provider_entity_id": "101", "desired_state": "SUSPENDED"},),
            now=NOW,
            locks=self.locks,
        )
        diagnostics = (
            DiagnosticResult("direct", DoctorStatus.PASS, ("direct.permission=EDITING",), 200),
            DiagnosticResult("metrica", DoctorStatus.PASS, (), 200),
            DiagnosticResult("yan_statistics", DoctorStatus.PASS, (), 200),
        )
        readiness = build_day12_launch_readiness(diagnostics=diagnostics)
        selection = build_live_candidate_selection(
            readiness=readiness,
            plan=self.plan,
            private_decision_ref="private-fixture",
            private_decision_digest="c" * 64,
            measurement_refs=("measurement-fixture",),
            provenance_refs=("provenance-fixture",),
        )
        self.arm = build_production_writer_arm(
            readiness=readiness,
            selection=selection,
            plan=self.plan,
            prepared_at=NOW,
            expires_at=NOW + timedelta(minutes=2),
            explicit_enable=True,
        )

    def reader(self, preflight_state="ACTIVE", readback_state="SUSPENDED"):
        return YandexDirectLiveStateReader(
            transport=FakeTransport([
                ok({"result": {"Campaigns": [{"Id": 101, "State": preflight_state, "Status": "ACCEPTED"}]}}),
                ok({"result": {"Campaigns": [{"Id": 101, "State": readback_state, "Status": "ACCEPTED"}]}}),
            ]),
            config=self.config,
        )

    def writer(self, response=None):
        if response is None:
            response = ok({"result": {"SuspendResults": [{"Id": 101}]}}, RequestId="req-live", Units="1/100/1000")
        return YandexDirectProductionWriter(
            transport=FakeTransport([response]),
            config=self.config,
            enabled=True,
        )


class TestGuardedExecution(ExecutionFixtures):
    def test_exact_success_launches_with_one_dispatch_and_complete_audit(self):
        writer = self.writer()
        reader = self.reader()
        result = execute_guarded_production_once(
            arm=self.arm,
            plan=self.plan,
            expected_preflight=self.expected_preflight,
            writer=writer,
            state_reader=reader,
            token=TOKEN,
            audit=self.audit,
            locks=self.locks,
            now=NOW,
        )
        self.assertEqual(ProductionTerminalState.GUARDED_PRODUCTION_LAUNCHED, result.state)
        self.assertEqual(1, result.dispatch_attempts)
        self.assertEqual(2, result.provider_read_attempts)
        self.assertTrue(result.audit_valid)
        self.assertEqual("EXECUTION_LOCK_RELEASED", self.audit.records[-1].event)
        self.assertFalse(self.locks.is_locked(self.target.lock_key, NOW))

    def test_toctou_mismatch_blocks_before_dispatch(self):
        writer = self.writer()
        reader = self.reader(preflight_state="SUSPENDED")
        result = execute_guarded_production_once(
            arm=self.arm, plan=self.plan, expected_preflight=self.expected_preflight,
            writer=writer, state_reader=reader, token=TOKEN, audit=self.audit,
            locks=self.locks, now=NOW,
        )
        self.assertEqual(ProductionTerminalState.PRODUCTION_WRITE_BLOCKED, result.state)
        self.assertEqual(0, result.dispatch_attempts)
        self.assertTrue(result.audit_valid)

    def test_runtime_kill_switch_blocks_before_dispatch(self):
        writer = self.writer()
        reader = self.reader()
        result = execute_guarded_production_once(
            arm=self.arm, plan=self.plan, expected_preflight=self.expected_preflight,
            writer=writer, state_reader=reader, token=TOKEN, audit=self.audit,
            locks=self.locks, now=NOW,
            runtime_kill_switches=(KillSwitch("target", self.target.target_ref, True),),
        )
        self.assertEqual(ProductionTerminalState.PRODUCTION_WRITE_BLOCKED, result.state)
        self.assertEqual(0, result.dispatch_attempts)
        self.assertTrue(result.audit_valid)

    def test_uncertain_transport_can_recover_only_from_exact_desired_readback(self):
        writer = self.writer(TransportError("timeout"))
        reader = self.reader(readback_state="SUSPENDED")
        result = execute_guarded_production_once(
            arm=self.arm, plan=self.plan, expected_preflight=self.expected_preflight,
            writer=writer, state_reader=reader, token=TOKEN, audit=self.audit,
            locks=self.locks, now=NOW,
        )
        self.assertEqual(ProductionTerminalState.GUARDED_PRODUCTION_LAUNCHED, result.state)
        self.assertEqual(1, result.dispatch_attempts)
        self.assertTrue(result.recovered_from_uncertain_transport)
        self.assertTrue(result.audit_valid)

    def test_provider_object_error_with_unchanged_state_is_blocked(self):
        writer = self.writer(ok({"result": {"SuspendResults": [{"Id": 101, "Errors": [{"Code": 9999}]}]}}))
        reader = self.reader(readback_state="ACTIVE")
        result = execute_guarded_production_once(
            arm=self.arm, plan=self.plan, expected_preflight=self.expected_preflight,
            writer=writer, state_reader=reader, token=TOKEN, audit=self.audit,
            locks=self.locks, now=NOW,
        )
        self.assertEqual(ProductionTerminalState.PRODUCTION_WRITE_BLOCKED, result.state)
        self.assertEqual(1, result.dispatch_attempts)
        self.assertTrue(result.audit_valid)

    def test_timeout_with_unchanged_state_is_uncertain_and_never_retried(self):
        writer = self.writer(TransportError("timeout"))
        reader = self.reader(readback_state="ACTIVE")
        result = execute_guarded_production_once(
            arm=self.arm, plan=self.plan, expected_preflight=self.expected_preflight,
            writer=writer, state_reader=reader, token=TOKEN, audit=self.audit,
            locks=self.locks, now=NOW,
        )
        self.assertEqual(ProductionTerminalState.PRODUCTION_EXECUTION_UNCERTAIN, result.state)
        self.assertEqual(1, result.dispatch_attempts)
        self.assertTrue(result.audit_valid)

    def test_existing_lock_blocks_without_provider_reads_or_dispatch(self):
        self.assertTrue(self.locks.acquire(self.target.lock_key, NOW, timedelta(minutes=2)))
        writer = self.writer()
        reader = self.reader()
        result = execute_guarded_production_once(
            arm=self.arm, plan=self.plan, expected_preflight=self.expected_preflight,
            writer=writer, state_reader=reader, token=TOKEN, audit=self.audit,
            locks=self.locks, now=NOW,
        )
        self.assertEqual(ProductionTerminalState.PRODUCTION_WRITE_BLOCKED, result.state)
        self.assertEqual(0, result.dispatch_attempts)
        self.assertEqual(0, result.provider_read_attempts)
        self.assertTrue(result.audit_valid)


if __name__ == "__main__":
    unittest.main()
