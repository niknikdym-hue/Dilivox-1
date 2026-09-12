from __future__ import annotations

import unittest

from profit_engine_runtime.development_status import (
    DEV_WORKFLOW_PATH,
    PREFLIGHT_WORKFLOW_PATH,
    _latest_workflow_run,
    collect_development_status,
)
from profit_engine_runtime.owner_control_v2 import HTML, build_html


class OwnerControlV2Tests(unittest.TestCase):
    def test_development_status_is_read_only_and_budgeted(self) -> None:
        status = collect_development_status(fetch_remote=False)
        self.assertTrue(status["read_only"])
        self.assertFalse(status["provider_write_allowed"])
        self.assertEqual(status["initial_openai_dev_envelope_usd"], 10.0)
        self.assertEqual(status["default_package_hard_cap_usd"], 3.0)
        self.assertEqual(status["dev_ai_cost_usd"], 0.0)
        self.assertEqual(status["remaining_dev_envelope_usd"], 10.0)
        self.assertEqual(status["dev_ai_cost_state"], "ACCEPTED_LEDGER")

    def test_workflow_identity_uses_path_not_dynamic_run_name(self) -> None:
        payload = {
            "workflow_runs": [
                {
                    "id": 1,
                    "name": "DILIVOX dev preflight · dynamic branch name",
                    "path": PREFLIGHT_WORKFLOW_PATH,
                    "status": "completed",
                    "conclusion": "success",
                },
                {
                    "id": 2,
                    "name": "DILIVOX bounded dev · changing title",
                    "path": DEV_WORKFLOW_PATH,
                    "status": "in_progress",
                    "conclusion": None,
                },
            ]
        }
        self.assertEqual(_latest_workflow_run(payload, PREFLIGHT_WORKFLOW_PATH)["id"], 1)
        self.assertEqual(_latest_workflow_run(payload, DEV_WORKFLOW_PATH)["id"], 2)

    def test_single_panel_contains_dev_visibility(self) -> None:
        html = build_html()
        self.assertIn("Разработка · API Codex", html)
        self.assertIn('id="devApiState"', html)
        self.assertIn('id="devEnvelope"', html)
        self.assertIn('id="devSpent"', html)
        self.assertIn("renderDevelopment", html)
        self.assertEqual(html, HTML)

    def test_panel_does_not_gain_provider_write_controls(self) -> None:
        self.assertNotIn("Direct.write", HTML)
        self.assertNotIn("YAN.write", HTML)
        self.assertIn("provider-write endpoint", HTML.lower())


if __name__ == "__main__":
    unittest.main()
