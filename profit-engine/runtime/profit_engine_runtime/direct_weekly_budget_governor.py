"""Read-only binding between current Direct WeeklySpendLimit truth and Budget Governor."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from decimal import Decimal, InvalidOperation
from enum import StrEnum
from hashlib import sha256
import json

from .campaign_factory import digest
from .day10_public import ActionProposal, GovernorDecision, GovernorState, ProposalKind
from .direct_controller import ProviderTarget
from .direct_weekly_budget_advisory import WeeklyBudgetAdvisory, WeeklyBudgetAdvisoryState


class WeeklyBudgetGovernorBindingState(StrEnum):
    SHADOW_GOVERNOR_READY = "SHADOW_GOVERNOR_READY"
    PENDING_OWNER_APPROVAL = "PENDING_OWNER_APPROVAL"
    BLOCKED_ADVISORY_HOLD = "BLOCKED_ADVISORY_HOLD"
    BLOCKED_TARGET_BINDING = "BLOCKED_TARGET_BINDING"
    BLOCKED_PROPOSAL_BINDING = "BLOCKED_PROPOSAL_BINDING"
    BLOCKED_GOVERNOR_BINDING = "BLOCKED_GOVERNOR_BINDING"


@dataclass(frozen=True)
class WeeklyBudgetGovernorBinding:
    binding_version: str
    site_id: str
    target_ref: str
    provider_entity_id: str
    campaign_id: str
    state: WeeklyBudgetGovernorBindingState
    reasons: tuple[str, ...]
    proposal_digest: str
    advisory_digest: str
    governor_state: str
    increase_percent: Decimal | None
    owner_approval_required: bool
    provider_write_allowed: bool
    binding_digest: str

    @property
    def integrity_valid(self) -> bool:
        value = asdict(self)
        recorded = value.pop("binding_digest")
        return recorded == _digest(value)


def bind_weekly_budget_governor(
    *,
    target: ProviderTarget,
    proposal: ActionProposal,
    advisory: WeeklyBudgetAdvisory,
    governor: GovernorDecision,
) -> WeeklyBudgetGovernorBinding:
    if not advisory.integrity_valid:
        raise ValueError("weekly-budget advisory integrity invalid")
    if not _proposal_integrity_valid(proposal):
        return _binding(
            target, proposal, advisory, governor,
            WeeklyBudgetGovernorBindingState.BLOCKED_PROPOSAL_BINDING,
            ("action_proposal_integrity_invalid",),
        )
    if governor.provider_write_allowed or governor.provider_requests != 0 or governor.advertising_spend != 0:
        return _binding(
            target, proposal, advisory, governor,
            WeeklyBudgetGovernorBindingState.BLOCKED_GOVERNOR_BINDING,
            ("governor_must_remain_read_only",),
        )
    if (
        target.entity_type != "campaign"
        or target.provider not in {"yandex_direct", "direct"}
        or target.site_id != proposal.site_id
        or proposal.target_refs.get("provider_target") != target.target_ref
        or str(target.provider_entity_id) != advisory.campaign_id
    ):
        return _binding(
            target, proposal, advisory, governor,
            WeeklyBudgetGovernorBindingState.BLOCKED_TARGET_BINDING,
            ("exact_campaign_target_binding_invalid",),
        )

    if advisory.state not in {
        WeeklyBudgetAdvisoryState.READY_FOR_SHADOW_PLAN,
        WeeklyBudgetAdvisoryState.PENDING_OWNER_APPROVAL,
    }:
        return _binding(
            target, proposal, advisory, governor,
            WeeklyBudgetGovernorBindingState.BLOCKED_ADVISORY_HOLD,
            tuple(dict.fromkeys((*advisory.reasons, advisory.state.value))),
        )

    if proposal.kind not in {
        ProposalKind.SCALE,
        ProposalKind.TEST,
        ProposalKind.LEARN,
        ProposalKind.REDUCE,
    }:
        return _binding(
            target, proposal, advisory, governor,
            WeeklyBudgetGovernorBindingState.BLOCKED_PROPOSAL_BINDING,
            ("proposal_kind_not_budget_plannable",),
        )

    try:
        current = Decimal(proposal.current_weekly_budget or "")
        proposed = Decimal(proposal.proposed_weekly_budget or "")
    except (InvalidOperation, ValueError):
        return _binding(
            target, proposal, advisory, governor,
            WeeklyBudgetGovernorBindingState.BLOCKED_PROPOSAL_BINDING,
            ("proposal_weekly_budget_missing_or_invalid",),
        )

    if (
        advisory.current_weekly_spend_limit is None
        or advisory.proposed_weekly_spend_limit is None
        or current != advisory.current_weekly_spend_limit
        or proposed != advisory.proposed_weekly_spend_limit
        or proposal.owner_approval_required != advisory.owner_approval_required
    ):
        return _binding(
            target, proposal, advisory, governor,
            WeeklyBudgetGovernorBindingState.BLOCKED_PROPOSAL_BINDING,
            ("proposal_budget_does_not_match_live_weekly_spend_limit_plan",),
        )

    if governor.increase_percent != advisory.increase_percent:
        return _binding(
            target, proposal, advisory, governor,
            WeeklyBudgetGovernorBindingState.BLOCKED_GOVERNOR_BINDING,
            ("governor_increase_percent_mismatch",),
        )

    if advisory.state == WeeklyBudgetAdvisoryState.PENDING_OWNER_APPROVAL:
        if governor.state != GovernorState.PENDING_OWNER_APPROVAL:
            return _binding(
                target, proposal, advisory, governor,
                WeeklyBudgetGovernorBindingState.BLOCKED_GOVERNOR_BINDING,
                ("above_20_budget_plan_must_remain_pending_owner_approval",),
            )
        return _binding(
            target, proposal, advisory, governor,
            WeeklyBudgetGovernorBindingState.PENDING_OWNER_APPROVAL,
            ("exact_owner_approval_required_above_20_percent",),
        )

    if governor.state != GovernorState.GOVERNOR_READY_FOR_DAY11_CONTROLLER:
        return _binding(
            target, proposal, advisory, governor,
            WeeklyBudgetGovernorBindingState.BLOCKED_GOVERNOR_BINDING,
            ("governor_not_ready_for_shadow_budget_plan",),
        )
    return _binding(
        target, proposal, advisory, governor,
        WeeklyBudgetGovernorBindingState.SHADOW_GOVERNOR_READY,
        (),
    )


def _proposal_integrity_valid(proposal: ActionProposal) -> bool:
    value = asdict(proposal)
    recorded = value.pop("proposal_digest")
    return recorded == digest(value)


def _binding(
    target: ProviderTarget,
    proposal: ActionProposal,
    advisory: WeeklyBudgetAdvisory,
    governor: GovernorDecision,
    state: WeeklyBudgetGovernorBindingState,
    reasons: tuple[str, ...],
) -> WeeklyBudgetGovernorBinding:
    core = {
        "binding_version": "1.0",
        "site_id": target.site_id,
        "target_ref": target.target_ref,
        "provider_entity_id": str(target.provider_entity_id),
        "campaign_id": advisory.campaign_id,
        "state": state,
        "reasons": reasons,
        "proposal_digest": proposal.proposal_digest,
        "advisory_digest": advisory.advisory_digest,
        "governor_state": governor.state.value,
        "increase_percent": governor.increase_percent,
        "owner_approval_required": advisory.owner_approval_required,
        "provider_write_allowed": False,
    }
    return WeeklyBudgetGovernorBinding(**core, binding_digest=_digest(core))


def _digest(value: object) -> str:
    return sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    ).hexdigest()
