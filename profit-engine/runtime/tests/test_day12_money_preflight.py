import unittest
from dataclasses import replace
from decimal import Decimal

from profit_engine_runtime.config import SiteConfig
from profit_engine_runtime.day12_money_preflight import (
    DIRECT_REPORTS_ENDPOINT,
    Day12MoneyProbe,
    DirectSpendObservation,
    MetricaRevenueObservation,
    MoneyPreflightState,
    YanControlObservation,
    build_money_preflight,
)
from profit_engine_runtime.models import HttpResponse
from profit_engine_runtime.transport import TransportError


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


def response(status, body, **headers):
    return HttpResponse(status, headers, body, headers.get("RequestId"))


class MoneyPreflightTests(unittest.TestCase):
    def setUp(self):
        self.config = SiteConfig(
            direct_client_login="owner-advertiser-fixture",
            metrica_counter_id="110349067",
            direct_endpoint="https://api.direct.yandex.com/json/v501",
            canonical_domain="dilivox.ru",
        )
        self.direct_tsv = "Date\tCampaignId\tClicks\tCost\n2026-08-28\t101\t4\t5.00\n"
        self.metrica = {
            "sampled": False,
            "contains_sensitive_data": False,
            "currency": "RUB",
            "data": [{
                "dimensions": [{"name": "2026-08-28"}, {"id": "101", "name": "campaign"}],
                "metrics": [10.0, 100, 90, 80],
            }],
        }
        self.yan = {
            "result": "ok",
            "data": {
                "points": [{
                    "dimensions": {"date": "2026-08-28", "domain": "dilivox.ru"},
                    "measures": [{
                        "partner_wo_nds": 20.0,
                        "hits": 200,
                        "hits_render": 180,
                        "shows": 160,
                    }],
                }]
            },
        }

    def probe(self, responses=None):
        return Day12MoneyProbe(
            transport=FakeTransport(responses or [
                response(200, self.direct_tsv, RequestId="direct-req", Units="1/99/1000"),
                response(200, self.metrica),
                response(200, self.yan),
            ]),
            config=self.config,
        )

    def run(self, probe=None):
        return (probe or self.probe()).run(
            campaign_id="101",
            date_from="2026-08-28",
            date_to="2026-08-28",
            direct_token="direct-token",
            metrica_token="metrica-token",
            yan_token="yan-token",
        )

    def test_ready_preflight_computes_observed_k5_and_control_share(self):
        preflight = self.run()
        self.assertEqual(MoneyPreflightState.READY_FOR_CANDIDATE_EVALUATION, preflight.state)
        self.assertEqual(Decimal("5.00"), preflight.direct_spend_rub)
        self.assertEqual(Decimal("10.0"), preflight.metrica_attributed_yan_revenue_rub)
        self.assertEqual(Decimal("20.0"), preflight.yan_control_revenue_rub)
        self.assertEqual(Decimal("2"), preflight.k5_observed)
        self.assertEqual(Decimal("0.5"), preflight.attributed_share_of_yan_control)
        self.assertEqual("direct-req", preflight.direct_request_id)
        self.assertFalse(preflight.provider_write_allowed)
        self.assertTrue(preflight.integrity_valid)

    def test_direct_request_uses_official_v501_reports_and_exact_campaign_filter(self):
        probe = self.probe()
        self.run(probe)
        request = probe.transport.requests[0]
        self.assertEqual(DIRECT_REPORTS_ENDPOINT, request.url)
        self.assertEqual("https://api.direct.yandex.com/json/v501/reports", request.url)
        self.assertEqual("owner-advertiser-fixture", request.headers["Client-Login"])
        self.assertEqual("false", request.headers["returnMoneyInMicros"])
        params = request.json_body["params"]
        self.assertEqual("YES", params["IncludeVAT"])
        self.assertEqual("YES", params["IncludeDiscount"])
        self.assertEqual([{
            "Field": "CampaignId", "Operator": "IN", "Values": [101]
        }], params["SelectionCriteria"]["Filter"])

    def test_metrica_request_is_exact_counter_and_direct_campaign_attribution(self):
        probe = self.probe()
        self.run(probe)
        request = probe.transport.requests[1]
        self.assertEqual("GET", request.method)
        self.assertEqual("110349067", request.query["ids"])
        self.assertIn("last_yandex_direct_clickDirectClickOrder", request.query["dimensions"])
        self.assertIn("ym:s:yanPartnerPrice", request.query["metrics"])
        self.assertEqual("full", request.query["accuracy"])

    def test_yan_request_uses_exact_domain_and_two_date_period(self):
        probe = self.probe()
        self.run(probe)
        request = probe.transport.requests[2]
        self.assertEqual(["2026-08-28", "2026-08-28"], request.query["period"])
        self.assertEqual("domain", request.query["entity_field"])
        self.assertIn("dilivox.ru", request.query["filter"])
        self.assertEqual("RUB", request.query["currency"])
        self.assertEqual("Europe/Moscow", request.query["timezone"])

    def test_direct_read_polling_is_bounded_and_read_only(self):
        probe = self.probe([
            response(201, None),
            response(202, None),
            response(200, self.direct_tsv),
        ])
        observed = probe.read_direct_spend(
            campaign_id="101", date_from="2026-08-28", date_to="2026-08-28",
            token="direct-token", max_report_polls=3,
        )
        self.assertEqual(Decimal("5.00"), observed.spend_rub)
        self.assertEqual(3, len(probe.transport.requests))
        timeout = self.probe([response(201, None), response(202, None)])
        with self.assertRaises(TransportError):
            timeout.read_direct_spend(
                campaign_id="101", date_from="2026-08-28", date_to="2026-08-28",
                token="direct-token", max_report_polls=2,
            )

    def test_unexpected_direct_campaign_is_rejected(self):
        probe = self.probe([response(
            200,
            "Date\tCampaignId\tClicks\tCost\n2026-08-28\t102\t4\t5.00\n",
        )])
        with self.assertRaises(ValueError):
            probe.read_direct_spend(
                campaign_id="101", date_from="2026-08-28", date_to="2026-08-28",
                token="direct-token",
            )

    def test_metrica_only_sums_exact_campaign_dimension(self):
        body = dict(self.metrica)
        body["data"] = [
            self.metrica["data"][0],
            {
                "dimensions": [{"name": "2026-08-28"}, {"id": "102"}],
                "metrics": [99.0, 999, 999, 999],
            },
        ]
        probe = self.probe([response(200, body)])
        observed = probe.read_metrica_attributed_revenue(
            campaign_id="101", date_from="2026-08-28", date_to="2026-08-28",
            token="metrica-token",
        )
        self.assertEqual(Decimal("10.0"), observed.attributed_yan_revenue_rub)
        self.assertEqual(1, observed.matched_rows)

    def test_reconciliation_violation_holds(self):
        direct = DirectSpendObservation("101", "2026-08-28", "2026-08-28", Decimal("5"), 4, 1, None, None)
        metrica = MetricaRevenueObservation(
            "101", "2026-08-28", "2026-08-28", Decimal("21.01"),
            Decimal("1"), Decimal("1"), Decimal("1"), 1, False, False, "RUB",
        )
        yan = YanControlObservation(
            "dilivox.ru", "2026-08-28", "2026-08-28", Decimal("20"),
            Decimal("1"), Decimal("1"), Decimal("1"), 1, "RUB",
        )
        value = build_money_preflight(site_id="dilivox", direct=direct, metrica=metrica, yan=yan)
        self.assertEqual(MoneyPreflightState.HOLD_DATA_QUALITY, value.state)
        self.assertIn("metrica_attributed_revenue_exceeds_yan_control_total", value.holds)
        self.assertFalse(value.provider_write_allowed)

    def test_sampled_or_sensitive_metrica_holds(self):
        base = MetricaRevenueObservation(
            "101", "2026-08-28", "2026-08-28", Decimal("10"),
            Decimal("1"), Decimal("1"), Decimal("1"), 1, False, False, "RUB",
        )
        direct = DirectSpendObservation("101", "2026-08-28", "2026-08-28", Decimal("5"), 4, 1, None, None)
        yan = YanControlObservation("dilivox.ru", "2026-08-28", "2026-08-28", Decimal("20"), Decimal("1"), Decimal("1"), Decimal("1"), 1, "RUB")
        for metrica in (replace(base, sampled=True), replace(base, contains_sensitive_data=True)):
            with self.subTest(metrica=metrica):
                value = build_money_preflight(site_id="dilivox", direct=direct, metrica=metrica, yan=yan)
                self.assertEqual(MoneyPreflightState.HOLD_DATA_QUALITY, value.state)
                self.assertFalse(value.provider_write_allowed)

    def test_zero_direct_spend_is_not_fake_infinite_k5(self):
        direct = DirectSpendObservation("101", "2026-08-28", "2026-08-28", Decimal("0"), 0, 0, None, None)
        metrica = MetricaRevenueObservation("101", "2026-08-28", "2026-08-28", Decimal("0"), Decimal("0"), Decimal("0"), Decimal("0"), 0, False, False, "RUB")
        yan = YanControlObservation("dilivox.ru", "2026-08-28", "2026-08-28", Decimal("0"), Decimal("0"), Decimal("0"), Decimal("0"), 0, "RUB")
        value = build_money_preflight(site_id="dilivox", direct=direct, metrica=metrica, yan=yan)
        self.assertEqual(MoneyPreflightState.NO_DIRECT_SPEND, value.state)
        self.assertIsNone(value.k5_observed)
        self.assertFalse(value.provider_write_allowed)

    def test_identity_and_date_mismatch_fail_closed(self):
        direct = DirectSpendObservation("101", "2026-08-28", "2026-08-28", Decimal("1"), 1, 1, None, None)
        metrica = MetricaRevenueObservation("102", "2026-08-28", "2026-08-28", Decimal("1"), Decimal("0"), Decimal("0"), Decimal("0"), 1, False, False, "RUB")
        yan = YanControlObservation("dilivox.ru", "2026-08-28", "2026-08-28", Decimal("1"), Decimal("0"), Decimal("0"), Decimal("0"), 1, "RUB")
        with self.assertRaises(ValueError):
            build_money_preflight(site_id="dilivox", direct=direct, metrica=metrica, yan=yan)
        with self.assertRaises(ValueError):
            self.run(self.probe()) if False else self.probe().run(
                campaign_id="101", date_from="2026-08-29", date_to="2026-08-28",
                direct_token="d", metrica_token="m", yan_token="y",
            )


if __name__ == "__main__":
    unittest.main()
