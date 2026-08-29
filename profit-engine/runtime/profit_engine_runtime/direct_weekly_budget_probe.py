"""Read-only exact Direct campaign probe for current WeeklySpendLimit ownership."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from .config import SiteConfig
from .direct_weekly_budget import WeeklyBudgetInspection, inspect_weekly_budget
from .models import HttpRequest, HttpResponse
from .transport import HttpTransport, TransportError


READ_ONLY = True


@dataclass(frozen=True)
class WeeklyBudgetProbeResult:
    campaign_id: str
    campaign_type: str
    state: str
    status: str
    inspection: WeeklyBudgetInspection
    request_id: str | None
    units: str | None
    provider_write_allowed: bool = False


class YandexDirectWeeklyBudgetProbe:
    READ_ONLY = True

    def __init__(self, *, transport: HttpTransport, config: SiteConfig):
        self.transport = transport
        self.config = config

    def read_exact(self, *, campaign_id: str, token: str) -> WeeklyBudgetProbeResult:
        if not token:
            raise ValueError("Direct OAuth token required")
        if not self.config.direct_client_login:
            raise ValueError("exact managed Direct target login required")
        provider_id = _provider_id(campaign_id)
        response = self.transport.send(HttpRequest(
            "POST",
            f"{self.config.direct_endpoint}/campaigns",
            {
                "Authorization": f"Bearer {token}",
                "Client-Login": self.config.direct_client_login,
                "Accept-Language": "en",
                "Content-Type": "application/json; charset=utf-8",
            },
            json_body={
                "method": "get",
                "params": {
                    "SelectionCriteria": {"Ids": [provider_id]},
                    "FieldNames": ["Id", "Type", "State", "Status"],
                    "TextCampaignFieldNames": [
                        "BiddingStrategy", "PackageBiddingStrategy", "WeeklyBudgetRollover"
                    ],
                    "MobileAppCampaignFieldNames": [
                        "BiddingStrategy", "PackageBiddingStrategy", "WeeklyBudgetRollover"
                    ],
                    "CpmBannerCampaignFieldNames": ["BiddingStrategy"],
                    "UnifiedCampaignFieldNames": [
                        "BiddingStrategy", "PackageBiddingStrategy", "WeeklyBudgetRollover"
                    ],
                    "Page": {"Limit": 1},
                },
            },
        ))
        item = _exact_campaign(response, provider_id)
        return WeeklyBudgetProbeResult(
            campaign_id=str(provider_id),
            campaign_type=str(item.get("Type", "UNKNOWN")),
            state=str(item.get("State", "UNKNOWN")),
            status=str(item.get("Status", "UNKNOWN")),
            inspection=inspect_weekly_budget(item),
            request_id=response.request_id,
            units=_header(response.headers, "Units"),
        )


def _provider_id(value: str) -> int:
    try:
        result = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("campaign id must be an integer Direct id") from exc
    if result <= 0:
        raise ValueError("campaign id must be positive")
    return result


def _exact_campaign(response: HttpResponse, provider_id: int) -> Mapping[str, Any]:
    if not 200 <= response.status_code < 300:
        raise TransportError("Direct weekly-budget probe returned non-success status", status_code=response.status_code)
    body = response.json_body if isinstance(response.json_body, dict) else {}
    if body.get("error"):
        raise TransportError("Direct weekly-budget probe returned top-level error", status_code=response.status_code)
    campaigns = body.get("result", {}).get("Campaigns", [])
    exact = next((item for item in campaigns if item.get("Id") == provider_id), None)
    if exact is None:
        raise TransportError("Direct weekly-budget probe did not return exact campaign")
    return exact


def _header(headers: Mapping[str, str], name: str) -> str | None:
    return next((value for key, value in headers.items() if key.lower() == name.lower()), None)
