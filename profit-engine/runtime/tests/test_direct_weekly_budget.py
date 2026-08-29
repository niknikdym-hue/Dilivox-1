import unittest
from dataclasses import replace
from decimal import Decimal

from profit_engine_runtime.direct_weekly_budget import (
    WeeklyBudgetCapability,
    build_weekly_budget_plan,
    inspect_weekly_budget,
)


class WeeklyBudgetPlannerTests(unittest.TestCase):
    def single_campaign(self, micros=100_000_000):
        return {
            "Id": 101,
            "TextCampaign": {
                "BiddingStrategy": {
                    "Search": {
                        "BiddingStrategyType": "WB_MAXIMUM_CLICKS",
                        "WbMaximumClicks": {
                            "WeeklySpendLimit": micros,
                            "BudgetType": "WEEKLY_BUDGET",
                        },
                    },
                    "Network": {
                        "BiddingStrategyType": "NETWORK_DEFAULT",
                        "NetworkDefault": {},
                    },
                }
            },
        }

    def test_exact_one_slot_is_inspectable_but_never_write_authority(self):
        inspection = inspect_weekly_budget(self.single_campaign())
        self.assertEqual(WeeklyBudgetCapability.EXACT_ONE_SLOT, inspection.capability)
        self.assertEqual(1, len(inspection.slots))
        self.assertTrue(inspection.integrity_valid)
        self.assertFalse(inspection.provider_write_allowed)
        slot = inspection.slots[0]
        self.assertEqual("TextCampaign", slot.campaign_type_field)
        self.assertEqual("Search", slot.placement)
        self.assertEqual("WB_MAXIMUM_CLICKS", slot.bidding_strategy_type)
        self.assertEqual("WbMaximumClicks", slot.strategy_field)
        self.assertEqual(Decimal("100"), slot.weekly_spend_limit)

    def test_exact_20_percent_needs_no_extra_owner_approval_but_20_01_does(self):
        inspection = inspect_weekly_budget(self.single_campaign())
        exact = build_weekly_budget_plan(
            inspection=inspection,
            proposed_weekly_spend_limit=Decimal("120"),
        )
        self.assertEqual(Decimal("20.0"), exact.increase_percent)
        self.assertFalse(exact.owner_approval_required)
        self.assertFalse(exact.provider_write_allowed)
        over = build_weekly_budget_plan(
            inspection=inspection,
            proposed_weekly_spend_limit=Decimal("120.01"),
        )
        self.assertEqual(Decimal("20.0100"), over.increase_percent)
        self.assertTrue(over.owner_approval_required)
        self.assertFalse(over.provider_write_allowed)

    def test_multiple_budget_slots_fail_closed(self):
        campaign = self.single_campaign()
        campaign["TextCampaign"]["BiddingStrategy"]["Network"] = {
            "BiddingStrategyType": "WB_MAXIMUM_CLICKS",
            "WbMaximumClicks": {"WeeklySpendLimit": 80_000_000},
        }
        inspection = inspect_weekly_budget(campaign)
        self.assertEqual(WeeklyBudgetCapability.AMBIGUOUS_MULTIPLE_SLOTS, inspection.capability)
        self.assertEqual(2, len(inspection.slots))
        with self.assertRaises(ValueError):
            build_weekly_budget_plan(
                inspection=inspection,
                proposed_weekly_spend_limit=Decimal("110"),
            )

    def test_absent_weekly_limit_fails_closed(self):
        campaign = self.single_campaign()
        del campaign["TextCampaign"]["BiddingStrategy"]["Search"]["WbMaximumClicks"]["WeeklySpendLimit"]
        inspection = inspect_weekly_budget(campaign)
        self.assertEqual(WeeklyBudgetCapability.NO_WEEKLY_SPEND_LIMIT, inspection.capability)
        with self.assertRaises(ValueError):
            build_weekly_budget_plan(
                inspection=inspection,
                proposed_weekly_spend_limit=Decimal("100"),
            )

    def test_malformed_provider_value_fails_closed(self):
        inspection = inspect_weekly_budget(self.single_campaign(micros="100000000"))
        self.assertEqual(WeeklyBudgetCapability.INVALID_PROVIDER_SHAPE, inspection.capability)
        self.assertFalse(inspection.provider_write_allowed)

    def test_missing_campaign_id_fails_closed(self):
        campaign = self.single_campaign()
        del campaign["Id"]
        inspection = inspect_weekly_budget(campaign)
        self.assertEqual(WeeklyBudgetCapability.INVALID_PROVIDER_SHAPE, inspection.capability)

    def test_integrity_tamper_blocks_plan(self):
        inspection = inspect_weekly_budget(self.single_campaign())
        tampered = replace(inspection, inspection_digest="0" * 64)
        with self.assertRaises(ValueError):
            build_weekly_budget_plan(
                inspection=tampered,
                proposed_weekly_spend_limit=Decimal("110"),
            )

    def test_fractional_micros_and_nonpositive_proposals_rejected(self):
        inspection = inspect_weekly_budget(self.single_campaign())
        for value in (Decimal("0"), Decimal("-1"), Decimal("1.0000001")):
            with self.subTest(value=value), self.assertRaises(ValueError):
                build_weekly_budget_plan(
                    inspection=inspection,
                    proposed_weekly_spend_limit=value,
                )


if __name__ == "__main__":
    unittest.main()
