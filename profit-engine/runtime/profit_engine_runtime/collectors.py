from __future__ import annotations

import csv
import io
from dataclasses import dataclass
from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Any, Mapping, Sequence

from .clients import _select_counter
from .config import SiteConfig
from .contracts import JsonValue
from .ingestion import NormalizedBatch, SourceResult, fact_key
from .models import HttpRequest, HttpResponse
from .raw_store import DataState
from .transport import HttpTransport, TransportError


READ_ONLY = True


def _iso_capture(value: str | None) -> str:
    return value or datetime.now(timezone.utc).isoformat()


def _decimal(value: Any) -> Decimal:
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError) as error:
        raise ValueError("invalid decimal money value") from error


@dataclass
class DirectCollector:
    transport: HttpTransport | None
    config: SiteConfig
    token: str | None
    day: str
    fixture_payload: JsonValue | None = None
    captured_at: str | None = None
    max_report_polls: int = 3

    provider = "direct"
    source_object_type = "campaign-day"
    report_fields = ("Date", "CampaignId", "Impressions", "Clicks", "Cost")

    def request_identity(self) -> JsonValue:
        return {"provider": self.provider, "source": self.source_object_type,
            "day": self.day, "fields": list(self.report_fields),
            "include_vat": True, "include_discount": True, "money_in_micros": False}

    def campaign_request(self) -> HttpRequest:
        return HttpRequest("POST", f"{self.config.direct_endpoint}/campaigns", self._headers(),
            json_body={"method": "get", "params": {"SelectionCriteria": {},
                "FieldNames": ["Id", "Name", "State", "Status"]}})

    def report_request(self) -> HttpRequest:
        headers = self._headers() | {
            "processingMode": "auto", "returnMoneyInMicros": "false",
            "skipReportHeader": "true", "skipColumnHeader": "false",
            "skipReportSummary": "true",
        }
        body = {"params": {"SelectionCriteria": {"DateFrom": self.day, "DateTo": self.day},
            "FieldNames": list(self.report_fields), "ReportName": f"profit-engine-{self.day}",
            "ReportType": "CAMPAIGN_PERFORMANCE_REPORT", "DateRangeType": "CUSTOM_DATE",
            "Format": "TSV", "IncludeVAT": "YES", "IncludeDiscount": "YES"}}
        return HttpRequest("POST", "https://api-direct.yandex.com/json/v501/reports", headers, json_body=body)

    def read(self) -> SourceResult:
        if self.fixture_payload is not None:
            payload = self.fixture_payload
        else:
            if not self.token: raise ValueError("missing Direct credential")
            if self.transport is None: raise ValueError("missing Direct transport")
            campaign = self.transport.send(self.campaign_request())
            if campaign.status_code != 200: raise TransportError("Direct campaign read failed", status_code=campaign.status_code)
            report: HttpResponse | None = None
            for _ in range(self.max_report_polls):
                report = self.transport.send(self.report_request())
                if report.status_code == 200: break
                if report.status_code not in {201, 202}:
                    raise TransportError("Direct report failed", status_code=report.status_code)
            assert report is not None
            payload = {"campaigns": campaign.json_body, "report_status": report.status_code,
                "report_tsv": report.json_body if isinstance(report.json_body, str) else None,
                "report_attempts": report.attempts,
                "money_basis": {"currency": "RUB", "include_vat": True,
                    "include_discount": True, "money_in_micros": False}}
        return SourceResult(self.provider, self.source_object_type, _iso_capture(self.captured_at),
            f"{self.day}T00:00:00+00:00", f"{self.day}T23:59:59+00:00",
            self.request_identity(), payload, data_state=DataState.ESTIMATED)

    def validate(self, source: SourceResult) -> tuple[str, ...]:
        if not isinstance(source.payload, dict): return ("malformed_direct_response",)
        payload = source.payload
        if payload.get("report_status") in {201, 202}: return ("direct_report_not_ready_timeout",)
        if payload.get("report_status") != 200 or not isinstance(payload.get("report_tsv"), str):
            return ("malformed_direct_response",)
        basis = payload.get("money_basis")
        if basis != {"currency": "RUB", "include_vat": True, "include_discount": True, "money_in_micros": False}:
            return ("ambiguous_currency_or_money_basis",)
        try: parse_direct_tsv(payload["report_tsv"])
        except ValueError: return ("malformed_direct_response",)
        return ()

    def normalize(self, source: SourceResult, raw_snapshot_id: str) -> NormalizedBatch:
        holds = self.validate(source)
        payload = source.payload if isinstance(source.payload, dict) else {}
        campaigns_body = payload.get("campaigns", {})
        campaigns = campaigns_body.get("result", {}).get("Campaigns", []) if isinstance(campaigns_body, dict) else []
        campaign_facts = []
        for item in campaigns:
            identity = {"site_provider": self.provider, "campaign_ref": str(item.get("Id")), "day": self.day}
            campaign_facts.append({"idempotency_key": fact_key(identity), "provider": self.provider,
                "provider_entity_ref": str(item.get("Id")), "observed_at": source.captured_at,
                "state": {key.lower(): item.get(key) for key in ("Name", "State", "Status")},
                "raw_snapshot_id": raw_snapshot_id})
        traffic = []
        if not holds:
            for row in parse_direct_tsv(str(payload["report_tsv"])):
                identity = {"provider": self.provider, "date": row["Date"], "campaign_ref": row["CampaignId"]}
                traffic.append({"idempotency_key": fact_key(identity), "provider": self.provider,
                    "occurred_on": row["Date"], "dimensions": {"campaign_ref": row["CampaignId"]},
                    "impressions": int(row["Impressions"]), "clicks": int(row["Clicks"]),
                    "spend_amount": _decimal(row["Cost"]), "currency_code": "RUB",
                    "provenance": {"include_vat": True, "include_discount": True,
                        "money_in_micros": False, "data_state": source.data_state.value},
                    "raw_snapshot_id": raw_snapshot_id})
        return NormalizedBatch(tuple(campaign_facts), tuple(traffic), (), holds)

    def _headers(self) -> dict[str, str]:
        headers = {"Authorization": f"Bearer {self.token or ''}", "Accept-Language": "en"}
        if self.config.direct_client_login: headers["Client-Login"] = self.config.direct_client_login
        return headers


def parse_direct_tsv(text: str) -> list[dict[str, str]]:
    reader = csv.DictReader(io.StringIO(text), delimiter="\t")
    if tuple(reader.fieldnames or ()) != DirectCollector.report_fields:
        raise ValueError("unexpected Direct report columns")
    rows = []
    for row in reader:
        if not row["Date"] or not row["CampaignId"]: raise ValueError("missing Direct identity")
        int(row["Impressions"]); int(row["Clicks"]); _decimal(row["Cost"])
        rows.append(dict(row))
    return rows


@dataclass
class MetricaCollector:
    transport: HttpTransport | None
    config: SiteConfig
    token: str | None
    day: str
    counter_id: str | None = None
    dimensions: tuple[str, ...] = ("ym:s:date",)
    fixture_payload: JsonValue | None = None
    captured_at: str | None = None

    provider = "metrica"
    source_object_type = "daily-traffic-monetization"
    metrics = ("ym:s:visits", "ym:s:yanPartnerPrice", "ym:s:yanRequests", "ym:s:yanRenders", "ym:s:yanShows")
    allowed_dimensions = frozenset({"ym:s:date", "ym:s:lastTrafficSource", "ym:s:UTMSource", "ym:s:UTMCampaign"})

    def request_identity(self) -> JsonValue:
        return {"provider": self.provider, "source": self.source_object_type, "day": self.day,
            "dimensions": list(self.dimensions), "metrics": list(self.metrics)}

    def report_request(self, counter_id: str | None = None) -> HttpRequest:
        selected_counter = counter_id or self.counter_id
        if not selected_counter: raise ValueError("missing private Metrica counter mapping")
        return HttpRequest("GET", self.config.metrica_reports_endpoint,
            {"Authorization": f"OAuth {self.token or ''}", "Accept": "application/json"},
            query={"ids": selected_counter, "date1": self.day, "date2": self.day,
                "dimensions": ",".join(self.dimensions), "metrics": ",".join(self.metrics),
                "accuracy": "full", "limit": "100000"})

    def read(self) -> SourceResult:
        if self.fixture_payload is not None: payload = self.fixture_payload
        else:
            if not self.token: raise ValueError("missing Metrica credential")
            if self.transport is None: raise ValueError("missing Metrica transport")
            selected_counter = self.counter_id
            if not selected_counter:
                counters = self.transport.send(HttpRequest("GET",
                    f"{self.config.metrica_management_endpoint}/counters",
                    {"Authorization": f"OAuth {self.token}", "Accept": "application/json"}))
                if counters.status_code != 200:
                    raise TransportError("Metrica counter discovery failed", status_code=counters.status_code)
                selected = _select_counter(counters.json_body, self.config)
                if selected is None: raise ValueError("canonical-domain Metrica counter not visible")
                selected_counter = str(selected["id"])
            response = self.transport.send(self.report_request(selected_counter))
            if response.status_code != 200: raise TransportError("Metrica report failed", status_code=response.status_code)
            payload = response.json_body
        return SourceResult(self.provider, self.source_object_type, _iso_capture(self.captured_at),
            f"{self.day}T00:00:00+00:00", f"{self.day}T23:59:59+00:00",
            self.request_identity(), payload, data_state=DataState.ESTIMATED,
            completeness=bool(isinstance(payload, dict) and not payload.get("pagination_incomplete", False)))

    def validate(self, source: SourceResult) -> tuple[str, ...]:
        holds = []
        if not set(self.dimensions).issubset(self.allowed_dimensions): holds.append("invalid_metrica_dimensions")
        if not isinstance(source.payload, dict) or not isinstance(source.payload.get("data"), list):
            return tuple((*holds, "malformed_metrica_response"))
        query = source.payload.get("query", {})
        returned_metrics = _metric_names(query.get("metrics", self.metrics)) if isinstance(query, dict) else ()
        if "ym:s:visits" not in returned_metrics: holds.append("missing_source")
        if "ym:s:yanPartnerPrice" not in returned_metrics: holds.append("metrica_monetization_unavailable")
        if source.payload.get("currency") not in {"RUB"}: holds.append("ambiguous_currency_or_money_basis")
        return tuple(holds)

    def normalize(self, source: SourceResult, raw_snapshot_id: str) -> NormalizedBatch:
        holds = self.validate(source); payload = source.payload if isinstance(source.payload, dict) else {}
        query = payload.get("query", {}); metrics = _metric_names(query.get("metrics", self.metrics)) if isinstance(query, dict) else self.metrics
        traffic, money = [], []
        for row in payload.get("data", []):
            if not isinstance(row, dict) or not isinstance(row.get("metrics"), list): continue
            values = dict(zip(metrics, row["metrics"])); dims = row.get("dimensions", [])
            dimension_values = tuple(str(item.get("name", "")) for item in dims if isinstance(item, dict))
            occurred = dimension_values[0] if dimension_values else self.day
            identity = {"provider": self.provider, "date": occurred, "dimensions": dimension_values}
            if "ym:s:visits" in values:
                traffic.append({"idempotency_key": fact_key(identity | {"kind": "traffic"}),
                    "provider": self.provider, "occurred_on": occurred,
                    "dimensions": {"values": dimension_values}, "visits": int(values["ym:s:visits"]),
                    "raw_snapshot_id": raw_snapshot_id,
                    "provenance": _metrica_provenance(payload)})
            if "ym:s:yanPartnerPrice" in values and "ambiguous_currency_or_money_basis" not in holds:
                money.append({"idempotency_key": fact_key(identity | {"kind": "monetization"}),
                    "provider": "yan", "measurement_source": self.provider, "occurred_on": occurred,
                    "dimensions": {"values": dimension_values},
                    "revenue_amount": _decimal(values["ym:s:yanPartnerPrice"]),
                    "currency_code": payload["currency"], "data_state": source.data_state.value,
                    "delivery": {"requests": values.get("ym:s:yanRequests"),
                        "renders": values.get("ym:s:yanRenders"), "shows": values.get("ym:s:yanShows")},
                    "raw_snapshot_id": raw_snapshot_id, "provenance": _metrica_provenance(payload)})
        return NormalizedBatch((), tuple(traffic), tuple(money), holds)


def _metrica_provenance(payload: Mapping[str, Any]) -> dict[str, Any]:
    return {"sampled": payload.get("sampled"), "sample_size": payload.get("sample_size"),
        "sample_space": payload.get("sample_space"), "data_lag": payload.get("data_lag"),
        "contains_sensitive_data": payload.get("contains_sensitive_data")}


def _metric_names(value: Any) -> tuple[str, ...]:
    if isinstance(value, str):
        return tuple(item for item in value.split(",") if item)
    if isinstance(value, Sequence):
        return tuple(str(item) for item in value)
    return ()


@dataclass
class YanCollector:
    transport: HttpTransport | None
    config: SiteConfig
    token: str | None
    day: str
    revenue_field: str | None = None
    currency: str | None = None
    timezone_name: str | None = None
    vat_basis: str | None = None
    fixture_payload: JsonValue | None = None
    captured_at: str | None = None

    provider = "yan"
    source_object_type = "partner-daily-statistics"
    delivery_fields = ("shows", "hits_render", "hits")

    def request_identity(self) -> JsonValue:
        return {"provider": self.provider, "source": self.source_object_type, "day": self.day,
            "dimension_field": "date|day", "delivery_fields": list(self.delivery_fields),
            "configured_revenue_field": self.revenue_field}

    def tree_request(self) -> HttpRequest:
        return HttpRequest("GET", f"{self.config.yan_stats_endpoint}/tree.json",
            {"Authorization": f"OAuth {self.token or ''}", "Accept": "application/json"},
            query={"lang": "en", "stat_type": "main"})

    def report_request(self, validated_revenue_field: str | None) -> HttpRequest:
        fields = list(self.delivery_fields) + ([validated_revenue_field] if validated_revenue_field else [])
        query: dict[str, str | list[str]] = {"lang": "en", "stat_type": "main",
            "period": "custom", "date_from": self.day, "date_to": self.day,
            "dimension_field": "date|day", "field": fields}
        if self.config.yan_resource_id:
            query["filter"] = f'["page_id","=","{self.config.yan_resource_id}"]'
        return HttpRequest("GET", f"{self.config.yan_stats_endpoint}/get.json",
            {"Authorization": f"OAuth {self.token or ''}", "Accept": "application/json"}, query=query)

    def read(self) -> SourceResult:
        if self.fixture_payload is not None: payload = self.fixture_payload
        else:
            if not self.token: raise ValueError("missing YAN credential")
            if self.transport is None: raise ValueError("missing YAN transport")
            tree_response = self.transport.send(self.tree_request())
            if tree_response.status_code != 200: raise TransportError("YAN tree failed", status_code=tree_response.status_code)
            selected = select_yan_revenue_field(tree_response.json_body, self.revenue_field)
            report_response = self.transport.send(self.report_request(selected))
            if report_response.status_code != 200: raise TransportError("YAN report failed", status_code=report_response.status_code)
            payload = {"tree": tree_response.json_body, "report": report_response.json_body,
                "selected_revenue_field": selected, "currency": self.currency,
                "timezone": self.timezone_name, "vat_basis": self.vat_basis}
        return SourceResult(self.provider, self.source_object_type, _iso_capture(self.captured_at),
            f"{self.day}T00:00:00+00:00", f"{self.day}T23:59:59+00:00",
            self.request_identity(), payload, data_state=DataState.ESTIMATED,
            completeness=bool(isinstance(payload, dict) and not payload.get("pagination_incomplete", False)))

    def validate(self, source: SourceResult) -> tuple[str, ...]:
        if not isinstance(source.payload, dict): return ("malformed_yan_response",)
        payload = source.payload; selected = select_yan_revenue_field(payload.get("tree"), payload.get("selected_revenue_field") or self.revenue_field)
        holds = []
        if not selected: holds.append("yan_revenue_semantics_unavailable")
        if not payload.get("currency") or not payload.get("timezone") or not payload.get("vat_basis"):
            holds.append("ambiguous_currency_or_money_basis")
        report = payload.get("report")
        if not isinstance(report, dict) or not isinstance(_yan_rows(report), list): holds.append("malformed_yan_response")
        return tuple(holds)

    def normalize(self, source: SourceResult, raw_snapshot_id: str) -> NormalizedBatch:
        holds = self.validate(source); payload = source.payload if isinstance(source.payload, dict) else {}
        selected = select_yan_revenue_field(payload.get("tree"), payload.get("selected_revenue_field") or self.revenue_field)
        facts = []
        if selected and not holds:
            for row in _yan_rows(payload.get("report", {})):
                if selected not in row: continue
                occurred = str(row.get("date") or row.get("day") or self.day)
                identity = {"provider": self.provider, "date": occurred, "revenue_field": selected}
                facts.append({"idempotency_key": fact_key(identity), "provider": self.provider,
                    "measurement_source": "yan_statistics", "occurred_on": occurred,
                    "dimensions": {"dimension_field": "date|day"},
                    "revenue_amount": _decimal(row[selected]), "currency_code": payload["currency"],
                    "data_state": source.data_state.value,
                    "delivery": {field: row.get(field) for field in self.delivery_fields if field in row},
                    "provenance": {"revenue_field": selected, "timezone": payload["timezone"],
                        "vat_basis": payload["vat_basis"], "tree_validated": True},
                    "raw_snapshot_id": raw_snapshot_id})
        return NormalizedBatch((), (), tuple(facts), holds)


def select_yan_revenue_field(tree: Any, configured: str | None = None) -> str | None:
    fields = _tree_fields(tree)
    if configured:
        return configured if configured in fields else None
    candidates = [name for name, item in fields.items() if item.get("semantic") == "revenue"]
    return candidates[0] if len(candidates) == 1 else None


def _tree_fields(tree: Any) -> dict[str, Mapping[str, Any]]:
    if not isinstance(tree, dict): return {}
    raw = tree.get("fields")
    if not raw:
        data = tree.get("data", {})
        raw = data.get("fields", []) if isinstance(data, dict) else []
    return {str(item.get("name")): item for item in raw if isinstance(item, dict) and item.get("name")}


def _yan_rows(report: Any) -> list[Mapping[str, Any]]:
    if not isinstance(report, dict): return []
    data = report.get("data", report)
    if isinstance(data, dict):
        rows = data.get("points", data.get("rows", []))
        return rows if isinstance(rows, list) else []
    return []
