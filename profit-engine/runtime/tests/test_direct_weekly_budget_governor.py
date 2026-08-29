import unittest
from dataclasses import replace
from decimal import Decimal

from profit_engine_runtime.day10_public import (
    GovernorDecision,
    GovernorState,
    ProposalKind,
    build_action_proposal,
)
from profit_engine_runtime.direct_controller import ProviderTarget
from profit_engine_runtime.direct_weekly_budget import inspect_weekly_budget
from profit_engine_runtime.direct_weekly_budget_advisory import build_weekly_budget_advisory
from profit_engine_runtime.direct_weekly_budget_governor import (
    WeeklyBudgetGovernorBindingState,
    bind_weekly_budget_governor,
)
from profit_engine_runtime.direct_weekly_budget_probe import WeeklyBudgetProbeResult


class WeeklyBudgetGovernorTests(unittest.TestCase):
    def setUp(self):
        self.target = ProviderTarget(
            "target-fixture",
            "dilivox",
            "yandex_direct",
            "advertiser-fixture",
            "campaign",
            "101",
        )

    def campaign(self, *, package=None):
        typed = {
            "BiddingStrategy": {
                "Search": {
                    "BiddingStrategyType": "WB_MAXIMUM_CLICKS",
                    "WbMaximumClicks": {"WeeklySpendLimit": 100_000_000},
                }
            }
        }
        if package is not None:
            typed["PackageBiddingStrategy"] = package
        return {"Id": 101, "TextCampaign": typed}

    def advisory(self, proposed=Decimal("120"), *, package=None):
        probe = WeeklyBudgetProbeResult(
            campaign_id="101",
            campaign_type="TEXT_CAMPAIGN",
            state="ON",
            status="ACCEPTED",
            inspection=inspect_weekly_budget(self.campaign(package=package)),
            request_id="req-fixture",
            units="1/99/1000",
        )
        return build_weekly_budget_advisory(
            probe=probe,
            proposed_weekly_spend_limit=proposed,
        )

    def proposal(self, proposed="120", *, kind=ProposalKind.SCALE):
        return build_action_proposal(
            proposal_id="proposal-fixture",
            site_id="dilivox",
            kind=kind,
            target_refs={"provider_target": self.target.target_ref},
            strategy_evidence_digest="a" * 64,
            measurement_refs=("measurement-fixture",),
            provenance_refs=("provenance-fixture",),
            current_weekly_budget="100",
            proposed_weekly_budget=proposed,
            private_decision_ref="private-fixture",
            private_decision_digest="b" * 64,
            audit_metadata={"fixture": "true"},
        )

    def governor(self, *, state=GovernorState.GOVERNOR_READY_FOR_DAY11_CONTROLLER, increase=Decimal("20")):
        return GovernorDecision(state, (), increase)

    def test_exact_20_percent_binds_shadow_ready_without_write_authority(self):
        binding = bind_weekly_budget_governor(
            target=self.target,
            proposal=self.proposal(),
            advisory=self.advisory(),
            governor=self.governor(),
        )
        self.assertEqual(WeeklyBudgetGovernorBindingState.SHADOW_GOVERNOR_READY, binding.state)
        self.assertFalse(binding.owner_approval_required)
        self.assertFalse(binding.provider_write_allowed)
        self.assertTrue(binding.integrity_valid)

    def test_20_01_percent_requires_pending_owner_approval(self):
        binding = bind_weekly_budget_governor(
            target=self.target,
            proposal=self.proposal("120.01"),
            advisory=self.advisory(Decimal("120.01")),
            governor=self.governor(
                state=GovernorState.PENDING_OWNER_APPROVAL,
                increase=Decimal("20.0100"),
            ),
        )
        self.assertEqual(WeeklyBudgetGovernorBindingState.PENDING_OWNER_APPROVAL, binding.state)
        self.assertTrue(binding.owner_approval_required)
        self.assertFalse(binding.provider_write_allowed)

    def test_above_20_cannot_be_promoted_by_ready_governor(self):
        binding = bind_weekly_budget_governor(
            target=self.target,
            proposal=self.proposal("120.01"),
            advisory=self.advisory(Decimal("120.01")),
            governor=self.governor(increase=Decimal("20.0100")),
        )
        self.assertEqual(WeeklyBudgetGovernorBindingState.BLOCKED_GOVERNOR_BINDING, binding.state)
        self.assertFalse(binding.provider_write_allowed)

    def test_package_advisory_hold_remains_blocked(self):
        binding = bind_weekly_budget_governor(
            target=self.target,
            proposal=self.proposal("110"),
            advisory=self.advisory(Decimal("110"), package={"StrategyId": 777}),
            governor=self.governor(increase=Decimal("10")),
        )
        self.assertEqual(WeeklyBudgetGovernorBindingState.BLOCKED_ADVISORY_HOLD, binding.state)
        self.assertFalse(binding.provider_write_allowed)

    def test_exact_target_binding_is_required(self):
        wrong = replace(self.target, provider_entity_id="102")
        binding = bind_weekly_budget_governor(
            target=wrong,
            proposal=self.proposal(),
            advisory=self.advisory(),
            governor=self.governor(),
        )
        self.assertEqual(WeeklyBudgetGovernorBindingState.BLOCKED_TARGET_BINDING, binding.state)

    def test_proposal_budget_must_match_live_weekly_limit_plan(self):
        binding = bind_weekly_budget_governor(
            target=self.target,
            proposal=self.proposal("119"),
            advisory=self.advisory(Decimal("120")),
            governor=self.governor(increase=Decimal("19")),
        )
        self.assertEqual(WeeklyBudgetGovernorBindingState.BLOCKED_PROPOSAL_BINDING, binding.state)

    def test_tampered_proposal_fails_closed(self):
        proposal = replace(self.proposal(), proposal_digest="0" * 64)
        binding = bind_weekly_budget_governor(
            target=self.target,
            proposal=proposal,
            advisory=self.advisory(),
            governor=self.governor(),
        )
        self.assertEqual(WeeklyBudgetGovernorBindingState.BLOCKED_PROPOSAL_BINDING, binding.state)

    def test_governor_increase_and_read_only_contract_must_match(self):
        for governor in (
            self.governor(increase=Decimal("19")),
            replace(self.governor(), provider_write_allowed=True),
            replace(self.governor(), provider_requests=1),
        ):
            with self.subTest(governor=governor):
                binding = bind_weekly_budget_governor(
                    target=self.target,
                    proposal=self.proposal(),
                    advisory=self.advisory(),
                    governor=governor,
                )
                self.assertEqual(WeeklyBudgetGovernorBindingState.BLOCKED_GOVERNOR_BINDING, binding.state)
                self.assertFalse(binding.provider_write_allowed)

    def test_stop_proposal_is_not_weekly_budget_plannable(self):
        binding = bind_weekly_budget_governor(
            target=self.target,
            proposal=self.proposal(kind=ProposalKind.STOP),
            advisory=self.advisory(),
            governor=self.governor(),
        )
        self.assertEqual(WeeklyBudgetGovernorBindingState.BLOCKED_PROPOSAL_BINDING, binding.state)


if __name__ == "__main__":
    unittest.main()
