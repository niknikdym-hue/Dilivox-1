from __future__ import annotations

import unittest

from profit_engine_runtime.day12_readiness import (
    ACCEPTED_TASK_011R_SHA,
    Day12ReadinessState,
    DirectPermissionState,
    build_day12_launch_readiness,
    observed_direct_permission,
)
from profit_engine_runtime.models import DiagnosticResult, DoctorStatus


def diagnostics(
    *,
    direct=DoctorStatus.PASS,
    metrica=DoctorStatus.PASS,
    yan=DoctorStatus.PASS,
    direct_permission: str | None = None,
):
    direct_checks = () if direct_permission is None else (f"direct.permission={direct_permission}",)
    return (
        DiagnosticResult("direct", direct, checks=direct_checks),
        DiagnosticResult("metrica", metrica),
        DiagnosticResult("yan_statistics", yan),
    )


class Day12ReadinessTests(unittest.TestCase):
    def test_reading_permission_blocks_even_when_all_doctors_pass(self):
        result = build_day12_launch_readiness(
            direct_permission=DirectPermissionState.READING,
            diagnostics=diagnostics(),
        )
        self.assertEqual(Day12ReadinessState.BLOCKED_OWNER_PERMISSION, result.state)
        self.assertFalse(result.provider_write_allowed)
        self.assertEqual(0, result.real_provider_requests)
        self.assertEqual(0, result.advertising_spend)
        self.assertFalse(result.production_writer_enabled)
        self.assertTrue(result.integrity_valid)

    def test_unknown_permission_fails_closed(self):
        result = build_day12_launch_readiness(
            diagnostics=diagnostics(),
        )
        self.assertEqual(Day12ReadinessState.BLOCKED_OWNER_PERMISSION, result.state)
        self.assertEqual(DirectPermissionState.UNKNOWN, result.direct_permission)

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

    def test_observed_reading_cannot_be_overridden_by_manual_editing(self):
        result = build_day12_launch_readiness(
            direct_permission=DirectPermissionState.EDITING,
            diagnostics=diagnostics(direct_permission="READING"),
        )
        self.assertEqual(DirectPermissionState.READING, result.direct_permission)
        self.assertEqual(Day12ReadinessState.BLOCKED_OWNER_PERMISSION, result.state)

    def test_observed_editing_advances_without_manual_permission_flag(self):
        result = build_day12_launch_readiness(
            diagnostics=diagnostics(direct_permission="EDITING"),
        )
        self.assertEqual(DirectPermissionState.EDITING, result.direct_permission)
        self.assertEqual(Day12ReadinessState.READY_FOR_LIVE_CANDIDATE_SELECTION, result.state)
        self.assertFalse(result.provider_write_allowed)

    def test_wrong_controller_sha_blocks_before_permission(self):
        result = build_day12_launch_readiness(
            direct_permission=DirectPermissionState.EDITING,
            diagnostics=diagnostics(),
            controller_sha="0" * 40,
        )
        self.assertEqual(Day12ReadinessState.BLOCKED_CONTROLLER_ACCEPTANCE, result.state)
        self.assertIn("accepted_task_011r_sha_mismatch", result.reasons)

    def test_missing_provider_result_is_not_attempted_and_blocks(self):
        result = build_day12_launch_readiness(
            direct_permission=DirectPermissionState.EDITING,
            diagnostics=(DiagnosticResult("direct", DoctorStatus.PASS), DiagnosticResult("metrica", DoctorStatus.PASS)),
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
                    direct_permission=DirectPermissionState.EDITING,
                    diagnostics=diagnostics(**kwargs),
                )
                self.assertEqual(Day12ReadinessState.BLOCKED_PROVIDER_CERTIFICATION, result.state)
                self.assertTrue(any(reason.startswith(provider + ":") for reason in result.reasons))
                self.assertFalse(result.provider_write_allowed)

    def test_all_gates_pass_only_to_candidate_selection_not_write(self):
        result = build_day12_launch_readiness(
            direct_permission=DirectPermissionState.EDITING,
            diagnostics=diagnostics(),
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
            direct_permission=DirectPermissionState.READING,
            diagnostics=diagnostics(),
        )
        from dataclasses import replace
        self.assertFalse(replace(result, readiness_digest="0" * 64).integrity_valid)


if __name__ == "__main__":
    unittest.main()
