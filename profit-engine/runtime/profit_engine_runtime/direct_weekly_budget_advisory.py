"""Read-only WeeklySpendLimit advisory gate for guarded M6 planning.

The advisory turns an exact live campaign budget probe into a deterministic planning
state. It never produces a provider request and never grants write authority.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from decimal import Decimal
from enum import StrEnum
from hashlib import sha256
import json

from .direct_weekly_budget import (
    WeeklyBudgetCapability,
    WeeklyBudgetPlan,
    build_weekly_budget_plan,
)
from .direct_weekly_budget_probe import WeeklyBudgetProbeResult


class WeeklyBudgetAdvisoryState(StrEnum):
    READY_FOR_SHADOW_PLAN = "READY_FOR_SHADOW_PLAN"
    PENDING_OWNER_APPROVAL = "PENDING_OWNER_APPROVAL"
    HOLD_NO_WEEKLY_SPEND_LIMIT = "HOLD_NO_WEEKLY_SPEND_LIMIT"
    HOLD_AMBIGUOUS_BUDGET_SCOPE = "HOLD_AMBIGUOUS_BUDGET_SCOPE"
    HOLD_PACKAGE_STRATEGY_SCOPE = "HOLD_PACKAGE_STRATEGY_SCOPE"
    HOLD_INVALID_PROVIDER_SHAPE = "HOLD_INVALID_PROVIDER_SHAPE"


@dataclass(frozen=True)
class WeeklyBudgetAdvisory:
    advisory_version: str
    campaign_id: str
    state: WeeklyBudgetAdvisoryState
    reasons: tuple[str, ...]
    inspection_digest: str
    plan_digest: str | None
    current_weekly_spend_limit: Decimal | None
    proposed_weekly_spend_limit: Decimal | None
    increase_percent: Decimal | None
    owner_approval_required: bool
    provider_write_allowed: bool
    advisory_digest: str

    @property
    def integrity_valid(self) -> bool:
        value = asdict(self)
        recorded = value.pop("advisory_digest")
        return recorded == _digest(value)


def build_weekly_budget_advisory(
    *,
    probe: WeeklyBudgetProbeResult,
    proposed_weekly_spend_limit: Decimal,
) -> WeeklyBudgetAdvisory:
    if probe.provider_write_allowed:
        raise ValueError("read-only budget probe must never grant provider write authority")
    inspection = probe.inspection
    if not inspection.integrity_valid:
        raise ValueError("weekly-budget inspection integrity invalid")
    if probe.campaign_id != inspection.campaign_id:
        raise ValueError("probe/inspection campaign mismatch")

    capability = inspection.capability
    if capability == WeeklyBudgetCapability.EXACT_ONE_SLOT:
        plan = build_weekly_budget_plan(
            inspection=inspection,
            proposed_weekly_spend_limit=proposed_weekly_spend_limit,
        )
        state = (
            WeeklyBudgetAdvisoryState.PENDING_OWNER_APPROVAL
            if plan.owner_approval_required
            else WeeklyBudgetAdvisoryState.READY_FOR_SHADOW_PLAN
        )
        reasons = (
            ("weekly_budget_increase_above_20_requires_owner_approval",)
            if plan.owner_approval_required
            else ()
        )
        return _advisory_from_plan(probe=probe, plan=plan, state=state, reasons=reasons)

    mapping = {
        WeeklyBudgetCapability.NO_WEEKLY_SPEND_LIMIT: (
            WeeklyBudgetAdvisoryState.HOLD_NO_WEEKLY_SPEND_LIMIT,
            "weekly_spend_limit_not_observed",
        ),
        WeeklyBudgetCapability.AMBIGUOUS_MULTIPLE_SLOTS: (
            WeeklyBudgetAdvisoryState.HOLD_AMBIGUOUS_BUDGET_SCOPE,
            "multiple_weekly_spend_limit_slots",
        ),
        WeeklyBudgetCapability.PACKAGE_STRATEGY_REQUIRES_SEPARATE_SCOPE: (
            WeeklyBudgetAdvisoryState.HOLD_PACKAGE_STRATEGY_SCOPE,
            "package_strategy_requires_separate_budget_scope",
        ),
        WeeklyBudgetCapability.INVALID_PROVIDER_SHAPE: (
            WeeklyBudgetAdvisoryState.HOLD_INVALID_PROVIDER_SHAPE,
            "invalid_or_incomplete_provider_budget_shape",
        ),
    }
    try:
        state, reason = mapping[capability]
    except KeyError as exc:
        raise ValueError("unsupported weekly-budget capability") from exc
    core = {
        "advisory_version": "1.0",
        "campaign_id": probe.campaign_id,
        "state": state,
        "reasons": tuple(dict.fromkeys((*inspection.reasons, reason))),
        "inspection_digest": inspection.inspection_digest,
        "plan_digest": None,
        "current_weekly_spend_limit": None,
        "proposed_weekly_spend_limit": None,
        "increase_percent": None,
        "owner_approval_required": False,
        "provider_write_allowed": False,
    }
    return WeeklyBudgetAdvisory(**core, advisory_digest=_digest(core))


def _advisory_from_plan(
    *,
    probe: WeeklyBudgetProbeResult,
    plan: WeeklyBudgetPlan,
    state: WeeklyBudgetAdvisoryState,
    reasons: tuple[str, ...],
) -> WeeklyBudgetAdvisory:
    if not plan.integrity_valid or plan.provider_write_allowed:
        raise ValueError("weekly-budget plan must be integrity-valid and read-only")
    core = {
        "advisory_version": "1.0",
        "campaign_id": probe.campaign_id,
        "state": state,
        "reasons": reasons,
        "inspection_digest": probe.inspection.inspection_digest,
        "plan_digest": plan.plan_digest,
        "current_weekly_spend_limit": plan.current_weekly_spend_limit,
        "proposed_weekly_spend_limit": plan.proposed_weekly_spend_limit,
        "increase_percent": plan.increase_percent,
        "owner_approval_required": plan.owner_approval_required,
        "provider_write_allowed": False,
    }
    return WeeklyBudgetAdvisory(**core, advisory_digest=_digest(core))


def _digest(value: object) -> str:
    return sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    ).hexdigest()
