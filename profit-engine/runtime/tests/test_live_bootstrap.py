from __future__ import annotations

import json
import stat
import tempfile
import unittest
from pathlib import Path

from profit_engine_runtime.live_bootstrap import DIRECT_OPERATOR_LOGIN, build_live_config, write_live_config


TARGET_LOGIN = "owner-advertiser-fixture"


class LiveBootstrapTests(unittest.TestCase):
    def test_live_bootstrap_writes_expected_non_secret_binding(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "dilivox.json"
            expected = build_live_config(TARGET_LOGIN)
            written = write_live_config(path, direct_target_login=TARGET_LOGIN)
            self.assertEqual(path, written)
            data = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(expected, data)
            self.assertEqual("READ_ONLY", data["rollout_mode"])
            self.assertEqual(DIRECT_OPERATOR_LOGIN, data["providers"]["direct"]["operator_login_ref"])
            self.assertEqual(TARGET_LOGIN, data["providers"]["direct"]["client_login_ref"])
            self.assertNotEqual(
                data["providers"]["direct"]["operator_login_ref"],
                data["providers"]["direct"]["client_login_ref"],
            )
            self.assertEqual("110349067", data["providers"]["metrica"]["counter_ref"])
            self.assertEqual(
                "keychain:ProfitEngine-YandexOAuth-Read/profit-engine",
                data["providers"]["direct"]["token_source_ref"],
            )
            self.assertEqual(
                "keychain:ProfitEngine-YAN-Statistics/profit-engine",
                data["providers"]["yan_statistics"]["token_source_ref"],
            )
            self.assertEqual(0o600, stat.S_IMODE(path.stat().st_mode))
            text = path.read_text(encoding="utf-8")
            self.assertNotIn("access_token", text)
            self.assertNotIn("Bearer ", text)

    def test_operator_login_cannot_be_reused_as_managed_target(self):
        with self.assertRaises(ValueError):
            build_live_config(DIRECT_OPERATOR_LOGIN)
        with self.assertRaises(ValueError):
            build_live_config("   ")

    def test_live_bootstrap_is_idempotent_for_exact_config(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "dilivox.json"
            expected = build_live_config(TARGET_LOGIN)
            write_live_config(path, direct_target_login=TARGET_LOGIN)
            write_live_config(path, direct_target_login=TARGET_LOGIN)
            self.assertEqual(expected, json.loads(path.read_text(encoding="utf-8")))

    def test_live_bootstrap_refuses_to_overwrite_different_config_without_force(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "dilivox.json"
            path.write_text('{"rollout_mode":"READ_ONLY"}\n', encoding="utf-8")
            path.chmod(0o600)
            with self.assertRaises(FileExistsError):
                write_live_config(path, direct_target_login=TARGET_LOGIN)
            write_live_config(path, direct_target_login=TARGET_LOGIN, force=True)
            self.assertEqual(
                build_live_config(TARGET_LOGIN),
                json.loads(path.read_text(encoding="utf-8")),
            )


if __name__ == "__main__":
    unittest.main()
