from __future__ import annotations

import unittest
from decimal import Decimal

from profit_engine_runtime.config import SiteConfig
from profit_engine_runtime.manual_search_read_model import ManualSearchReadModel, public_result
from profit_engine_runtime.models import HttpResponse


class FakeTransport:
    def __init__(self, responses):
        self.responses = list(responses)
        self.requests = []

    def send(self, request):
        self.requests.append(request)
        return self.responses.pop(0)


def response(status, body, **headers):
    return HttpResponse(status, headers, body, headers.get("RequestId"))


class ManualSearchReadModelTests(unittest.TestCase):
    def setUp(self):
        self.config = SiteConfig(
            direct_operator_login="manager",
            direct_client_login="target",
            direct_endpoint="https://api.direct.yandex.com/json/v501",
        )
        self.campaign = {
            "result": {"Campaigns": [{
                "Id": 101,
                "Name": "DILIVOX | SEARCH | PROFIT ENGINE",
                "State": "ON",
                "Status": "ACCEPTED",
                "Type": "UNIFIED_CAMPAIGN",
                "UnifiedCampaign": {
                    "BiddingStrategy": {
                        "Search": {
                            "BiddingStrategyType": "HIGHEST_POSITION",
                            "HighestPosition": {"WeeklySpendLimit": 700000000},
                        },
                        "Network": {"BiddingStrategyType": "SERVING_OFF"},
                    }
                },
            }]}
        }
        self.keywords = {
            "result": {"Keywords": [{
                "Id": 501,
                "Keyword": "интерактивные истории",
                "State": "ON",
                "Status": "ACCEPTED",
                "ServingStatus": "ELIGIBLE",
                "AdGroupId": 301,
                "CampaignId": 101,
                "StrategyPriority": "NORMAL",
                "AutotargetingSearchBidIsAuto": "NO",
            }]}
        }
        self.bids = {
            "result": {"KeywordBids": [{
                "KeywordId": 501,
                "AdGroupId": 301,
                "CampaignId": 101,
                "ServingStatus": "ELIGIBLE",
                "StrategyPriority": "NORMAL",
                "Search": {
                    "Bid": 12500000,
                    "AutotargetingSearchBidIsAuto": "NO",
                    "AuctionBids": {"AuctionBidItems": [{"TrafficVolume": 100, "Bid": 15000000, "Price": 13000000}]},
                },
            }]}
        }
        self.report = (
            "CampaignId\tAdGroupId\tCriterionId\tCriterion\tCriterionType\tImpressions\tClicks\tCost\tAvgCpc\n"
            "101\t301\t501\tинтерактивные истории\tKEYWORD\t100\t4\t20.00\t5.00\n"
        )

    def test_manual_search_shape_reads_keywords_bids_auction_and_cost_without_write(self):
        transport = FakeTransport([
            response(200, self.campaign),
            response(200, self.keywords),
            response(200, self.bids),
            response(200, self.report),
        ])
        result = ManualSearchReadModel(transport=transport, config=self.config).run(
            campaign_id="101",
            date_from="2026-08-01",
            date_to="2026-08-30",
            token="secret",
        )
        self.assertTrue(result.manual_search_shape_ready)
        self.assertEqual(Decimal("700"), result.weekly_spend_limit_rub)
        self.assertEqual(1, result.keyword_count)
        cell = result.cells[0]
        self.assertEqual("12.5", cell["search_bid_rub"])
        self.assertEqual("20.00", cell["cost_rub"])
        self.assertEqual("5.00", cell["avg_cpc_rub"])
        self.assertEqual("15", cell["auction_bids"][0]["bid_rub"])
        self.assertIsNone(cell["revenue_rub"])
        self.assertEqual("REVENUE_ATTRIBUTION_NOT_JOINED_YET", cell["economic_grain_state"])
        self.assertFalse(result.provider_write_allowed)
        self.assertEqual(["POST", "POST", "POST", "POST"], [r.method for r in transport.requests])
        self.assertTrue(all(r.json_body.get("method") == "get" for r in transport.requests[:3]))
        self.assertNotIn("method", transport.requests[3].json_body)

    def test_wrong_strategy_holds_before_keyword_or_report_reads(self):
        campaign = self.campaign.copy()
        campaign["result"] = {"Campaigns": [dict(self.campaign["result"]["Campaigns"][0])]}
        campaign["result"]["Campaigns"][0]["UnifiedCampaign"] = {
            "BiddingStrategy": {
                "Search": {"BiddingStrategyType": "WB_MAXIMUM_CLICKS"},
                "Network": {"BiddingStrategyType": "SERVING_OFF"},
            }
        }
        transport = FakeTransport([response(200, campaign)])
        result = ManualSearchReadModel(transport=transport, config=self.config).run(
            campaign_id="101", date_from="2026-08-01", date_to="2026-08-30", token="secret"
        )
        self.assertFalse(result.manual_search_shape_ready)
        self.assertIn("search_strategy_is_not_highest_position", result.holds)
        self.assertIn("weekly_spend_limit_missing", result.holds)
        self.assertEqual(1, len(transport.requests))

    def test_network_must_be_off(self):
        campaign = self.campaign.copy()
        campaign["result"] = {"Campaigns": [dict(self.campaign["result"]["Campaigns"][0])]}
        campaign["result"]["Campaigns"][0]["UnifiedCampaign"] = {
            "BiddingStrategy": {
                "Search": {"BiddingStrategyType": "HIGHEST_POSITION", "HighestPosition": {"WeeklySpendLimit": 100000000}},
                "Network": {"BiddingStrategyType": "NETWORK_DEFAULT"},
            }
        }
        result = ManualSearchReadModel(transport=FakeTransport([response(200, campaign)]), config=self.config).run(
            campaign_id="101", date_from="2026-08-01", date_to="2026-08-30", token="secret"
        )
        self.assertIn("network_is_not_serving_off", result.holds)

    def test_public_result_explicitly_has_zero_write_authority_and_no_fake_k5(self):
        transport = FakeTransport([
            response(200, self.campaign), response(200, self.keywords), response(200, self.bids), response(200, self.report)
        ])
        value = public_result(ManualSearchReadModel(transport=transport, config=self.config).run(
            campaign_id="101", date_from="2026-08-01", date_to="2026-08-30", token="secret"
        ))
        self.assertFalse(value["provider_write_allowed"])
        self.assertEqual(0, value["provider_write_requests"])
        self.assertFalse(value["revenue_attribution_ready"])
        self.assertEqual("MS2_ATTRIBUTION_GRAIN", value["next_phase"])
        self.assertIsNone(value["cells"][0]["k5"])


if __name__ == "__main__":
    unittest.main()
