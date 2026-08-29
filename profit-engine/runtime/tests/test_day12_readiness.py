from __future__ import annotations

import unittest

from profit_engine_runtime.day12_readiness import (
    ACCEPTED_TASK_011R_SHA,
    Day12ReadinessState,
    DirectPermissionState,
    build_day12_launch_readiness,
    manager_ui_permission_required,
    observed_direct_permission,
)
from profit_engine_runtime.models import DiagnosticResult, DoctorStatus
from profit_engine_runtime.owner_permission import OwnerPermissionEvidence


def diagnostics(
    *,
    direct=DoctorStatus.PASS,
    metrica=DoctorStatus.PASS,
    yan=DoctorStatus.PASS,
    direct_permission: str | None = None,
    manager_ui_required: bool = False,
):
    checks: list[str] = []
    if manager_ui_required:
        checks.append("direct.permission_source=MANAGER_ACCOUNT_UI_REQUIRED")
    if direct_permission is not None:
        checks.append(f"direct.permission={direct_permission}")
    return (
        DiagnosticResult("direct", direct, checks=tuple(checks)),
        DiagnosticResult("metrica", metrica),
        DiagnosticResult("yan_statistics", yan),
    )


def owner_editing_evidence() -> OwnerPermissionEvidence:
    return OwnerPermissionEvidence(
        schema_version="profit-engine.day12.direct-manager-permission.v1",
        permission="EDITING",
        operator_login="reklamadymova",
        target_login_sha256="0" * 64,
        source="YANDEX_DIRECT_MANAGING_ACCOUNT_UI",
        owner_confirmed=True,
        confirmed_at="2026-08-29T00:00:00Z",
        evidence_digest="1" * 64,
    )


class Day12ReadinessTests(unittest.TestCase):
    def test_reading_permission_blocks_even_when_all_doctors_pass(self):
        result = build_day12_launch_readiness(
            diagnostics=diagnostics(direct_permission="READING"),
        )
        self.assertEqual(Day12ReadinessState.BLOCKED_OWNER_PERMISSION, result.state)
        self.assertEqual(DirectPermissionState.READING, result.direct_permission)
        self.assertEqual("DIRECT_PROVIDER", result.direct_permission_source)
        self.assertFalse(result.provider_write_allowed)
        self.assertEqual(0, result.real_provider_requests)
        self.assertEqual(0, result.advertising_spend)
        self.assertFalse(result.production_writer_enabled)
        self.assertTrue(result.integrity_valid)

    def test_unknown_provider_permission_fails_closed(self):
        result = build_day12_launch_readiness(diagnostics=diagnostics())
        self.assertEqual(Day12ReadinessState.BLOCKED_OWNER_PERMISSION, result.state)
        self.assertEqual(DirectPermissionState.UNKNOWN, result.direct_permission)
        self.assertIn("direct_editing_permission_not_provider_confirmed", result.reasons)

    def test_manager_ui_path_requires_owner_evidence(self):
        input_diagnostics = diagnostics(
            direct_permission="UNKNOWN",
            manager_ui_required=True,
        )
        self.assertTrue(manager_ui_permission_required(input_diagnostics))
        result = build_day12_launch_readiness(diagnostics=input_diagnostics)
        self.assertEqual(Day12ReadinessState.BLOCKED_OWNER_PERMISSION, result.state)
        self.assertEqual("OWNER_UI_EVIDENCE_REQUIRED", result.direct_permission_source)
        self.assertIn("direct_manager_editing_owner_ui_evidence_required", result.reasons)

    def test_manager_ui_owner_evidence_can_only_advance_to_candidate_selection(self):
        result = build_day12_launch_readiness(
            diagnostics=diagnostics(
                direct_permission="UNKNOWN",
                manager_ui_required=True,
            ),
            owner_permission_evidence=owner_editing_evidence(),
        )
        self.assertEqual(DirectPermissionState.EDITING, result.direct_permission)
        self.assertEqual("OWNER_UI_EVIDENCE", result.direct_permission_source)
        self.assertEqual(Day12ReadinessState.READY_FOR_LIVE_CANDIDATE_SELECTION, result.state)
        self.assertFalse(result.provider_write_allowed)
        self.assertFalse(result.production_writer_enabled)
        self.assertEqual(0, result.real_provider_requests)
        self.assertEqual(0, result.advertising_spend)

    def test_owner_evidence_does_not_override_provider_reading_outside_manager_path(self):
        result = build_day12_launch_readiness(
            diagnostics=diagnostics(direct_permission="READING"),
            owner_permission_evidence=owner_editing_evidence(),
        )
        self.assertEqual(DirectPermissionState.READING, result.direct_permission)
        self.assertEqual(Day12ReadinessState.BLOCKED_OWNER_PERMISSION, result.state)

    def test_observed_permission_is_extracted_from_direct_doctor(self):
        self.assertEqual(
            DirectPermissionState.EDITING,
            observed_direct_permission(diagnostics(direct_permission="EDITING")),
        )
        self.assertEqual(
            DirectPermissionState.READING,
            observed_direct_permission(diagnostics(direct_permission="READING")),
        )
        self.assertEqual(
            DirectPermissionState.UNKNOWN,
            observed_direct_permission(diagnostics(direct_permission="unexpected")),
        )

    def test_manual_permission_override_is_not_an_api(self):
        with self.assertRaises(TypeError):
            build_day12_launch_readiness(
                direct_permission=DirectPermissionState.EDITING,
                diagnostics=diagnostics(),
            )

    def test_observed_editing_advances_without_manual_permission_flag(self):
        result = build_day12_launch_readiness(
            diagnostics=diagnostics(direct_permission="EDITING"),
        )
        self.assertEqual(DirectPermissionState.EDITING, result.direct_permission)
        self.assertEqual(Day12ReadinessState.READY_FOR_LIVE_CANDIDATE_SELECTION, result.state)
        self.assertFalse(result.provider_write_allowed)

    def test_wrong_controller_sha_blocks_before_permission(self):
        result = build_day12_launch_readiness(
            diagnostics=diagnostics(direct_permission="EDITING"),
            controller_sha="0" * 40,
        )
        self.assertEqual(Day12ReadinessState.BLOCKED_CONTROLLER_ACCEPTANCE, result.state)
        self.assertIn("accepted_task_011r_sha_mismatch", result.reasons)

    def test_missing_provider_result_is_not_attempted_and_blocks(self):
        result = build_day12_launch_readiness(
            diagnostics=(
                DiagnosticResult("direct", DoctorStatus.PASS, checks=("direct.permission=EDITING",)),
                DiagnosticResult("metrica", DoctorStatus.PASS),
            ),
        )
        self.assertEqual(Day12ReadinessState.BLOCKED_PROVIDER_CERTIFICATION, result.state)
        self.assertIn("yan_statistics:NOT_ATTEMPTED", result.reasons)

    def test_any_provider_failure_blocks(self):
        for provider, kwargs in (
            ("direct", {"direct": DoctorStatus.BLOCKED_ACCESS}),
            ("metrica", {"metrica": DoctorStatus.BLOCKED_MISSING_CREDENTIAL}),
            ("yan_statistics", {"yan": DoctorStatus.PROVIDER_ERROR}),
        ):
            with self.subTest(provider=provider):
                result = build_day12_launch_readiness(
                    diagnostics=diagnostics(direct_permission="EDITING", **kwargs),
                )
                self.assertEqual(Day12ReadinessState.BLOCKED_PROVIDER_CERTIFICATION, result.state)
                self.assertTrue(any(reason.startswith(provider + ":") for reason in result.reasons))
                self.assertFalse(result.provider_write_allowed)

    def test_all_gates_pass_only_to_candidate_selection_not_write(self):
        result = build_day12_launch_readiness(
            diagnostics=diagnostics(direct_permission="EDITING"),
            controller_sha=ACCEPTED_TASK_011R_SHA,
        )
        self.assertEqual(Day12ReadinessState.READY_FOR_LIVE_CANDIDATE_SELECTION, result.state)
        self.assertFalse(result.provider_write_allowed)
        self.assertEqual(0, result.real_provider_requests)
        self.assertEqual(0, result.advertising_spend)
        self.assertFalse(result.production_writer_enabled)
        self.assertTrue(result.integrity_valid)

    def test_digest_tamper_detection(self):
        result = build_day12_launch_readiness(
            diagnostics=diagnostics(direct_permission="READING"),
        )
        from dataclasses import replace
        self.assertFalse(replace(result, readiness_digest="0" * 64).integrity_valid)


if __name__ == "__main__":
    unittest.main()
