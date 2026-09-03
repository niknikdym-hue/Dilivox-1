"""Read-only money preflight for exact Dilivox Direct campaign evaluation.

The preflight joins three observations for one completed date window:
- exact Yandex Direct campaign spend;
- Metrica YAN revenue attributed to the exact Direct campaign;
- YAN Statistics domain revenue as a control total.

No function in this module grants provider write authority.
"""
from __future__ import annotations

import csv
import io
from dataclasses import asdict, dataclass
from datetime import date
from decimal import Decimal, InvalidOperation
from enum import StrEnum
from hashlib import sha256
import json
from typing import Any, Mapping

from .config import SiteConfig
from .models import HttpRequest, HttpResponse
from .transport import HttpTransport, TransportError


DIRECT_REPORTS_ENDPOINT = "https://api.direct.yandex.com/json/v501/reports"
METRICA_CAMPAIGN_DIMENSION = "ym:s:last_yandex_direct_clickDirectClickOrder"
METRICA_DIMENSIONS = ("ym:s:date", METRICA_CAMPAIGN_DIMENSION)
METRICA_METRICS = (
    "ym:s:yanPartnerPrice",
    "ym:s:yanRequests",
    "ym:s:yanRenders",
    "ym:s:yanShows",
)
DIRECT_FIELDS = ("Date", "CampaignId", "Clicks", "Cost")
YAN_FIELDS = ("partner_wo_nds", "hits", "hits_render", "shows")
RECONCILIATION_TOLERANCE = Decimal("0.05")
MONEY_CURRENCY = "RUB"


class MoneyPreflightState(StrEnum):
    READY_FOR_CANDIDATE_EVALUATION = "READY_FOR_CANDIDATE_EVALUATION"
    NO_DIRECT_SPEND = "NO_DIRECT_SPEND"
    HOLD_DATA_QUALITY = "HOLD_DATA_QUALITY"


@dataclass(frozen=True)
class DirectSpendObservation:
    campaign_id: str
    date_from: str
    date_to: str
    spend_rub: Decimal
    clicks: int
    report_rows: int
    request_id: str | None
    units: str | None


@dataclass(frozen=True)
class MetricaRevenueObservation:
    campaign_id: str
    date_from: str
    date_to: str
    attributed_yan_revenue_rub: Decimal
    yan_requests: Decimal
    yan_renders: Decimal
    yan_shows: Decimal
    matched_rows: int
    sampled: bool
    contains_sensitive_data: bool
    currency: str | None


@dataclass(frozen=True)
class YanControlObservation:
    domain: str
    date_from: str
    date_to: str
    revenue_rub: Decimal
    hits: Decimal
    hits_render: Decimal
    shows: Decimal
    points: int
    currency: str


@dataclass(frozen=True)
class Day12MoneyPreflight:
    preflight_version: str
    site_id: str
    campaign_id: str
    date_from: str
    date_to: str
    state: MoneyPreflightState
    holds: tuple[str, ...]
    direct_spend_rub: Decimal
    metrica_attributed_yan_revenue_rub: Decimal
    yan_control_revenue_rub: Decimal
    k5_observed: Decimal | None
    attributed_share_of_yan_control: Decimal | None
    direct_request_id: str | None
    direct_units: str | None
    provider_write_allowed: bool
    preflight_digest: str

    @property
    def integrity_valid(self) -> bool:
        value = asdict(self)
        recorded = value.pop("preflight_digest")
        return recorded == _digest(value)


class Day12MoneyProbe:
    READ_ONLY = True

    def __init__(self, *, transport: HttpTransport, config: SiteConfig):
        self.transport = transport
        self.config = config

    def run(
        self,
        *,
        campaign_id: str,
        date_from: str,
        date_to: str,
        direct_token: str,
        metrica_token: str,
        yan_token: str,
        max_report_polls: int = 3,
    ) -> Day12MoneyPreflight:
        provider_id = _campaign_id(campaign_id)
        _date_window(date_from, date_to)
        if not self.config.direct_client_login:
            raise ValueError("exact managed Direct target login required")
        if not self.config.metrica_counter_id:
            raise ValueError("exact Metrica counter id required")
        if not all((direct_token, metrica_token, yan_token)):
            raise ValueError("all three read credentials are required")

        direct = self.read_direct_spend(
            campaign_id=str(provider_id),
            date_from=date_from,
            date_to=date_to,
            token=direct_token,
            max_report_polls=max_report_polls,
        )
        metrica = self.read_metrica_attributed_revenue(
            campaign_id=str(provider_id),
            date_from=date_from,
            date_to=date_to,
            token=metrica_token,
        )
        yan = self.read_yan_control(date_from=date_from, date_to=date_to, token=yan_token)
        return build_money_preflight(site_id=self.config.site_id, direct=direct, metrica=metrica, yan=yan)

    def read_direct_spend(
        self,
        *,
        campaign_id: str,
        date_from: str,
        date_to: str,
        token: str,
        max_report_polls: int = 3,
    ) -> DirectSpendObservation:
        provider_id = _campaign_id(campaign_id)
        _date_window(date_from, date_to)
        if max_report_polls < 1 or max_report_polls > 5:
            raise ValueError("Direct report polling must be bounded to 1..5 read attempts")

        response: HttpResponse | None = None
        for _ in range(max_report_polls):
            response = self.transport.send(HttpRequest(
                "POST",
                DIRECT_REPORTS_ENDPOINT,
                {
                    "Authorization": f"Bearer {token}",
                    "Client-Login": self.config.direct_client_login or "",
                    "Accept-Language": "en",
                    "processingMode": "auto",
                    "returnMoneyInMicros": "false",
                    "skipReportHeader": "true",
                    "skipColumnHeader": "false",
                    "skipReportSummary": "true",
                    "Content-Type": "application/json; charset=utf-8",
                },
                json_body={
                    "params": {
                        "SelectionCriteria": {
                            "DateFrom": date_from,
                            "DateTo": date_to,
                            "Filter": [{"Field": "CampaignId", "Operator": "IN", "Values": [provider_id]}],
                        },
                        "FieldNames": list(DIRECT_FIELDS),
                        "ReportName": f"profit-engine-day12-{provider_id}-{date_from}-{date_to}",
                        "ReportType": "CAMPAIGN_PERFORMANCE_REPORT",
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
                raise TransportError("Direct spend report failed", status_code=response.status_code)

        assert response is not None
        if response.status_code != 200 or not isinstance(response.json_body, str):
            raise TransportError("Direct spend report did not become ready", status_code=response.status_code)

        rows = _direct_rows(response.json_body)
        spend = Decimal("0")
        clicks = 0
        for row in rows:
            if row["CampaignId"] != str(provider_id):
                raise ValueError("Direct report returned an unexpected campaign id")
            spend += _money(row["Cost"])
            clicks += int(row["Clicks"])
        return DirectSpendObservation(
            campaign_id=str(provider_id),
            date_from=date_from,
            date_to=date_to,
            spend_rub=spend,
            clicks=clicks,
            report_rows=len(rows),
            request_id=response.request_id,
            units=_header(response.headers, "Units"),
        )

    def read_metrica_attributed_revenue(
        self,
        *,
        campaign_id: str,
        date_from: str,
        date_to: str,
        token: str,
    ) -> MetricaRevenueObservation:
        provider_id = str(_campaign_id(campaign_id))
        _date_window(date_from, date_to)
        response = self.transport.send(HttpRequest(
            "GET",
            self.config.metrica_reports_endpoint,
            {"Authorization": f"OAuth {token}", "Accept": "application/json"},
            query={
                "ids": str(self.config.metrica_counter_id),
                "date1": date_from,
                "date2": date_to,
                "dimensions": ",".join(METRICA_DIMENSIONS),
                "metrics": ",".join(METRICA_METRICS),
                "currency": MONEY_CURRENCY,
                "accuracy": "full",
                "limit": "100000",
            },
        ))
        if response.status_code != 200 or not isinstance(response.json_body, dict):
            raise TransportError("Metrica campaign revenue report failed", status_code=response.status_code)
        body = response.json_body
        data = body.get("data")
        if not isinstance(data, list):
            raise ValueError("Metrica report data is malformed")

        revenue = Decimal("0")
        requests = Decimal("0")
        renders = Decimal("0")
        shows = Decimal("0")
        matched = 0
        for row in data:
            if not isinstance(row, Mapping):
                continue
            dimensions = row.get("dimensions")
            metrics = row.get("metrics")
            if not isinstance(dimensions, list) or len(dimensions) < 2 or not isinstance(metrics, list):
                continue
            if _dimension_value(dimensions[1]) != provider_id:
                continue
            if len(metrics) != len(METRICA_METRICS):
                raise ValueError("Metrica metrics shape mismatch")
            values = [_decimal_metric(value) for value in metrics]
            revenue += values[0]
            requests += values[1]
            renders += values[2]
            shows += values[3]
            matched += 1

        return MetricaRevenueObservation(
            campaign_id=provider_id,
            date_from=date_from,
            date_to=date_to,
            attributed_yan_revenue_rub=revenue,
            yan_requests=requests,
            yan_renders=renders,
            yan_shows=shows,
            matched_rows=matched,
            sampled=bool(body.get("sampled", False)),
            contains_sensitive_data=bool(body.get("contains_sensitive_data", False)),
            currency=MONEY_CURRENCY,
        )

    def read_yan_control(self, *, date_from: str, date_to: str, token: str) -> YanControlObservation:
        _date_window(date_from, date_to)
        response = self.transport.send(HttpRequest(
            "GET",
            f"{self.config.yan_stats_endpoint}/get.json",
            {"Authorization": f"OAuth {token}", "Accept": "application/json"},
            query={
                "lang": "en",
                "stat_type": "main",
                "period": [date_from, date_to],
                "dimension_field": "date|day",
                "entity_field": "domain",
                "field": list(YAN_FIELDS),
                "filter": f'["domain","=","{self.config.canonical_domain}"]',
                "currency": MONEY_CURRENCY,
                "timezone": "Europe/Moscow",
            },
        ))
        if response.status_code != 200 or not isinstance(response.json_body, dict):
            raise TransportError("YAN control report failed", status_code=response.status_code)
        body = response.json_body
        if body.get("result") != "ok":
            raise TransportError("YAN control report returned application error", status_code=response.status_code)
        data = body.get("data")
        if not isinstance(data, Mapping):
            raise ValueError("YAN control report data is malformed")
        points = data.get("points")
        if not isinstance(points, list):
            raise ValueError("YAN control report points are malformed")

        revenue = Decimal("0")
        hits = Decimal("0")
        renders = Decimal("0")
        shows = Decimal("0")
        exact_points = 0
        expected_domain = self.config.canonical_domain.casefold().removeprefix("www.").rstrip("/")
        for point in points:
            if not isinstance(point, Mapping):
                continue
            dimensions = point.get("dimensions") or {}
            if not isinstance(dimensions, Mapping):
                continue
            domain = str(dimensions.get("domain", "")).casefold().removeprefix("www.").rstrip("/")
            if domain != expected_domain:
                raise ValueError("YAN control report returned unexpected domain")
            measures = point.get("measures")
            if not isinstance(measures, list):
                continue
            exact_points += 1
            for measure in measures:
                if not isinstance(measure, Mapping):
                    continue
                revenue += _decimal_metric(measure.get("partner_wo_nds", 0))
                hits += _decimal_metric(measure.get("hits", 0))
                renders += _decimal_metric(measure.get("hits_render", 0))
                shows += _decimal_metric(measure.get("shows", 0))

        return YanControlObservation(
            domain=self.config.canonical_domain,
            date_from=date_from,
            date_to=date_to,
            revenue_rub=revenue,
            hits=hits,
            hits_render=renders,
            shows=shows,
            points=exact_points,
            currency=MONEY_CURRENCY,
        )


def build_money_preflight(
    *,
    site_id: str,
    direct: DirectSpendObservation,
    metrica: MetricaRevenueObservation,
    yan: YanControlObservation,
) -> Day12MoneyPreflight:
    if not site_id:
        raise ValueError("site_id required")
    identity = (direct.campaign_id, direct.date_from, direct.date_to)
    if (metrica.campaign_id, metrica.date_from, metrica.date_to) != identity:
        raise ValueError("Direct/Metrica money window identity mismatch")
    if (yan.date_from, yan.date_to) != identity[1:]:
        raise ValueError("YAN control window mismatch")

    holds: list[str] = []
    if direct.spend_rub < 0 or metrica.attributed_yan_revenue_rub < 0 or yan.revenue_rub < 0:
        holds.append("negative_money_value")
    if metrica.currency != MONEY_CURRENCY or yan.currency != MONEY_CURRENCY:
        holds.append("ambiguous_currency_or_money_basis")
    if metrica.sampled:
        holds.append("metrica_sampled")
    if metrica.contains_sensitive_data:
        holds.append("metrica_sensitive_data_restriction")
    if metrica.attributed_yan_revenue_rub > 0 and yan.revenue_rub <= 0:
        holds.append("metrica_revenue_without_yan_control_revenue")
    if yan.revenue_rub > 0:
        excess = metrica.attributed_yan_revenue_rub - yan.revenue_rub
        if excess > yan.revenue_rub * RECONCILIATION_TOLERANCE:
            holds.append("metrica_attributed_revenue_exceeds_yan_control_total")

    k5 = metrica.attributed_yan_revenue_rub / direct.spend_rub if direct.spend_rub > 0 else None
    share = metrica.attributed_yan_revenue_rub / yan.revenue_rub if yan.revenue_rub > 0 else None

    if holds:
        state = MoneyPreflightState.HOLD_DATA_QUALITY
    elif direct.spend_rub == 0:
        state = MoneyPreflightState.NO_DIRECT_SPEND
    else:
        state = MoneyPreflightState.READY_FOR_CANDIDATE_EVALUATION

    core = {
        "preflight_version": "1.1",
        "site_id": site_id,
        "campaign_id": direct.campaign_id,
        "date_from": direct.date_from,
        "date_to": direct.date_to,
        "state": state,
        "holds": tuple(dict.fromkeys(holds)),
        "direct_spend_rub": direct.spend_rub,
        "metrica_attributed_yan_revenue_rub": metrica.attributed_yan_revenue_rub,
        "yan_control_revenue_rub": yan.revenue_rub,
        "k5_observed": k5,
        "attributed_share_of_yan_control": share,
        "direct_request_id": direct.request_id,
        "direct_units": direct.units,
        "provider_write_allowed": False,
    }
    return Day12MoneyPreflight(**core, preflight_digest=_digest(core))


def _direct_rows(text: str) -> list[dict[str, str]]:
    reader = csv.DictReader(io.StringIO(text), delimiter="\t")
    if tuple(reader.fieldnames or ()) != DIRECT_FIELDS:
        raise ValueError("unexpected Direct spend report columns")
    rows: list[dict[str, str]] = []
    for row in reader:
        if not row.get("Date") or not row.get("CampaignId"):
            raise ValueError("Direct spend row missing identity")
        int(row["Clicks"])
        _money(row["Cost"])
        rows.append(dict(row))
    return rows


def _money(value: Any) -> Decimal:
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError("invalid Direct money value") from exc


def _decimal_metric(value: Any) -> Decimal:
    if value is None:
        return Decimal("0")
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError("invalid provider metric value") from exc


def _dimension_value(value: Any) -> str:
    if isinstance(value, Mapping):
        if value.get("id") is not None:
            return str(value["id"])
        if value.get("name") is not None:
            return str(value["name"])
    return str(value) if value is not None else ""


def _campaign_id(value: str) -> int:
    try:
        result = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("campaign id must be an integer Direct id") from exc
    if result <= 0:
        raise ValueError("campaign id must be positive")
    return result


def _date_window(date_from: str, date_to: str) -> None:
    try:
        start = date.fromisoformat(date_from)
        end = date.fromisoformat(date_to)
    except ValueError as exc:
        raise ValueError("money preflight dates must be YYYY-MM-DD") from exc
    if start > end:
        raise ValueError("money preflight start date must not be after end date")


def _header(headers: Mapping[str, str], name: str) -> str | None:
    return next((value for key, value in headers.items() if key.lower() == name.lower()), None)


def _digest(value: object) -> str:
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")).hexdigest()
