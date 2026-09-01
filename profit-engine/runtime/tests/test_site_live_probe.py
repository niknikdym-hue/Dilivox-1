from __future__ import annotations

import unittest

from profit_engine_runtime.site_live_probe import MARKERS, inspect_html, probe_site


class SiteLiveProbeTests(unittest.TestCase):
    def test_complete_marker_set_passes_both_pages(self):
        html = "\n".join(MARKERS.values())
        result = probe_site(fetcher=lambda _: html)
        self.assertEqual("PRODUCTION_INSTRUMENTATION_PRESENT", result["state"])
        self.assertFalse(result["provider_write_allowed"])
        self.assertEqual(0, result["provider_write_requests"])
        self.assertEqual(2, len(result["pages"]))

    def test_partial_marker_set_is_not_accepted(self):
        html = MARKERS["metrica_counter"]
        result = probe_site(fetcher=lambda _: html)
        self.assertEqual("PRODUCTION_INSTRUMENTATION_MISSING_OR_PARTIAL", result["state"])

    def test_parallel_task006_controller_is_not_required_by_canonical_probe(self):
        html = "\n".join(MARKERS.values())
        self.assertNotIn("ProfitEngineEvents", html)
        self.assertNotIn("ProfitEngineSiteAgent", html)
        self.assertEqual("PRODUCTION_INSTRUMENTATION_PRESENT", probe_site(fetcher=lambda _: html)["state"])

    def test_inspection_hashes_html_without_exposing_other_data(self):
        html = "<html>" + "".join(MARKERS.values()) + "</html>"
        page = inspect_html("https://dilivox.ru/", html)
        self.assertTrue(page.http_ok)
        self.assertTrue(all(page.markers.values()))
        self.assertEqual(64, len(page.html_sha256 or ""))
        self.assertEqual(len(html.encode("utf-8")), page.bytes)


if __name__ == "__main__":
    unittest.main()
