"""Day-10 public materialization, proposal, and safety contracts.

No object in this module can call a provider or mutate a site/budget.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field, replace
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation
from enum import StrEnum
from typing import Any, Mapping, Sequence

from .campaign_factory import digest
from .money_ledger import (
    AcquisitionRegistry, AttributionResult, DerivedVersions, DirectSpendInput,
    Measurement, MoneyState, Reconciliation, ReconciliationState,
    classify_attribution, cohort_k5, period_k5, reconcile,
)


ATTRIBUTION_MODEL = "last_yandex_direct_click"
ATTRIBUTION_DIMENSIONS = (
    "ym:s:date",
    "ym:s:last_yandex_direct_clickDirectClickOrder",
    "ym:s:last_yandex_direct_clickDirectBannerGroup",
    "ym:s:last_yandex_direct_clickUTMSource",
    "ym:s:last_yandex_direct_clickUTMMedium",
    "ym:s:last_yandex_direct_clickUTMCampaign",
    "ym:s:last_yandex_direct_clickUTMContent",
    "ym:s:last_yandex_direct_clickUTMTerm",
)
ATTRIBUTION_METRICS = (
    "ym:s:yanPartnerPrice", "ym:s:yanRequests", "ym:s:yanRenders", "ym:s:yanShows",
)


def _names(value: Any) -> tuple[str, ...]:
    if isinstance(value, str):
        return tuple(item for item in value.split(",") if item)
    if isinstance(value, Sequence):
        return tuple(str(item) for item in value)
    return ()


def _dimension_value(item: Any) -> str | None:
    if not isinstance(item, Mapping):
        return None
    value = item.get("id", item.get("name"))
    return str(value) if value not in (None, "") else None


@dataclass(frozen=True)
class MetricaAttributionFact:
    fact_version: str
    site_id: str
    window_date: str
    attribution_model: str
    direct_campaign_ref: str | None
    direct_group_ref: str | None
    utm_dimensions: Mapping[str, str | None]
    attributed_yan_revenue: Decimal | None
    delivery: Mapping[str, int | None]
    currency: str | None
    money_basis: str | None
    timezone: str | None
    sampled: bool | None
    sample_size: int | None
    sample_space: int | None
    accuracy: str | None
    data_lag: int | None
    disclosure: Any
    raw_source_ref: str
    source_state: str
    hold_reasons: tuple[str, ...]
    fact_digest: str

    @property
    def optimizer_consumable(self) -> bool:
        return not self.hold_reasons and self.attributed_yan_revenue is not None


def normalize_metrica_attribution(
    *, site_id: str, payload: Mapping[str, Any], raw_source_ref: str,
    source_state: str, expected_model: str = ATTRIBUTION_MODEL,
) -> tuple[MetricaAttributionFact, ...]:
    query = payload.get("query", {}) if isinstance(payload, Mapping) else {}
    returned_dimensions = _names(query.get("dimensions")) if isinstance(query, Mapping) else ()
    returned_metrics = _names(query.get("metrics")) if isinstance(query, Mapping) else ()
    base_holds: list[str] = []
    if expected_model != ATTRIBUTION_MODEL:
        base_holds.append("incompatible_attribution_model")
    if returned_dimensions != ATTRIBUTION_DIMENSIONS:
        base_holds.append("metrica_named_attribution_dimensions_missing_or_incompatible")
    if not set(ATTRIBUTION_METRICS).issubset(returned_metrics):
        base_holds.append("metrica_attribution_metrics_missing")
    if payload.get("currency") != "RUB":
        base_holds.append("metrica_currency_missing_or_incompatible")
    if not payload.get("money_basis") or not payload.get("timezone"):
        base_holds.append("metrica_money_basis_or_timezone_missing")
    if not raw_source_ref:
        base_holds.append("missing_raw_source_ref")
    rows = payload.get("data")
    if not isinstance(rows, list):
        rows = []
        base_holds.append("malformed_metrica_attribution_response")
    facts: list[MetricaAttributionFact] = []
    for row_index, row in enumerate(rows):
        holds = list(base_holds)
        raw_dimensions = row.get("dimensions", []) if isinstance(row, Mapping) else []
        raw_metrics = row.get("metrics", []) if isinstance(row, Mapping) else []
        if len(raw_dimensions) != len(returned_dimensions):
            holds.append("metrica_dimension_cardinality_mismatch")
        if len(raw_metrics) != len(returned_metrics):
            holds.append("metrica_metric_cardinality_mismatch")
        dimension_map = {name: _dimension_value(value) for name, value in zip(returned_dimensions, raw_dimensions)}
        metric_map = dict(zip(returned_metrics, raw_metrics))
        campaign_ref = dimension_map.get(ATTRIBUTION_DIMENSIONS[1])
        group_ref = dimension_map.get(ATTRIBUTION_DIMENSIONS[2])
        if not campaign_ref:
            holds.append("metrica_direct_campaign_dimension_value_missing")
        try:
            revenue = Decimal(str(metric_map["ym:s:yanPartnerPrice"])) if "ym:s:yanPartnerPrice" in metric_map else None
        except (InvalidOperation, ValueError):
            revenue = None
            holds.append("metrica_attributed_revenue_malformed")
        occurred = dimension_map.get("ym:s:date")
        if not occurred:
            holds.append("metrica_named_date_dimension_missing")
            occurred = "UNKNOWN"
        delivery: dict[str, int | None] = {}
        for public_name, metric_name in (("requests", "ym:s:yanRequests"), ("renders", "ym:s:yanRenders"), ("shows", "ym:s:yanShows")):
            try:
                delivery[public_name] = int(metric_map[metric_name]) if metric_name in metric_map else None
            except (TypeError, ValueError):
                delivery[public_name] = None
                holds.append(f"metrica_delivery_{public_name}_malformed")
        core = {
            "fact_version": "1.0", "site_id": site_id, "window_date": occurred,
            "attribution_model": expected_model, "direct_campaign_ref": campaign_ref,
            "direct_group_ref": group_ref,
            "utm_dimensions": {
                "utm_source": dimension_map.get(ATTRIBUTION_DIMENSIONS[3]),
                "utm_medium": dimension_map.get(ATTRIBUTION_DIMENSIONS[4]),
                "utm_campaign": dimension_map.get(ATTRIBUTION_DIMENSIONS[5]),
                "utm_content": dimension_map.get(ATTRIBUTION_DIMENSIONS[6]),
                "utm_term": dimension_map.get(ATTRIBUTION_DIMENSIONS[7]),
            },
            "attributed_yan_revenue": revenue, "delivery": delivery,
            "currency": payload.get("currency"), "money_basis": payload.get("money_basis"),
            "timezone": payload.get("timezone"), "sampled": payload.get("sampled"),
            "sample_size": payload.get("sample_size"), "sample_space": payload.get("sample_space"),
            "accuracy": payload.get("accuracy"), "data_lag": payload.get("data_lag"),
            "disclosure": payload.get("contains_sensitive_data"), "raw_source_ref": raw_source_ref,
            "source_state": source_state, "hold_reasons": tuple(sorted(set(holds))),
        }
        facts.append(MetricaAttributionFact(**core, fact_digest=digest(core | {"row_index": row_index})))
    if not facts and base_holds:
        core = {
            "fact_version": "1.0", "site_id": site_id, "window_date": "UNKNOWN",
            "attribution_model": expected_model, "direct_campaign_ref": None, "direct_group_ref": None,
            "utm_dimensions": {}, "attributed_yan_revenue": None, "delivery": {},
            "currency": payload.get("currency"), "money_basis": payload.get("money_basis"),
            "timezone": payload.get("timezone"), "sampled": payload.get("sampled"),
            "sample_size": payload.get("sample_size"), "sample_space": payload.get("sample_space"),
            "accuracy": payload.get("accuracy"), "data_lag": payload.get("data_lag"),
            "disclosure": payload.get("contains_sensitive_data"), "raw_source_ref": raw_source_ref,
            "source_state": source_state, "hold_reasons": tuple(sorted(set(base_holds))),
        }
        facts.append(MetricaAttributionFact(**core, fact_digest=digest(core)))
    return tuple(facts)


@dataclass(frozen=True)
class YanControlInput:
    revenue: Decimal | None
    currency: str
    scope: str
    money_basis: str
    timezone: str
    raw_source_ref: str


@dataclass(frozen=True)
class CohortRevenueEvidence:
    evidence_version: str
    site_id: str
    cohort_ref: str
    window_days: int
    window_start: str
    window_end: str
    attributed_cohort_revenue: Decimal | None
    currency: str
    money_basis: str
    timezone: str
    source_state: str
    reconciliation_state: ReconciliationState
    source_refs: tuple[str, ...]
    linkage_evidence_refs: tuple[str, ...]
    linkage_basis: str
    mature: bool
    late_arrival_open: bool
    hold_reasons: tuple[str, ...]
    evidence_digest: str

    @property
    def optimizer_consumable(self) -> bool:
        return (self.attributed_cohort_revenue is not None and not self.hold_reasons
            and self.reconciliation_state == ReconciliationState.MATCHED
            and self.source_state in {"FINAL", "RECONCILED"} and self.mature
            and not self.late_arrival_open)

    @property
    def integrity_valid(self) -> bool:
        value = asdict(self)
        recorded = value.pop("evidence_digest")
        return recorded == digest(value)


def build_cohort_revenue_evidence(
    *, site_id: str, cohort_ref: str, window_days: int, window_start: str,
    window_end: str, attributed_cohort_revenue: Decimal | None, currency: str,
    money_basis: str, timezone: str, source_state: str,
    reconciliation_state: ReconciliationState, source_refs: Sequence[str],
    linkage_evidence_refs: Sequence[str], linkage_basis: str,
    mature: bool, late_arrival_open: bool = False,
) -> CohortRevenueEvidence:
    holds: list[str] = []
    if window_days not in {1, 7, 30}: holds.append("cohort_window_invalid")
    if attributed_cohort_revenue is None: holds.append("cohort_revenue_missing")
    elif not isinstance(attributed_cohort_revenue, Decimal): holds.append("cohort_revenue_not_decimal")
    if not source_refs: holds.append("cohort_source_provenance_missing")
    if not linkage_evidence_refs or not linkage_basis: holds.append("cohort_linkage_proof_missing")
    if source_state not in {"FINAL", "RECONCILED"}: holds.append("cohort_source_state_not_final")
    if reconciliation_state != ReconciliationState.MATCHED: holds.append("cohort_reconciliation_not_matched")
    if not mature: holds.append("cohort_window_immature")
    if late_arrival_open: holds.append("late_arrival_window_open")
    if not currency or not money_basis or not timezone: holds.append("cohort_money_basis_incomplete")
    core = {"evidence_version":"1.0","site_id":site_id,"cohort_ref":cohort_ref,
        "window_days":window_days,"window_start":window_start,"window_end":window_end,
        "attributed_cohort_revenue":attributed_cohort_revenue,"currency":currency,
        "money_basis":money_basis,"timezone":timezone,"source_state":source_state,
        "reconciliation_state":reconciliation_state,"source_refs":tuple(source_refs),
        "linkage_evidence_refs":tuple(linkage_evidence_refs),"linkage_basis":linkage_basis,
        "mature":mature,"late_arrival_open":late_arrival_open,
        "hold_reasons":tuple(sorted(set(holds)))}
    return CohortRevenueEvidence(**core,evidence_digest=digest(core))


@dataclass(frozen=True)
class MaterializedLedger:
    materializer_version: str
    source_digest: str
    derived_version: int
    acquisition_status: str
    attribution: AttributionResult
    reconciliation: Reconciliation
    period_measurement: Measurement
    cohort_measurements: tuple[Measurement, ...]
    raw_source_refs: tuple[str, ...]
    hold_reasons: tuple[str, ...]
    materialization_digest: str


@dataclass
class LedgerMaterializer:
    acquisitions: AcquisitionRegistry = field(default_factory=AcquisitionRegistry)
    versions: DerivedVersions = field(default_factory=DerivedVersions)
    outputs: dict[str, list[MaterializedLedger]] = field(default_factory=dict)

    def materialize(
        self, *, acquisition: Mapping[str, Any], direct: DirectSpendInput,
        metrica: MetricaAttributionFact, yan: YanControlInput,
        direct_campaigns: set[str], as_of: datetime, cohort_start: datetime,
        cohort_evidence: Sequence[CohortRevenueEvidence] = (),
        tolerance: Decimal = Decimal("0.01"),
    ) -> MaterializedLedger:
        source = {"acquisition": acquisition, "direct": asdict(direct), "metrica": asdict(metrica),
            "yan": asdict(yan), "cohort_evidence": tuple(asdict(item) for item in cohort_evidence)}
        source_digest = digest(source)
        existing = self.outputs.get(source_digest)
        if existing:
            return existing[-1]
        acquisition_status, acquisition_holds = self.acquisitions.register(acquisition)
        first_party = acquisition.get("attribution", {}).get("campaign_id")
        attribution = classify_attribution(
            first_party_campaign=first_party, metrica_campaign=metrica.direct_campaign_ref,
            direct_campaigns=direct_campaigns,
        )
        direct_holds = direct.validate()
        rec = reconcile(
            metrica.attributed_yan_revenue, yan.revenue,
            metrica_scope=f"site-day:{metrica.window_date}", yan_scope=yan.scope,
            currency_a=metrica.currency or "UNKNOWN", currency_b=yan.currency,
            basis_a=metrica.money_basis, basis_b=yan.money_basis,
            timezone_a=metrica.timezone or "UNKNOWN", timezone_b=yan.timezone, tolerance=tolerance,
        )
        upstream_holds = tuple(sorted(set((*acquisition_holds, *direct_holds, *metrica.hold_reasons, *attribution.hold_reasons))))
        period = period_k5(
            direct.spend, metrica.attributed_yan_revenue,
            currency_spend=direct.currency or "UNKNOWN", currency_revenue=metrica.currency or "UNKNOWN",
            grade=attribution.grade, reconciliation=rec.state, upstream_held=bool(upstream_holds),
        )
        evidence_by_window = {item.window_days: item for item in cohort_evidence}
        duplicate_windows = {days for days in evidence_by_window
            if sum(item.window_days == days for item in cohort_evidence) > 1}
        cohort_values = tuple(self._cohort_measurement(
            days=days, evidence=evidence_by_window.get(days), acquisition=acquisition,
            direct=direct, metrica=metrica, attribution=attribution,
            as_of=as_of, cohort_start=cohort_start, duplicate=days in duplicate_windows,
        ) for days in (1, 7, 30))
        key = f"{acquisition.get('acquisition_id')}:{metrica.window_date}"
        period = self.versions.recompute(f"{key}:period", period)
        cohort_values = tuple(self.versions.recompute(f"{key}:{item.kind}", item) for item in cohort_values)
        derived_version = period.version
        holds = tuple(sorted(set((*upstream_holds, *rec.hold_reasons, *period.hold_reasons, *(reason for item in cohort_values for reason in item.hold_reasons)))))
        refs = tuple(ref for ref in (direct.raw_source_ref, metrica.raw_source_ref, yan.raw_source_ref) if ref)
        core = {
            "materializer_version": "1.0", "source_digest": source_digest, "derived_version": derived_version,
            "acquisition_status": acquisition_status, "attribution": asdict(attribution),
            "reconciliation": asdict(rec), "period_measurement": asdict(period),
            "cohort_measurements": tuple(asdict(item) for item in cohort_values),
            "raw_source_refs": refs, "hold_reasons": holds,
        }
        output = MaterializedLedger(
            "1.0", source_digest, derived_version, acquisition_status, attribution, rec, period,
            cohort_values, refs, holds, digest(core),
        )
        self.outputs.setdefault(source_digest, []).append(output)
        return output

    @staticmethod
    def _cohort_measurement(*, days: int, evidence: CohortRevenueEvidence | None,
        acquisition: Mapping[str, Any], direct: DirectSpendInput,
        metrica: MetricaAttributionFact, attribution: AttributionResult,
        as_of: datetime, cohort_start: datetime, duplicate: bool) -> Measurement:
        expected_ref = str(acquisition.get("cohort_ref"))
        contextual_holds: list[str] = []
        if evidence is None:
            contextual_holds.append("explicit_cohort_revenue_evidence_missing")
        else:
            if not evidence.integrity_valid: contextual_holds.append("cohort_evidence_digest_mismatch")
            if duplicate: contextual_holds.append("conflicting_cohort_evidence")
            if evidence.site_id != acquisition.get("site_id"): contextual_holds.append("cohort_site_mismatch")
            if evidence.cohort_ref != expected_ref: contextual_holds.append("cohort_ref_mismatch")
            expected_start = cohort_start.date().isoformat()
            expected_end = (cohort_start + timedelta(days=days-1)).date().isoformat()
            if evidence.window_start != expected_start or evidence.window_end != expected_end:
                contextual_holds.append("cohort_window_boundary_mismatch")
            if evidence.currency != (direct.currency or "UNKNOWN"): contextual_holds.append("cohort_currency_mismatch")
            if evidence.money_basis != metrica.money_basis: contextual_holds.append("cohort_money_basis_mismatch")
            if evidence.timezone != metrica.timezone: contextual_holds.append("cohort_timezone_mismatch")
            contextual_holds.extend(evidence.hold_reasons)
        valid = evidence is not None and evidence.optimizer_consumable and not contextual_holds
        result = cohort_k5(days, direct.spend,
            evidence.attributed_cohort_revenue if valid else None,
            cohort_ref=expected_ref, grade=attribution.grade,
            link_proven=valid and attribution.cohort_link_proven,
            as_of=as_of, cohort_start=cohort_start,
            reconciliation=evidence.reconciliation_state if evidence is not None else ReconciliationState.SOURCE_MISSING)
        if not valid:
            reasons = tuple(dict.fromkeys((*result.hold_reasons,
                "NOT_COMPUTABLE_ATTRIBUTION_HOLD", *contextual_holds)))
            return replace(result, value=None, numerator=None, state=MoneyState.NOT_COMPUTABLE,
                hold_reasons=reasons)
        return replace(result, numerator_source=evidence.source_refs,
            money_basis=evidence.money_basis,
            window_start=evidence.window_start, window_end=evidence.window_end)


class ProposalKind(StrEnum):
    LEARN = "LEARN"; TEST = "TEST"; SCALE = "SCALE"; HOLD = "HOLD"
    REDUCE = "REDUCE"; STOP = "STOP"; QUARANTINE = "QUARANTINE"


@dataclass(frozen=True)
class ActionProposal:
    proposal_version: str
    proposal_id: str
    proposal_digest: str
    site_id: str
    kind: ProposalKind
    target_refs: Mapping[str, str]
    strategy_evidence_digest: str
    measurement_refs: tuple[str, ...]
    provenance_refs: tuple[str, ...]
    current_weekly_budget: str | None
    proposed_weekly_budget: str | None
    budget_delta: str | None
    guard_requirements: tuple[str, ...]
    owner_approval_required: bool
    private_decision_ref: str
    private_decision_digest: str
    audit_metadata: Mapping[str, str]
    requires_budget_governor: bool = True
    provider_write_allowed: bool = False


def build_action_proposal(
    *, proposal_id: str, site_id: str, kind: ProposalKind, target_refs: Mapping[str, str],
    strategy_evidence_digest: str, measurement_refs: Sequence[str], provenance_refs: Sequence[str],
    current_weekly_budget: str | None, proposed_weekly_budget: str | None,
    private_decision_ref: str, private_decision_digest: str, audit_metadata: Mapping[str, str],
) -> ActionProposal:
    delta: str | None = None
    try:
        if current_weekly_budget is not None and proposed_weekly_budget is not None:
            delta = str(Decimal(proposed_weekly_budget) - Decimal(current_weekly_budget))
    except (InvalidOperation, ValueError):
        delta = None
    owner_required = False
    try:
        if current_weekly_budget and proposed_weekly_budget:
            current, proposed = Decimal(current_weekly_budget), Decimal(proposed_weekly_budget)
            owner_required = current > 0 and proposed > current * Decimal("1.20")
    except (InvalidOperation, ValueError):
        pass
    core = {
        "proposal_version": "1.0", "proposal_id": proposal_id, "site_id": site_id, "kind": kind,
        "target_refs": dict(target_refs), "strategy_evidence_digest": strategy_evidence_digest,
        "measurement_refs": tuple(measurement_refs), "provenance_refs": tuple(provenance_refs),
        "current_weekly_budget": current_weekly_budget, "proposed_weekly_budget": proposed_weekly_budget,
        "budget_delta": delta, "guard_requirements": ("data-quality", "reconciliation", "maturity", "kill-switch", "budget-governor"),
        "owner_approval_required": owner_required, "private_decision_ref": private_decision_ref,
        "private_decision_digest": private_decision_digest, "audit_metadata": dict(audit_metadata),
        "requires_budget_governor": True, "provider_write_allowed": False,
    }
    return ActionProposal(**core, proposal_digest=digest(core))


class GovernorState(StrEnum):
    GOVERNOR_READY_FOR_DAY11_CONTROLLER = "GOVERNOR_READY_FOR_DAY11_CONTROLLER"
    PENDING_OWNER_APPROVAL = "PENDING_OWNER_APPROVAL"
    BLOCKED_DATA_QUALITY = "BLOCKED_DATA_QUALITY"
    BLOCKED_BUDGET_BASELINE = "BLOCKED_BUDGET_BASELINE"
    BLOCKED_KILL_SWITCH = "BLOCKED_KILL_SWITCH"
    BLOCKED_PROPOSAL_CONTRACT = "BLOCKED_PROPOSAL_CONTRACT"


@dataclass(frozen=True)
class GuardContext:
    data_quality_hold: bool
    reconciliation_state: ReconciliationState
    money_state: MoneyState
    mature: bool
    optimizer_consumable: bool
    global_kill_switch: bool
    structural_valid: bool
    owner_approval_evidence: str | None = None


@dataclass(frozen=True)
class GovernorDecision:
    state: GovernorState
    reasons: tuple[str, ...]
    increase_percent: Decimal | None
    provider_requests: int = 0
    advertising_spend: int = 0
    provider_write_allowed: bool = False


def govern(proposal: ActionProposal, guards: GuardContext) -> GovernorDecision:
    if proposal.provider_write_allowed or not proposal.requires_budget_governor or not guards.structural_valid:
        return GovernorDecision(GovernorState.BLOCKED_PROPOSAL_CONTRACT, ("proposal_contract_invalid",), None)
    if guards.global_kill_switch:
        return GovernorDecision(GovernorState.BLOCKED_KILL_SWITCH, ("global_kill_switch",), None)
    safety_kinds = {ProposalKind.STOP, ProposalKind.HOLD, ProposalKind.QUARANTINE}
    if proposal.kind in safety_kinds:
        return GovernorDecision(GovernorState.GOVERNOR_READY_FOR_DAY11_CONTROLLER, (), Decimal("0"))
    if proposal.kind in {ProposalKind.SCALE, ProposalKind.TEST, ProposalKind.LEARN, ProposalKind.REDUCE}:
        try:
            if proposal.current_weekly_budget is None or proposal.proposed_weekly_budget is None:
                raise InvalidOperation
            current = Decimal(proposal.current_weekly_budget); proposed = Decimal(proposal.proposed_weekly_budget)
            if current <= 0 or proposed < 0 or proposal.budget_delta is None or Decimal(proposal.budget_delta) != proposed-current:
                raise InvalidOperation
        except (InvalidOperation, ValueError):
            return GovernorDecision(GovernorState.BLOCKED_BUDGET_BASELINE, ("budget_baseline_or_decimal_invalid",), None)
        increase = ((proposed-current)/current)*Decimal("100")
        if proposal.kind in {ProposalKind.SCALE, ProposalKind.TEST} and (
            guards.data_quality_hold or guards.reconciliation_state != ReconciliationState.MATCHED
            or guards.money_state == MoneyState.NOT_COMPUTABLE or not guards.mature or not guards.optimizer_consumable
        ):
            return GovernorDecision(GovernorState.BLOCKED_DATA_QUALITY, ("accepted_money_evidence_required",), increase)
        if increase > Decimal("20.00") and not guards.owner_approval_evidence:
            return GovernorDecision(GovernorState.PENDING_OWNER_APPROVAL, ("owner_approval_required_above_20_percent",), increase)
        return GovernorDecision(GovernorState.GOVERNOR_READY_FOR_DAY11_CONTROLLER, (), increase)
    return GovernorDecision(GovernorState.BLOCKED_PROPOSAL_CONTRACT, ("proposal_kind_invalid",), None)


@dataclass(frozen=True)
class SiteExperimentIntent:
    intent_version: str
    intent_id: str
    action: str
    experiment_ref: str
    variant_refs: tuple[str, ...]
    kill_switch_ref: str
    action_proposal_ref: str
    executable: bool
    provider_requests: int
    site_requests: int
    intent_digest: str


def build_site_experiment_intent(*, intent_id: str, action: str, experiment_ref: str, variant_refs: Sequence[str], kill_switch_ref: str, action_proposal_ref: str) -> SiteExperimentIntent:
    if action not in {"activation", "hold", "stop", "kill-switch"}:
        raise ValueError("unsupported inert site experiment action")
    core = {"intent_version":"1.0","intent_id":intent_id,"action":action,"experiment_ref":experiment_ref,"variant_refs":tuple(variant_refs),"kill_switch_ref":kill_switch_ref,"action_proposal_ref":action_proposal_ref,"executable":False,"provider_requests":0,"site_requests":0}
    return SiteExperimentIntent(**core,intent_digest=digest(core))
