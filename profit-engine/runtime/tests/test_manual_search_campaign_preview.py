from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from profit_engine_runtime.manual_search_campaign_preview import build_manual_search_preview


class ManualSearchCampaignPreviewTests(unittest.TestCase):
    def registry(self):
        directory = tempfile.TemporaryDirectory()
        path = Path(directory.name) / "content.json"
        path.write_text(json.dumps({
            "items": [{
                "site_id": "dilivox",
                "content_id": "content-catalog-1",
                "canonical_url": "/istorii/",
                "content_type": "catalog",
                "active": True,
                "monetization_eligible": True,
            }]
        }), encoding="utf-8")
        return directory, path

    def test_dedicated_campaign_preview_is_valid_but_inert(self):
        directory, path = self.registry()
        self.addCleanup(directory.cleanup)
        value = build_manual_search_preview(
            registry_path=path,
            weekly_budget_rub="700",
            keywords=["интерактивные истории", "детективы читать онлайн"],
        )
        self.assertEqual("DILIVOX | SEARCH | PROFIT ENGINE", value["campaign_name"])
        self.assertEqual("HIGHEST_POSITION", value["provider_shape"]["search_bidding_strategy_type"])
        self.assertEqual("SERVING_OFF", value["provider_shape"]["network_bidding_strategy_type"])
        self.assertEqual("700", value["provider_shape"]["weekly_spend_limit_rub"])
        self.assertEqual("PREVIEW_VALID", value["factory_preview"]["state"])
        self.assertFalse(value["provider_write_allowed"])
        self.assertFalse(value["create_authorized"])
        self.assertEqual(0, value["provider_requests"])
        self.assertEqual(0, value["advertising_spend"])
        self.assertTrue(all(not intent["executable"] for intent in value["factory_preview"]["intents"]))

    def test_keyword_universe_is_deduped_and_bounded(self):
        directory, path = self.registry()
        self.addCleanup(directory.cleanup)
        value = build_manual_search_preview(
            registry_path=path,
            weekly_budget_rub="1",
            keywords=["  тест   история ", "тест история"],
        )
        self.assertEqual(["тест история"], value["keywords"])
        with self.assertRaises(ValueError):
            build_manual_search_preview(registry_path=path, weekly_budget_rub="1", keywords=[])
        with self.assertRaises(ValueError):
            build_manual_search_preview(registry_path=path, weekly_budget_rub="1", keywords=[str(i) for i in range(101)])

    def test_budget_must_be_positive_and_remains_owner_fixed(self):
        directory, path = self.registry()
        self.addCleanup(directory.cleanup)
        with self.assertRaises(ValueError):
            build_manual_search_preview(registry_path=path, weekly_budget_rub="0", keywords=["x"])
        value = build_manual_search_preview(registry_path=path, weekly_budget_rub="500", keywords=["x"])
        self.assertTrue(value["provider_shape"]["weekly_budget_owner_fixed_for_initial_learning"])
        self.assertTrue(value["factory_preview"]["budget_proposal"]["owner_approval_required"])


if __name__ == "__main__":
    unittest.main()
