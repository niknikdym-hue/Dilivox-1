from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from profit_engine_runtime.clients import YandexDirectReadClient
from profit_engine_runtime.config import SiteConfig, load_site_config
from profit_engine_runtime.models import DoctorStatus, HttpRequest, HttpResponse


TOKEN = "fixture-manager-token"
OPERATOR = "manager-fixture"
TARGET = "owner-advertiser-fixture"


class FakeTransport:
    def __init__(self, responses):
        self.responses = list(responses)
        self.requests: list[HttpRequest] = []

    def send(self, request: HttpRequest) -> HttpResponse:
        self.requests.append(request)
        return self.responses.pop(0)


def ok(body=None, **headers):
    return HttpResponse(200, headers, body if body is not None else {}, headers.get("RequestId"))


class DirectManagerBindingTests(unittest.TestCase):
    def test_manager_path_separates_operator_from_managed_target_and_never_infers_editing(self):
        config = SiteConfig(
            direct_operator_login=OPERATOR,
            direct_client_login=TARGET,
        )
        operator = {"result": {"Clients": [{"ClientId": 1, "Login": OPERATOR, "Type": "CLIENT"}]}}
        campaign_probe = {"result": {"Campaigns": [{"Id": 101, "Name": "Probe", "State": "ON", "Status": "ACCEPTED"}]}}
        transport = FakeTransport([
            ok(operator),
            ok(campaign_probe, RequestId="campaigns", Units="1/100/1000", **{"Units-Used-Login": TARGET}),
        ])
        result = YandexDirectReadClient(transport, config).diagnose(TOKEN)

        self.assertEqual(DoctorStatus.PASS, result.status)
        self.assertEqual(2, len(transport.requests))
        self.assertNotIn("Client-Login", transport.requests[0].headers)
        self.assertTrue(transport.requests[0].url.endswith("/clients"))
        self.assertTrue(transport.requests[1].url.endswith("/campaigns"))
        self.assertEqual(TARGET, transport.requests[1].headers["Client-Login"])
        self.assertIn("direct.operator_identity=PASS", result.checks)
        self.assertIn("direct.permission_source=MANAGER_ACCOUNT_UI_REQUIRED", result.checks)
        self.assertIn("direct.permission=UNKNOWN", result.checks)
        self.assertIn("campaigns.get(target,limit=1)", result.checks)
        self.assertIn("direct.target_units_login=PASS", result.checks)
        self.assertNotIn("direct.permission=EDITING", result.checks)

    def test_manager_path_rejects_mismatched_units_used_login(self):
        config = SiteConfig(direct_operator_login=OPERATOR, direct_client_login=TARGET)
        operator = {"result": {"Clients": [{"ClientId": 1, "Login": OPERATOR, "Type": "CLIENT"}]}}
        transport = FakeTransport([
            ok(operator),
            ok({"result": {"Campaigns": []}}, **{"Units-Used-Login": "different-target"}),
        ])
        result = YandexDirectReadClient(transport, config).diagnose(TOKEN)
        self.assertEqual(DoctorStatus.BLOCKED_ACCESS, result.status)

    def test_manager_path_requires_distinct_target_before_network(self):
        config = SiteConfig(direct_operator_login=OPERATOR)
        transport = FakeTransport([])
        result = YandexDirectReadClient(transport, config).diagnose(TOKEN)
        self.assertEqual(DoctorStatus.BLOCKED_ACCESS, result.status)
        self.assertEqual([], transport.requests)

    def test_private_registry_rejects_operator_target_alias(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "site.json"
            path.write_text(json.dumps({
                "rollout_mode": "READ_ONLY",
                "providers": {
                    "direct": {
                        "operator_login_ref": OPERATOR,
                        "client_login_ref": OPERATOR,
                    }
                },
            }), encoding="utf-8")
            path.chmod(0o600)
            with self.assertRaises(ValueError):
                load_site_config(path)


if __name__ == "__main__":
    unittest.main()
