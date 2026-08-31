from __future__ import annotations

import json
import unittest

from profit_engine_runtime.day12_metrica_yan_compatibility_cli import (
    DIRECT_DIM,
    DILIVOX_CAMPAIGNS,
    YAN_METRICS,
    _provider_error,
    build_probe_queries,
)


class MetricaYanCompatibilityTests(unittest.TestCase):
    def test_probe_matrix_is_bounded_and_read_only_query_shapes_are_exact(self):
        probes = build_probe_queries(
            counter_id="110349067",
            date_from="2026-08-01",
            date_to="2026-08-30",
        )
        self.assertEqual(6, len(probes))
        names = [name for name, _ in probes]
        self.assertEqual(len(names), len(set(names)))
        for _, query in probes:
            self.assertEqual("110349067", query["ids"])
            self.assertEqual("2026-08-01", query["date1"])
            self.assertEqual("2026-08-30", query["date2"])
            self.assertEqual("full", query["accuracy"])
            self.assertEqual("100000", query["limit"])

        by_name = dict(probes)
        self.assertEqual(YAN_METRICS, by_name["yan_total_by_date"]["metrics"])
        self.assertIn(DIRECT_DIM, by_name["direct_campaign_dimension_visits"]["dimensions"])
        self.assertEqual("ym:s:visits", by_name["direct_campaign_dimension_visits"]["metrics"])
        self.assertEqual(YAN_METRICS, by_name["direct_campaign_dimension_yan"]["metrics"])
        for index, campaign_id in enumerate(DILIVOX_CAMPAIGNS, start=1):
            query = by_name[f"direct_campaign_filter_yan_{index}"]
            self.assertEqual("ym:s:date", query["dimensions"])
            self.assertEqual(YAN_METRICS, query["metrics"])
            self.assertEqual(f"{DIRECT_DIM}=='{campaign_id}'", query["filters"])

    def test_provider_error_extracts_safe_diagnostic_fields(self):
        body = json.dumps({
            "errors": [{
                "error_type": "invalid_parameter",
                "code": 4001,
                "message": "incompatible dimensions and metrics",
            }]
        }).encode("utf-8")
        self.assertEqual(
            ("invalid_parameter", "4001", "incompatible dimensions and metrics"),
            _provider_error(body),
        )
        self.assertEqual((None, None, None), _provider_error(b"not-json"))


if __name__ == "__main__":
    unittest.main()
