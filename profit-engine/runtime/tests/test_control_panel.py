from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from profit_engine_runtime import control_panel


class ControlPanelTests(unittest.TestCase):
    def test_completed_window_is_exact_length(self):
        start, end = control_panel.completed_window(30)
        from datetime import date
        self.assertEqual(29, (date.fromisoformat(end) - date.fromisoformat(start)).days)

    def test_missing_private_config_fails_closed_without_provider_calls(self):
        with tempfile.TemporaryDirectory() as directory:
            snapshot = Path(directory) / "snapshot.json"
            control_dir = Path(directory) / "control"
            with patch.object(control_panel, "SNAPSHOT_PATH", snapshot), patch.object(
                control_panel, "CONTROL_DIR", control_dir
            ), patch.object(control_panel, "run_campaign_inventory") as inventory, patch.object(
                control_panel, "run_metrica_yan_probe"
            ) as compatibility, patch.object(control_panel, "audit_goals") as goals:
                value = control_panel.collect_snapshot(Path(directory) / "missing.json")
            self.assertEqual("BLOCKED_LOCAL_CONFIG", value["state"])
            self.assertFalse(value["provider_write_allowed"])
            self.assertEqual("LOCKED", value["writer_state"])
            self.assertEqual("STOP", value["owner_advice"]["primary_action"]["severity"])
            inventory.assert_not_called()
            compatibility.assert_not_called()
            goals.assert_not_called()

    def test_panel_is_decision_first_and_has_no_provider_write_endpoint(self):
        html = control_panel.HTML
        self.assertIn("Пульт прибыли", html)
        self.assertIn("Что делать сейчас", html)
        self.assertIn("Приоритетные действия", html)
        self.assertIn("Сделать", html)
        self.assertIn("Зачем", html)
        self.assertIn("Не делать", html)
        self.assertIn("Ручной Яндекс Поиск", html)
        self.assertIn("WRITER LOCKED", html)
        self.assertIn("/api/refresh", html)
        self.assertNotIn("/api/write", html)
        self.assertNotIn("/api/suspend", html)
        self.assertNotIn("/api/resume", html)
        self.assertNotIn("/api/bid", html)

    def test_panel_does_not_present_pe_goals_as_owner_work(self):
        html = control_panel.HTML
        self.assertIn("Используем существующие dv_*", html)
        self.assertNotIn("PE · История 75%", html)
        self.assertNotIn("pe_story_progress_75", html)


if __name__ == "__main__":
    unittest.main()
