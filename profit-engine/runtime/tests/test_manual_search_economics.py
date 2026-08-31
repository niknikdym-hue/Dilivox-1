from __future__ import annotations

import unittest
from decimal import Decimal

from profit_engine_runtime.manual_search_economics import (
    EconomicEvidenceState,
    RevenueEvidence,
    RevenueGrain,
    build_criterion_economics,
)
from profit_engine_runtime.manual_search_shadow_controller import (
    BidDecision,
    ShadowBidPolicy,
    propose_bid,
)


class ManualSearchEconomicsTests(unittest.TestCase):
    def evidence(self, *, grain=RevenueGrain.EXACT_CRITERION, revenue="100", reconciled=True, share="1", members=()):
        return RevenueEvidence(
            evidence_id="rev-1",
            grain=grain,
            key="501" if grain == RevenueGrain.EXACT_CRITERION else "cluster-a",
            revenue_rub=Decimal(revenue),
            date_from="2026-08-01",
            date_to="2026-08-30",
            reconciled=reconciled,
            attribution_share=Decimal(share),
            source="fixture",
            members=tuple(members),
        )

    def economics(self, *, spend="20", clicks=10, evidence=None):
        return build_criterion_economics(
            criterion_id="501",
            spend_rub=Decimal(spend),
            clicks=clicks,
            date_from="2026-08-01",
            date_to="2026-08-30",
            evidence=[evidence or self.evidence()],
        )

    def test_exact_reconciled_evidence_computes_k5(self):
        value = self.economics(spend="20", evidence=self.evidence(revenue="100"))
        self.assertEqual(EconomicEvidenceState.READY, value.evidence_state)
        self.assertEqual(Decimal("5"), value.k5)
        self.assertTrue(value.automation_eligible)
        self.assertEqual(64, len(value.digest))

    def test_cluster_evidence_can_apply_only_to_explicit_member(self):
        value = self.economics(evidence=self.evidence(grain=RevenueGrain.QUERY_CLUSTER, members=("501", "502")))
        self.assertEqual(EconomicEvidenceState.READY, value.evidence_state)
        missing = build_criterion_economics(
            criterion_id="503", spend_rub=Decimal("20"), clicks=10,
            date_from="2026-08-01", date_to="2026-08-30",
            evidence=[self.evidence(grain=RevenueGrain.QUERY_CLUSTER, members=("501", "502"))],
        )
        self.assertEqual(EconomicEvidenceState.ATTRIBUTION_INCOMPLETE, missing.evidence_state)
        self.assertIsNone(missing.k5)

    def test_campaign_or_landing_revenue_is_never_assigned_to_criterion(self):
        for grain in (RevenueGrain.CAMPAIGN_ONLY, RevenueGrain.LANDING_COHORT):
            with self.subTest(grain=grain):
                value = self.economics(evidence=self.evidence(grain=grain))
                self.assertEqual(EconomicEvidenceState.REVENUE_GRAIN_TOO_COARSE, value.evidence_state)
                self.assertIsNone(value.revenue_rub)
                self.assertIsNone(value.k5)
                self.assertFalse(value.automation_eligible)

    def test_unreconciled_or_low_share_holds(self):
        unreconciled = self.economics(evidence=self.evidence(reconciled=False))
        low_share = self.economics(evidence=self.evidence(share="0.50"))
        self.assertEqual(EconomicEvidenceState.RECONCILIATION_HOLD, unreconciled.evidence_state)
        self.assertEqual(EconomicEvidenceState.RECONCILIATION_HOLD, low_share.evidence_state)

    def test_zero_spend_never_becomes_infinite_k5(self):
        value = self.economics(spend="0", clicks=0)
        self.assertEqual(EconomicEvidenceState.NO_SPEND, value.evidence_state)
        self.assertIsNone(value.k5)
        self.assertFalse(value.automation_eligible)

    def test_shadow_controller_is_non_executable_and_bounded(self):
        strong = self.economics(spend="20", clicks=10, evidence=self.evidence(revenue="140"))
        p = propose_bid(economics=strong, current_bid_rub=Decimal("10"))
        self.assertEqual(BidDecision.RAISE_BID, p.decision)
        self.assertEqual(Decimal("11.00"), p.proposed_bid_rub)
        self.assertFalse(p.executable)
        self.assertFalse(p.provider_write_allowed)

        target = self.economics(spend="20", clicks=10, evidence=self.evidence(revenue="100"))
        self.assertEqual(BidDecision.HOLD, propose_bid(economics=target, current_bid_rub=Decimal("10")).decision)

        weak = self.economics(spend="20", clicks=10, evidence=self.evidence(revenue="80"))
        lowered = propose_bid(economics=weak, current_bid_rub=Decimal("10"))
        self.assertEqual(BidDecision.LOWER_BID, lowered.decision)
        self.assertEqual(Decimal("8.50"), lowered.proposed_bid_rub)

    def test_controller_quarantines_coarse_data_and_pauses_only_on_mature_bad_evidence(self):
        coarse = self.economics(evidence=self.evidence(grain=RevenueGrain.CAMPAIGN_ONLY))
        self.assertEqual(BidDecision.QUARANTINE, propose_bid(economics=coarse, current_bid_rub=Decimal("10")).decision)

        bad = self.economics(spend="120", clicks=25, evidence=self.evidence(revenue="120"))
        paused = propose_bid(economics=bad, current_bid_rub=Decimal("10"))
        self.assertEqual(BidDecision.PAUSE_TERM, paused.decision)
        self.assertEqual(Decimal("10.00"), paused.proposed_bid_rub)

    def test_controller_respects_bid_ceiling_and_sample_thresholds(self):
        strong = self.economics(spend="20", clicks=10, evidence=self.evidence(revenue="200"))
        ceiling_policy = ShadowBidPolicy(max_search_bid_rub=Decimal("10"))
        held = propose_bid(economics=strong, current_bid_rub=Decimal("10"), policy=ceiling_policy)
        self.assertEqual(BidDecision.HOLD, held.decision)

        immature = self.economics(spend="5", clicks=2, evidence=self.evidence(revenue="100"))
        learn = propose_bid(economics=immature, current_bid_rub=Decimal("10"))
        self.assertEqual(BidDecision.LEARN, learn.decision)


if __name__ == "__main__":
    unittest.main()
