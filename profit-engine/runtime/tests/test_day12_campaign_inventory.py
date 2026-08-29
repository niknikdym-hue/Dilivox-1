import unittest

from profit_engine_runtime.config import SiteConfig
from profit_engine_runtime.day12_campaign_inventory import YandexDirectCampaignInventory
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


class CampaignInventoryTests(unittest.TestCase):
    def setUp(self):
        self.config = SiteConfig(
            direct_operator_login="reklamadymova",
            direct_client_login="owner-advertiser-fixture",
            direct_endpoint="https://api.direct.yandex.com/json/v501",
        )

    def test_inventory_uses_exact_target_and_never_selects_candidate(self):
        transport = FakeTransport([
            ok({"result": {"Campaigns": [
                {"Id": 102, "Name": "B", "Type": "TEXT_CAMPAIGN", "State": "SUSPENDED", "Status": "ACCEPTED"},
                {"Id": 101, "Name": "A", "Type": "UNIFIED_CAMPAIGN", "State": "ON", "Status": "ACCEPTED"},
            ]}}, RequestId="req-1", Units="1/99/1000")
        ])
        inventory = YandexDirectCampaignInventory(transport=transport, config=self.config).read_all(token=TOKEN)
        self.assertEqual(2, inventory.total_campaigns)
        self.assertEqual(("101", "102"), tuple(item.campaign_id for item in inventory.items))
        self.assertEqual("ACTIVE", inventory.items[0].normalized_state)
        self.assertEqual("SUSPENDED", inventory.items[1].normalized_state)
        self.assertFalse(inventory.provider_write_allowed)
        self.assertFalse(inventory.candidate_selected)
        self.assertTrue(inventory.integrity_valid)
        request = transport.requests[0]
        self.assertEqual("https://api.direct.yandex.com/json/v501/campaigns", request.url)
        self.assertEqual("owner-advertiser-fixture", request.headers["Client-Login"])
        self.assertEqual("get", request.json_body["method"])
        self.assertEqual({}, request.json_body["params"]["SelectionCriteria"])
        self.assertEqual(["Id", "Name", "Type", "State", "Status"], request.json_body["params"]["FieldNames"])

    def test_pagination_uses_limited_by_as_next_offset(self):
        transport = FakeTransport([
            ok({"result": {
                "Campaigns": [{"Id": 101, "Name": "A", "Type": "TEXT_CAMPAIGN", "State": "ON", "Status": "ACCEPTED"}],
                "LimitedBy": 1,
            }}),
            ok({"result": {
                "Campaigns": [{"Id": 102, "Name": "B", "Type": "TEXT_CAMPAIGN", "State": "OFF", "Status": "ACCEPTED"}]
            }}),
        ])
        inventory = YandexDirectCampaignInventory(transport=transport, config=self.config).read_all(
            token=TOKEN, page_size=1, max_pages=2
        )
        self.assertEqual(2, inventory.page_count)
        self.assertEqual(0, transport.requests[0].json_body["params"]["Page"]["Offset"])
        self.assertEqual(1, transport.requests[1].json_body["params"]["Page"]["Offset"])

    def test_nonadvancing_or_excess_pagination_fails_closed(self):
        transport = FakeTransport([ok({"result": {"Campaigns": [], "LimitedBy": 0}})])
        with self.assertRaises(ValueError):
            YandexDirectCampaignInventory(transport=transport, config=self.config).read_all(token=TOKEN)
        transport = FakeTransport([
            ok({"result": {"Campaigns": [], "LimitedBy": 1}}),
        ])
        with self.assertRaises(ValueError):
            YandexDirectCampaignInventory(transport=transport, config=self.config).read_all(
                token=TOKEN, max_pages=1
            )

    def test_duplicate_campaign_id_fails_closed(self):
        transport = FakeTransport([
            ok({"result": {"Campaigns": [
                {"Id": 101, "Name": "A", "Type": "TEXT_CAMPAIGN", "State": "ON", "Status": "ACCEPTED"},
                {"Id": 101, "Name": "A2", "Type": "TEXT_CAMPAIGN", "State": "ON", "Status": "ACCEPTED"},
            ]}})
        ])
        with self.assertRaises(ValueError):
            YandexDirectCampaignInventory(transport=transport, config=self.config).read_all(token=TOKEN)

    def test_missing_token_or_target_blocks_before_network(self):
        transport = FakeTransport([])
        with self.assertRaises(ValueError):
            YandexDirectCampaignInventory(transport=transport, config=self.config).read_all(token="")
        with self.assertRaises(ValueError):
            YandexDirectCampaignInventory(transport=transport, config=SiteConfig()).read_all(token=TOKEN)
        self.assertEqual([], transport.requests)

    def test_operator_target_alias_blocks_before_network(self):
        transport = FakeTransport([])
        config = SiteConfig(
            direct_operator_login="reklamadymova",
            direct_client_login="ReklamaDymova",
        )
        with self.assertRaises(ValueError):
            YandexDirectCampaignInventory(transport=transport, config=config).read_all(token=TOKEN)
        self.assertEqual([], transport.requests)

    def test_top_level_error_and_malformed_item_fail_closed(self):
        for response in (
            HttpResponse(403, {}, {"error": {"error_code": 53}}),
            ok({"result": {"Campaigns": [{"Id": "x"}]}}),
        ):
            with self.subTest(status=response.status_code):
                with self.assertRaises((TransportError, ValueError)):
                    YandexDirectCampaignInventory(
                        transport=FakeTransport([response]), config=self.config
                    ).read_all(token=TOKEN)


if __name__ == "__main__":
    unittest.main()
