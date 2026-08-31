from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum
from hashlib import sha256
import json
from typing import Any, Mapping, Sequence


class RevenueGrain(StrEnum):
    EXACT_CRITERION = "EXACT_CRITERION"
    QUERY_CLUSTER = "QUERY_CLUSTER"
    LANDING_COHORT = "LANDING_COHORT"
    CAMPAIGN_ONLY = "CAMPAIGN_ONLY"
    NONE = "NONE"


class EconomicEvidenceState(StrEnum):
    READY = "READY"
    NO_SPEND = "NO_SPEND"
    REVENUE_GRAIN_TOO_COARSE = "REVENUE_GRAIN_TOO_COARSE"
    ATTRIBUTION_INCOMPLETE = "ATTRIBUTION_INCOMPLETE"
    RECONCILIATION_HOLD = "RECONCILIATION_HOLD"
    IDENTITY_HOLD = "IDENTITY_HOLD"


@dataclass(frozen=True)
class RevenueEvidence:
    evidence_id: str
    grain: RevenueGrain
    key: str
    revenue_rub: Decimal
    date_from: str
    date_to: str
    reconciled: bool
    attribution_share: Decimal
    source: str
    members: tuple[str, ...] = ()


@dataclass(frozen=True)
class CriterionEconomics:
    criterion_id: str
    spend_rub: Decimal
    clicks: int
    revenue_rub: Decimal | None
    k5: Decimal | None
    evidence_state: EconomicEvidenceState
    revenue_grain: RevenueGrain
    revenue_evidence_id: str | None
    attribution_share: Decimal | None
    automation_eligible: bool
    reasons: tuple[str, ...]
    digest: str


def build_criterion_economics(
    *,
    criterion_id: str,
    spend_rub: Decimal,
    clicks: int,
    date_from: str,
    date_to: str,
    evidence: Sequence[RevenueEvidence],
    min_attribution_share: Decimal = Decimal("0.80"),
) -> CriterionEconomics:
    if not str(criterion_id).isdigit():
        return _result(
            criterion_id=str(criterion_id), spend=spend_rub, clicks=clicks,
            revenue=None, k5=None, state=EconomicEvidenceState.IDENTITY_HOLD,
            grain=RevenueGrain.NONE, evidence_id=None, share=None, eligible=False,
            reasons=("criterion_id_not_numeric",),
        )
    if spend_rub < 0 or clicks < 0:
        raise ValueError("spend/clicks must not be negative")

    matches = [item for item in evidence if item.date_from == date_from and item.date_to == date_to and _applies(item, str(criterion_id))]
    exact = [item for item in matches if item.grain == RevenueGrain.EXACT_CRITERION]
    cluster = [item for item in matches if item.grain == RevenueGrain.QUERY_CLUSTER]
    selected: RevenueEvidence | None = None
    reasons: list[str] = []

    if len(exact) == 1:
        selected = exact[0]
    elif len(exact) > 1:
        reasons.append("multiple_exact_revenue_evidence")
    elif len(cluster) == 1:
        selected = cluster[0]
    elif len(cluster) > 1:
        reasons.append("multiple_cluster_revenue_evidence")

    if selected is None:
        coarse = [item for item in matches if item.grain in {RevenueGrain.LANDING_COHORT, RevenueGrain.CAMPAIGN_ONLY}]
        if coarse:
            return _result(
                criterion_id=str(criterion_id), spend=spend_rub, clicks=clicks,
                revenue=None, k5=None, state=EconomicEvidenceState.REVENUE_GRAIN_TOO_COARSE,
                grain=coarse[0].grain, evidence_id=coarse[0].evidence_id,
                share=coarse[0].attribution_share, eligible=False,
                reasons=("coarse_revenue_must_not_be_assigned_to_criterion",),
            )
        return _result(
            criterion_id=str(criterion_id), spend=spend_rub, clicks=clicks,
            revenue=None, k5=None, state=EconomicEvidenceState.ATTRIBUTION_INCOMPLETE,
            grain=RevenueGrain.NONE, evidence_id=None, share=None, eligible=False,
            reasons=tuple(reasons or ["no_criterion_or_cluster_revenue_evidence"]),
        )

    if not selected.reconciled:
        return _result(
            criterion_id=str(criterion_id), spend=spend_rub, clicks=clicks,
            revenue=None, k5=None, state=EconomicEvidenceState.RECONCILIATION_HOLD,
            grain=selected.grain, evidence_id=selected.evidence_id,
            share=selected.attribution_share, eligible=False,
            reasons=("revenue_evidence_not_reconciled",),
        )
    if selected.attribution_share < min_attribution_share or selected.attribution_share > Decimal("1"):
        return _result(
            criterion_id=str(criterion_id), spend=spend_rub, clicks=clicks,
            revenue=None, k5=None, state=EconomicEvidenceState.RECONCILIATION_HOLD,
            grain=selected.grain, evidence_id=selected.evidence_id,
            share=selected.attribution_share, eligible=False,
            reasons=("attribution_share_below_required_threshold",),
        )
    if selected.revenue_rub < 0:
        raise ValueError("revenue must not be negative")
    if spend_rub == 0:
        return _result(
            criterion_id=str(criterion_id), spend=spend_rub, clicks=clicks,
            revenue=selected.revenue_rub, k5=None, state=EconomicEvidenceState.NO_SPEND,
            grain=selected.grain, evidence_id=selected.evidence_id,
            share=selected.attribution_share, eligible=False,
            reasons=("zero_spend_has_no_k5",),
        )

    k5 = selected.revenue_rub / spend_rub
    return _result(
        criterion_id=str(criterion_id), spend=spend_rub, clicks=clicks,
        revenue=selected.revenue_rub, k5=k5, state=EconomicEvidenceState.READY,
        grain=selected.grain, evidence_id=selected.evidence_id,
        share=selected.attribution_share, eligible=True, reasons=(),
    )


def materialize_economics(
    *,
    cells: Sequence[Mapping[str, Any]],
    date_from: str,
    date_to: str,
    revenue_evidence: Sequence[RevenueEvidence],
) -> tuple[CriterionEconomics, ...]:
    result: list[CriterionEconomics] = []
    for cell in cells:
        criterion_id = str(cell.get("keyword_id") or cell.get("criterion_id") or "")
        spend = Decimal(str(cell.get("cost_rub") or "0"))
        clicks = int(cell.get("clicks") or 0)
        result.append(build_criterion_economics(
            criterion_id=criterion_id,
            spend_rub=spend,
            clicks=clicks,
            date_from=date_from,
            date_to=date_to,
            evidence=revenue_evidence,
        ))
    return tuple(result)


def _applies(evidence: RevenueEvidence, criterion_id: str) -> bool:
    if evidence.grain == RevenueGrain.EXACT_CRITERION:
        return evidence.key == criterion_id
    if evidence.grain == RevenueGrain.QUERY_CLUSTER:
        return criterion_id in evidence.members
    if evidence.grain in {RevenueGrain.LANDING_COHORT, RevenueGrain.CAMPAIGN_ONLY}:
        return True
    return False


def _result(
    *, criterion_id: str, spend: Decimal, clicks: int, revenue: Decimal | None,
    k5: Decimal | None, state: EconomicEvidenceState, grain: RevenueGrain,
    evidence_id: str | None, share: Decimal | None, eligible: bool, reasons: tuple[str, ...],
) -> CriterionEconomics:
    core = {
        "criterion_id": criterion_id,
        "spend_rub": format(spend, "f"),
        "clicks": clicks,
        "revenue_rub": format(revenue, "f") if revenue is not None else None,
        "k5": format(k5, "f") if k5 is not None else None,
        "evidence_state": state.value,
        "revenue_grain": grain.value,
        "revenue_evidence_id": evidence_id,
        "attribution_share": format(share, "f") if share is not None else None,
        "automation_eligible": eligible,
        "reasons": reasons,
    }
    digest = sha256(json.dumps(core, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    return CriterionEconomics(
        criterion_id=criterion_id,
        spend_rub=spend,
        clicks=clicks,
        revenue_rub=revenue,
        k5=k5,
        evidence_state=state,
        revenue_grain=grain,
        revenue_evidence_id=evidence_id,
        attribution_share=share,
        automation_eligible=eligible,
        reasons=reasons,
        digest=digest,
    )
