from __future__ import annotations

import unittest

from profit_engine_runtime.owner_advisor import build_owner_advice


class OwnerAdvisorTests(unittest.TestCase):
    def test_below_target_prioritizes_cost_reduction_and_blocks_budget_growth(self):
        advice = build_owner_advice(
            monetization_ready=True,
            campaigns=[{"campaign_id": "1"}, {"campaign_id": "2"}],
            manual_search_state={"state": "BUILD_FIRST"},
            money=[
                {
                    "label": "Dilivox",
                    "state": "READY_FOR_CANDIDATE_EVALUATION",
                    "direct_spend_rub": "100.00",
                    "metrica_attributed_yan_revenue_rub": "400.00",
                    "k5_observed": "4.00",
                },
                {
                    "label": "dilivox.ru",
                    "state": "NO_DIRECT_SPEND",
                    "direct_spend_rub": "0.00",
                    "metrica_attributed_yan_revenue_rub": "0.00",
                    "k5_observed": None,
                },
            ],
        )
        self.assertEqual("BELOW_TARGET", advice["portfolio"]["status"])
        self.assertEqual("4.00", advice["portfolio"]["k5"])
        self.assertIn("снизить стоимость", advice["primary_action"]["title"])
        self.assertIn("не увеличивать", advice["primary_action"]["prohibited"].lower())
        self.assertFalse(advice["provider_write_allowed"])
        self.assertEqual("LOCKED", advice["writer_state"])

    def test_target_met_recommends_hold_not_immediate_scale(self):
        advice = build_owner_advice(
            monetization_ready=True,
            campaigns=[{"campaign_id": "1"}],
            manual_search_state={},
            money=[{
                "label": "Dilivox",
                "state": "READY_FOR_CANDIDATE_EVALUATION",
                "direct_spend_rub": "100.00",
                "metrica_attributed_yan_revenue_rub": "550.00",
                "k5_observed": "5.50",
            }],
        )
        self.assertEqual("TARGET_MET", advice["portfolio"]["status"])
        self.assertEqual("5.50", advice["portfolio"]["k5"])
        self.assertIn("удерживать", advice["primary_action"]["title"].lower())
        self.assertIn("подтверждение", advice["primary_action"]["do_now"].lower())

    def test_data_hold_outranks_profit_recommendations(self):
        advice = build_owner_advice(
            monetization_ready=True,
            campaigns=[{"campaign_id": "1"}],
            manual_search_state={"state": "BUILD_FIRST"},
            money=[{
                "label": "Dilivox",
                "state": "HOLD_DATA_QUALITY",
                "direct_spend_rub": "100.00",
                "metrica_attributed_yan_revenue_rub": "700.00",
                "k5_observed": None,
                "holds": ["reconciliation_outside_tolerance"],
            }],
        )
        self.assertEqual("DATA_HOLD", advice["portfolio"]["status"])
        self.assertEqual("STOP", advice["primary_action"]["severity"])
        self.assertIn("не принимать", advice["primary_action"]["title"].lower())

    def test_missing_monetization_blocks_ad_changes(self):
        advice = build_owner_advice(
            monetization_ready=False,
            campaigns=[],
            manual_search_state={},
            money=[],
        )
        self.assertEqual("DATA_HOLD", advice["portfolio"]["status"])
        self.assertEqual("STOP", advice["primary_action"]["severity"])
        self.assertIn("не менять рекламу", advice["primary_action"]["title"].lower())


if __name__ == "__main__":
    unittest.main()
