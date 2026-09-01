from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from profit_engine_runtime import metrica_goals_cli as goals


REGISTRY = {
    "schema_version": "1.0",
    "site_id": "dilivox",
    "goals": [
        {
            "key": "story_completed",
            "name": "PE · История завершена",
            "identifier": "pe_story_completed",
            "metrica_type": "action",
            "condition_type": "exact",
            "role": "high_value_proxy",
            "native_bidding_eligible": False,
        },
        {
            "key": "next_story_clicked",
            "name": "PE · Следующая история",
            "identifier": "pe_next_story_clicked",
            "metrica_type": "action",
            "condition_type": "exact",
            "role": "recirculation_proxy",
            "native_bidding_eligible": False,
        },
    ],
}


class MetricaGoalsTests(unittest.TestCase):
    def fixture_paths(self):
        directory = tempfile.TemporaryDirectory()
        root = Path(directory.name)
        config = root / "dilivox.json"
        config.write_text(json.dumps({
            "site_id": "dilivox",
            "canonical_domain": "dilivox.ru",
            "rollout_mode": "READ_ONLY",
            "providers": {
                "direct": {
                    "token_source_ref": "env:TEST_TOKEN",
                    "operator_login_ref": "manager",
                    "client_login_ref": "target",
                },
                "metrica": {"counter_ref": "110349067"},
                "yan_statistics": {},
            },
        }), encoding="utf-8")
        config.chmod(0o600)
        registry = root / "goals.json"
        registry.write_text(json.dumps(REGISTRY, ensure_ascii=False), encoding="utf-8")
        return directory, config, registry

    def test_audit_passes_only_exact_action_goals(self):
        directory, config, registry = self.fixture_paths()
        self.addCleanup(directory.cleanup)
        provider = {
            "goals": [
                {"type": "action", "conditions": [{"type": "exact", "url": "pe_story_completed"}]},
                {"type": "action", "conditions": [{"type": "exact", "url": "pe_next_story_clicked"}]},
                {"type": "url", "conditions": [{"type": "contain", "url": "/other"}]},
            ]
        }
        with patch.object(goals, "resolve_secret", return_value="secret-token"), patch.object(
            goals, "_request_json", return_value=(200, provider)
        ):
            result = goals.audit_goals(config_path=config, goals_path=registry)
        self.assertEqual("PASS", result["state"])
        self.assertEqual(2, result["expected_goal_count"])
        self.assertEqual(3, result["provider_goal_count"])
        self.assertFalse(result["provider_write_allowed"])
        self.assertEqual(0, result["provider_write_requests"])

    def test_audit_reports_missing_duplicate_and_wrong_type(self):
        directory, config, registry = self.fixture_paths()
        self.addCleanup(directory.cleanup)
        provider = {
            "goals": [
                {"type": "url", "conditions": [{"type": "exact", "url": "pe_story_completed"}]},
                {"type": "action", "conditions": [{"type": "exact", "url": "pe_story_completed"}]},
            ]
        }
        with patch.object(goals, "resolve_secret", return_value="secret-token"), patch.object(
            goals, "_request_json", return_value=(200, provider)
        ):
            result = goals.audit_goals(config_path=config, goals_path=registry)
        self.assertEqual("REWORK_REQUIRED", result["state"])
        self.assertIn("pe_story_completed", result["duplicate_identifiers"])
        self.assertIn("pe_next_story_clicked", result["missing_identifiers"])

    def test_live_create_payload_is_minimal_and_omits_is_favorite(self):
        payload = goals._action_goal_create_payload(REGISTRY["goals"][0])
        self.assertEqual(
            {
                "goal": {
                    "name": "PE · История завершена",
                    "type": "action",
                    "conditions": [{"type": "exact", "url": "pe_story_completed"}],
                }
            },
            payload,
        )
        self.assertNotIn("is_favorite", payload["goal"])
        self.assertNotIn("id", payload["goal"])
        self.assertNotIn("status", payload["goal"])
        self.assertNotIn("default_price", payload["goal"])

    def test_apply_creates_only_missing_then_requires_pass_readback(self):
        directory, config, registry = self.fixture_paths()
        self.addCleanup(directory.cleanup)
        before = {
            "mode": "DILIVOX_METRICA_GOALS_AUDIT_READ_ONLY",
            "state": "REWORK_REQUIRED",
            "missing_identifiers": ["pe_next_story_clicked"],
            "invalid_identifiers": [],
            "duplicate_identifiers": [],
        }
        after = {
            "mode": "DILIVOX_METRICA_GOALS_AUDIT_READ_ONLY",
            "state": "PASS",
            "missing_identifiers": [],
            "invalid_identifiers": [],
            "duplicate_identifiers": [],
        }
        calls = []

        def request_json(request):
            calls.append(request)
            return 200, {"goal": {"type": "action"}}

        with patch.object(goals, "resolve_secret", return_value="secret-token"), patch.object(
            goals, "audit_goals", side_effect=[before, after]
        ), patch.object(goals, "_request_json", side_effect=request_json):
            result = goals.apply_missing_goals(config_path=config, goals_path=registry)
        self.assertEqual("APPLIED_AND_VERIFIED", result["state"])
        self.assertEqual(["pe_next_story_clicked"], result["created"])
        self.assertEqual(1, result["provider_write_requests"])
        self.assertEqual("POST", calls[0].method)
        body = json.loads(calls[0].data.decode("utf-8"))
        self.assertEqual({"name", "type", "conditions"}, set(body["goal"]))
        self.assertNotIn("is_favorite", body["goal"])
        self.assertEqual("application/json; charset=utf-8", calls[0].headers["Content-type"])

    def test_registry_rejects_duplicate_identifiers(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "goals.json"
            broken = dict(REGISTRY)
            broken["goals"] = [REGISTRY["goals"][0], dict(REGISTRY["goals"][0])]
            path.write_text(json.dumps(broken), encoding="utf-8")
            with self.assertRaises(ValueError):
                goals._load_registry(path)


if __name__ == "__main__":
    unittest.main()
