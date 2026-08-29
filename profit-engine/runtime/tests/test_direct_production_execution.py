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
        self.registry = ProviderIdentityRegistry()
        self.registry.register(self.target)
        self.proposal = build_action_proposal(
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
        self.governor = bind_governor(
            self.proposal,
            GovernorDecision(GovernorState.GOVERNOR_READY_FOR_DAY11_CONTROLLER, (), None),
        )
        diagnostics = (
            DiagnosticResult("direct", DoctorStatus.PASS, ("direct.permission=EDITING",), 200),
            DiagnosticResult("metrica", DoctorStatus.PASS, (), 200),
            DiagnosticResult("yan_statistics", DoctorStatus.PASS, (), 200),
        )
        self.readiness = build_day12_launch_readiness(diagnostics=diagnostics)

    def case(self, *, method="campaign.suspend", normalized_state="ACTIVE"):
        preflight = build_preflight(
            target=self.target,
            normalized_state=normalized_state,
            status="ACCEPTED",
            current_provider_daily_budget=None,
            currency=None,
            strategy_subtype="not-required-for-suspend-resume",
            fetched_at=NOW,
            ttl=timedelta(minutes=5),
            source_ref="accepted-live-preflight",
        )
        desired = "SUSPENDED" if method.endswith(".suspend") else "ACTIVE"
        locks = ExecutionLockRegistry()
        plan, audit = build_controller_plan(
            proposal=self.proposal,
            governor=self.governor,
            registry=self.registry,
            target_ref=self.target.target_ref,
            preflight=preflight,
            method=method,
            request_objects=({"provider_entity_id": "101", "desired_state": desired},),
            now=NOW,
            locks=locks,
        )
        selection = build_live_candidate_selection(
            readiness=self.readiness,
            plan=plan,
            private_decision_ref="private-fixture",
            private_decision_digest="c" * 64,
            measurement_refs=("measurement-fixture",),
            provenance_refs=("provenance-fixture",),
        )
        arm = build_production_writer_arm(
            readiness=self.readiness,
            selection=selection,
            plan=plan,
            prepared_at=NOW,
            expires_at=NOW + timedelta(minutes=2),
            explicit_enable=True,
        )
        return plan, audit, preflight, arm, locks

    def reader(self, *, preflight_state="ON", readback_state="SUSPENDED"):
        return YandexDirectLiveStateReader(
            transport=FakeTransport([
                ok({"result": {"Campaigns": [{"Id": 101, "State": preflight_state, "Status": "ACCEPTED"}]}}),
                ok({"result": {"Campaigns": [{"Id": 101, "State": readback_state, "Status": "ACCEPTED"}]}}),
            ]),
            config=self.config,
        )

    def writer(self, *, method="campaign.suspend", response=None):
        action = "SuspendResults" if method.endswith(".suspend") else "ResumeResults"
        if response is None:
            response = ok({"result": {action: [{"Id": 101}]}}, RequestId="req-live", Units="1/100/1000")
        return YandexDirectProductionWriter(
            transport=FakeTransport([response]),
            config=self.config,
            enabled=True,
        )

    def execute(self, *, plan, audit, preflight, arm, locks, writer, reader, switches=()):
        return execute_guarded_production_once(
            arm=arm,
            plan=plan,
            expected_preflight=preflight,
            writer=writer,
            state_reader=reader,
            token=TOKEN,
            audit=audit,
            locks=locks,
            now=NOW,
            runtime_kill_switches=switches,
        )


class TestGuardedExecution(ExecutionFixtures):
    def test_provider_on_normalizes_to_active_and_suspend_launches(self):
        plan, audit, preflight, arm, locks = self.case()
        writer = self.writer()
        reader = self.reader(preflight_state="ON", readback_state="SUSPENDED")
        result = self.execute(
            plan=plan, audit=audit, preflight=preflight, arm=arm, locks=locks,
            writer=writer, reader=reader,
        )
        self.assertEqual(ProductionTerminalState.GUARDED_PRODUCTION_LAUNCHED, result.state)
        self.assertEqual(1, result.dispatch_attempts)
        self.assertEqual(2, result.provider_read_attempts)
        self.assertTrue(result.audit_valid)
        self.assertEqual("EXECUTION_LOCK_RELEASED", audit.records[-1].event)
        self.assertFalse(locks.is_locked(self.target.lock_key, NOW))

    def test_resume_from_suspended_verifies_provider_on_as_active(self):
        plan, audit, preflight, arm, locks = self.case(
            method="campaign.resume", normalized_state="SUSPENDED"
        )
        writer = self.writer(method="campaign.resume")
        reader = self.reader(preflight_state="SUSPENDED", readback_state="ON")
        result = self.execute(
            plan=plan, audit=audit, preflight=preflight, arm=arm, locks=locks,
            writer=writer, reader=reader,
        )
        self.assertEqual(ProductionTerminalState.GUARDED_PRODUCTION_LAUNCHED, result.state)
        self.assertEqual(1, result.dispatch_attempts)
        self.assertTrue(result.audit_valid)

    def test_incoherent_suspend_from_suspended_blocks_before_provider(self):
        plan, audit, preflight, arm, locks = self.case(
            method="campaign.suspend", normalized_state="SUSPENDED"
        )
        writer = self.writer()
        reader = self.reader(preflight_state="SUSPENDED", readback_state="SUSPENDED")
        result = self.execute(
            plan=plan, audit=audit, preflight=preflight, arm=arm, locks=locks,
            writer=writer, reader=reader,
        )
        self.assertEqual(ProductionTerminalState.PRODUCTION_WRITE_BLOCKED, result.state)
        self.assertEqual(0, result.dispatch_attempts)
        self.assertEqual(0, result.provider_read_attempts)
        self.assertTrue(result.audit_valid)

    def test_toctou_mismatch_blocks_before_dispatch(self):
        plan, audit, preflight, arm, locks = self.case()
        writer = self.writer()
        reader = self.reader(preflight_state="SUSPENDED")
        result = self.execute(
            plan=plan, audit=audit, preflight=preflight, arm=arm, locks=locks,
            writer=writer, reader=reader,
        )
        self.assertEqual(ProductionTerminalState.PRODUCTION_WRITE_BLOCKED, result.state)
        self.assertEqual(0, result.dispatch_attempts)
        self.assertTrue(result.audit_valid)

    def test_runtime_kill_switch_blocks_before_dispatch(self):
        plan, audit, preflight, arm, locks = self.case()
        writer = self.writer()
        reader = self.reader()
        result = self.execute(
            plan=plan, audit=audit, preflight=preflight, arm=arm, locks=locks,
            writer=writer, reader=reader,
            switches=(KillSwitch("target", self.target.target_ref, True),),
        )
        self.assertEqual(ProductionTerminalState.PRODUCTION_WRITE_BLOCKED, result.state)
        self.assertEqual(0, result.dispatch_attempts)
        self.assertTrue(result.audit_valid)

    def test_uncertain_transport_can_recover_only_from_exact_desired_readback(self):
        plan, audit, preflight, arm, locks = self.case()
        writer = self.writer(response=TransportError("timeout"))
        reader = self.reader(readback_state="SUSPENDED")
        result = self.execute(
            plan=plan, audit=audit, preflight=preflight, arm=arm, locks=locks,
            writer=writer, reader=reader,
        )
        self.assertEqual(ProductionTerminalState.GUARDED_PRODUCTION_LAUNCHED, result.state)
        self.assertEqual(1, result.dispatch_attempts)
        self.assertTrue(result.recovered_from_uncertain_transport)
        self.assertTrue(result.audit_valid)

    def test_provider_object_error_without_id_with_unchanged_state_is_blocked(self):
        plan, audit, preflight, arm, locks = self.case()
        writer = self.writer(response=ok({"result": {"SuspendResults": [{"Errors": [{"Code": 9999}]}]}}))
        reader = self.reader(readback_state="ON")
        result = self.execute(
            plan=plan, audit=audit, preflight=preflight, arm=arm, locks=locks,
            writer=writer, reader=reader,
        )
        self.assertEqual(ProductionTerminalState.PRODUCTION_WRITE_BLOCKED, result.state)
        self.assertEqual(1, result.dispatch_attempts)
        self.assertTrue(result.audit_valid)

    def test_timeout_with_unchanged_state_is_uncertain_and_never_retried(self):
        plan, audit, preflight, arm, locks = self.case()
        writer = self.writer(response=TransportError("timeout"))
        reader = self.reader(readback_state="ON")
        result = self.execute(
            plan=plan, audit=audit, preflight=preflight, arm=arm, locks=locks,
            writer=writer, reader=reader,
        )
        self.assertEqual(ProductionTerminalState.PRODUCTION_EXECUTION_UNCERTAIN, result.state)
        self.assertEqual(1, result.dispatch_attempts)
        self.assertTrue(result.audit_valid)

    def test_existing_lock_blocks_without_provider_reads_or_dispatch(self):
        plan, audit, preflight, arm, locks = self.case()
        self.assertTrue(locks.acquire(self.target.lock_key, NOW, timedelta(minutes=2)))
        writer = self.writer()
        reader = self.reader()
        result = self.execute(
            plan=plan, audit=audit, preflight=preflight, arm=arm, locks=locks,
            writer=writer, reader=reader,
        )
        self.assertEqual(ProductionTerminalState.PRODUCTION_WRITE_BLOCKED, result.state)
        self.assertEqual(0, result.dispatch_attempts)
        self.assertEqual(0, result.provider_read_attempts)
        self.assertTrue(result.audit_valid)


if __name__ == "__main__":
    unittest.main()
