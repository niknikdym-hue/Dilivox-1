from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum
from hashlib import sha256
import json

from .manual_search_economics import CriterionEconomics, EconomicEvidenceState


class BidDecision(StrEnum):
    LEARN = "LEARN"
    HOLD = "HOLD"
    RAISE_BID = "RAISE_BID"
    LOWER_BID = "LOWER_BID"
    PAUSE_TERM = "PAUSE_TERM"
    QUARANTINE = "QUARANTINE"


@dataclass(frozen=True)
class ShadowBidPolicy:
    target_k5: Decimal = Decimal("5")
    strong_k5: Decimal = Decimal("6")
    weak_k5: Decimal = Decimal("3")
    min_clicks: int = 8
    min_spend_rub: Decimal = Decimal("20")
    pause_min_clicks: int = 20
    pause_min_spend_rub: Decimal = Decimal("100")
    raise_step_pct: Decimal = Decimal("0.10")
    lower_step_pct: Decimal = Decimal("0.15")
    max_search_bid_rub: Decimal = Decimal("50")
    min_search_bid_rub: Decimal = Decimal("0.30")


@dataclass(frozen=True)
class ShadowBidProposal:
    criterion_id: str
    decision: BidDecision
    current_bid_rub: Decimal | None
    proposed_bid_rub: Decimal | None
    bid_change_pct: Decimal | None
    k5: Decimal | None
    clicks: int
    spend_rub: Decimal
    evidence_state: str
    automation_eligible: bool
    reasons: tuple[str, ...]
    executable: bool
    provider_write_allowed: bool
    digest: str


def propose_bid(
    *,
    economics: CriterionEconomics,
    current_bid_rub: Decimal | None,
    policy: ShadowBidPolicy = ShadowBidPolicy(),
) -> ShadowBidProposal:
    reasons: list[str] = []
    decision = BidDecision.HOLD
    proposed = current_bid_rub
    change: Decimal | None = Decimal("0") if current_bid_rub is not None else None

    if current_bid_rub is None or current_bid_rub <= 0:
        decision = BidDecision.QUARANTINE
        proposed = None
        change = None
        reasons.append("current_bid_missing_or_invalid")
    elif economics.evidence_state in {
        EconomicEvidenceState.REVENUE_GRAIN_TOO_COARSE,
        EconomicEvidenceState.RECONCILIATION_HOLD,
        EconomicEvidenceState.IDENTITY_HOLD,
    }:
        decision = BidDecision.QUARANTINE
        reasons.extend(economics.reasons or ("economic_evidence_hold",))
    elif economics.evidence_state == EconomicEvidenceState.ATTRIBUTION_INCOMPLETE:
        decision = BidDecision.LEARN
        reasons.append("revenue_attribution_incomplete")
    elif economics.evidence_state == EconomicEvidenceState.NO_SPEND:
        decision = BidDecision.LEARN
        reasons.append("no_spend_for_k5")
    elif economics.evidence_state != EconomicEvidenceState.READY:
        decision = BidDecision.HOLD
        reasons.append("economic_state_not_ready")
    elif economics.clicks < policy.min_clicks or economics.spend_rub < policy.min_spend_rub:
        decision = BidDecision.LEARN
        reasons.append("sample_below_bid_decision_threshold")
    elif economics.k5 is None:
        decision = BidDecision.QUARANTINE
        reasons.append("ready_state_without_k5")
    elif economics.k5 >= policy.strong_k5:
        candidate = min(current_bid_rub * (Decimal("1") + policy.raise_step_pct), policy.max_search_bid_rub)
        if candidate > current_bid_rub:
            decision = BidDecision.RAISE_BID
            proposed = candidate
            change = (candidate / current_bid_rub) - Decimal("1")
            reasons.append("k5_above_strong_threshold")
        else:
            decision = BidDecision.HOLD
            reasons.append("max_bid_ceiling_reached")
    elif economics.k5 >= policy.target_k5:
        decision = BidDecision.HOLD
        reasons.append("k5_meets_target")
    elif economics.k5 >= policy.weak_k5:
        candidate = max(current_bid_rub * (Decimal("1") - policy.lower_step_pct), policy.min_search_bid_rub)
        if candidate < current_bid_rub:
            decision = BidDecision.LOWER_BID
            proposed = candidate
            change = (candidate / current_bid_rub) - Decimal("1")
            reasons.append("k5_below_target")
        else:
            decision = BidDecision.HOLD
            reasons.append("min_bid_floor_reached")
    elif economics.clicks >= policy.pause_min_clicks and economics.spend_rub >= policy.pause_min_spend_rub:
        decision = BidDecision.PAUSE_TERM
        proposed = current_bid_rub
        change = Decimal("0")
        reasons.append("persistent_low_k5_after_sufficient_evidence")
    else:
        candidate = max(current_bid_rub * (Decimal("1") - policy.lower_step_pct), policy.min_search_bid_rub)
        decision = BidDecision.LOWER_BID if candidate < current_bid_rub else BidDecision.HOLD
        proposed = candidate
        change = (candidate / current_bid_rub) - Decimal("1") if candidate != current_bid_rub else Decimal("0")
        reasons.append("low_k5_but_pause_evidence_not_mature")

    proposed = _money(proposed) if proposed is not None else None
    change = change.quantize(Decimal("0.0001")) if change is not None else None
    core = {
        "criterion_id": economics.criterion_id,
        "decision": decision.value,
        "current_bid_rub": format(current_bid_rub, "f") if current_bid_rub is not None else None,
        "proposed_bid_rub": format(proposed, "f") if proposed is not None else None,
        "bid_change_pct": format(change, "f") if change is not None else None,
        "k5": format(economics.k5, "f") if economics.k5 is not None else None,
        "clicks": economics.clicks,
        "spend_rub": format(economics.spend_rub, "f"),
        "evidence_state": economics.evidence_state.value,
        "automation_eligible": economics.automation_eligible,
        "reasons": tuple(reasons),
        "executable": False,
        "provider_write_allowed": False,
    }
    digest = sha256(json.dumps(core, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    return ShadowBidProposal(
        criterion_id=economics.criterion_id,
        decision=decision,
        current_bid_rub=current_bid_rub,
        proposed_bid_rub=proposed,
        bid_change_pct=change,
        k5=economics.k5,
        clicks=economics.clicks,
        spend_rub=economics.spend_rub,
        evidence_state=economics.evidence_state.value,
        automation_eligible=economics.automation_eligible,
        reasons=tuple(reasons),
        executable=False,
        provider_write_allowed=False,
        digest=digest,
    )


def _money(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"))
