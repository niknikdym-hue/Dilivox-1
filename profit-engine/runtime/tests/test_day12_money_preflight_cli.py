import json
import tempfile
import unittest
from pathlib import Path

from profit_engine_runtime.day12_money_preflight_cli import run_money_preflight
from profit_engine_runtime.models import HttpResponse


YANDEX_TOKEN = "fixture-yandex-token-value"
YAN_TOKEN = "fixture-yan-token-value"


class FakeTransport:
    def __init__(self, responses):
        self.responses = list(responses)
        self.requests = []

    def send(self, request):
        self.requests.append(request)
        return self.responses.pop(0)


def response(status, body, **headers):
    return HttpResponse(status, headers, body, headers.get("RequestId"))


class MoneyPreflightCliTests(unittest.TestCase):
    def private_config(self, directory: str) -> Path:
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
                    "client_login_ref": "owner-advertiser-fixture",
                },
                "metrica": {
                    "management_endpoint": "https://api-metrika.yandex.net/management/v1",
                    "reports_endpoint": "https://api-metrika.yandex.net/stat/v1/data",
                    "counter_ref": "110349067",
                },
                "yan_statistics": {
                    "endpoint": "https://partner.yandex.ru/api/statistics2",
                    "token_source_ref": "keychain:yan/account",
                    "currency": "RUB",
                    "timezone": "Europe/Moscow",
                },
            },
        }), encoding="utf-8")
        path.chmod(0o600)
        return path

    def resolver(self, reference: str):
        return {
            "keychain:direct/account": YANDEX_TOKEN,
            "keychain:yan/account": YAN_TOKEN,
        }.get(reference)

    def transport(self):
        direct_tsv = "Date\tCampaignId\tClicks\tCost\n2026-08-28\t101\t3\t4.00\n"
        metrica = {
            "sampled": False,
            "contains_sensitive_data": False,
            "currency": "RUB",
            "data": [{
                "dimensions": [{"name": "2026-08-28"}, {"id": "101"}],
                "metrics": [8.0, 100, 90, 80],
            }],
        }
        yan = {
            "result": "ok",
            "data": {"points": [{
                "dimensions": {"date": "2026-08-28", "domain": "dilivox.ru"},
                "measures": [{
                    "partner_wo_nds": 16.0,
                    "hits": 200,
                    "hits_render": 180,
                    "shows": 160,
                }],
            }]},
        }
        return FakeTransport([
            response(200, direct_tsv, RequestId="direct-req", Units="1/99/1000"),
            response(200, metrica),
            response(200, yan),
        ])

    def test_cli_function_loads_private_refs_and_prints_no_credentials(self):
        with tempfile.TemporaryDirectory() as directory:
            transport = self.transport()
            public = run_money_preflight(
                config_path=self.private_config(directory),
                campaign_id="101",
                date_from="2026-08-28",
                date_to="2026-08-28",
                transport=transport,
                secret_resolver=self.resolver,
            )
        serialized = json.dumps(public)
        self.assertNotIn(YANDEX_TOKEN, serialized)
        self.assertNotIn(YAN_TOKEN, serialized)
        self.assertEqual("DAY12_MONEY_PREFLIGHT_READ_ONLY", public["mode"])
        self.assertEqual("READY_FOR_CANDIDATE_EVALUATION", public["state"])
        self.assertEqual("4.00", public["direct_spend_rub"])
        self.assertEqual("8.0", public["metrica_attributed_yan_revenue_rub"])
        self.assertEqual("16.0", public["yan_control_revenue_rub"])
        self.assertEqual("2", public["k5_observed"])
        self.assertEqual("0.5", public["attributed_share_of_yan_control"])
        self.assertFalse(public["provider_write_allowed"])
        self.assertFalse(public["credential_values_printed"])
        self.assertEqual(3, len(transport.requests))

    def test_missing_private_config_fails_before_provider_calls(self):
        transport = FakeTransport([])
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(FileNotFoundError):
                run_money_preflight(
                    config_path=Path(directory) / "missing.json",
                    campaign_id="101",
                    date_from="2026-08-28",
                    date_to="2026-08-28",
                    transport=transport,
                    secret_resolver=self.resolver,
                )
        self.assertEqual([], transport.requests)

    def test_missing_credentials_fail_before_provider_calls(self):
        transport = FakeTransport([])
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                run_money_preflight(
                    config_path=self.private_config(directory),
                    campaign_id="101",
                    date_from="2026-08-28",
                    date_to="2026-08-28",
                    transport=transport,
                    secret_resolver=lambda _ref: None,
                )
        self.assertEqual([], transport.requests)

    def test_operator_target_alias_config_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.private_config(directory)
            data = json.loads(path.read_text(encoding="utf-8"))
            data["providers"]["direct"]["client_login_ref"] = "ReklamaDymova"
            path.write_text(json.dumps(data), encoding="utf-8")
            path.chmod(0o600)
            with self.assertRaises(ValueError):
                run_money_preflight(
                    config_path=path,
                    campaign_id="101",
                    date_from="2026-08-28",
                    date_to="2026-08-28",
                    transport=FakeTransport([]),
                    secret_resolver=self.resolver,
                )


if __name__ == "__main__":
    unittest.main()
