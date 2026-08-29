import unittest
from dataclasses import replace
from decimal import Decimal

from profit_engine_runtime.direct_weekly_budget import (
    WeeklyBudgetCapability,
    inspect_weekly_budget,
)
from profit_engine_runtime.direct_weekly_budget_advisory import (
    WeeklyBudgetAdvisoryState,
    build_weekly_budget_advisory,
)
from profit_engine_runtime.direct_weekly_budget_probe import WeeklyBudgetProbeResult


class WeeklyBudgetAdvisoryTests(unittest.TestCase):
    def campaign(self, *, micros=100_000_000, package=None, second_slot=False):
        bidding = {
            "Search": {
                "BiddingStrategyType": "WB_MAXIMUM_CLICKS",
                "WbMaximumClicks": {"WeeklySpendLimit": micros},
            },
            "Network": {
                "BiddingStrategyType": "NETWORK_DEFAULT",
                "NetworkDefault": {},
            },
        }
        if second_slot:
            bidding["Network"] = {
                "BiddingStrategyType": "WB_MAXIMUM_CLICKS",
                "WbMaximumClicks": {"WeeklySpendLimit": 80_000_000},
            }
        typed = {"BiddingStrategy": bidding}
        if package is not None:
            typed["PackageBiddingStrategy"] = package
        return {"Id": 101, "TextCampaign": typed}

    def probe(self, campaign):
        return WeeklyBudgetProbeResult(
            campaign_id="101",
            campaign_type="TEXT_CAMPAIGN",
            state="ON",
            status="ACCEPTED",
            inspection=inspect_weekly_budget(campaign),
            request_id="req-fixture",
            units="1/99/1000",
        )

    def test_exact_slot_ready_shadow_plan_never_write_authority(self):
        advisory = build_weekly_budget_advisory(
            probe=self.probe(self.campaign()),
            proposed_weekly_spend_limit=Decimal("120"),
        )
        self.assertEqual(WeeklyBudgetAdvisoryState.READY_FOR_SHADOW_PLAN, advisory.state)
        self.assertEqual(Decimal("100"), advisory.current_weekly_spend_limit)
        self.assertEqual(Decimal("120"), advisory.proposed_weekly_spend_limit)
        self.assertEqual(Decimal("20.0"), advisory.increase_percent)
        self.assertFalse(advisory.owner_approval_required)
        self.assertFalse(advisory.provider_write_allowed)
        self.assertTrue(advisory.integrity_valid)
        self.assertIsNotNone(advisory.plan_digest)

    def test_20_01_percent_is_pending_owner_approval(self):
        advisory = build_weekly_budget_advisory(
            probe=self.probe(self.campaign()),
            proposed_weekly_spend_limit=Decimal("120.01"),
        )
        self.assertEqual(WeeklyBudgetAdvisoryState.PENDING_OWNER_APPROVAL, advisory.state)
        self.assertTrue(advisory.owner_approval_required)
        self.assertFalse(advisory.provider_write_allowed)
        self.assertIn("weekly_budget_increase_above_20_requires_owner_approval", advisory.reasons)

    def test_package_strategy_maps_to_explicit_hold(self):
        advisory = build_weekly_budget_advisory(
            probe=self.probe(self.campaign(package={"StrategyId": 777})),
            proposed_weekly_spend_limit=Decimal("110"),
        )
        self.assertEqual(WeeklyBudgetAdvisoryState.HOLD_PACKAGE_STRATEGY_SCOPE, advisory.state)
        self.assertFalse(advisory.provider_write_allowed)
        self.assertIsNone(advisory.plan_digest)

    def test_multiple_slots_map_to_ambiguous_hold(self):
        advisory = build_weekly_budget_advisory(
            probe=self.probe(self.campaign(second_slot=True)),
            proposed_weekly_spend_limit=Decimal("110"),
        )
        self.assertEqual(WeeklyBudgetAdvisoryState.HOLD_AMBIGUOUS_BUDGET_SCOPE, advisory.state)
        self.assertFalse(advisory.provider_write_allowed)

    def test_absent_limit_maps_to_no_limit_hold(self):
        campaign = self.campaign()
        del campaign["TextCampaign"]["BiddingStrategy"]["Search"]["WbMaximumClicks"]["WeeklySpendLimit"]
        advisory = build_weekly_budget_advisory(
            probe=self.probe(campaign),
            proposed_weekly_spend_limit=Decimal("110"),
        )
        self.assertEqual(WeeklyBudgetAdvisoryState.HOLD_NO_WEEKLY_SPEND_LIMIT, advisory.state)
        self.assertFalse(advisory.provider_write_allowed)

    def test_invalid_provider_shape_maps_to_hold(self):
        advisory = build_weekly_budget_advisory(
            probe=self.probe(self.campaign(micros="100000000")),
            proposed_weekly_spend_limit=Decimal("110"),
        )
        self.assertEqual(WeeklyBudgetCapability.INVALID_PROVIDER_SHAPE, self.probe(self.campaign(micros="100000000")).inspection.capability)
        self.assertEqual(WeeklyBudgetAdvisoryState.HOLD_INVALID_PROVIDER_SHAPE, advisory.state)
        self.assertFalse(advisory.provider_write_allowed)

    def test_tampered_inspection_and_campaign_mismatch_fail_closed(self):
        probe = self.probe(self.campaign())
        tampered = replace(probe.inspection, inspection_digest="0" * 64)
        with self.assertRaises(ValueError):
            build_weekly_budget_advisory(
                probe=replace(probe, inspection=tampered),
                proposed_weekly_spend_limit=Decimal("110"),
            )
        with self.assertRaises(ValueError):
            build_weekly_budget_advisory(
                probe=replace(probe, campaign_id="102"),
                proposed_weekly_spend_limit=Decimal("110"),
            )

    def test_probe_write_authority_is_rejected(self):
        probe = self.probe(self.campaign())
        with self.assertRaises(ValueError):
            build_weekly_budget_advisory(
                probe=replace(probe, provider_write_allowed=True),
                proposed_weekly_spend_limit=Decimal("110"),
            )


if __name__ == "__main__":
    unittest.main()
