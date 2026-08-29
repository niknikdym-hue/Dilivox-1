"""Strategy-aware Direct weekly-budget capability planner.

This module replaces assumptions around legacy Campaign.DailyBudget with an explicit
read-only model of WeeklySpendLimit embedded in the campaign bidding strategy.
It never sends provider writes and deliberately fails closed when budget ownership
is absent or ambiguous across strategy placements.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from decimal import Decimal, InvalidOperation
from enum import StrEnum
from hashlib import sha256
import json
from typing import Any, Mapping


MICROS = Decimal("1000000")


class WeeklyBudgetCapability(StrEnum):
    EXACT_ONE_SLOT = "EXACT_ONE_SLOT"
    NO_WEEKLY_SPEND_LIMIT = "NO_WEEKLY_SPEND_LIMIT"
    AMBIGUOUS_MULTIPLE_SLOTS = "AMBIGUOUS_MULTIPLE_SLOTS"
    INVALID_PROVIDER_SHAPE = "INVALID_PROVIDER_SHAPE"


@dataclass(frozen=True)
class WeeklySpendLimitSlot:
    campaign_id: str
    campaign_type_field: str
    placement: str
    bidding_strategy_type: str
    strategy_field: str
    weekly_spend_limit_micros: int
    budget_type: str | None

    @property
    def weekly_spend_limit(self) -> Decimal:
        return Decimal(self.weekly_spend_limit_micros) / MICROS


@dataclass(frozen=True)
class WeeklyBudgetInspection:
    inspection_version: str
    campaign_id: str
    capability: WeeklyBudgetCapability
    slots: tuple[WeeklySpendLimitSlot, ...]
    reasons: tuple[str, ...]
    provider_write_allowed: bool
    inspection_digest: str

    @property
    def integrity_valid(self) -> bool:
        value = asdict(self)
        recorded = value.pop("inspection_digest")
        return recorded == _digest(value)


@dataclass(frozen=True)
class WeeklyBudgetPlan:
    plan_version: str
    campaign_id: str
    campaign_type_field: str
    placement: str
    bidding_strategy_type: str
    strategy_field: str
    current_weekly_spend_limit_micros: int
    proposed_weekly_spend_limit_micros: int
    current_weekly_spend_limit: Decimal
    proposed_weekly_spend_limit: Decimal
    increase_percent: Decimal
    owner_approval_required: bool
    inspection_digest: str
    provider_write_allowed: bool
    plan_digest: str

    @property
    def integrity_valid(self) -> bool:
        value = asdict(self)
        recorded = value.pop("plan_digest")
        return recorded == _digest(value)


def inspect_weekly_budget(campaign: Mapping[str, Any]) -> WeeklyBudgetInspection:
    campaign_id = str(campaign.get("Id", ""))
    if not campaign_id:
        return _inspection("", WeeklyBudgetCapability.INVALID_PROVIDER_SHAPE, (), ("campaign_id_missing",))

    slots: list[WeeklySpendLimitSlot] = []
    malformed = False
    for type_field, typed_value in campaign.items():
        if not type_field.endswith("Campaign") or not isinstance(typed_value, Mapping):
            continue
        bidding = typed_value.get("BiddingStrategy")
        if not isinstance(bidding, Mapping):
            continue
        for placement in ("Search", "Network"):
            placement_value = bidding.get(placement)
            if not isinstance(placement_value, Mapping):
                continue
            strategy_type = str(placement_value.get("BiddingStrategyType", ""))
            for strategy_field, strategy_value in placement_value.items():
                if strategy_field in {"BiddingStrategyType", "PlacementTypes"}:
                    continue
                if not isinstance(strategy_value, Mapping) or "WeeklySpendLimit" not in strategy_value:
                    continue
                raw = strategy_value.get("WeeklySpendLimit")
                if raw is None:
                    continue
                if type(raw) is not int or raw < 0:
                    malformed = True
                    continue
                slots.append(WeeklySpendLimitSlot(
                    campaign_id=campaign_id,
                    campaign_type_field=type_field,
                    placement=placement,
                    bidding_strategy_type=strategy_type,
                    strategy_field=strategy_field,
                    weekly_spend_limit_micros=raw,
                    budget_type=(
                        str(strategy_value.get("BudgetType"))
                        if strategy_value.get("BudgetType") is not None
                        else None
                    ),
                ))

    ordered = tuple(sorted(
        slots,
        key=lambda item: (
            item.campaign_type_field,
            item.placement,
            item.bidding_strategy_type,
            item.strategy_field,
        ),
    ))
    if malformed:
        return _inspection(campaign_id, WeeklyBudgetCapability.INVALID_PROVIDER_SHAPE, ordered, ("weekly_spend_limit_invalid",))
    if not ordered:
        return _inspection(campaign_id, WeeklyBudgetCapability.NO_WEEKLY_SPEND_LIMIT, (), ("weekly_spend_limit_not_observed",))
    if len(ordered) != 1:
        return _inspection(
            campaign_id,
            WeeklyBudgetCapability.AMBIGUOUS_MULTIPLE_SLOTS,
            ordered,
            ("multiple_weekly_spend_limit_slots_require_strategy_specific_reconciliation",),
        )
    return _inspection(campaign_id, WeeklyBudgetCapability.EXACT_ONE_SLOT, ordered, ())


def build_weekly_budget_plan(
    *,
    inspection: WeeklyBudgetInspection,
    proposed_weekly_spend_limit: Decimal,
) -> WeeklyBudgetPlan:
    if not inspection.integrity_valid:
        raise ValueError("weekly-budget inspection integrity invalid")
    if inspection.capability != WeeklyBudgetCapability.EXACT_ONE_SLOT or len(inspection.slots) != 1:
        raise ValueError("exactly one observed WeeklySpendLimit slot is required")
    if not isinstance(proposed_weekly_spend_limit, Decimal):
        raise ValueError("proposed weekly spend limit must be Decimal")
    if proposed_weekly_spend_limit <= 0:
        raise ValueError("proposed weekly spend limit must be positive")

    micros = proposed_weekly_spend_limit * MICROS
    if micros != micros.to_integral_value():
        raise ValueError("proposed weekly spend limit cannot be represented in integer micros")

    slot = inspection.slots[0]
    current = slot.weekly_spend_limit
    if current <= 0:
        raise ValueError("current WeeklySpendLimit must be positive for bounded percentage control")
    try:
        increase_percent = (
            (proposed_weekly_spend_limit - current) / current * Decimal("100")
        )
    except (InvalidOperation, ZeroDivisionError) as exc:
        raise ValueError("weekly budget percentage calculation failed") from exc

    core = {
        "plan_version": "1.0",
        "campaign_id": inspection.campaign_id,
        "campaign_type_field": slot.campaign_type_field,
        "placement": slot.placement,
        "bidding_strategy_type": slot.bidding_strategy_type,
        "strategy_field": slot.strategy_field,
        "current_weekly_spend_limit_micros": slot.weekly_spend_limit_micros,
        "proposed_weekly_spend_limit_micros": int(micros),
        "current_weekly_spend_limit": current,
        "proposed_weekly_spend_limit": proposed_weekly_spend_limit,
        "increase_percent": increase_percent,
        "owner_approval_required": increase_percent > Decimal("20.00"),
        "inspection_digest": inspection.inspection_digest,
        "provider_write_allowed": False,
    }
    return WeeklyBudgetPlan(**core, plan_digest=_digest(core))


def _inspection(
    campaign_id: str,
    capability: WeeklyBudgetCapability,
    slots: tuple[WeeklySpendLimitSlot, ...],
    reasons: tuple[str, ...],
) -> WeeklyBudgetInspection:
    core = {
        "inspection_version": "1.0",
        "campaign_id": campaign_id,
        "capability": capability,
        "slots": slots,
        "reasons": reasons,
        "provider_write_allowed": False,
    }
    return WeeklyBudgetInspection(**core, inspection_digest=_digest(core))


def _digest(value: object) -> str:
    return sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    ).hexdigest()
