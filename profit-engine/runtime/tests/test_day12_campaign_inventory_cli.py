import json
import tempfile
import unittest
from pathlib import Path

from profit_engine_runtime.day12_campaign_inventory_cli import run_campaign_inventory
from profit_engine_runtime.models import HttpResponse


TOKEN = "fixture-direct-token-value"


class FakeTransport:
    def __init__(self, responses):
        self.responses = list(responses)
        self.requests = []

    def send(self, request):
        self.requests.append(request)
        return self.responses.pop(0)


class CampaignInventoryCliTests(unittest.TestCase):
    def config_path(self, directory: str) -> Path:
        path = Path(directory) / "dilivox.json"
        path.write_text(json.dumps({
            "site_id": "dilivox",
            "canonical_domain": "dilivox.ru",
            "rollout_mode": "READ_ONLY",
            "providers": {
                "direct": {
                    "endpoint": "https://api.direct.yandex.com/json/v501",
                    "token_source_ref": "keychain:direct/account",
                    "operator_login_ref": "reklamadymova",
                    "client_login_ref": "owner-advertiser-fixture"
                },
                "metrica": {},
                "yan_statistics": {}
            }
        }), encoding="utf-8")
        path.chmod(0o600)
        return path

    def test_cli_prints_exact_ids_states_but_no_token(self):
        transport = FakeTransport([
            HttpResponse(200, {"RequestId": "req-1", "Units": "1/99/1000"}, {
                "result": {"Campaigns": [
                    {"Id": 101, "Name": "Campaign A", "Type": "TEXT_CAMPAIGN", "State": "ON", "Status": "ACCEPTED"},
                    {"Id": 102, "Name": "Campaign B", "Type": "UNIFIED_CAMPAIGN", "State": "SUSPENDED", "Status": "ACCEPTED"}
                ]}
            }, "req-1")
        ])
        with tempfile.TemporaryDirectory() as directory:
            public = run_campaign_inventory(
                config_path=self.config_path(directory),
                transport=transport,
                secret_resolver=lambda ref: TOKEN if ref == "keychain:direct/account" else None,
            )
        text = json.dumps(public)
        self.assertNotIn(TOKEN, text)
        self.assertEqual("DAY12_DIRECT_CAMPAIGN_INVENTORY_READ_ONLY", public["mode"])
        self.assertEqual(2, public["total_campaigns"])
        self.assertEqual("101", public["campaigns"][0]["campaign_id"])
        self.assertEqual("ACTIVE", public["campaigns"][0]["state"])
        self.assertEqual("102", public["campaigns"][1]["campaign_id"])
        self.assertEqual("SUSPENDED", public["campaigns"][1]["state"])
        self.assertFalse(public["provider_write_allowed"])
        self.assertFalse(public["candidate_selected"])
        self.assertFalse(public["credential_values_printed"])

    def test_missing_config_or_credential_blocks_before_network(self):
        transport = FakeTransport([])
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(FileNotFoundError):
                run_campaign_inventory(
                    config_path=Path(directory) / "missing.json",
                    transport=transport,
                    secret_resolver=lambda _ref: TOKEN,
                )
            path = self.config_path(directory)
            with self.assertRaises(ValueError):
                run_campaign_inventory(
                    config_path=path,
                    transport=transport,
                    secret_resolver=lambda _ref: None,
                )
        self.assertEqual([], transport.requests)

    def test_operator_target_alias_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.config_path(directory)
            data = json.loads(path.read_text(encoding="utf-8"))
            data["providers"]["direct"]["client_login_ref"] = "ReklamaDymova"
            path.write_text(json.dumps(data), encoding="utf-8")
            path.chmod(0o600)
            with self.assertRaises(ValueError):
                run_campaign_inventory(
                    config_path=path,
                    transport=FakeTransport([]),
                    secret_resolver=lambda _ref: TOKEN,
                )


if __name__ == "__main__":
    unittest.main()
