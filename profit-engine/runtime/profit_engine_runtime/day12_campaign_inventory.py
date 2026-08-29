"""Exact read-only Yandex Direct campaign inventory for Day-12 candidate evidence.

Inventory never selects a commercial winner and never grants write authority. It
only establishes exact campaign IDs and current provider states for the already
bound managed advertiser.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from typing import Any, Mapping

from .config import SiteConfig
from .models import HttpRequest, HttpResponse
from .transport import HttpTransport, TransportError


READ_ONLY = True
MAX_CAMPAIGNS = 10_000


@dataclass(frozen=True)
class CampaignInventoryItem:
    campaign_id: str
    name: str
    campaign_type: str
    normalized_state: str
    provider_state: str
    status: str


@dataclass(frozen=True)
class CampaignInventory:
    inventory_version: str
    site_id: str
    total_campaigns: int
    items: tuple[CampaignInventoryItem, ...]
    page_count: int
    request_ids: tuple[str, ...]
    units: tuple[str, ...]
    provider_write_allowed: bool
    candidate_selected: bool
    inventory_digest: str

    @property
    def integrity_valid(self) -> bool:
        value = asdict(self)
        recorded = value.pop("inventory_digest")
        return recorded == _digest(value)


class YandexDirectCampaignInventory:
    READ_ONLY = True

    def __init__(self, *, transport: HttpTransport, config: SiteConfig):
        self.transport = transport
        self.config = config

    def read_all(
        self,
        *,
        token: str,
        page_size: int = 500,
        max_pages: int = 20,
    ) -> CampaignInventory:
        if not token:
            raise ValueError("Direct OAuth token required")
        if not self.config.direct_client_login:
            raise ValueError("exact managed Direct target login required")
        if self.config.direct_operator_login and (
            self.config.direct_operator_login.casefold() == self.config.direct_client_login.casefold()
        ):
            raise ValueError("Direct operator and managed target must differ")
        if page_size < 1 or page_size > 10_000:
            raise ValueError("campaign inventory page_size must be 1..10000")
        if max_pages < 1 or max_pages > 100:
            raise ValueError("campaign inventory max_pages must be 1..100")

        offset = 0
        items: list[CampaignInventoryItem] = []
        seen: set[str] = set()
        request_ids: list[str] = []
        units: list[str] = []
        page_count = 0

        while page_count < max_pages:
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
                        "SelectionCriteria": {},
                        "FieldNames": ["Id", "Name", "Type", "State", "Status"],
                        "Page": {"Limit": page_size, "Offset": offset},
                    },
                },
            ))
            page_count += 1
            body = _success_body(response)
            if response.request_id:
                request_ids.append(response.request_id)
            unit_value = _header(response.headers, "Units")
            if unit_value:
                units.append(unit_value)

            campaigns = body.get("result", {}).get("Campaigns", [])
            if not isinstance(campaigns, list):
                raise ValueError("Direct campaign inventory returned malformed Campaigns")
            for raw in campaigns:
                item = _inventory_item(raw)
                if item.campaign_id in seen:
                    raise ValueError("Direct campaign inventory returned duplicate campaign id")
                seen.add(item.campaign_id)
                items.append(item)
                if len(items) > MAX_CAMPAIGNS:
                    raise ValueError("Direct campaign inventory exceeds Day-12 bounded scope")

            result = body.get("result", {})
            limited_by = result.get("LimitedBy") if isinstance(result, Mapping) else None
            if limited_by is None:
                break
            try:
                next_offset = int(limited_by)
            except (TypeError, ValueError) as exc:
                raise ValueError("Direct campaign inventory LimitedBy is invalid") from exc
            if next_offset <= offset:
                raise ValueError("Direct campaign inventory pagination did not advance")
            offset = next_offset
        else:
            raise ValueError("Direct campaign inventory exceeded bounded page count")

        ordered = tuple(sorted(items, key=lambda item: int(item.campaign_id)))
        core = {
            "inventory_version": "1.0",
            "site_id": self.config.site_id,
            "total_campaigns": len(ordered),
            "items": ordered,
            "page_count": page_count,
            "request_ids": tuple(request_ids),
            "units": tuple(units),
            "provider_write_allowed": False,
            "candidate_selected": False,
        }
        return CampaignInventory(**core, inventory_digest=_digest(core))


def _success_body(response: HttpResponse) -> Mapping[str, Any]:
    if not 200 <= response.status_code < 300:
        raise TransportError("Direct campaign inventory returned non-success status", status_code=response.status_code)
    if not isinstance(response.json_body, Mapping):
        raise ValueError("Direct campaign inventory response is not JSON object")
    if response.json_body.get("error"):
        raise TransportError("Direct campaign inventory returned top-level error", status_code=response.status_code)
    return response.json_body


def _inventory_item(value: Any) -> CampaignInventoryItem:
    if not isinstance(value, Mapping):
        raise ValueError("Direct campaign inventory item is malformed")
    try:
        provider_id = int(value.get("Id"))
    except (TypeError, ValueError) as exc:
        raise ValueError("Direct campaign inventory item has invalid Id") from exc
    if provider_id <= 0:
        raise ValueError("Direct campaign inventory campaign Id must be positive")
    provider_state = str(value.get("State", "UNKNOWN")).upper()
    return CampaignInventoryItem(
        campaign_id=str(provider_id),
        name=str(value.get("Name", "")),
        campaign_type=str(value.get("Type", "UNKNOWN")),
        normalized_state="ACTIVE" if provider_state == "ON" else provider_state,
        provider_state=provider_state,
        status=str(value.get("Status", "UNKNOWN")),
    )


def _header(headers: Mapping[str, str], name: str) -> str | None:
    return next((value for key, value in headers.items() if key.lower() == name.lower()), None)


def _digest(value: object) -> str:
    return sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    ).hexdigest()
