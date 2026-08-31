from __future__ import annotations

import csv
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from io import StringIO
from pathlib import Path
from typing import Any, Callable

from .config import DEFAULT_CONFIG_PATH, load_site_config, resolve_secret
from .models import HttpRequest, HttpResponse
from .transport import HttpTransport, TransportError, UrllibTransport


DIRECT_REPORTS_ENDPOINT = "https://api.direct.yandex.com/json/v501/reports"
MAX_KEYWORDS = 10_000


@dataclass(frozen=True)
class ManualSearchReadResult:
    site_id: str
    campaign_id: str
    campaign_name: str | None
    campaign_state: str | None
    campaign_status: str | None
    campaign_type: str | None
    search_strategy: str | None
    network_strategy: str | None
    weekly_spend_limit_rub: Decimal | None
    manual_search_shape_ready: bool
    holds: tuple[str, ...]
    keyword_count: int
    report_rows: int
    cells: tuple[dict[str, Any], ...]
    provider_write_allowed: bool = False


class ManualSearchReadModel:
    """Read-only exact Direct model for the P0 manual-search controller."""

    def __init__(self, *, transport: HttpTransport, config: Any):
        self.transport = transport
        self.config = config

    def run(self, *, campaign_id: str, date_from: str, date_to: str, token: str) -> ManualSearchReadResult:
        provider_id = _campaign_id(campaign_id)
        _date_window(date_from, date_to)
        campaign = self._campaign(provider_id, token)
        holds: list[str] = []

        if str(campaign.get("Type")) != "UNIFIED_CAMPAIGN":
            holds.append("campaign_is_not_unified")

        unified = campaign.get("UnifiedCampaign") or {}
        bidding = unified.get("BiddingStrategy") or {}
        search = bidding.get("Search") or {}
        network = bidding.get("Network") or {}
        search_type = search.get("BiddingStrategyType")
        network_type = network.get("BiddingStrategyType")
        weekly = _weekly_limit(search)

        if search_type != "HIGHEST_POSITION":
            holds.append("search_strategy_is_not_highest_position")
        if network_type != "SERVING_OFF":
            holds.append("network_is_not_serving_off")
        if weekly is None:
            holds.append("weekly_spend_limit_missing")

        shape_ready = not holds
        if not shape_ready:
            return ManualSearchReadResult(
                site_id=self.config.site_id,
                campaign_id=str(provider_id),
                campaign_name=campaign.get("Name"),
                campaign_state=campaign.get("State"),
                campaign_status=campaign.get("Status"),
                campaign_type=campaign.get("Type"),
                search_strategy=search_type,
                network_strategy=network_type,
                weekly_spend_limit_rub=weekly,
                manual_search_shape_ready=False,
                holds=tuple(holds),
                keyword_count=0,
                report_rows=0,
                cells=(),
            )

        keywords = self._keywords(provider_id, token)
        bids = self._bids(provider_id, token)
        report = self._criteria_report(provider_id, date_from, date_to, token)

        keyword_by_id = {str(item.get("Id")): item for item in keywords}
        bid_by_id = {str(item.get("KeywordId")): item for item in bids}
        report_by_id: dict[str, dict[str, Decimal | int | str]] = {}
        for row in report:
            criterion_id = str(row.get("CriterionId", ""))
            if not criterion_id.isdigit():
                continue
            existing = report_by_id.setdefault(criterion_id, {
                "impressions": 0,
                "clicks": 0,
                "cost_rub": Decimal("0"),
                "avg_cpc_weighted_numerator": Decimal("0"),
                "criterion": str(row.get("Criterion", "")),
                "criterion_type": str(row.get("CriterionType", "")),
            })
            impressions = _int(row.get("Impressions"))
            clicks = _int(row.get("Clicks"))
            cost = _decimal(row.get("Cost"))
            avg_cpc = _decimal(row.get("AvgCpc"))
            existing["impressions"] = int(existing["impressions"]) + impressions
            existing["clicks"] = int(existing["clicks"]) + clicks
            existing["cost_rub"] = Decimal(existing["cost_rub"]) + cost
            existing["avg_cpc_weighted_numerator"] = Decimal(existing["avg_cpc_weighted_numerator"]) + (avg_cpc * clicks)

        ids = sorted(set(keyword_by_id) | set(bid_by_id) | set(report_by_id), key=lambda x: int(x) if x.isdigit() else 10**30)
        cells: list[dict[str, Any]] = []
        for keyword_id in ids:
            keyword = keyword_by_id.get(keyword_id, {})
            bid = bid_by_id.get(keyword_id, {})
            stats = report_by_id.get(keyword_id, {})
            search_bid = bid.get("Search") or {}
            clicks = int(stats.get("clicks", 0))
            weighted = Decimal(stats.get("avg_cpc_weighted_numerator", Decimal("0")))
            cells.append({
                "keyword_id": keyword_id,
                "ad_group_id": str(keyword.get("AdGroupId") or bid.get("AdGroupId") or ""),
                "keyword": keyword.get("Keyword") or stats.get("criterion"),
                "criterion_type": stats.get("criterion_type"),
                "state": keyword.get("State"),
                "status": keyword.get("Status"),
                "serving_status": keyword.get("ServingStatus") or bid.get("ServingStatus"),
                "strategy_priority": bid.get("StrategyPriority") or keyword.get("StrategyPriority"),
                "autotargeting_search_bid_is_auto": search_bid.get("AutotargetingSearchBidIsAuto") or keyword.get("AutotargetingSearchBidIsAuto"),
                "search_bid_rub": _micros_text(search_bid.get("Bid")),
                "auction_bids": _auction_public(search_bid.get("AuctionBids")),
                "impressions": int(stats.get("impressions", 0)),
                "clicks": clicks,
                "cost_rub": _decimal_text(stats.get("cost_rub", Decimal("0"))),
                "avg_cpc_rub": _decimal_text(weighted / clicks if clicks else Decimal("0")),
                "revenue_rub": None,
                "k5": None,
                "economic_grain_state": "REVENUE_ATTRIBUTION_NOT_JOINED_YET",
            })

        return ManualSearchReadResult(
            site_id=self.config.site_id,
            campaign_id=str(provider_id),
            campaign_name=campaign.get("Name"),
            campaign_state=campaign.get("State"),
            campaign_status=campaign.get("Status"),
            campaign_type=campaign.get("Type"),
            search_strategy=search_type,
            network_strategy=network_type,
            weekly_spend_limit_rub=weekly,
            manual_search_shape_ready=True,
            holds=(),
            keyword_count=len(keywords),
            report_rows=len(report),
            cells=tuple(cells),
        )

    def _headers(self, token: str) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {token}",
            "Client-Login": self.config.direct_client_login or "",
            "Accept-Language": "en",
        }

    def _campaign(self, campaign_id: int, token: str) -> dict[str, Any]:
        response = self.transport.send(HttpRequest(
            "POST", f"{self.config.direct_endpoint}/campaigns", self._headers(token),
            json_body={
                "method": "get",
                "params": {
                    "SelectionCriteria": {"Ids": [campaign_id]},
                    "FieldNames": ["Id", "Name", "State", "Status", "Type"],
                    "UnifiedCampaignFieldNames": ["CounterIds", "BiddingStrategy", "TrackingParams", "AttributionModel"],
                    "UnifiedCampaignSearchStrategyPlacementTypesFieldNames": ["SearchResults", "ProductGallery", "DynamicPlaces", "Maps", "SearchOrganizationList"],
                },
            },
        ))
        _success(response)
        campaigns = response.json_body.get("result", {}).get("Campaigns", []) if isinstance(response.json_body, dict) else []
        if len(campaigns) != 1 or str(campaigns[0].get("Id")) != str(campaign_id):
            raise ValueError("exact campaign was not returned uniquely")
        return campaigns[0]

    def _keywords(self, campaign_id: int, token: str) -> list[dict[str, Any]]:
        response = self.transport.send(HttpRequest(
            "POST", f"{self.config.direct_endpoint}/keywords", self._headers(token),
            json_body={
                "method": "get",
                "params": {
                    "SelectionCriteria": {"CampaignIds": [campaign_id]},
                    "FieldNames": [
                        "Id", "Keyword", "State", "Status", "ServingStatus", "AdGroupId", "CampaignId",
                        "StrategyPriority", "AutotargetingSearchBidIsAuto"
                    ],
                    "Page": {"Limit": MAX_KEYWORDS},
                },
            },
        ))
        _success(response)
        result = response.json_body.get("result", {}) if isinstance(response.json_body, dict) else {}
        if result.get("LimitedBy") is not None:
            raise ValueError("keyword inventory exceeds the bounded 10000-object launch read")
        values = result.get("Keywords", [])
        if not isinstance(values, list):
            raise ValueError("invalid Keywords.get response")
        for item in values:
            if str(item.get("CampaignId")) != str(campaign_id):
                raise ValueError("keyword inventory contains an unexpected campaign")
        return values

    def _bids(self, campaign_id: int, token: str) -> list[dict[str, Any]]:
        response = self.transport.send(HttpRequest(
            "POST", f"{self.config.direct_endpoint}/keywordbids", self._headers(token),
            json_body={
                "method": "get",
                "params": {
                    "SelectionCriteria": {"CampaignIds": [campaign_id]},
                    "FieldNames": ["KeywordId", "AdGroupId", "CampaignId", "ServingStatus", "StrategyPriority"],
                    "SearchFieldNames": ["Bid", "AutotargetingSearchBidIsAuto", "AuctionBids"],
                    "Page": {"Limit": MAX_KEYWORDS},
                },
            },
        ))
        _success(response)
        result = response.json_body.get("result", {}) if isinstance(response.json_body, dict) else {}
        if result.get("LimitedBy") is not None:
            raise ValueError("keyword bid inventory exceeds the bounded 10000-object launch read")
        values = result.get("KeywordBids", [])
        if not isinstance(values, list):
            raise ValueError("invalid KeywordBids.get response")
        for item in values:
            if str(item.get("CampaignId")) != str(campaign_id):
                raise ValueError("keyword bids contain an unexpected campaign")
        return values

    def _criteria_report(self, campaign_id: int, date_from: str, date_to: str, token: str, max_polls: int = 3) -> list[dict[str, str]]:
        headers = {
            **self._headers(token),
            "processingMode": "auto",
            "returnMoneyInMicros": "false",
            "skipReportHeader": "true",
            "skipColumnHeader": "false",
            "skipReportSummary": "true",
            "Content-Type": "application/json; charset=utf-8",
        }
        response: HttpResponse | None = None
        for _ in range(max_polls):
            response = self.transport.send(HttpRequest(
                "POST", DIRECT_REPORTS_ENDPOINT, headers,
                json_body={
                    "params": {
                        "SelectionCriteria": {
                            "DateFrom": date_from,
                            "DateTo": date_to,
                            "Filter": [{"Field": "CampaignId", "Operator": "IN", "Values": [campaign_id]}],
                        },
                        "FieldNames": [
                            "CampaignId", "AdGroupId", "CriterionId", "Criterion", "CriterionType",
                            "Impressions", "Clicks", "Cost", "AvgCpc"
                        ],
                        "ReportName": f"profit-engine-manual-search-{campaign_id}-{date_from}-{date_to}",
                        "ReportType": "CRITERIA_PERFORMANCE_REPORT",
                        "DateRangeType": "CUSTOM_DATE",
                        "Format": "TSV",
                        "IncludeVAT": "YES",
                        "IncludeDiscount": "YES",
                    }
                },
            ))
            if response.status_code == 200:
                break
            if response.status_code not in {201, 202}:
                raise TransportError("manual-search criteria report failed", status_code=response.status_code)
        if response is None or response.status_code != 200 or not isinstance(response.json_body, str):
            raise TransportError("manual-search criteria report did not become ready", status_code=response.status_code if response else None)
        reader = csv.DictReader(StringIO(response.json_body), delimiter="\t")
        rows = list(reader)
        for row in rows:
            if row.get("CampaignId") != str(campaign_id):
                raise ValueError("criteria report returned an unexpected campaign")
        return rows


def run_manual_search_read(
    *,
    campaign_id: str,
    date_from: str,
    date_to: str,
    config_path: Path = DEFAULT_CONFIG_PATH,
    transport: HttpTransport | None = None,
    secret_resolver: Callable[[str], str | None] = resolve_secret,
) -> ManualSearchReadResult:
    config, present = load_site_config(config_path)
    if not present:
        raise FileNotFoundError(f"private Dilivox config not found at {config_path}")
    if not config.direct_client_login or not config.direct_operator_login:
        raise ValueError("exact Direct operator/target binding is required")
    token = secret_resolver(config.yandex_oauth_token_ref)
    if not token:
        raise ValueError("Direct OAuth credential is unavailable")
    return ManualSearchReadModel(transport=transport or UrllibTransport(max_attempts=3, backoff_seconds=0.2), config=config).run(
        campaign_id=campaign_id, date_from=date_from, date_to=date_to, token=token
    )


def public_result(value: ManualSearchReadResult) -> dict[str, Any]:
    return {
        "mode": "MANUAL_SEARCH_PROFIT_READ_MODEL_READ_ONLY",
        "site_id": value.site_id,
        "campaign_id": value.campaign_id,
        "campaign_name": value.campaign_name,
        "campaign_state": value.campaign_state,
        "campaign_status": value.campaign_status,
        "campaign_type": value.campaign_type,
        "search_strategy": value.search_strategy,
        "network_strategy": value.network_strategy,
        "weekly_spend_limit_rub": _decimal_text(value.weekly_spend_limit_rub),
        "manual_search_shape_ready": value.manual_search_shape_ready,
        "holds": list(value.holds),
        "keyword_count": value.keyword_count,
        "report_rows": value.report_rows,
        "cells": list(value.cells),
        "provider_write_allowed": False,
        "provider_write_requests": 0,
        "revenue_attribution_ready": False,
        "next_phase": "MS2_ATTRIBUTION_GRAIN",
    }


def _campaign_id(value: str) -> int:
    try:
        result = int(str(value))
    except ValueError as exc:
        raise ValueError("campaign_id must be numeric") from exc
    if result <= 0:
        raise ValueError("campaign_id must be positive")
    return result


def _date_window(start: str, end: str) -> None:
    from datetime import date
    if date.fromisoformat(start) > date.fromisoformat(end):
        raise ValueError("date_from must not be after date_to")


def _weekly_limit(search: dict[str, Any]) -> Decimal | None:
    highest = search.get("HighestPosition") if isinstance(search, dict) else None
    if not isinstance(highest, dict) or highest.get("WeeklySpendLimit") is None:
        return None
    return _micros_decimal(highest["WeeklySpendLimit"])


def _micros_decimal(value: Any) -> Decimal:
    return Decimal(str(value)) / Decimal("1000000")


def _micros_text(value: Any) -> str | None:
    if value is None:
        return None
    return _decimal_text(_micros_decimal(value))


def _auction_public(value: Any) -> list[dict[str, Any]]:
    items = value.get("AuctionBidItems", []) if isinstance(value, dict) else []
    result = []
    for item in items if isinstance(items, list) else []:
        result.append({
            "traffic_volume": item.get("TrafficVolume"),
            "bid_rub": _micros_text(item.get("Bid")),
            "price_rub": _micros_text(item.get("Price")),
        })
    return result


def _int(value: Any) -> int:
    try:
        return int(str(value or "0").replace("--", "0"))
    except ValueError:
        return 0


def _decimal(value: Any) -> Decimal:
    try:
        text = str(value or "0").replace("--", "0").replace(",", ".")
        return Decimal(text)
    except (InvalidOperation, ValueError):
        return Decimal("0")


def _decimal_text(value: Any) -> str | None:
    if value is None:
        return None
    return format(Decimal(value), "f")


def _success(response: HttpResponse) -> None:
    if not 200 <= response.status_code < 300:
        raise TransportError("Direct read returned non-success status", status_code=response.status_code)
    if isinstance(response.json_body, dict) and response.json_body.get("error"):
        raise TransportError("Direct read returned an application error", status_code=response.status_code)
