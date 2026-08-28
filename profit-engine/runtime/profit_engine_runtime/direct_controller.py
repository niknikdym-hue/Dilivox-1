"""Day-11 guarded Direct controller contracts.

This module is deliberately incapable of reaching Yandex Direct.  It produces
immutable plans and can exercise their state machine only through the in-memory
transport defined here.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field, replace
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
from enum import StrEnum
from threading import Lock
from typing import Any, Mapping, Sequence

from .campaign_factory import digest
from .day10_public import ActionProposal, GovernorDecision, GovernorState
from .redaction import redact


REAL_PROVIDER_REQUESTS = 0
ADVERTISING_SPEND = 0
PRODUCTION_WRITER_ENABLED = False
MAX_AUTONOMOUS_BUDGET_MUTATIONS_PER_CAMPAIGN_PER_DAY = 1
MAX_MUTATION_OBJECTS_PER_PROVIDER_REQUEST = 1
SAFE_METHODS = frozenset({
    "campaign.suspend", "campaign.resume", "ad.suspend", "ad.resume",
    "campaign.update_budget",
})


class ControllerState(StrEnum):
    CONTROLLER_PLAN_VALID = "CONTROLLER_PLAN_VALID"
    CONTROLLER_PLAN_INVALID = "CONTROLLER_PLAN_INVALID"
    BLOCKED_GOVERNOR_NOT_READY = "BLOCKED_GOVERNOR_NOT_READY"
    BLOCKED_OWNER_APPROVAL = "BLOCKED_OWNER_APPROVAL"
    BLOCKED_KILL_SWITCH = "BLOCKED_KILL_SWITCH"
    BLOCKED_STALE_PROVIDER_STATE = "BLOCKED_STALE_PROVIDER_STATE"
    BLOCKED_PROVIDER_CAPABILITY = "BLOCKED_PROVIDER_CAPABILITY"
    BLOCKED_BUDGET_MAPPING = "BLOCKED_BUDGET_MAPPING"
    BLOCKED_MUTATION_CADENCE = "BLOCKED_MUTATION_CADENCE"
    BLOCKED_EXECUTION_LOCK = "BLOCKED_EXECUTION_LOCK"
    READY_FOR_DAY12_EXECUTION = "READY_FOR_DAY12_EXECUTION"


@dataclass(frozen=True)
class GovernorEvidence:
    evidence_version: str
    proposal_digest: str
    decision: GovernorDecision
    evidence_digest: str

    @property
    def integrity_valid(self) -> bool:
        value = asdict(self); recorded = value.pop("evidence_digest")
        return recorded == digest(value)


def bind_governor(proposal: ActionProposal, decision: GovernorDecision) -> GovernorEvidence:
    core = {"evidence_version": "1.0", "proposal_digest": proposal.proposal_digest,
            "decision": decision}
    canonical = core | {"decision": asdict(decision)}
    return GovernorEvidence(**core, evidence_digest=digest(canonical))


@dataclass(frozen=True)
class ProviderTarget:
    target_ref: str
    site_id: str
    provider: str
    advertiser_ref: str
    entity_type: str
    provider_entity_id: str

    @property
    def lock_key(self) -> str:
        return ":".join((self.site_id, self.provider, self.advertiser_ref,
                         self.entity_type, self.provider_entity_id))


@dataclass
class ProviderIdentityRegistry:
    targets: dict[str, ProviderTarget] = field(default_factory=dict)

    def register(self, target: ProviderTarget) -> None:
        if not all((target.target_ref, target.site_id, target.provider,
                    target.advertiser_ref, target.provider_entity_id)):
            raise ValueError("exact provider identity required")
        if target.entity_type not in {"campaign", "ad"}:
            raise ValueError("unsupported entity type")
        self.targets[target.target_ref] = target

    def resolve_exact(self, target_ref: str) -> ProviderTarget | None:
        return self.targets.get(target_ref)


@dataclass(frozen=True)
class ProviderPreflightSnapshot:
    snapshot_version: str
    target_ref: str
    site_id: str
    provider: str
    advertiser_ref: str
    entity_type: str
    provider_entity_id: str
    normalized_state: str
    status: str
    current_provider_daily_budget: Decimal | None
    currency: str | None
    strategy_subtype: str
    fetched_at: str
    expires_at: str
    source_ref: str
    request_id: str | None
    units: int | None
    dq_holds: tuple[str, ...]
    snapshot_digest: str

    @property
    def integrity_valid(self) -> bool:
        value = asdict(self); recorded = value.pop("snapshot_digest")
        return recorded == digest(value)


def build_preflight(*, target: ProviderTarget, normalized_state: str, status: str,
                    current_provider_daily_budget: Decimal | None, currency: str | None,
                    strategy_subtype: str, fetched_at: datetime, ttl: timedelta,
                    source_ref: str, request_id: str | None = None,
                    units: int | None = None, dq_holds: Sequence[str] = ()) -> ProviderPreflightSnapshot:
    core = {"snapshot_version":"1.0", "target_ref":target.target_ref,
            "site_id":target.site_id, "provider":target.provider,
            "advertiser_ref":target.advertiser_ref, "entity_type":target.entity_type,
            "provider_entity_id":target.provider_entity_id,
            "normalized_state":normalized_state, "status":status,
            "current_provider_daily_budget":current_provider_daily_budget,
            "currency":currency, "strategy_subtype":strategy_subtype,
            "fetched_at":fetched_at.isoformat(), "expires_at":(fetched_at+ttl).isoformat(),
            "source_ref":source_ref, "request_id":request_id, "units":units,
            "dq_holds":tuple(sorted(set(dq_holds)))}
    return ProviderPreflightSnapshot(**core, snapshot_digest=digest(core))


@dataclass(frozen=True)
class OwnerApprovalEvidence:
    evidence_version: str
    approval_id: str
    proposal_digest: str
    site_id: str
    target_ref: str
    action_kind: str
    approved_weekly_budget: Decimal
    currency: str
    approved_at: str
    expires_at: str
    superseded: bool
    authority_ref: str
    evidence_digest: str

    @property
    def integrity_valid(self) -> bool:
        value = asdict(self); recorded = value.pop("evidence_digest")
        return recorded == digest(value)


def build_owner_approval(**values: Any) -> OwnerApprovalEvidence:
    core = {"evidence_version":"1.0", **values}
    return OwnerApprovalEvidence(**core, evidence_digest=digest(core))


@dataclass(frozen=True)
class ProviderBudgetPlan:
    plan_version: str
    current_weekly_budget: Decimal
    proposed_weekly_budget: Decimal
    current_provider_daily_budget: Decimal
    proposed_provider_daily_budget: Decimal
    active_days: tuple[int, ...]
    active_day_basis_ref: str
    mapping_version: str
    currency: str
    provider_integer_micros: int
    rounding_rule: str
    preflight_digest: str
    proposal_digest: str
    governor_evidence_digest: str
    owner_approval_digest: str | None
    plan_digest: str

    @property
    def integrity_valid(self) -> bool:
        value=asdict(self); recorded=value.pop("plan_digest")
        return recorded == digest(value)


def build_budget_plan(*, proposal: ActionProposal, governor: GovernorEvidence,
                      preflight: ProviderPreflightSnapshot, proposed_daily: Decimal,
                      active_days: Sequence[int], active_day_basis_ref: str,
                      owner_approval: OwnerApprovalEvidence | None = None,
                      mapping_version: str = "explicit-active-days-v1",
                      rounding_rule: str = "exact-micros") -> ProviderBudgetPlan:
    try:
        current = Decimal(proposal.current_weekly_budget or "")
        proposed = Decimal(proposal.proposed_weekly_budget or "")
    except (InvalidOperation, ValueError) as exc:
        raise ValueError("weekly budgets must be Decimal-compatible") from exc
    if not isinstance(proposed_daily, Decimal) or preflight.current_provider_daily_budget is None:
        raise ValueError("provider daily budgets must be Decimal")
    days = tuple(active_days)
    if not days or len(set(days)) != len(days) or any(day not in range(1, 8) for day in days):
        raise ValueError("explicit active-day basis required")
    if not active_day_basis_ref or preflight.currency != "RUB":
        raise ValueError("budget basis or currency invalid")
    if proposed_daily * len(days) != proposed or preflight.current_provider_daily_budget * len(days) != current:
        raise ValueError("weekly/provider mapping is not exact")
    micros = proposed_daily * Decimal("1000000")
    if micros != micros.to_integral_value():
        raise ValueError("provider micros conversion is inexact")
    core={"plan_version":"1.0", "current_weekly_budget":current,
          "proposed_weekly_budget":proposed,
          "current_provider_daily_budget":preflight.current_provider_daily_budget,
          "proposed_provider_daily_budget":proposed_daily,"active_days":days,
          "active_day_basis_ref":active_day_basis_ref,"mapping_version":mapping_version,
          "currency":"RUB","provider_integer_micros":int(micros),
          "rounding_rule":rounding_rule,"preflight_digest":preflight.snapshot_digest,
          "proposal_digest":proposal.proposal_digest,"governor_evidence_digest":governor.evidence_digest,
          "owner_approval_digest":owner_approval.evidence_digest if owner_approval else None}
    return ProviderBudgetPlan(**core, plan_digest=digest(core))


@dataclass(frozen=True)
class KillSwitch:
    scope: str
    scope_ref: str
    active: bool


@dataclass(frozen=True)
class MutationCadenceEvidence:
    evidence_version: str
    campaign_ref: str
    day: str
    timezone_offset_minutes: int
    day_basis_ref: str
    prior_autonomous_mutations: int | None
    audit_ref: str
    source_refs: tuple[str, ...]
    evidence_digest: str

    @property
    def integrity_valid(self) -> bool:
        value=asdict(self); recorded=value.pop("evidence_digest")
        return recorded == digest(value)


def build_mutation_cadence_evidence(*, campaign_ref: str, day: str,
                                    timezone_offset_minutes: int,
                                    day_basis_ref: str,
                                    prior_autonomous_mutations: int | None,
                                    audit_ref: str,
                                    source_refs: Sequence[str]) -> MutationCadenceEvidence:
    core={"evidence_version":"1.0","campaign_ref":campaign_ref,"day":day,
          "timezone_offset_minutes":timezone_offset_minutes,"day_basis_ref":day_basis_ref,
          "prior_autonomous_mutations":prior_autonomous_mutations,"audit_ref":audit_ref,
          "source_refs":tuple(source_refs)}
    return MutationCadenceEvidence(**core,evidence_digest=digest(core))


@dataclass(frozen=True)
class TrustedOwnerAuthorityRegistry:
    authority_refs: frozenset[str]

    def contains(self, authority_ref: str) -> bool:
        return bool(authority_ref) and authority_ref in self.authority_refs


@dataclass
class ExecutionLockRegistry:
    leases: dict[str, datetime] = field(default_factory=dict)
    _guard: Lock = field(default_factory=Lock, repr=False, compare=False)

    def is_locked(self, key: str, now: datetime) -> bool:
        with self._guard:
            return key in self.leases and self.leases[key] > now

    def acquire(self, key: str, now: datetime, ttl: timedelta) -> bool:
        with self._guard:
            if key in self.leases and self.leases[key] > now: return False
            self.leases[key] = now + ttl
            return True

    def release(self, key: str) -> None:
        with self._guard:
            self.leases.pop(key, None)


@dataclass(frozen=True)
class AuditRecord:
    sequence: int
    event: str
    occurred_at: str
    metadata: Mapping[str, Any]
    previous_hash: str
    record_hash: str


@dataclass
class AuditChain:
    records: list[AuditRecord] = field(default_factory=list)

    def append(self, event: str, occurred_at: datetime, metadata: Mapping[str, Any],
               secrets: Sequence[str] = ()) -> AuditRecord:
        safe = redact(dict(metadata), secrets)
        core={"sequence":len(self.records),"event":event,"occurred_at":occurred_at.isoformat(),
              "metadata":safe,"previous_hash":self.records[-1].record_hash if self.records else "GENESIS"}
        record=AuditRecord(**core, record_hash=digest(core)); self.records.append(record); return record

    def valid(self) -> bool:
        previous="GENESIS"
        for index, record in enumerate(self.records):
            core=asdict(record); recorded=core.pop("record_hash")
            if record.sequence != index or record.previous_hash != previous or digest(core) != recorded: return False
            previous=record.record_hash
        return True


@dataclass(frozen=True)
class RollbackPlan:
    plan_version: str
    source_preflight_digest: str
    method: str | None
    desired_state: Mapping[str, Any]
    executable: bool
    reason: str
    plan_digest: str


def derive_rollback(method: str, preflight: ProviderPreflightSnapshot) -> RollbackPlan:
    rollback_method: str | None = None; desired: dict[str, Any] = {}; reason="exact_preflight"
    if method == "campaign.update_budget" and preflight.current_provider_daily_budget is not None:
        rollback_method="campaign.update_budget"; desired={"daily_budget":preflight.current_provider_daily_budget}
    elif method.endswith(".suspend") and preflight.normalized_state == "ACTIVE":
        rollback_method=method.replace(".suspend", ".resume"); desired={"state":"ACTIVE"}
    elif method.endswith(".resume") and preflight.normalized_state == "SUSPENDED":
        rollback_method=method.replace(".resume", ".suspend"); desired={"state":"SUSPENDED"}
    else: reason="prior_state_does_not_prove_safe_inverse"
    core={"plan_version":"1.0","source_preflight_digest":preflight.snapshot_digest,
          "method":rollback_method,"desired_state":desired,"executable":False,"reason":reason}
    return RollbackPlan(**core, plan_digest=digest(core))


def pre_dispatch_snapshot_matches(expected: ProviderPreflightSnapshot,
                                  fresh: ProviderPreflightSnapshot,
                                  now: datetime) -> bool:
    """Fail-closed TOCTOU comparison over all mutation-relevant provider state."""
    return (expected.integrity_valid and fresh.integrity_valid and not fresh.dq_holds
        and now < datetime.fromisoformat(fresh.expires_at)
        and expected.target_ref == fresh.target_ref
        and expected.provider_entity_id == fresh.provider_entity_id
        and expected.normalized_state == fresh.normalized_state
        and expected.status == fresh.status
        and expected.current_provider_daily_budget == fresh.current_provider_daily_budget
        and expected.currency == fresh.currency
        and expected.strategy_subtype == fresh.strategy_subtype)


def _kill_switch_applies(switch: KillSwitch, target: ProviderTarget,
                         proposal: ActionProposal, method: str) -> bool:
    refs = {
        "global": {"*", "profit-engine"},
        "site": {target.site_id},
        "provider": {target.provider},
        "advertiser": {target.advertiser_ref},
        "target": {target.target_ref, target.provider_entity_id},
        "experiment": {proposal.proposal_id, method},
        "action": {proposal.proposal_id, method},
    }
    return switch.active and switch.scope_ref in refs.get(switch.scope, set())


@dataclass(frozen=True)
class ControllerPlan:
    plan_version: str
    state: ControllerState
    reasons: tuple[str, ...]
    proposal_digest: str
    proposal_id: str
    governor_evidence_digest: str
    target: ProviderTarget
    method: str
    request_objects: tuple[Mapping[str, Any], ...]
    preflight_digest: str
    budget_plan_digest: str | None
    rollback_plan: RollbackPlan
    provider_requests: int
    advertising_spend: int
    production_writer_enabled: bool
    plan_digest: str

    @property
    def integrity_valid(self) -> bool:
        value=asdict(self); recorded=value.pop("plan_digest")
        return recorded == digest(value)


def _proposal_valid(proposal: ActionProposal) -> bool:
    value=asdict(proposal); recorded=value.pop("proposal_digest")
    return recorded == digest(value)


def _blocked(state: ControllerState, reason: str) -> tuple[ControllerState, tuple[str, ...]]:
    return state, (reason,)


def _cadence_valid(cadence: MutationCadenceEvidence | None,
                   target_ref: str, now: datetime) -> bool:
    if cadence is None or not cadence.integrity_valid or cadence.evidence_version != "1.0":
        return False
    if cadence.campaign_ref != target_ref or cadence.prior_autonomous_mutations != 0:
        return False
    if not cadence.day_basis_ref or not cadence.audit_ref or not cadence.source_refs:
        return False
    if not -840 <= cadence.timezone_offset_minutes <= 840:
        return False
    basis = timezone(timedelta(minutes=cadence.timezone_offset_minutes))
    return cadence.day == now.astimezone(basis).date().isoformat()


def _request_matches(method: str, request: Mapping[str, Any], target: ProviderTarget,
                     budget_plan: ProviderBudgetPlan | None) -> bool:
    if method == "campaign.update_budget":
        if budget_plan is None or set(request) != {
            "provider_entity_id", "daily_budget", "provider_integer_micros"
        }:
            return False
        return (request["provider_entity_id"] == target.provider_entity_id
            and isinstance(request["daily_budget"], Decimal)
            and request["daily_budget"] == budget_plan.proposed_provider_daily_budget
            and type(request["provider_integer_micros"]) is int
            and request["provider_integer_micros"] == budget_plan.provider_integer_micros)
    desired = "SUSPENDED" if method.endswith(".suspend") else "ACTIVE"
    return (set(request) == {"provider_entity_id", "desired_state"}
        and request["provider_entity_id"] == target.provider_entity_id
        and request["desired_state"] == desired)


def derive_expected_readback(plan: ControllerPlan) -> Mapping[str, Any]:
    request = plan.request_objects[0]
    if plan.method == "campaign.update_budget":
        return {"provider_entity_id":request["provider_entity_id"],
                "daily_budget":request["daily_budget"],
                "provider_integer_micros":request["provider_integer_micros"]}
    return {"provider_entity_id":request["provider_entity_id"],
            "normalized_state":request["desired_state"]}


def _owner_approval_valid(approval: OwnerApprovalEvidence | None,
                          authorities: TrustedOwnerAuthorityRegistry | None,
                          proposal: ActionProposal, target_ref: str, method: str,
                          budget_plan: ProviderBudgetPlan, now: datetime) -> bool:
    try:
        return (approval is not None and approval.integrity_valid
            and approval.evidence_version == "1.0" and bool(approval.approval_id)
            and not approval.superseded and authorities is not None
            and authorities.contains(approval.authority_ref)
            and approval.proposal_digest == proposal.proposal_digest
            and approval.site_id == proposal.site_id and approval.target_ref == target_ref
            and approval.action_kind == method
            and approval.approved_weekly_budget == budget_plan.proposed_weekly_budget
            and approval.currency == budget_plan.currency
            and datetime.fromisoformat(approval.approved_at) <= now < datetime.fromisoformat(approval.expires_at)
            and budget_plan.owner_approval_digest == approval.evidence_digest)
    except (TypeError, ValueError):
        return False


def build_controller_plan(*, proposal: ActionProposal, governor: GovernorEvidence,
                          registry: ProviderIdentityRegistry, target_ref: str,
                          preflight: ProviderPreflightSnapshot, method: str,
                          request_objects: Sequence[Mapping[str, Any]], now: datetime,
                          budget_plan: ProviderBudgetPlan | None = None,
                          owner_approval: OwnerApprovalEvidence | None = None,
                          cadence: MutationCadenceEvidence | None = None,
                          kill_switches: Sequence[KillSwitch] = (),
                          locks: ExecutionLockRegistry | None = None,
                          trusted_owner_authorities: TrustedOwnerAuthorityRegistry | None = None,
                          ) -> tuple[ControllerPlan, AuditChain]:
    state=ControllerState.READY_FOR_DAY12_EXECUTION; reasons: tuple[str,...]=()
    safe_request_objects = tuple(redact(dict(item)) for item in request_objects)
    target=registry.resolve_exact(target_ref)
    if target is None:
        # Safe placeholder contains no inferred provider identity.
        target=ProviderTarget(target_ref, proposal.site_id, "unknown", "unknown", "unknown", "unknown")
        state,reasons=_blocked(ControllerState.CONTROLLER_PLAN_INVALID,"unregistered_exact_target")
    elif not _proposal_valid(proposal) or not governor.integrity_valid or governor.proposal_digest != proposal.proposal_digest or not proposal.requires_budget_governor or proposal.provider_write_allowed or governor.decision.state != GovernorState.GOVERNOR_READY_FOR_DAY11_CONTROLLER:
        state,reasons=_blocked(ControllerState.BLOCKED_GOVERNOR_NOT_READY,"proposal_governor_binding_invalid")
    elif target.site_id != proposal.site_id or proposal.target_refs.get("provider_target") != target_ref:
        state,reasons=_blocked(ControllerState.CONTROLLER_PLAN_INVALID,"proposal_target_binding_invalid")
    elif method not in SAFE_METHODS or (method.startswith("campaign.") and target.entity_type != "campaign") or (method.startswith("ad.") and target.entity_type != "ad"):
        state,reasons=_blocked(ControllerState.BLOCKED_PROVIDER_CAPABILITY,"method_not_allowlisted_for_target")
    elif len(request_objects) != MAX_MUTATION_OBJECTS_PER_PROVIDER_REQUEST:
        state,reasons=_blocked(ControllerState.BLOCKED_PROVIDER_CAPABILITY,"exactly_one_request_object_required")
    elif safe_request_objects != tuple(dict(item) for item in request_objects):
        state,reasons=_blocked(ControllerState.CONTROLLER_PLAN_INVALID,"sensitive_request_payload_rejected")
    elif not preflight.integrity_valid or preflight.target_ref != target_ref or preflight.provider_entity_id != target.provider_entity_id or preflight.dq_holds or now >= datetime.fromisoformat(preflight.expires_at):
        state,reasons=_blocked(ControllerState.BLOCKED_STALE_PROVIDER_STATE,"preflight_stale_mismatched_or_held")
    elif any(_kill_switch_applies(s, target, proposal, method) for s in kill_switches):
        state,reasons=_blocked(ControllerState.BLOCKED_KILL_SWITCH,"applicable_kill_switch_active")
    elif locks is None or locks.is_locked(target.lock_key, now):
        state,reasons=_blocked(ControllerState.BLOCKED_EXECUTION_LOCK,"target_lock_held")
    elif method == "campaign.update_budget":
        if budget_plan is None or not budget_plan.integrity_valid or budget_plan.preflight_digest != preflight.snapshot_digest or budget_plan.proposal_digest != proposal.proposal_digest or budget_plan.governor_evidence_digest != governor.evidence_digest:
            state,reasons=_blocked(ControllerState.BLOCKED_BUDGET_MAPPING,"budget_mapping_missing_or_invalid")
        elif not _cadence_valid(cadence,target_ref,now):
            state,reasons=_blocked(ControllerState.BLOCKED_MUTATION_CADENCE,"cadence_not_proven_clean")
        else:
            try: increase=governor.decision.increase_percent or Decimal("0")
            except InvalidOperation: increase=Decimal("999")
            if increase > Decimal("20.00"):
                valid=_owner_approval_valid(owner_approval,trusted_owner_authorities,
                    proposal,target_ref,method,budget_plan,now)
                if not valid: state,reasons=_blocked(ControllerState.BLOCKED_OWNER_APPROVAL,"exact_owner_approval_required")
    if state == ControllerState.READY_FOR_DAY12_EXECUTION and not _request_matches(method,safe_request_objects[0],target,budget_plan):
        state,reasons=_blocked(ControllerState.CONTROLLER_PLAN_INVALID,"mutation_request_not_exactly_bound")
    rollback=derive_rollback(method,preflight)
    core={"plan_version":"1.0","state":state,"reasons":reasons,"proposal_digest":proposal.proposal_digest,
          "proposal_id":proposal.proposal_id,
          "governor_evidence_digest":governor.evidence_digest,"target":target,"method":method,
          "request_objects":safe_request_objects,"preflight_digest":preflight.snapshot_digest,
          "budget_plan_digest":budget_plan.plan_digest if budget_plan else None,"rollback_plan":rollback,
          "provider_requests":0,"advertising_spend":0,"production_writer_enabled":False}
    plan=ControllerPlan(**core,plan_digest="")
    canonical=asdict(plan); canonical.pop("plan_digest")
    plan=replace(plan,plan_digest=digest(canonical))
    audit=AuditChain(); audit.append("PLAN_CREATED",now,{"plan_digest":plan.plan_digest,"state":state})
    audit.append("PREFLIGHT_CAPTURED",now,{"snapshot_digest":preflight.snapshot_digest,"RequestId":preflight.request_id,"Units":preflight.units})
    audit.append("AUTHORIZATION_READY" if state == ControllerState.READY_FOR_DAY12_EXECUTION else "BLOCKED",now,{"state":state,"reasons":reasons})
    return plan,audit


@dataclass(frozen=True)
class FakeResponse:
    transport_state: str
    http_status: int | None
    top_level_error: str | None = None
    object_state: str | None = None
    warnings: tuple[str, ...] = ()
    request_id: str | None = None
    units: int | None = None


@dataclass
class InMemoryDirectTransport:
    response: FakeResponse
    readback: Mapping[str, Any]
    fresh_preflight: ProviderPreflightSnapshot
    dispatch_count: int = 0
    read_count: int = 0
    preflight_read_count: int = 0

    def dispatch_once(self, _plan: ControllerPlan) -> FakeResponse:
        self.dispatch_count += 1
        return self.response

    def read_back(self, _target: ProviderTarget) -> Mapping[str, Any]:
        self.read_count += 1
        return self.readback

    def read_fresh_preflight(self, _target: ProviderTarget) -> ProviderPreflightSnapshot:
        self.preflight_read_count += 1
        return self.fresh_preflight


@dataclass(frozen=True)
class SyntheticOutcome:
    state: str
    dispatch_attempts: int
    readback_attempts: int
    request_id: str | None
    units: int | None


def simulate_with_fake(plan: ControllerPlan, transport: InMemoryDirectTransport,
                       expected_preflight: ProviderPreflightSnapshot,
                       preflight_state: Mapping[str, Any], audit: AuditChain,
                       now: datetime, locks: ExecutionLockRegistry | None,
                       runtime_kill_switches: Sequence[KillSwitch] = (),
                       caller_expected_state: Mapping[str, Any] | None = None,
                       lock_ttl: timedelta = timedelta(minutes=2)) -> SyntheticOutcome:
    if plan.state != ControllerState.READY_FOR_DAY12_EXECUTION or not plan.integrity_valid:
        return SyntheticOutcome("NOT_DISPATCHED",0,0,None,None)
    derived_expected=derive_expected_readback(plan)
    if caller_expected_state is not None and caller_expected_state != derived_expected:
        audit.append("BLOCKED",now,{"state":"BLOCKED_READBACK_EXPECTATION"})
        return SyntheticOutcome("BLOCKED_READBACK_EXPECTATION",0,0,None,None)
    if locks is None or not locks.acquire(plan.target.lock_key,now,lock_ttl):
        audit.append("BLOCKED",now,{"state":"BLOCKED_EXECUTION_LOCK"})
        return SyntheticOutcome("BLOCKED_EXECUTION_LOCK",0,0,None,None)
    audit.append("EXECUTION_LOCK_ACQUIRED",now,{"lock_key":plan.target.lock_key})
    response: FakeResponse | None = None
    try:
        if expected_preflight.snapshot_digest != plan.preflight_digest:
            audit.append("BLOCKED",now,{"state":"BLOCKED_STALE_PROVIDER_STATE"})
            return SyntheticOutcome("BLOCKED_STALE_PROVIDER_STATE",0,0,None,None)
        fresh=transport.read_fresh_preflight(plan.target)
        audit.append("PREFLIGHT_RECHECKED",now,{"snapshot_digest":fresh.snapshot_digest})
        if not pre_dispatch_snapshot_matches(expected_preflight,fresh,now):
            audit.append("BLOCKED",now,{"state":"BLOCKED_STALE_PROVIDER_STATE"})
            return SyntheticOutcome("BLOCKED_STALE_PROVIDER_STATE",0,0,None,None)
        runtime_refs={
            "global":{"*","profit-engine"},"site":{plan.target.site_id},
            "provider":{plan.target.provider},"advertiser":{plan.target.advertiser_ref},
            "target":{plan.target.target_ref,plan.target.provider_entity_id},
            "experiment":{plan.proposal_id,plan.method},"action":{plan.proposal_id,plan.method},
        }
        if any(s.active and s.scope_ref in runtime_refs.get(s.scope,set()) for s in runtime_kill_switches):
            audit.append("BLOCKED",now,{"state":"BLOCKED_KILL_SWITCH"})
            return SyntheticOutcome("BLOCKED_KILL_SWITCH",0,0,None,None)
        audit.append("DISPATCH_STARTED",now,{"method":plan.method,"object_count":1})
        response=transport.dispatch_once(plan)
        audit.append("PROVIDER_RESPONSE_RECEIVED",now,{"transport_state":response.transport_state,
            "http_status":response.http_status,"top_level_error":response.top_level_error,
            "object_state":response.object_state,"warnings":response.warnings,
            "RequestId":response.request_id,"Units":response.units})
        readback=transport.read_back(plan.target)
        if readback == derived_expected and (response.transport_state == "TIMEOUT" or
            (response.http_status == 200 and not response.top_level_error and response.object_state == "SUCCESS")):
            state="RECOVERED_APPLIED" if response.transport_state == "TIMEOUT" else "SYNTHETIC_COMPLETED"
            audit.append("READBACK_VERIFIED",now,{"state":state}); audit.append("COMPLETED",now,{"synthetic":True})
        elif response.transport_state == "TIMEOUT" and readback == preflight_state:
            state="EXPLICIT_RETRY_PLAN_REQUIRED"; audit.append("EXECUTION_UNCERTAIN",now,{"state":state})
        else:
            state="EXECUTION_UNCERTAIN_REVIEW"; audit.append("EXECUTION_UNCERTAIN",now,{"state":state})
        return SyntheticOutcome(state,transport.dispatch_count,transport.read_count,response.request_id,response.units)
    finally:
        locks.release(plan.target.lock_key)
        audit.append("EXECUTION_LOCK_RELEASED",now,{"lock_key":plan.target.lock_key})


def assert_no_real_writer_reachable() -> bool:
    return not PRODUCTION_WRITER_ENABLED and REAL_PROVIDER_REQUESTS == 0
