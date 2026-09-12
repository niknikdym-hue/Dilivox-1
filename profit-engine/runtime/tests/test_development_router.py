from __future__ import annotations

import unittest

from profit_engine_runtime.development_router import (
    INITIAL_OPENAI_DEV_ENVELOPE_USD,
    classify_task,
    route_manifest,
)


class DevelopmentRouterTests(unittest.TestCase):
    def test_deterministic_quality_equivalent_is_free(self) -> None:
        route = classify_task(
            {
                "task_id": "T-FREE",
                "deterministic": True,
                "free_quality_equivalent": True,
                "quality_floor": "exact",
            }
        )
        self.assertEqual(route.execution_route, "G0")
        self.assertIsNone(route.model_route)
        self.assertEqual(route.hard_cap_usd, "0.00")
        self.assertFalse(route.owner_approval_required)

    def test_new_code_routes_directly_to_terra(self) -> None:
        route = classify_task(
            {
                "task_id": "T-CODE",
                "new_code": True,
                "quality_floor": "production-grade",
            }
        )
        self.assertEqual(route.execution_route, "G2")
        self.assertEqual(route.model_route, "gpt-5.6-terra")
        self.assertIn("not confidently sufficient", route.why_not_cheaper or "")

    def test_high_risk_routes_directly_to_sol(self) -> None:
        route = classify_task(
            {
                "task_id": "T-RISK",
                "title": "Money reconciliation and idempotency",
                "quality_floor": "capital-safe",
            }
        )
        self.assertEqual(route.execution_route, "G3")
        self.assertEqual(route.model_route, "gpt-5.6-sol")
        self.assertEqual(route.hard_cap_usd, "3.00")

    def test_astra_is_not_auto_authorized(self) -> None:
        route = classify_task(
            {
                "task_id": "T-ASTRA",
                "architecture": True,
                "astra_justified": True,
            }
        )
        self.assertEqual(route.execution_route, "G4")
        self.assertEqual(route.model_route, "gpt-6-astra")
        self.assertTrue(route.owner_approval_required)
        self.assertIsNone(route.hard_cap_usd)

    def test_explicit_sol_is_respected_without_cheaper_trial(self) -> None:
        route = classify_task(
            {
                "task_id": "T-EXPLICIT",
                "model_route": "sol",
                "quality_floor": "high",
            }
        )
        self.assertEqual(route.execution_route, "G3")
        self.assertEqual(route.model_route, "gpt-5.6-sol")

    def test_manifest_locks_safety_defaults(self) -> None:
        manifest = route_manifest({"task_id": "T1", "new_code": True})
        self.assertEqual(manifest["initial_openai_dev_envelope_usd"], f"{INITIAL_OPENAI_DEV_ENVELOPE_USD:.2f}")
        self.assertFalse(manifest["free_first"])
        self.assertTrue(manifest["quality_first"])
        self.assertFalse(manifest["auto_paid_retry"])
        self.assertFalse(manifest["auto_merge"])
        self.assertFalse(manifest["auto_deploy"])

    def test_unknown_explicit_route_fails(self) -> None:
        with self.assertRaises(ValueError):
            classify_task({"task_id": "BAD", "model_route": "cheapest-model-ever"})


if __name__ == "__main__":
    unittest.main()
