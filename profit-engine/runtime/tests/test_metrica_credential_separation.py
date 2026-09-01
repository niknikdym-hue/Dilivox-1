from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from profit_engine_runtime.config import DEFAULT_METRICA_WRITE_TOKEN_REF, load_site_config
from profit_engine_runtime import metrica_goals_cli as goals


class MetricaCredentialSeparationTests(unittest.TestCase):
    def _config(self) -> tuple[tempfile.TemporaryDirectory, Path]:
        directory = tempfile.TemporaryDirectory()
        path = Path(directory.name) / "dilivox.json"
        path.write_text(json.dumps({
            "site_id": "dilivox",
            "canonical_domain": "dilivox.ru",
            "rollout_mode": "READ_ONLY",
            "providers": {
                "direct": {
                    "token_source_ref": "keychain:DirectRead/profit-engine",
                    "operator_login_ref": "manager",
                    "client_login_ref": "target",
                },
                "metrica": {
                    "token_source_ref": "keychain:MetricaRead/profit-engine",
                    "write_token_source_ref": "keychain:MetricaWrite/profit-engine",
                    "counter_ref": "110349067",
                },
                "yan_statistics": {"token_source_ref": "keychain:YanRead/profit-engine"},
            },
        }), encoding="utf-8")
        path.chmod(0o600)
        return directory, path

    def test_config_preserves_three_provider_credentials_and_metrica_write(self) -> None:
        directory, path = self._config(); self.addCleanup(directory.cleanup)
        config, present = load_site_config(path)
        self.assertTrue(present)
        self.assertEqual("keychain:DirectRead/profit-engine", config.yandex_oauth_token_ref)
        self.assertEqual("keychain:MetricaRead/profit-engine", config.metrica_oauth_token_ref)
        self.assertEqual("keychain:MetricaWrite/profit-engine", config.metrica_write_token_ref)
        self.assertEqual("keychain:YanRead/profit-engine", config.yan_stats_token_ref)

    def test_write_token_defaults_to_dedicated_keychain_not_direct_token(self) -> None:
        directory, path = self._config(); self.addCleanup(directory.cleanup)
        value = json.loads(path.read_text(encoding="utf-8"))
        del value["providers"]["metrica"]["write_token_source_ref"]
        path.write_text(json.dumps(value), encoding="utf-8"); path.chmod(0o600)
        config, _ = load_site_config(path)
        self.assertEqual(DEFAULT_METRICA_WRITE_TOKEN_REF, config.metrica_write_token_ref)
        self.assertNotEqual(config.yandex_oauth_token_ref, config.metrica_write_token_ref)

    def test_missing_write_token_blocks_before_provider_post(self) -> None:
        directory, config_path = self._config(); self.addCleanup(directory.cleanup)
        registry_path = Path(directory.name) / "goals.json"
        registry_path.write_text(json.dumps({
            "schema_version": "1.0", "site_id": "dilivox", "goals": [{
                "key": "story_completed", "name": "PE · История завершена",
                "identifier": "pe_story_completed", "metrica_type": "action",
                "condition_type": "exact", "role": "high_value_proxy",
                "native_bidding_eligible": False,
            }]
        }, ensure_ascii=False), encoding="utf-8")
        before = {
            "state": "REWORK_REQUIRED", "missing_identifiers": ["pe_story_completed"],
            "invalid_identifiers": [], "duplicate_identifiers": [],
        }
        def resolver(ref: str) -> str | None:
            return None if "MetricaWrite" in ref else "read-token"
        with patch.object(goals, "audit_goals", return_value=before), patch.object(
            goals, "resolve_secret", side_effect=resolver
        ), patch.object(goals, "_request_json") as request_json:
            result = goals.apply_missing_goals(config_path=config_path, goals_path=registry_path)
        self.assertEqual(goals.WRITE_TOKEN_REQUIRED, result["state"])
        self.assertEqual(0, result["provider_write_requests"])
        request_json.assert_not_called()


if __name__ == "__main__":
    unittest.main()
