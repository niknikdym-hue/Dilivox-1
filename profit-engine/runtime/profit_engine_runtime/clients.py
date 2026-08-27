from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from .config import SiteConfig
from .models import DiagnosticResult, DoctorStatus, HttpRequest, HttpResponse
from .transport import HttpTransport, TransportError


READ_ONLY = True


class ProviderReadClient(ABC):
    READ_ONLY = True

    def __init__(self, transport: HttpTransport, config: SiteConfig):
        self.transport = transport
        self.config = config

    @abstractmethod
    def diagnose(self, token: str | None) -> DiagnosticResult: ...

    @staticmethod
    def _error(provider: str, exc: TransportError, checks: tuple[str, ...]) -> DiagnosticResult:
        status = DoctorStatus.BLOCKED_ACCESS if exc.status_code in {401, 403} else DoctorStatus.PROVIDER_ERROR
        return DiagnosticResult(
            provider=provider,
            status=status,
            checks=checks,
            http_status=exc.status_code,
            detail=str(exc),
        )


class YandexDirectReadClient(ProviderReadClient):
    def diagnose(self, token: str | None) -> DiagnosticResult:
        provider = "direct"
        if not token:
            return DiagnosticResult(provider, DoctorStatus.BLOCKED_MISSING_CREDENTIAL, detail="missing shared Yandex OAuth read token")
        headers = {"Authorization": f"Bearer {token}", "Accept-Language": "en"}
        if self.config.direct_client_login:
            headers["Client-Login"] = self.config.direct_client_login
        checks: list[str] = []
        try:
            client = self.transport.send(HttpRequest(
                "POST", f"{self.config.direct_endpoint}/clients", headers,
                json_body={"method": "get", "params": {"FieldNames": ["ClientId", "Login", "Type"]}},
            ))
            _require_success(client)
            checks.append("clients.get")
            campaigns = self.transport.send(HttpRequest(
                "POST", f"{self.config.direct_endpoint}/campaigns", headers,
                json_body={"method": "get", "params": {"SelectionCriteria": {}, "FieldNames": ["Id", "Name", "State", "Status"], "Page": {"Limit": 1}}},
            ))
            _require_success(campaigns)
            checks.append("campaigns.get(limit=1)")
            units = _header(campaigns, "Units")
            return DiagnosticResult(provider, DoctorStatus.PASS, tuple(checks), campaigns.status_code, campaigns.request_id, units)
        except TransportError as exc:
            return self._error(provider, exc, tuple(checks))


class YandexMetricaReadClient(ProviderReadClient):
    def diagnose(self, token: str | None) -> DiagnosticResult:
        provider = "metrica"
        if not token:
            return DiagnosticResult(provider, DoctorStatus.BLOCKED_MISSING_CREDENTIAL, detail="missing shared Yandex OAuth read token")
        headers = {"Authorization": f"OAuth {token}", "Accept": "application/json"}
        checks: list[str] = []
        try:
            counters = self.transport.send(HttpRequest("GET", f"{self.config.metrica_management_endpoint}/counters", headers))
            _require_success(counters)
            checks.append("counters.list")
            counter = _select_counter(counters.json_body, self.config)
            if counter is None:
                return DiagnosticResult(provider, DoctorStatus.BLOCKED_ACCESS, tuple(checks), counters.status_code, counters.request_id, detail="Dilivox counter not visible or not privately mapped")
            counter_id = str(counter.get("id"))
            permission = counter.get("permission", "unknown")
            checks.append(f"counter.permission={permission}")
            report = self.transport.send(HttpRequest(
                "GET", self.config.metrica_reports_endpoint, headers,
                query={"ids": counter_id, "metrics": "ym:s:visits,ym:s:yanPartnerPrice", "date1": "yesterday", "date2": "yesterday", "limit": "1"},
            ))
            _require_success(report)
            checks.append("yan_monetization.report_probe")
            return DiagnosticResult(provider, DoctorStatus.PASS, tuple(checks), report.status_code, report.request_id)
        except TransportError as exc:
            return self._error(provider, exc, tuple(checks))


class YanPartnerStatsReadClient(ProviderReadClient):
    def diagnose(self, token: str | None) -> DiagnosticResult:
        provider = "yan_statistics"
        if not token:
            return DiagnosticResult(provider, DoctorStatus.BLOCKED_MISSING_CREDENTIAL, detail="missing YAN Statistics API OAuth token")
        headers = {"Authorization": f"OAuth {token}", "Accept": "application/json"}
        checks: list[str] = []
        try:
            tree = self.transport.send(HttpRequest(
                "GET", f"{self.config.yan_stats_endpoint}/tree.json", headers,
                query={"lang": "en", "stat_type": "main"},
            ))
            _require_success(tree)
            checks.append("statistics.tree")
            query: dict[str, str | list[str]] = {
                "lang": "en", "stat_type": "main", "period": "yesterday",
                "dimension_field": "date|day", "entity_field": "page_id",
                "field": ["shows", "hits_render"], "limits": "1",
            }
            if self.config.yan_resource_id:
                query["filter"] = f'["page_id","=","{self.config.yan_resource_id}"]'
            report = self.transport.send(HttpRequest(
                "GET", f"{self.config.yan_stats_endpoint}/get.json", headers, query=query,
            ))
            _require_success(report)
            checks.append("statistics.report(yesterday,limit=1)")
            return DiagnosticResult(provider, DoctorStatus.PASS, tuple(checks), report.status_code, report.request_id)
        except TransportError as exc:
            return self._error(provider, exc, tuple(checks))


def _select_counter(body: Any, config: SiteConfig) -> dict[str, Any] | None:
    counters = body.get("counters", []) if isinstance(body, dict) else []
    if config.metrica_counter_id:
        return next((item for item in counters if str(item.get("id")) == config.metrica_counter_id), None)
    domain = config.canonical_domain.lower().removeprefix("www.")
    for item in counters:
        sites = [str(item.get("site", ""))]
        site2 = item.get("site2") or {}
        sites.extend([str(site2.get("site", "")), str(site2.get("domain", ""))])
        if any(domain == candidate.lower().removeprefix("www.").rstrip("/") for candidate in sites):
            return item
    return None


def _require_success(response: HttpResponse) -> None:
    if not 200 <= response.status_code < 300:
        raise TransportError("provider returned non-success status", status_code=response.status_code)
    if isinstance(response.json_body, dict) and (response.json_body.get("error") or response.json_body.get("result") == "error"):
        raise TransportError("provider returned an application error", status_code=response.status_code)


def _header(response: HttpResponse, name: str) -> str | None:
    return next((value for key, value in response.headers.items() if key.lower() == name.lower()), None)
