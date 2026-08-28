from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from hashlib import sha256
import json
from typing import Sequence

from .day12_readiness import Day12LaunchReadiness, Day12ReadinessState
from .direct_controller import (
    ADVERTISING_SPEND,
    PRODUCTION_WRITER_ENABLED,
    REAL_PROVIDER_REQUESTS,
    ControllerPlan,
    ControllerState,
)


def _digest(value: object) -> str:
    return sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    ).hexdigest()


@dataclass(frozen=True)
class LiveCandidateSelection:
    selection_version: str
    site_id: str
    provider: str
    target_ref: str
    provider_entity_id: str
    method: str
    proposal_digest: str
    governor_evidence_digest: str
    controller_plan_digest: str
    private_decision_ref: str
    private_decision_digest: str
    measurement_refs: tuple[str, ...]
    provenance_refs: tuple[str, ...]
    selected_by: str
    selection_digest: str

    @property
    def integrity_valid(self) -> bool:
        value = asdict(self)
        recorded = value.pop("selection_digest")
        return recorded == _digest(value)


def build_live_candidate_selection(
    *,
    readiness: Day12LaunchReadiness,
    plan: ControllerPlan,
    private_decision_ref: str,
    private_decision_digest: str,
    measurement_refs: Sequence[str],
    provenance_refs: Sequence[str],
    selected_by: str = "CENTRAL_BRAIN",
) -> LiveCandidateSelection:
    if not readiness.integrity_valid:
        raise ValueError("day12 readiness integrity invalid")
    if readiness.state != Day12ReadinessState.READY_FOR_LIVE_CANDIDATE_SELECTION:
        raise ValueError("day12 readiness is not candidate-selection ready")
    if readiness.provider_write_allowed:
        raise ValueError("readiness must not itself authorize provider write")
    if not plan.integrity_valid or plan.state != ControllerState.READY_FOR_DAY12_EXECUTION:
        raise ValueError("controller plan is not Day12-ready")
    if not private_decision_ref or len(private_decision_digest) != 64:
        raise ValueError("exact private decision reference/digest required")
    measurements = tuple(measurement_refs)
    provenance = tuple(provenance_refs)
    if not measurements or not provenance:
        raise ValueError("accepted measurement and provenance references required")
    if selected_by != "CENTRAL_BRAIN":
        raise ValueError("public runtime cannot self-select a commercial candidate")

    core = {
        "selection_version": "1.0",
        "site_id": plan.target.site_id,
        "provider": plan.target.provider,
        "target_ref": plan.target.target_ref,
        "provider_entity_id": plan.target.provider_entity_id,
        "method": plan.method,
        "proposal_digest": plan.proposal_digest,
        "governor_evidence_digest": plan.governor_evidence_digest,
        "controller_plan_digest": plan.plan_digest,
        "private_decision_ref": private_decision_ref,
        "private_decision_digest": private_decision_digest,
        "measurement_refs": measurements,
        "provenance_refs": provenance,
        "selected_by": selected_by,
    }
    return LiveCandidateSelection(**core, selection_digest=_digest(core))


@dataclass(frozen=True)
class WriterArmIntent:
    arm_version: str
    selection_digest: str
    controller_plan_digest: str
    site_id: str
    provider: str
    target_ref: str
    provider_entity_id: str
    method: str
    max_dispatch_attempts: int
    prepared_at: str
    expires_at: str
    executable: bool
    armed: bool
    provider_write_allowed: bool
    real_provider_requests: int
    advertising_spend: int
    production_writer_enabled: bool
    arm_digest: str

    @property
    def integrity_valid(self) -> bool:
        value = asdict(self)
        recorded = value.pop("arm_digest")
        return recorded == _digest(value)


def build_inert_writer_arm_intent(
    *,
    selection: LiveCandidateSelection,
    plan: ControllerPlan,
    prepared_at: datetime,
    expires_at: datetime,
) -> WriterArmIntent:
    if not selection.integrity_valid:
        raise ValueError("candidate selection integrity invalid")
    if not plan.integrity_valid or plan.state != ControllerState.READY_FOR_DAY12_EXECUTION:
        raise ValueError("controller plan is not Day12-ready")
    if selection.controller_plan_digest != plan.plan_digest:
        raise ValueError("candidate/plan digest mismatch")
    if (
        selection.site_id != plan.target.site_id
        or selection.provider != plan.target.provider
        or selection.target_ref != plan.target.target_ref
        or selection.provider_entity_id != plan.target.provider_entity_id
        or selection.method != plan.method
        or selection.proposal_digest != plan.proposal_digest
        or selection.governor_evidence_digest != plan.governor_evidence_digest
    ):
        raise ValueError("candidate is not exactly bound to controller plan")
    if expires_at <= prepared_at:
        raise ValueError("writer arm intent expiry must be after preparation time")

    core = {
        "arm_version": "1.0",
        "selection_digest": selection.selection_digest,
        "controller_plan_digest": plan.plan_digest,
        "site_id": selection.site_id,
        "provider": selection.provider,
        "target_ref": selection.target_ref,
        "provider_entity_id": selection.provider_entity_id,
        "method": selection.method,
        "max_dispatch_attempts": 1,
        "prepared_at": prepared_at.isoformat(),
        "expires_at": expires_at.isoformat(),
        "executable": False,
        "armed": False,
        "provider_write_allowed": False,
        "real_provider_requests": REAL_PROVIDER_REQUESTS,
        "advertising_spend": ADVERTISING_SPEND,
        "production_writer_enabled": PRODUCTION_WRITER_ENABLED,
    }
    return WriterArmIntent(**core, arm_digest=_digest(core))
