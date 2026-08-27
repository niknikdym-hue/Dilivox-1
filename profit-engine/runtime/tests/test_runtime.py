from __future__ import annotations

import json
import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import patch

from profit_engine_runtime.clients import (
    READ_ONLY,
    YanPartnerStatsReadClient,
    YandexDirectReadClient,
    YandexMetricaReadClient,
)
from profit_engine_runtime.config import DEFAULT_CONFIG_PATH, SiteConfig, load_site_config
from profit_engine_runtime.models import DoctorStatus, HttpRequest, HttpResponse
from profit_engine_runtime.redaction import REDACTED, safe_json
from profit_engine_runtime.transport import (
    TransportError,
    UrllibTransport,
    public_request_log,
)


TOKEN = "fixture-super-secret-token-value"


class FakeTransport:
    def __init__(self, responses):
        self.responses = list(responses)
        self.requests: list[HttpRequest] = []

    def send(self, request: HttpRequest) -> HttpResponse:
        self.requests.append(request)
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response


def ok(body=None, **headers):
    return HttpResponse(200, headers, body if body is not None else {}, headers.get("RequestId"))


class RuntimeTests(unittest.TestCase):
    def setUp(self):
        self.config = SiteConfig()

    def test_runtime_is_explicitly_read_only(self):
        self.assertTrue(READ_ONLY)
        for client in (YandexDirectReadClient, YandexMetricaReadClient, YanPartnerStatsReadClient):
            self.assertTrue(client.READ_ONLY)
            self.assertFalse(any(name in client.__dict__ for name in ("add", "update", "delete", "suspend", "resume")))

    def test_direct_request_shape_and_redacted_log(self):
        transport = FakeTransport([ok({}, RequestId="req-client"), ok({}, RequestId="req-campaign", Units="1/100/1000")])
        result = YandexDirectReadClient(transport, self.config).diagnose(TOKEN)
        self.assertEqual(DoctorStatus.PASS, result.status)
        self.assertEqual(2, len(transport.requests))
        for request in transport.requests:
            self.assertEqual("POST", request.method)
            self.assertEqual(f"Bearer {TOKEN}", request.headers["Authorization"])
            self.assertEqual("get", request.json_body["method"])
            logged = public_request_log(request)
            self.assertNotIn(TOKEN, logged)
            self.assertIn(REDACTED, logged)
        self.assertTrue(transport.requests[0].url.endswith("/clients"))
        self.assertTrue(transport.requests[1].url.endswith("/campaigns"))
        self.assertEqual("req-campaign", result.request_id)
        self.assertEqual("1/100/1000", result.provider_units)

    def test_metrica_read_shapes(self):
        counters = {"counters": [{"id": 123, "site": "dilivox.ru", "permission": "view"}]}
        transport = FakeTransport([ok(counters), ok({"data": []}, RequestId="metrica-report")])
        result = YandexMetricaReadClient(transport, self.config).diagnose(TOKEN)
        self.assertEqual(DoctorStatus.PASS, result.status)
        self.assertEqual(["GET", "GET"], [request.method for request in transport.requests])
        self.assertTrue(transport.requests[0].url.endswith("/counters"))
        self.assertEqual("ym:s:visits,ym:s:yanPartnerPrice", transport.requests[1].query["metrics"])
        self.assertEqual(f"OAuth {TOKEN}", transport.requests[0].headers["Authorization"])

    def test_yan_statistics_read_shapes(self):
        transport = FakeTransport([ok({"result": "ok", "data": {"tree": []}}), ok({"result": "ok", "data": {"points": []}})])
        result = YanPartnerStatsReadClient(transport, self.config).diagnose(TOKEN)
        self.assertEqual(DoctorStatus.PASS, result.status)
        self.assertEqual(["GET", "GET"], [request.method for request in transport.requests])
        self.assertTrue(transport.requests[0].url.endswith("/tree.json"))
        self.assertTrue(transport.requests[1].url.endswith("/get.json"))
        self.assertEqual("yesterday", transport.requests[1].query["period"])
        self.assertEqual(f"OAuth {TOKEN}", transport.requests[0].headers["Authorization"])

    def test_missing_tokens_are_classified_without_transport_calls(self):
        for client_type in (YandexDirectReadClient, YandexMetricaReadClient, YanPartnerStatsReadClient):
            transport = FakeTransport([])
            result = client_type(transport, self.config).diagnose(None)
            self.assertEqual(DoctorStatus.BLOCKED_MISSING_CREDENTIAL, result.status)
            self.assertEqual([], transport.requests)

    def test_401_and_403_are_access_blockers(self):
        for code in (401, 403):
            result = YandexDirectReadClient(
                FakeTransport([TransportError("denied", status_code=code)]), self.config
            ).diagnose(TOKEN)
            self.assertEqual(DoctorStatus.BLOCKED_ACCESS, result.status)
            self.assertEqual(code, result.http_status)
            self.assertNotIn(TOKEN, result.detail or "")

    def test_retry_is_bounded(self):
        request = HttpRequest("GET", "https://example.invalid/read")
        error = urllib.error.HTTPError(request.url, 503, "unavailable", {}, None)
        with patch("urllib.request.urlopen", side_effect=error) as mocked:
            with self.assertRaises(TransportError) as raised:
                UrllibTransport(max_attempts=3, backoff_seconds=0).send(request)
        self.assertEqual(3, mocked.call_count)
        self.assertEqual(3, raised.exception.attempts)

    def test_redaction_covers_logs_exceptions_and_snapshots(self):
        sample = {"Authorization": f"Bearer {TOKEN}", "nested": [TOKEN], "counter_id": "private-id"}
        serialized = safe_json(sample, [TOKEN])
        self.assertNotIn(TOKEN, serialized)
        self.assertNotIn("private-id", serialized)
        self.assertGreaterEqual(serialized.count(REDACTED), 3)

    def test_private_registry_default_is_outside_repository(self):
        repository = Path(__file__).resolve().parents[3]
        self.assertFalse(DEFAULT_CONFIG_PATH.is_relative_to(repository))

    def test_private_registry_requires_0600_and_read_only(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "site.json"
            path.write_text(json.dumps({"rollout_mode": "READ_ONLY", "providers": {}}), encoding="utf-8")
            path.chmod(0o600)
            config, present = load_site_config(path)
            self.assertTrue(present)
            self.assertEqual("READ_ONLY", config.rollout_mode)
            path.chmod(0o644)
            with self.assertRaises(ValueError):
                load_site_config(path)

    def test_public_example_contains_placeholders_not_real_values(self):
        profit_engine_root = Path(__file__).resolve().parents[2]
        example = profit_engine_root / "config/sites/dilivox.example.json"
        text = example.read_text(encoding="utf-8")
        parsed = json.loads(text)
        self.assertEqual("READ_ONLY", parsed["rollout_mode"])
        self.assertIn("PRIVATE_LOCAL_VALUE", text)
        self.assertNotIn(TOKEN, text)


if __name__ == "__main__":
    unittest.main()
