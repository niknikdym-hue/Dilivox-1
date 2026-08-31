from __future__ import annotations

from dataclasses import asdict, replace
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Sequence

from .campaign_factory import (
    AdGroupSpec,
    BudgetRequest,
    CampaignSpec,
    CreativeSpec,
    ProviderCapability,
    TrackingPlan,
    YANDEX_DIRECT_DRY_RUN,
    build_preview,
    load_content_registry,
)


CAMPAIGN_NAME = "DILIVOX | SEARCH | PROFIT ENGINE"


def manual_search_capability() -> ProviderCapability:
    strategies = dict(YANDEX_DIRECT_DRY_RUN.strategies)
    strategies["unified_performance"] = frozenset({*strategies["unified_performance"], "manual_search"})
    return replace(
        YANDEX_DIRECT_DRY_RUN,
        strategies=strategies,
        metadata_version="direct-v5-v501-manual-search-preview-1",
    )


def _budget(value: str) -> str:
    try:
        parsed = Decimal(value)
    except (InvalidOperation, ValueError) as exc:
        raise ValueError("weekly budget must be a decimal RUB value") from exc
    if parsed <= 0:
        raise ValueError("weekly budget must be positive")
    return format(parsed, "f")


def _keywords(values: Sequence[str]) -> tuple[str, ...]:
    cleaned = tuple(dict.fromkeys(" ".join(str(value).split()) for value in values if str(value).strip()))
    if not cleaned:
        raise ValueError("at least one search keyword is required")
    if len(cleaned) > 100:
        raise ValueError("P0 dry-run keyword universe is capped at 100 terms")
    if any(len(value) > 255 for value in cleaned):
        raise ValueError("keyword exceeds bounded preview length")
    return cleaned


def build_manual_search_preview(
    *,
    registry_path: Path,
    weekly_budget_rub: str,
    keywords: Sequence[str],
    landing_content_id: str | None = None,
) -> dict[str, Any]:
    registry = load_content_registry(registry_path)
    if landing_content_id:
        landing = registry.get(landing_content_id)
    else:
        landing = next(
            (
                item for item in registry.values()
                if item.get("active") and item.get("content_type") == "catalog" and item.get("monetization_eligible")
            ),
            None,
        )
    if not landing:
        raise ValueError("active monetization-eligible Dilivox landing is not available")

    keyword_set = _keywords(keywords)
    budget = _budget(weekly_budget_rub)
    creative = CreativeSpec(
        spec_version="1.0",
        template_id="manual-search-dilivox",
        template_version="1",
        creative_id="creative-dilivox-search-p0",
        variant_id="control-a",
        content_id=landing["content_id"],
        headline="Интерактивные истории Dilivox",
        body="Читайте историю, выбирайте версию и открывайте развязку.",
        destination_ref=landing["canonical_url"],
        provider_format="performance_ad",
        asset_refs=(),
        provenance=("owner:p0-manual-search", "content-registry:canonical"),
    )
    spec = CampaignSpec(
        spec_version="1.0",
        site_id="dilivox",
        provider_id="yandex_direct",
        campaign_key="dilivox-search-profit-engine-p0",
        campaign_type="unified_performance",
        objective_kind="owner_profit_k5",
        landing_content_id=landing["content_id"],
        destination_url=landing["canonical_url"],
        strategy_kind="manual_search",
        strategy_parameters={},
        budget_request=BudgetRequest(
            amount=budget,
            currency="RUB",
            period="weekly",
            basis="owner_fixed_initial_manual_search_learning_budget",
            evidence_ref="owner:p0-manual-search-priority",
            baseline_ref=None,
            requires_budget_governor=True,
            provider_write_allowed=False,
            owner_approval_required=True,
        ),
        geo=("RU",),
        schedule={"timezone": "Europe/Moscow", "window": "always"},
        tracking_plan=TrackingPlan({
            "campaign_id": "{campaign_id}",
            "ad_id": "{ad_id}",
            "group_id": "{gbid}",
            "criterion_id": "{criterion_id}",
            "utm_source": "yandex",
            "utm_medium": "cpc",
            "utm_campaign": "dilivox-search-profit-engine",
            "utm_term": "{keyword}",
        }),
        goal_refs=(),
        ad_groups=(AdGroupSpec(
            group_key="search-control-a",
            group_type="performance",
            targeting_kind="keyword",
            targeting_values=keyword_set,
            creative_refs=(creative.creative_id,),
        ),),
        creative_refs=(creative.creative_id,),
        evidence_refs=(
            "ACQUISITION_STRATEGY_LAB:P0_MANUAL_SEARCH",
            "TASK-014:MS5_DRY_RUN",
        ),
        experiment_ref="manual-search-control-a",
        provider_write_allowed=False,
        safety_mode="DAY8_DRY_RUN",
    )
    preview = build_preview(spec, (creative,), (), registry, manual_search_capability())
    return {
        "mode": "MANUAL_SEARCH_DEDICATED_CAMPAIGN_DRY_RUN",
        "campaign_name": CAMPAIGN_NAME,
        "provider_shape": {
            "campaign_type": "UNIFIED_CAMPAIGN",
            "search_bidding_strategy_type": "HIGHEST_POSITION",
            "network_bidding_strategy_type": "SERVING_OFF",
            "weekly_spend_limit_rub": budget,
            "weekly_budget_owner_fixed_for_initial_learning": True,
            "keyword_count": len(keyword_set),
            "autotargeting_default": "OFF_UNTIL_SEPARATE_TEST_CELL",
        },
        "landing": {
            "content_id": landing["content_id"],
            "canonical_url": landing["canonical_url"],
            "content_type": landing["content_type"],
        },
        "keywords": list(keyword_set),
        "factory_preview": asdict(preview),
        "provider_requests": 0,
        "advertising_spend": 0,
        "provider_write_allowed": False,
        "create_authorized": False,
        "next_gate": "MS6_SEPARATE_GUARDED_CAMPAIGN_CREATE_ACCEPTANCE",
    }
