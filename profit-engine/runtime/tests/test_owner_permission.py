from __future__ import annotations

from datetime import datetime, timezone
import json
import stat
import tempfile
import unittest
from pathlib import Path

from profit_engine_runtime.owner_permission import (
    SCHEMA_VERSION,
    SOURCE,
    build_owner_permission_payload,
    evidence_digest,
    load_owner_permission_evidence,
    record_owner_permission_evidence,
    target_login_sha256,
)


OPERATOR = "reklamadymova"
TARGET = "owner-advertiser-fixture"
NOW = datetime(2026, 8, 29, 0, 50, tzinfo=timezone.utc)


def payload(*, confirmed_at="2026-08-29T00:30:00Z", permission="EDITING", target=TARGET):
    value = {
        "schema_version": SCHEMA_VERSION,
        "permission": permission,
        "operator_login": OPERATOR,
        "target_login_sha256": target_login_sha256(target),
        "source": SOURCE,
        "owner_confirmed": True,
        "confirmed_at": confirmed_at,
    }
    return {**value, "evidence_digest": evidence_digest(value)}


class OwnerPermissionEvidenceTests(unittest.TestCase):
    def write(self, directory: str, value: dict[str, object], mode=0o600) -> Path:
        path = Path(directory) / "permission.json"
        path.write_text(json.dumps(value), encoding="utf-8")
        path.chmod(mode)
        return path

    def test_recorder_requires_explicit_owner_confirmation(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "permission.json"
            with self.assertRaises(ValueError):
                record_owner_permission_evidence(
                    path,
                    operator_login=OPERATOR,
                    target_login=TARGET,
                    confirmed_at=NOW,
                    owner_confirmed=False,
                )
            self.assertFalse(path.exists())

    def test_recorder_writes_atomic_0600_hash_bound_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "nested" / "permission.json"
            recorded = record_owner_permission_evidence(
                path,
                operator_login=OPERATOR,
                target_login=TARGET,
                confirmed_at=NOW,
                owner_confirmed=True,
            )
            self.assertEqual(path, recorded)
            self.assertEqual(0o600, stat.S_IMODE(path.stat().st_mode))
            text = path.read_text(encoding="utf-8")
            self.assertNotIn(TARGET, text)
            self.assertIn(target_login_sha256(TARGET), text)
            evidence = load_owner_permission_evidence(
                path,
                operator_login=OPERATOR,
                target_login=TARGET,
                now=NOW,
            )
            self.assertEqual("EDITING", evidence.permission)
            self.assertTrue(evidence.owner_confirmed)
            leftovers = [item.name for item in path.parent.iterdir() if item != path]
            self.assertEqual([], leftovers)

    def test_recorder_rejects_operator_target_alias(self):
        with self.assertRaises(ValueError):
            build_owner_permission_payload(
                operator_login=OPERATOR,
                target_login="ReklamaDymova",
                confirmed_at=NOW,
                owner_confirmed=True,
            )

    def test_valid_fresh_exact_evidence_loads(self):
        with tempfile.TemporaryDirectory() as directory:
            evidence = load_owner_permission_evidence(
                self.write(directory, payload()),
                operator_login=OPERATOR,
                target_login=TARGET,
                now=NOW,
            )
        self.assertEqual("EDITING", evidence.permission)
        self.assertTrue(evidence.owner_confirmed)

    def test_permissions_must_be_0600(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.write(directory, payload(), mode=0o644)
            with self.assertRaises(ValueError):
                load_owner_permission_evidence(path, operator_login=OPERATOR, target_login=TARGET, now=NOW)

    def test_target_binding_is_exact_and_not_plaintext_in_evidence(self):
        value = payload()
        self.assertNotIn(TARGET, json.dumps(value))
        with tempfile.TemporaryDirectory() as directory:
            path = self.write(directory, value)
            with self.assertRaises(ValueError):
                load_owner_permission_evidence(path, operator_login=OPERATOR, target_login="different", now=NOW)

    def test_reading_never_passes(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.write(directory, payload(permission="READING"))
            with self.assertRaises(ValueError):
                load_owner_permission_evidence(path, operator_login=OPERATOR, target_login=TARGET, now=NOW)

    def test_stale_future_and_tampered_evidence_fail_closed(self):
        cases = [
            payload(confirmed_at="2026-08-27T00:00:00Z"),
            payload(confirmed_at="2026-08-29T01:30:00Z"),
        ]
        tampered = payload()
        tampered["owner_confirmed"] = False
        cases.append(tampered)
        for index, value in enumerate(cases):
            with self.subTest(index=index), tempfile.TemporaryDirectory() as directory:
                path = self.write(directory, value)
                with self.assertRaises(ValueError):
                    load_owner_permission_evidence(path, operator_login=OPERATOR, target_login=TARGET, now=NOW)

    def test_unexpected_fields_fail_closed(self):
        value = payload()
        value["write_authority"] = True
        with tempfile.TemporaryDirectory() as directory:
            path = self.write(directory, value)
            with self.assertRaises(ValueError):
                load_owner_permission_evidence(path, operator_login=OPERATOR, target_login=TARGET, now=NOW)


if __name__ == "__main__":
    unittest.main()
