"""Public-safe Acquisition Strategy Lab contracts.

The lab validates evidence and builds inert experiment previews. It deliberately
does not compare cells or make commercial decisions.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import StrEnum
from typing import Any, Mapping, Sequence

from .campaign_factory import YANDEX_DIRECT_DRY_RUN, canonical_json, digest
from .money_ledger import AttributionGrade, Measurement, MoneyState, ReconciliationState


class ProxyState(StrEnum):
    PROXY_UNPROVEN = "PROXY_UNPROVEN"
    PROXY_EVIDENCE_PENDING = "PROXY_EVIDENCE_PENDING"
    PROXY_MONEY_ASSOCIATION_SUPPORTED = "PROXY_MONEY_ASSOCIATION_SUPPORTED"
    PROXY_REJECTED = "PROXY_REJECTED"


class MaturityState(StrEnum):
    MATURE = "MATURE"
    IMMATURE = "IMMATURE"
    LATE_ARRIVAL_OPEN = "LATE_ARRIVAL_OPEN"


class LabState(StrEnum):
    CELL_ELIGIBLE_FOR_EXPERIMENT_PREVIEW = "CELL_ELIGIBLE_FOR_EXPERIMENT_PREVIEW"
    CELL_HELD_DATA_QUALITY = "CELL_HELD_DATA_QUALITY"
    CELL_HELD_ATTRIBUTION = "CELL_HELD_ATTRIBUTION"
    CELL_HELD_MATURITY = "CELL_HELD_MATURITY"
    CELL_BLOCKED_MONEY_EVIDENCE = "CELL_BLOCKED_MONEY_EVIDENCE"
    CELL_BLOCKED_PROVIDER_CAPABILITY = "CELL_BLOCKED_PROVIDER_CAPABILITY"
    EXPERIMENT_PREVIEW_VALID = "EXPERIMENT_PREVIEW_VALID"
    EXPERIMENT_PREVIEW_INVALID = "EXPERIMENT_PREVIEW_INVALID"
    BLOCKED_PRIVATE_CORE_REQUIRED = "BLOCKED_PRIVATE_CORE_REQUIRED"


ALLOWED_LAB_STATES = frozenset(LabState)
COHORT_MEASUREMENTS = frozenset({"K5_1D", "K5_7D", "K5_30D"})
APPROVED_MEASUREMENTS = COHORT_MEASUREMENTS | {"period_K5"}
AUTONOMOUS_GRADES = frozenset({AttributionGrade.A, AttributionGrade.B, AttributionGrade.D})
SENSITIVE_DECISION_REQUESTS = frozenset({"rank", "select", "winner", "allocate", "learned-score", "scale-candidate"})


@dataclass(frozen=True)
class StrategyCellRequest:
    cell_version: str
    site_id: str
    cell_key: str
    campaign_preview_ref: str
    campaign_spec_digest: str
    campaign_type: str
    strategy_kind: str
    landing_content_id: str
    dimensions: Mapping[str, str]
    measurement_ref: str
    evidence_refs: tuple[str, ...]
    cohort_link_proven: bool
    maturity_state: MaturityState
    proxy_goal_ref: str | None = None
    proxy_state: ProxyState | None = None
    source_state: str = "FINAL"


@dataclass(frozen=True)
class StrategyCell:
    cell_version: str
    site_id: str
    cell_key: str
    campaign_preview_ref: str
    campaign_spec_digest: str
    campaign_type: str
    strategy_kind: str
    landing_content_id: str
    dimensions: Mapping[str, str]
    measurement_kind: str
    measurement_ref: str
    evidence_refs: tuple[str, ...]
    attribution_grade: AttributionGrade
    reconciliation_state: ReconciliationState
    money_state: MoneyState
    source_state: str
    cohort_link_proven: bool
    maturity_state: MaturityState
    proxy_goal_ref: str | None
    proxy_state: ProxyState | None
    eligibility_state: LabState
    hold_reasons: tuple[str, ...]
    cell_digest: str

    @property
    def eligible(self) -> bool:
        return self.eligibility_state == LabState.CELL_ELIGIBLE_FOR_EXPERIMENT_PREVIEW


def _cell_state(holds: Sequence[str]) -> LabState:
    if any(item.startswith("provider_") or item.startswith("strategy_") for item in holds):
        return LabState.CELL_BLOCKED_PROVIDER_CAPABILITY
    if any(item in {"immature_cohort", "late_arrival_window_open"} for item in holds):
        return LabState.CELL_HELD_MATURITY
    if any(item in {"attribution_grade_not_autonomous", "cohort_link_not_proven", "metrica_only_cohort_forbidden"} for item in holds):
        return LabState.CELL_HELD_ATTRIBUTION
    if any(item in {"measurement_not_computable", "measurement_kind_incompatible", "measurement_not_optimizer_consumable"} for item in holds):
        return LabState.CELL_BLOCKED_MONEY_EVIDENCE
    return LabState.CELL_HELD_DATA_QUALITY if holds else LabState.CELL_ELIGIBLE_FOR_EXPERIMENT_PREVIEW


def evaluate_cell(request: StrategyCellRequest, measurement: Measurement) -> StrategyCell:
    holds: list[str] = []
    if request.cell_version != "1.0" or not request.cell_key or request.site_id != measurement.site_id:
        holds.append("cell_contract_invalid")
    supported = YANDEX_DIRECT_DRY_RUN.strategies.get(request.campaign_type)
    if not supported:
        holds.append("provider_campaign_type_unsupported")
    elif request.strategy_kind not in supported:
        holds.append("strategy_kind_unsupported")
    if measurement.kind not in APPROVED_MEASUREMENTS:
        holds.append("measurement_kind_incompatible")
    if not measurement.optimizer_consumable:
        holds.append("measurement_not_optimizer_consumable")
    if measurement.reconciliation != ReconciliationState.MATCHED:
        holds.append("reconciliation_not_matched")
    if measurement.state == MoneyState.NOT_COMPUTABLE:
        holds.append("measurement_not_computable")
    if request.maturity_state == MaturityState.IMMATURE:
        holds.append("immature_cohort")
    elif request.maturity_state == MaturityState.LATE_ARRIVAL_OPEN:
        holds.append("late_arrival_window_open")
    if not request.evidence_refs or not measurement.numerator_source or not measurement.denominator_source:
        holds.append("missing_provenance")
    if request.source_state not in {"FINAL", "RECONCILED"}:
        holds.append("source_state_not_accepted")
    if measurement.grade not in AUTONOMOUS_GRADES:
        holds.append("attribution_grade_not_autonomous")
    if measurement.kind in COHORT_MEASUREMENTS:
        if measurement.grade == AttributionGrade.C:
            holds.append("metrica_only_cohort_forbidden")
        if not request.cohort_link_proven:
            holds.append("cohort_link_not_proven")
    if measurement.grade == AttributionGrade.D and "private-map-evidence" not in request.evidence_refs:
        holds.append("private_map_evidence_missing")
    needs_proxy = request.strategy_kind in {"conversion_click", "pay_for_conversion", "value_crr", "maximum_profit"}
    if needs_proxy and (not request.proxy_goal_ref or request.proxy_state != ProxyState.PROXY_MONEY_ASSOCIATION_SUPPORTED):
        holds.append("proxy_money_association_not_supported")
    if request.proxy_state == ProxyState.PROXY_REJECTED:
        holds.append("proxy_rejected")
    holds = sorted(set(holds))
    state = _cell_state(holds)
    core = {
        **asdict(request),
        "measurement_kind": measurement.kind,
        "attribution_grade": measurement.grade,
        "reconciliation_state": measurement.reconciliation,
        "money_state": measurement.state,
        "eligibility_state": state,
        "hold_reasons": tuple(holds),
    }
    return StrategyCell(**core, cell_digest=digest(core))


@dataclass(frozen=True)
class ObservationContract:
    window_days: int
    maturity_required: bool
    late_arrival_grace_days: int
    evidence_prerequisites: tuple[str, ...]


@dataclass(frozen=True)
class ExperimentPreview:
    experiment_version: str
    experiment_key: str
    control_cell_ref: str
    treatment_cell_refs: tuple[str, ...]
    holdout_declared: bool
    hypothesis_label: str
    primary_measurement_kind: str
    observation_contract: ObservationContract
    campaign_preview_refs: tuple[str, ...]
    budget_proposal_refs: tuple[str, ...]
    guardrail_refs: tuple[str, ...]
    prerequisite_errors: tuple[str, ...]
    state: LabState
    preview_digest: str
    provider_write_allowed: bool = False
    provider_requests: int = 0
    advertising_spend: int = 0


def build_experiment_preview(
    *, experiment_key: str, control: StrategyCell, treatments: Sequence[StrategyCell],
    hypothesis_label: str, primary_measurement_kind: str,
    observation_contract: ObservationContract, campaign_preview_refs: Sequence[str],
    budget_proposal_refs: Sequence[str], guardrail_refs: Sequence[str], holdout_declared: bool,
) -> ExperimentPreview:
    errors: list[str] = []
    if not experiment_key or not hypothesis_label or not treatments:
        errors.append("experiment_contract_incomplete")
    all_cells = (control, *treatments)
    refs = [cell.cell_digest for cell in all_cells]
    if len(refs) != len(set(refs)):
        errors.append("control_treatment_not_distinct")
    if not control.eligible:
        errors.append("control_cell_not_eligible")
    if any(not cell.eligible for cell in treatments):
        errors.append("treatment_cell_not_eligible")
    if any(cell.measurement_kind != primary_measurement_kind for cell in all_cells):
        errors.append("primary_measurement_mismatch")
    if not holdout_declared:
        errors.append("holdout_control_required")
    if observation_contract.window_days <= 0 or observation_contract.late_arrival_grace_days < 0 or not observation_contract.maturity_required:
        errors.append("observation_maturity_contract_invalid")
    if not observation_contract.evidence_prerequisites:
        errors.append("evidence_prerequisites_missing")
    expected_campaign_refs = {cell.campaign_preview_ref for cell in all_cells}
    if not expected_campaign_refs.issubset(set(campaign_preview_refs)):
        errors.append("campaign_preview_reference_missing")
    if not budget_proposal_refs:
        errors.append("inert_budget_proposal_reference_missing")
    if not guardrail_refs:
        errors.append("guardrail_reference_missing")
    errors = sorted(set(errors))
    state = LabState.EXPERIMENT_PREVIEW_INVALID if errors else LabState.EXPERIMENT_PREVIEW_VALID
    core = {
        "experiment_version": "1.0", "experiment_key": experiment_key,
        "control_cell_ref": control.cell_digest,
        "treatment_cell_refs": tuple(cell.cell_digest for cell in treatments),
        "holdout_declared": holdout_declared, "hypothesis_label": hypothesis_label,
        "primary_measurement_kind": primary_measurement_kind,
        "observation_contract": asdict(observation_contract),
        "campaign_preview_refs": tuple(campaign_preview_refs),
        "budget_proposal_refs": tuple(budget_proposal_refs), "guardrail_refs": tuple(guardrail_refs),
        "prerequisite_errors": tuple(errors), "state": state,
        "provider_write_allowed": False, "provider_requests": 0, "advertising_spend": 0,
    }
    return ExperimentPreview(**core, preview_digest=digest(core))


@dataclass(frozen=True)
class PublicStrategyEvidencePackage:
    package_version: str
    site_id: str
    cell_refs: tuple[str, ...]
    measurement_refs: tuple[str, ...]
    accepted_evidence_states: tuple[Mapping[str, str], ...]
    experiment_preview_ref: str
    capability_version: str
    safety_state: Mapping[str, Any]
    package_digest: str


def build_evidence_package(cells: Sequence[StrategyCell], preview: ExperimentPreview) -> PublicStrategyEvidencePackage:
    core = {
        "package_version": "1.0", "site_id": cells[0].site_id if cells else "",
        "cell_refs": tuple(cell.cell_digest for cell in cells),
        "measurement_refs": tuple(cell.measurement_ref for cell in cells),
        "accepted_evidence_states": tuple({
            "cell_ref": cell.cell_digest,
            "eligibility_state": cell.eligibility_state,
            "measurement_ref": cell.measurement_ref,
            "money_state": cell.money_state,
            "reconciliation_state": cell.reconciliation_state,
            "attribution_grade": cell.attribution_grade,
            "source_state": cell.source_state,
        } for cell in cells),
        "experiment_preview_ref": preview.preview_digest,
        "capability_version": YANDEX_DIRECT_DRY_RUN.metadata_version,
        "safety_state": {"provider_write_allowed": False, "provider_requests": 0, "advertising_spend": 0},
    }
    return PublicStrategyEvidencePackage(**core, package_digest=digest(core))


def private_decision_boundary(request_kind: str) -> LabState:
    """Fail closed for every commercially sensitive decision request."""
    if request_kind in SENSITIVE_DECISION_REQUESTS:
        return LabState.BLOCKED_PRIVATE_CORE_REQUIRED
    return LabState.BLOCKED_PRIVATE_CORE_REQUIRED
