"""Deterministic Day-8 campaign/creative preview factory.

This module deliberately has no transport or provider client. Provider operation
names are inert audit metadata and every generated intent is non-executable.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from decimal import Decimal, InvalidOperation
from enum import StrEnum
from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Mapping, Sequence


class PreviewState(StrEnum):
    PREVIEW_VALID = "PREVIEW_VALID"
    PREVIEW_INVALID = "PREVIEW_INVALID"
    BLOCKED_PROVIDER_CAPABILITY = "BLOCKED_PROVIDER_CAPABILITY"
    BLOCKED_MISSING_CONTENT_ID = "BLOCKED_MISSING_CONTENT_ID"
    BLOCKED_TRACKING_CONTRACT = "BLOCKED_TRACKING_CONTRACT"
    BLOCKED_BUDGET_GOVERNOR_REQUIRED = "BLOCKED_BUDGET_GOVERNOR_REQUIRED"
    BLOCKED_PRIVATE_CORE_REQUIRED = "BLOCKED_PRIVATE_CORE_REQUIRED"


ALLOWED_STATES = frozenset(PreviewState)
TRACKING_ALLOWLIST = frozenset({
    "yclid", "campaign_id", "ad_id", "group_id", "criterion_id",
    "phrase_id", "keyword_id", "utm_source", "utm_medium",
    "utm_campaign", "utm_content", "utm_term",
})
DIRECT_VARIABLES = {
    "campaign_id": "{campaign_id}",
    "ad_id": "{ad_id}",
    "group_id": "{gbid}",
    "criterion_id": "{criterion_id}",
    "phrase_id": "{phrase_id}",
    "keyword_id": "{keyword}",
}


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)


def digest(value: Any) -> str:
    return sha256(canonical_json(value).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class BudgetRequest:
    amount: str
    currency: str
    period: str
    basis: str
    evidence_ref: str
    baseline_ref: str | None = None
    requires_budget_governor: bool = True
    provider_write_allowed: bool = False
    owner_approval_required: bool = True

    def errors(self) -> tuple[str, ...]:
        errors: list[str] = []
        try:
            amount = Decimal(self.amount)
            if amount <= 0:
                errors.append("budget_amount_not_positive")
        except (InvalidOperation, ValueError):
            errors.append("budget_amount_not_decimal")
        if not self.requires_budget_governor or self.provider_write_allowed:
            errors.append("budget_governor_required")
        if self.currency != "RUB" or self.period not in {"daily", "weekly"} or not self.basis:
            errors.append("budget_contract_invalid")
        return tuple(errors)


@dataclass(frozen=True)
class TrackingPlan:
    parameters: Mapping[str, str]

    def errors(self, supported_variables: frozenset[str]) -> tuple[str, ...]:
        errors: list[str] = []
        keys = list(self.parameters)
        if len(keys) != len(set(keys)):
            errors.append("tracking_parameter_collision")
        unknown = sorted(set(keys) - TRACKING_ALLOWLIST)
        if unknown:
            errors.append("tracking_key_not_allowlisted:" + ",".join(unknown))
        seen_values: set[str] = set()
        for key, value in self.parameters.items():
            if not isinstance(value, str) or not value or len(value) > 128:
                errors.append(f"tracking_value_invalid:{key}")
                continue
            if value in seen_values and value.startswith("{"):
                errors.append("tracking_dynamic_collision")
            seen_values.add(value)
            if value.startswith("{") and value.endswith("}") and value not in supported_variables:
                errors.append(f"unsupported_dynamic_variable:{value}")
        return tuple(errors)


@dataclass(frozen=True)
class CreativeSpec:
    spec_version: str
    template_id: str
    template_version: str
    creative_id: str
    variant_id: str
    content_id: str
    headline: str
    body: str
    destination_ref: str
    provider_format: str
    asset_refs: tuple[str, ...]
    provenance: tuple[str, ...]
    validation_state: str = "UNVALIDATED"
    rejection_reasons: tuple[str, ...] = ()

    @property
    def identity(self) -> str:
        return digest(asdict(self))[:24]


@dataclass(frozen=True)
class AssetSpec:
    asset_id: str
    source_ref: str
    content_id: str
    sha256: str
    mime_type: str
    width: int
    height: int
    usage_scope: str
    provider_compatibility: str
    version: int = 1
    replaces_asset_id: str | None = None
    transformation_intent: Mapping[str, Any] | None = None

    def errors(self) -> tuple[str, ...]:
        errors: list[str] = []
        if len(self.sha256) != 64 or any(c not in "0123456789abcdef" for c in self.sha256):
            errors.append("asset_sha256_invalid")
        if self.width <= 0 or self.height <= 0 or not self.mime_type.startswith("image/"):
            errors.append("asset_metadata_invalid")
        if self.transformation_intent and not self.transformation_intent.get("transformation_version"):
            errors.append("asset_transformation_not_versioned")
        if self.provider_compatibility not in {"compatible", "transformation_required"}:
            errors.append("asset_provider_incompatible")
        return tuple(errors)


@dataclass
class AssetRegistry:
    assets: dict[str, AssetSpec] = field(default_factory=dict)

    def register(self, asset: AssetSpec) -> tuple[str, tuple[str, ...]]:
        if asset.errors():
            return "rejected", asset.errors()
        old = self.assets.get(asset.asset_id)
        if old == asset:
            return "idempotent", ()
        if old is not None:
            return "rejected", ("asset_identity_conflict",)
        if asset.replaces_asset_id and asset.replaces_asset_id not in self.assets:
            return "rejected", ("asset_replacement_unknown",)
        self.assets[asset.asset_id] = asset
        return "created", ()


@dataclass(frozen=True)
class AdGroupSpec:
    group_key: str
    group_type: str
    targeting_kind: str
    targeting_values: tuple[str, ...]
    creative_refs: tuple[str, ...]


@dataclass(frozen=True)
class CampaignSpec:
    spec_version: str
    site_id: str
    provider_id: str
    campaign_key: str
    campaign_type: str
    objective_kind: str
    landing_content_id: str
    destination_url: str
    strategy_kind: str
    strategy_parameters: Mapping[str, Any]
    budget_request: BudgetRequest
    geo: tuple[str, ...]
    schedule: Mapping[str, str]
    tracking_plan: TrackingPlan
    goal_refs: tuple[str, ...]
    ad_groups: tuple[AdGroupSpec, ...]
    creative_refs: tuple[str, ...]
    evidence_refs: tuple[str, ...]
    experiment_ref: str | None = None
    provider_write_allowed: bool = False
    safety_mode: str = "DAY8_DRY_RUN"


@dataclass(frozen=True)
class ProviderCapability:
    provider_id: str
    campaign_groups: Mapping[str, frozenset[str]]
    strategies: Mapping[str, frozenset[str]]
    creative_limits: Mapping[str, Mapping[str, int]]
    tracking_variables: frozenset[str]
    entity_services: Mapping[str, str]
    metadata_version: str


YANDEX_DIRECT_DRY_RUN = ProviderCapability(
    provider_id="yandex_direct",
    campaign_groups={"text": frozenset({"text"}), "unified_performance": frozenset({"performance"})},
    strategies={
        "text": frozenset({"cpc", "conversion_click", "pay_for_conversion", "value_crr"}),
        "unified_performance": frozenset({"cpc", "conversion_click", "value_crr", "maximum_profit"}),
    },
    creative_limits={"text_ad": {"headline": 56, "body": 81}, "performance_ad": {"headline": 56, "body": 81}},
    tracking_variables=frozenset(DIRECT_VARIABLES.values()),
    entity_services={
        "campaign": "Campaigns", "ad_group": "AdGroups", "targeting": "Keywords",
        "asset": "AdImages", "ad": "Ads", "tracking": "Ads", "readiness": "Ads",
    },
    metadata_version="direct-v5-v501-preview-1",
)


@dataclass(frozen=True)
class Intent:
    intent_id: str
    dependencies: tuple[str, ...]
    entity_type: str
    service: str
    proposed_operation: str
    parameters: Mapping[str, Any]
    rollback_intent_ref: str | None
    executable: bool = False


@dataclass(frozen=True)
class Preview:
    preview_version: str
    state: PreviewState
    spec_digest: str
    preview_digest: str
    entity_counts: Mapping[str, int]
    dependency_order: tuple[str, ...]
    tracking_plan: Mapping[str, str]
    strategy_request: Mapping[str, Any]
    budget_proposal: Mapping[str, Any]
    creative_variants: tuple[Mapping[str, Any], ...]
    assets: tuple[Mapping[str, Any], ...]
    intents: tuple[Mapping[str, Any], ...]
    rollback_graph: tuple[str, ...]
    warnings: tuple[str, ...]
    errors: tuple[str, ...]
    unsupported_features: tuple[str, ...]
    provider_requests: int = 0
    advertising_spend: int = 0
    provider_write_allowed: bool = False


def load_content_registry(path: Path) -> dict[str, Mapping[str, Any]]:
    value = json.loads(path.read_text(encoding="utf-8"))
    return {item["content_id"]: item for item in value["items"]}


def _state(errors: Sequence[str]) -> PreviewState:
    if any(e.startswith("content_") or e.startswith("destination_") for e in errors):
        return PreviewState.BLOCKED_MISSING_CONTENT_ID
    if any("tracking" in e or "dynamic_variable" in e for e in errors):
        return PreviewState.BLOCKED_TRACKING_CONTRACT
    if "budget_governor_required" in errors:
        return PreviewState.BLOCKED_BUDGET_GOVERNOR_REQUIRED
    if any(e.startswith("provider_") or e.startswith("strategy_") or e.startswith("campaign_group_") for e in errors):
        return PreviewState.BLOCKED_PROVIDER_CAPABILITY
    if "private_core_required" in errors:
        return PreviewState.BLOCKED_PRIVATE_CORE_REQUIRED
    return PreviewState.PREVIEW_INVALID if errors else PreviewState.PREVIEW_VALID


def _intent_id(spec_key: str, kind: str, key: str) -> str:
    return "intent-" + digest({"spec": spec_key, "kind": kind, "key": key})[:20]


def build_preview(
    spec: CampaignSpec,
    creatives: Sequence[CreativeSpec],
    assets: Sequence[AssetSpec],
    content_registry: Mapping[str, Mapping[str, Any]],
    capability: ProviderCapability = YANDEX_DIRECT_DRY_RUN,
) -> Preview:
    errors: list[str] = []
    unsupported: list[str] = []
    if spec.spec_version != "1.0" or spec.safety_mode != "DAY8_DRY_RUN" or spec.provider_write_allowed:
        errors.append("provider_write_safety_invalid")
    if spec.provider_id != capability.provider_id:
        errors.append("provider_not_supported")
    landing = content_registry.get(spec.landing_content_id)
    if not landing:
        errors.append("content_id_missing_or_unknown")
    elif not landing.get("active"):
        errors.append("content_id_inactive")
    elif spec.destination_url != landing.get("canonical_url"):
        errors.append("destination_not_canonical")
    errors.extend(spec.budget_request.errors())
    errors.extend(spec.tracking_plan.errors(capability.tracking_variables))
    if spec.campaign_type not in capability.campaign_groups:
        errors.append("provider_campaign_type_unsupported")
    else:
        supported_groups = capability.campaign_groups[spec.campaign_type]
        if any(group.group_type not in supported_groups for group in spec.ad_groups):
            errors.append("campaign_group_subtype_mismatch")
        if spec.strategy_kind not in capability.strategies[spec.campaign_type]:
            errors.append("strategy_combination_unsupported")
    if spec.strategy_kind in {"conversion_click", "pay_for_conversion", "value_crr", "maximum_profit"} and not spec.goal_refs:
        errors.append("strategy_goal_required")
    if set(spec.strategy_parameters) - {"goal_ref", "target_cpa", "target_crr", "payment_model"}:
        errors.append("strategy_parameter_unsupported")
    if not spec.geo or not spec.schedule:
        errors.append("campaign_geo_schedule_invalid")
    creative_by_id = {item.creative_id: item for item in creatives}
    if len(creative_by_id) != len(creatives) or len({item.variant_id for item in creatives}) != len(creatives):
        errors.append("duplicate_creative_identity")
    if set(spec.creative_refs) != set(creative_by_id):
        errors.append("creative_reference_mismatch")
    asset_by_id = {item.asset_id: item for item in assets}
    if len(asset_by_id) != len(assets):
        errors.append("duplicate_asset_identity")
    for asset in assets:
        errors.extend(asset.errors())
        if asset.content_id != spec.landing_content_id:
            errors.append("asset_content_mismatch")
    creative_results: dict[str, tuple[str, ...]] = {}
    for creative in creatives:
        creative_errors: list[str] = []
        limits = capability.creative_limits.get(creative.provider_format)
        if not limits:
            creative_errors.append("provider_creative_format_unsupported")
            creative_results[creative.creative_id] = tuple(creative_errors)
            errors.extend(creative_errors)
            continue
        if not creative.headline or not creative.body or not creative.destination_ref:
            creative_errors.append("creative_required_field_missing")
        if len(creative.headline) > limits["headline"] or len(creative.body) > limits["body"]:
            creative_errors.append("creative_provider_limit_exceeded")
        if creative.content_id != spec.landing_content_id or creative.destination_ref != spec.destination_url:
            creative_errors.append("creative_destination_mismatch")
        if any(ref not in asset_by_id for ref in creative.asset_refs):
            creative_errors.append("creative_asset_missing")
        creative_results[creative.creative_id] = tuple(creative_errors)
        errors.extend(creative_errors)
    group_keys = [group.group_key for group in spec.ad_groups]
    if len(group_keys) != len(set(group_keys)):
        errors.append("duplicate_entity_key")

    intents: list[Intent] = []
    campaign_id = _intent_id(spec.campaign_key, "campaign", spec.campaign_key)
    campaign_rollback = _intent_id(spec.campaign_key, "rollback", campaign_id)
    intents.append(Intent(campaign_id, (), "campaign", "Campaigns", "future_create", {"campaign_key": spec.campaign_key}, campaign_rollback))
    for group in spec.ad_groups:
        group_id = _intent_id(spec.campaign_key, "ad_group", group.group_key)
        group_rollback = _intent_id(spec.campaign_key, "rollback", group_id)
        intents.append(Intent(group_id, (campaign_id,), "ad_group", "AdGroups", "future_create", {"group_key": group.group_key}, group_rollback))
        targeting_id = _intent_id(spec.campaign_key, "targeting", group.group_key)
        targeting_rollback = _intent_id(spec.campaign_key, "rollback", targeting_id)
        intents.append(Intent(targeting_id, (group_id,), "targeting", "Keywords", "future_create", {"kind": group.targeting_kind, "values": group.targeting_values}, targeting_rollback))
        for creative_ref in group.creative_refs:
            creative = creative_by_id.get(creative_ref)
            if not creative:
                continue
            asset_intents: list[str] = []
            for asset_ref in creative.asset_refs:
                asset_id = _intent_id(spec.campaign_key, "asset", asset_ref)
                asset_intents.append(asset_id)
                if not any(item.intent_id == asset_id for item in intents):
                    intents.append(Intent(asset_id, (), "asset", "AdImages", "future_upload", {"asset_ref": asset_ref}, _intent_id(spec.campaign_key, "rollback", asset_id)))
            ad_id = _intent_id(spec.campaign_key, "ad", creative_ref)
            intents.append(Intent(ad_id, tuple([group_id, *asset_intents]), "ad", "Ads", "future_create", {"creative_ref": creative_ref}, _intent_id(spec.campaign_key, "rollback", ad_id)))
    tracking_id = _intent_id(spec.campaign_key, "tracking", "tracking")
    ad_ids = tuple(item.intent_id for item in intents if item.entity_type == "ad")
    intents.append(Intent(tracking_id, ad_ids, "tracking", "Ads", "future_associate_tracking", dict(spec.tracking_plan.parameters), _intent_id(spec.campaign_key, "rollback", tracking_id)))
    readiness_id = _intent_id(spec.campaign_key, "readiness", "readiness")
    intents.append(Intent(readiness_id, (tracking_id,), "readiness", "Ads", "future_moderation_readiness_check", {}, None))

    forward_intents = tuple(intents)
    rollback_graph = tuple(item.rollback_intent_ref for item in reversed(forward_intents) if item.rollback_intent_ref)
    previous_rollback_dependency = readiness_id
    forward_by_rollback = {item.rollback_intent_ref: item for item in forward_intents if item.rollback_intent_ref}
    for rollback_id in rollback_graph:
        target = forward_by_rollback[rollback_id]
        intents.append(Intent(
            rollback_id, (previous_rollback_dependency,), "rollback", target.service,
            "future_rollback", {"target_intent_ref": target.intent_id}, None,
        ))
        previous_rollback_dependency = rollback_id
    dependency_order = tuple(item.intent_id for item in intents)
    state = _state(errors)
    spec_value = asdict(spec)
    spec_digest = digest(spec_value)
    core = {
        "preview_version": "1.0",
        "state": state,
        "spec_digest": spec_digest,
        "entity_counts": {kind: sum(i.entity_type == kind for i in intents) for kind in sorted({i.entity_type for i in intents})},
        "dependency_order": dependency_order,
        "tracking_plan": dict(sorted(spec.tracking_plan.parameters.items())),
        "strategy_request": {"kind": spec.strategy_kind, "parameters": spec.strategy_parameters},
        "budget_proposal": asdict(spec.budget_request),
        "creative_variants": tuple(
            asdict(item) | {
                "variant_identity": item.identity,
                "validation_state": "REJECTED" if creative_results.get(item.creative_id) else "VALID",
                "rejection_reasons": creative_results.get(item.creative_id, ()),
            }
            for item in creatives
        ),
        "assets": tuple(asdict(item) for item in assets),
        "intents": tuple(asdict(item) for item in intents),
        "rollback_graph": rollback_graph,
        "warnings": (), "errors": tuple(sorted(set(errors))), "unsupported_features": tuple(sorted(set(unsupported))),
        "provider_requests": 0, "advertising_spend": 0, "provider_write_allowed": False,
    }
    return Preview(**core, preview_digest=digest(core))


def synthetic_fixture(registry_path: Path, scenario: str = "valid") -> Preview:
    registry = load_content_registry(registry_path)
    active = next(item for item in registry.values() if item.get("active") and item.get("content_type") == "story")
    content_id = active["content_id"]
    tracking: Mapping[str, str] = {
        "campaign_id": "{campaign_id}", "ad_id": "{ad_id}", "group_id": "{gbid}",
        "utm_source": "yandex", "utm_medium": "cpc", "utm_campaign": "synthetic-day8",
    }
    campaign_type, strategy = "text", "cpc"
    if scenario == "missing-content":
        content_id = "00000000-0000-4000-8000-000000000000"
    elif scenario == "invalid-tracking":
        tracking = {"email": "{unsupported_private_value}"}
    elif scenario == "invalid-capability":
        campaign_type, strategy = "text", "maximum_profit"
    asset = AssetSpec("asset-synthetic-1", "fixture://synthetic-image", active["content_id"], "a" * 64, "image/png", 1080, 607, "direct-preview", "compatible")
    creative = CreativeSpec("1.0", "synthetic-story", "1", "creative-synthetic-1", "variant-a", active["content_id"], "Синтетическая история", "Читайте синтетический пример истории", active["canonical_url"], "text_ad", (asset.asset_id,), ("fixture:day8",))
    spec = CampaignSpec(
        "1.0", "dilivox", "yandex_direct", "campaign-synthetic-day8", campaign_type, "traffic",
        content_id, active["canonical_url"], strategy, {}, BudgetRequest("100.00", "RUB", "daily", "synthetic-proposal", "fixture:day8"),
        ("RU",), {"timezone": "Europe/Moscow", "window": "always"}, TrackingPlan(tracking), (),
        (AdGroupSpec("group-synthetic-1", "text", "keyword", ("синтетическая история",), (creative.creative_id,)),),
        (creative.creative_id,), ("fixture:day8",),
    )
    return build_preview(spec, (creative,), (asset,), registry)
