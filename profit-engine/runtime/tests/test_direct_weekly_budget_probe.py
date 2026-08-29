import unittest

from profit_engine_runtime.config import SiteConfig
from profit_engine_runtime.direct_weekly_budget import WeeklyBudgetCapability
from profit_engine_runtime.direct_weekly_budget_probe import YandexDirectWeeklyBudgetProbe
from profit_engine_runtime.models import HttpResponse
from profit_engine_runtime.transport import TransportError


TOKEN = "fixture-token"


class FakeTransport:
    def __init__(self, responses):
        self.responses = list(responses)
        self.requests = []

    def send(self, request):
        self.requests.append(request)
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response


def ok(body, **headers):
    return HttpResponse(200, headers, body, headers.get("RequestId"))


class WeeklyBudgetProbeTests(unittest.TestCase):
    def setUp(self):
        self.config = SiteConfig(
            direct_client_login="owner-advertiser-fixture",
            direct_endpoint="https://api.direct.yandex.com/json/v501",
        )

    def campaign(self, *, package=None):
        typed = {
            "BiddingStrategy": {
                "Search": {
                    "BiddingStrategyType": "WB_MAXIMUM_CLICKS",
                    "WbMaximumClicks": {"WeeklySpendLimit": 100_000_000},
                }
            }
        }
        if package is not None:
            typed["PackageBiddingStrategy"] = package
        return {
            "Id": 101,
            "Type": "TEXT_CAMPAIGN",
            "State": "ON",
            "Status": "ACCEPTED",
            "TextCampaign": typed,
        }

    def test_request_is_exact_read_only_current_campaign_shape(self):
        transport = FakeTransport([
            ok({"result": {"Campaigns": [self.campaign()]}}, RequestId="req-1", Units="1/99/1000")
        ])
        result = YandexDirectWeeklyBudgetProbe(transport=transport, config=self.config).read_exact(
            campaign_id="101", token=TOKEN
        )
        self.assertEqual(WeeklyBudgetCapability.EXACT_ONE_SLOT, result.inspection.capability)
        self.assertFalse(result.provider_write_allowed)
        self.assertEqual("req-1", result.request_id)
        self.assertEqual("1/99/1000", result.units)
        request = transport.requests[0]
        self.assertEqual("POST", request.method)
        self.assertEqual("https://api.direct.yandex.com/json/v501/campaigns", request.url)
        self.assertEqual("Bearer " + TOKEN, request.headers["Authorization"])
        self.assertEqual("owner-advertiser-fixture", request.headers["Client-Login"])
        self.assertEqual("get", request.json_body["method"])
        params = request.json_body["params"]
        self.assertEqual({"Ids": [101]}, params["SelectionCriteria"])
        self.assertEqual(["Id", "Type", "State", "Status"], params["FieldNames"])
        self.assertEqual(
            ["BiddingStrategy", "PackageBiddingStrategy", "WeeklyBudgetRollover"],
            params["TextCampaignFieldNames"],
        )
        self.assertEqual(
            ["BiddingStrategy", "PackageBiddingStrategy", "WeeklyBudgetRollover"],
            params["UnifiedCampaignFieldNames"],
        )
        self.assertEqual(["BiddingStrategy"], params["CpmBannerCampaignFieldNames"])

    def test_package_strategy_is_reported_as_hold(self):
        transport = FakeTransport([
            ok({"result": {"Campaigns": [self.campaign(package={"StrategyId": 777})]}})
        ])
        result = YandexDirectWeeklyBudgetProbe(transport=transport, config=self.config).read_exact(
            campaign_id="101", token=TOKEN
        )
        self.assertEqual(
            WeeklyBudgetCapability.PACKAGE_STRATEGY_REQUIRES_SEPARATE_SCOPE,
            result.inspection.capability,
        )
        self.assertFalse(result.provider_write_allowed)

    def test_missing_target_login_blocks_before_network(self):
        transport = FakeTransport([])
        probe = YandexDirectWeeklyBudgetProbe(transport=transport, config=SiteConfig())
        with self.assertRaises(ValueError):
            probe.read_exact(campaign_id="101", token=TOKEN)
        self.assertEqual([], transport.requests)

    def test_wrong_campaign_or_non_success_fails_closed(self):
        for response in (
            ok({"result": {"Campaigns": [{"Id": 102}]}}),
            HttpResponse(403, {}, {"error": {"error_code": 53}}),
        ):
            with self.subTest(response=response.status_code):
                probe = YandexDirectWeeklyBudgetProbe(
                    transport=FakeTransport([response]), config=self.config
                )
                with self.assertRaises(TransportError):
                    probe.read_exact(campaign_id="101", token=TOKEN)

    def test_invalid_campaign_id_blocks_before_network(self):
        transport = FakeTransport([])
        probe = YandexDirectWeeklyBudgetProbe(transport=transport, config=self.config)
        for value in ("", "abc", "0", "-1"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                probe.read_exact(campaign_id=value, token=TOKEN)
        self.assertEqual([], transport.requests)


if __name__ == "__main__":
    unittest.main()
