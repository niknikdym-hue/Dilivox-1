from __future__ import annotations

import tempfile
import unittest
from dataclasses import replace
from decimal import Decimal
from pathlib import Path

from profit_engine_runtime.collectors import (
    DirectCollector, MetricaCollector, YanCollector, parse_direct_tsv,
    select_yan_revenue_field,
)
from profit_engine_runtime.config import SiteConfig
from profit_engine_runtime.fixtures import DIRECT, FIXTURE_CAPTURED_AT, METRICA, YAN
from profit_engine_runtime.ingestion import InMemoryRelationalStore, IngestionOrchestrator, RunStatus
from profit_engine_runtime.models import HttpResponse
from profit_engine_runtime.raw_store import LocalRawStore


class FakeTransport:
    def __init__(self, responses):
        self.responses = list(responses)
        self.requests = []
    def send(self, request):
        self.requests.append(request)
        return self.responses.pop(0)


def response(status, body, attempts=1):
    return HttpResponse(status, {}, body, attempts=attempts)


class IngestionTests(unittest.TestCase):
    day = "2026-08-26"
    config = SiteConfig()

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.relational = InMemoryRelationalStore()
        self.orchestrator = IngestionOrchestrator(LocalRawStore(Path(self.temp.name) / "raw"), self.relational)

    def tearDown(self): self.temp.cleanup()

    def direct(self, payload=DIRECT):
        return DirectCollector(None, self.config, None, self.day,
            fixture_payload=payload, captured_at=FIXTURE_CAPTURED_AT)

    def metrica(self, payload=METRICA, dimensions=("ym:s:date",)):
        return MetricaCollector(None, self.config, None, self.day, dimensions=dimensions,
            fixture_payload=payload, captured_at=FIXTURE_CAPTURED_AT)

    def yan(self, payload=YAN):
        return YanCollector(None, self.config, None, self.day, revenue_field="fixture_revenue",
            currency="RUB", timezone_name="Europe/Moscow", vat_basis="fixture-explicit",
            fixture_payload=payload, captured_at=FIXTURE_CAPTURED_AT)

    def test_direct_campaign_and_report_normalization(self):
        outcome = self.orchestrator.run("fixture-site", self.direct())
        self.assertEqual(RunStatus.COMPLETE, outcome.status)
        campaign = next(iter(self.relational.campaign_snapshots.values()))
        traffic = next(iter(self.relational.traffic_facts.values()))
        self.assertEqual("fixture-campaign-a", campaign["provider_entity_ref"])
        self.assertEqual(Decimal("12.340000"), traffic["spend_amount"])
        self.assertTrue(traffic["provenance"]["include_vat"])
        self.assertTrue(traffic["provenance"]["include_discount"])
        self.assertFalse(traffic["provenance"]["money_in_micros"])

    def test_direct_report_request_is_read_only_and_explicit(self):
        collector = DirectCollector(None, self.config, "fixture-token", self.day)
        request = collector.report_request()
        self.assertEqual("POST", request.method)
        self.assertEqual("https://api-direct.yandex.com/json/v501/reports", request.url)
        self.assertEqual(list(collector.report_fields), request.json_body["params"]["FieldNames"])
        self.assertEqual("YES", request.json_body["params"]["IncludeVAT"])
        self.assertEqual("YES", request.json_body["params"]["IncludeDiscount"])
        self.assertEqual("false", request.headers["returnMoneyInMicros"])

    def test_direct_tsv_parser_rejects_wrong_columns_and_float_is_never_used(self):
        rows = parse_direct_tsv(DIRECT["report_tsv"])
        self.assertEqual("12.340000", rows[0]["Cost"])
        with self.assertRaises(ValueError): parse_direct_tsv("Date\tCost\n2026-08-26\t1.0\n")

    def test_direct_200_and_bounded_201_202(self):
        campaigns = {"result": {"Campaigns": []}}
        transport = FakeTransport([response(200, campaigns), response(201, None), response(202, None), response(200, DIRECT["report_tsv"])])
        collector = DirectCollector(transport, self.config, "fixture-token", self.day,
            captured_at=FIXTURE_CAPTURED_AT, max_report_polls=3)
        source = collector.read()
        self.assertEqual(200, source.payload["report_status"])
        self.assertEqual(4, len(transport.requests))
        timeout_transport = FakeTransport([response(200, campaigns), response(201, None), response(202, None)])
        timeout = DirectCollector(timeout_transport, self.config, "fixture-token", self.day,
            captured_at=FIXTURE_CAPTURED_AT, max_report_polls=2)
        held = self.orchestrator.run("fixture-site", timeout)
        self.assertEqual(RunStatus.HELD, held.status)
        self.assertIn("direct_report_not_ready_timeout", held.hold_reasons)

    def test_metrica_normalizes_visits_money_and_accuracy_metadata(self):
        outcome = self.orchestrator.run("fixture-site", self.metrica())
        self.assertEqual(RunStatus.COMPLETE, outcome.status)
        traffic = next(iter(self.relational.traffic_facts.values()))
        money = next(iter(self.relational.monetization_facts.values()))
        self.assertEqual(31, traffic["visits"])
        self.assertEqual(Decimal("18.250000"), money["revenue_amount"])
        self.assertFalse(money["provenance"]["sampled"])
        self.assertEqual("metrica", money["measurement_source"])

    def test_metrica_accepts_provider_csv_metric_metadata(self):
        payload = dict(METRICA)
        payload["query"] = {"metrics": ",".join(METRICA["query"]["metrics"])}
        outcome = self.orchestrator.run("fixture-site", self.metrica(payload))
        self.assertEqual(RunStatus.COMPLETE, outcome.status)
        self.assertEqual(1, outcome.monetization_fact_count)

    def test_invalid_metrica_dimensions_and_missing_money_hold(self):
        payload = {"query": {"metrics": ["ym:s:visits"]}, "data": [], "currency": "RUB"}
        outcome = self.orchestrator.run("fixture-site", self.metrica(payload, ("ym:s:forbidden",)))
        self.assertEqual(RunStatus.HELD, outcome.status)
        self.assertIn("invalid_metrica_dimensions", outcome.hold_reasons)
        self.assertIn("metrica_monetization_unavailable", outcome.hold_reasons)
        self.assertFalse(outcome.optimizer_consumable)

    def test_metrica_canonical_domain_discovery(self):
        transport = FakeTransport([
            response(200, {"counters": [{"id": 123, "site": "dilivox.ru"}]}),
            response(200, METRICA),
        ])
        collector = MetricaCollector(transport, self.config, "fixture-token", self.day,
            captured_at=FIXTURE_CAPTURED_AT)
        collector.read()
        self.assertTrue(transport.requests[0].url.endswith("/counters"))
        self.assertEqual("123", transport.requests[1].query["ids"])

    def test_yan_tree_driven_revenue_and_delivery(self):
        self.assertEqual("fixture_revenue", select_yan_revenue_field(YAN["tree"]))
        outcome = self.orchestrator.run("fixture-site", self.yan())
        self.assertEqual(RunStatus.COMPLETE, outcome.status)
        money = next(iter(self.relational.monetization_facts.values()))
        self.assertEqual(Decimal("18.250000"), money["revenue_amount"])
        self.assertTrue(money["provenance"]["tree_validated"])
        self.assertEqual(61, money["delivery"]["shows"])

    def test_yan_explicit_field_must_exist_in_tree(self):
        tree = {"fields": [{"name": "provider_money_field"}]}
        self.assertEqual("provider_money_field", select_yan_revenue_field(tree, "provider_money_field"))
        self.assertIsNone(select_yan_revenue_field(tree, "unknown_field"))

    def test_missing_yan_revenue_semantics_is_hold_not_zero(self):
        payload = dict(YAN)
        payload["tree"] = {"fields": [{"name": "shows", "semantic": "delivery"}]}
        payload["selected_revenue_field"] = None
        collector = replace(self.yan(payload), revenue_field=None)
        outcome = self.orchestrator.run("fixture-site", collector)
        self.assertEqual(RunStatus.HELD, outcome.status)
        self.assertIn("yan_revenue_semantics_unavailable", outcome.hold_reasons)
        self.assertEqual(0, outcome.monetization_fact_count)

    def test_raw_is_accepted_before_normalization(self):
        self.orchestrator.run("fixture-site", self.direct())
        self.assertLess(self.relational.operation_log.index("raw:accepted"),
            self.relational.operation_log.index("facts:normalized"))

    def test_same_content_replay_is_idempotent_and_deterministic(self):
        first = self.orchestrator.run("fixture-site", self.direct())
        first_facts = dict(self.relational.traffic_facts)
        second = self.orchestrator.run("fixture-site", self.direct())
        self.assertTrue(second.replay)
        self.assertEqual(first.run_id, second.run_id)
        self.assertEqual(first_facts, self.relational.traffic_facts)
        self.assertEqual(1, len(self.relational.traffic_facts))

    def test_conflicting_raw_identity_holds_without_new_facts(self):
        self.orchestrator.run("fixture-site", self.direct())
        changed = dict(DIRECT); changed["report_tsv"] = DIRECT["report_tsv"].replace("12.340000", "99.000000")
        outcome = self.orchestrator.run("fixture-site", self.direct(changed))
        self.assertEqual(RunStatus.HELD, outcome.status)
        self.assertIn("raw_snapshot_conflict", outcome.hold_reasons)
        self.assertEqual(1, len(self.relational.traffic_facts))

    def test_incomplete_pagination_and_stale_window_hold(self):
        partial = dict(METRICA); partial["pagination_incomplete"] = True
        partial_result = self.orchestrator.run("fixture-site", self.metrica(partial))
        self.assertIn("incomplete_pagination", partial_result.hold_reasons)
        stale = replace(self.direct(), captured_at="2026-09-10T12:00:00+00:00")
        stale_result = self.orchestrator.run("other-site", stale)
        self.assertIn("stale_source_window", stale_result.hold_reasons)

    def test_money_ambiguity_is_held(self):
        ambiguous = dict(METRICA); ambiguous["currency"] = None
        outcome = self.orchestrator.run("fixture-site", self.metrica(ambiguous))
        self.assertIn("ambiguous_currency_or_money_basis", outcome.hold_reasons)
        self.assertFalse(outcome.optimizer_consumable)

    def test_missing_live_credentials_fail_without_provider_call(self):
        collector = DirectCollector(FakeTransport([]), self.config, None, self.day,
            captured_at=FIXTURE_CAPTURED_AT)
        outcome = self.orchestrator.run("fixture-site", collector)
        self.assertEqual(RunStatus.FAILED, outcome.status)
        self.assertEqual([], collector.transport.requests)


if __name__ == "__main__": unittest.main()
