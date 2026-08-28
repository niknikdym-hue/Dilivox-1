from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import unittest

from profit_engine_runtime.day10_public import (
    GovernorDecision,
    GovernorState,
    ProposalKind,
    build_action_proposal,
)
from profit_engine_runtime.day12_launch_gate import (
    build_inert_writer_arm_intent,
    build_live_candidate_selection,
)
from profit_engine_runtime.day12_readiness import (
    DirectPermissionState,
    build_day12_launch_readiness,
)
from profit_engine_runtime.direct_controller import (
    ExecutionLockRegistry,
    MutationCadenceEvidence,
    ProviderIdentityRegistry,
    ProviderTarget,
    bind_governor,
    build_budget_plan,
    build_controller_plan,
    build_mutation_cadence_evidence,
    build_preflight,
)
from profit_engine_runtime.models import DiagnosticResult, DoctorStatus


NOW = datetime(2026, 8, 28, 18, tzinfo=timezone.utc)


def all_pass_diagnostics():
    return (
        DiagnosticResult("direct", DoctorStatus.PASS),
        DiagnosticResult("metrica", DoctorStatus.PASS),
        DiagnosticResult("yan_statistics", DoctorStatus.PASS),
    )


class Day12LaunchGateTests(unittest.TestCase):
    def setUp(self):
        self.target = ProviderTarget(
            "target-fixture-1", "dilivox", "yandex_direct",
            "advertiser-fixture", "campaign", "entity-fixture-101",
        )
        registry = ProviderIdentityRegistry()
        registry.register(self.target)
        proposal = build_action_proposal(
            proposal_id="proposal-fixture",
            site_id="dilivox",
            kind=ProposalKind.SCALE,
            target_refs={"provider_target": self.target.target_ref},
            strategy_evidence_digest="a" * 64,
            measurement_refs=("measurement-fixture",),
            provenance_refs=("provenance-fixture",),
            current_weekly_budget="100.00",
            proposed_weekly_budget="110.00",
            private_decision_ref="private-fixture",
            private_decision_digest="b" * 64,
            audit_metadata={"fixture": "true"},
        )
        governor = bind_governor(
            proposal,
            GovernorDecision(
                GovernorState.GOVERNOR_READY_FOR_DAY11_CONTROLLER,
                (),
                Decimal("10.00"),
            ),
        )
        preflight = build_preflight(
            target=self.target,
            normalized_state="ACTIVE",
            status="ACCEPTED",
            current_provider_daily_budget=Decimal("20.00"),
            currency="RUB",
            strategy_subtype="fixture-strategy",
            fetched_at=NOW,
            ttl=timedelta(minutes=5),
            source_ref="raw-fixture",
        )
        budget = build_budget_plan(
            proposal=proposal,
            governor=governor,
            preflight=preflight,
            proposed_daily=Decimal("22.00"),
            active_days=(1, 2, 3, 4, 5),
            active_day_basis_ref="schedule-fixture-v1",
        )
        cadence = build_mutation_cadence_evidence(
            campaign_ref=self.target.target_ref,
            day="2026-08-28",
            timezone_offset_minutes=0,
            day_basis_ref="utc-day-v1",
            prior_autonomous_mutations=0,
            audit_ref="audit-fixture",
            source_refs=("source-fixture",),
        )
        self.plan, _ = build_controller_plan(
            proposal=proposal,
            governor=governor,
            registry=registry,
            target_ref=self.target.target_ref,
            preflight=preflight,
            method="campaign.update_budget",
            request_objects=({
                "provider_entity_id": self.target.provider_entity_id,
                "daily_budget": Decimal("22.00"),
                "provider_integer_micros": 22_000_000,
            },),
            now=NOW,
            budget_plan=budget,
            cadence=cadence,
            locks=ExecutionLockRegistry(),
        )
        self.ready = build_day12_launch_readiness(
            direct_permission=DirectPermissionState.EDITING,
            diagnostics=all_pass_diagnostics(),
        )

    def selection(self):
        return build_live_candidate_selection(
            readiness=self.ready,
            plan=self.plan,
            private_decision_ref="private-selection-1",
            private_decision_digest="c" * 64,
            measurement_refs=("measurement-live-1",),
            provenance_refs=("provenance-live-1",),
        )

    def test_blocked_readiness_cannot_create_candidate(self):
        blocked = build_day12_launch_readiness(
            direct_permission=DirectPermissionState.READING,
            diagnostics=all_pass_diagnostics(),
        )
        with self.assertRaises(ValueError):
            build_live_candidate_selection(
                readiness=blocked,
                plan=self.plan,
                private_decision_ref="private-selection-1",
                private_decision_digest="c" * 64,
                measurement_refs=("measurement-live-1",),
                provenance_refs=("provenance-live-1",),
            )

    def test_public_runtime_cannot_self_select_commercial_winner(self):
        with self.assertRaises(ValueError):
            build_live_candidate_selection(
                readiness=self.ready,
                plan=self.plan,
                private_decision_ref="private-selection-1",
                private_decision_digest="c" * 64,
                measurement_refs=("measurement-live-1",),
                provenance_refs=("provenance-live-1",),
                selected_by="PUBLIC_RUNTIME",
            )

    def test_exact_candidate_binding_is_integrity_valid(self):
        selection = self.selection()
        self.assertTrue(selection.integrity_valid)
        self.assertEqual(self.plan.plan_digest, selection.controller_plan_digest)
        self.assertEqual(self.target.target_ref, selection.target_ref)
        self.assertEqual(self.target.provider_entity_id, selection.provider_entity_id)
        self.assertEqual("CENTRAL_BRAIN", selection.selected_by)

    def test_selection_tamper_is_detected(self):
        selection = self.selection()
        self.assertFalse(replace(selection, target_ref="wrong").integrity_valid)

    def test_inert_writer_arm_is_exact_one_shot_and_non_executable(self):
        selection = self.selection()
        arm = build_inert_writer_arm_intent(
            selection=selection,
            plan=self.plan,
            prepared_at=NOW,
            expires_at=NOW + timedelta(minutes=10),
        )
        self.assertTrue(arm.integrity_valid)
        self.assertEqual(1, arm.max_dispatch_attempts)
        self.assertFalse(arm.executable)
        self.assertFalse(arm.armed)
        self.assertFalse(arm.provider_write_allowed)
        self.assertEqual(0, arm.real_provider_requests)
        self.assertEqual(0, arm.advertising_spend)
        self.assertFalse(arm.production_writer_enabled)

    def test_tampered_or_expired_arm_input_fails_closed(self):
        selection = self.selection()
        tampered_plan = replace(self.plan, plan_digest="0" * 64)
        with self.assertRaises(ValueError):
            build_inert_writer_arm_intent(
                selection=selection,
                plan=tampered_plan,
                prepared_at=NOW,
                expires_at=NOW + timedelta(minutes=10),
            )
        with self.assertRaises(ValueError):
            build_inert_writer_arm_intent(
                selection=selection,
                plan=self.plan,
                prepared_at=NOW,
                expires_at=NOW,
            )


if __name__ == "__main__":
    unittest.main()
