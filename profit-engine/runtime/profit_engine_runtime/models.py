from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Mapping


class DoctorStatus(StrEnum):
    PASS = "PASS"
    BLOCKED_MISSING_CREDENTIAL = "BLOCKED_MISSING_CREDENTIAL"
    BLOCKED_ACCESS = "BLOCKED_ACCESS"
    PROVIDER_ERROR = "PROVIDER_ERROR"
    NOT_ATTEMPTED = "NOT_ATTEMPTED"


@dataclass(frozen=True)
class HttpRequest:
    method: str
    url: str
    headers: Mapping[str, str] = field(default_factory=dict)
    query: Mapping[str, str | list[str]] = field(default_factory=dict)
    json_body: Mapping[str, Any] | None = None
    timeout_seconds: float = 10.0


@dataclass(frozen=True)
class HttpResponse:
    status_code: int
    headers: Mapping[str, str]
    json_body: Any = None
    request_id: str | None = None
    attempts: int = 1


@dataclass(frozen=True)
class DiagnosticResult:
    provider: str
    status: DoctorStatus
    checks: tuple[str, ...] = ()
    http_status: int | None = None
    request_id: str | None = None
    provider_units: str | None = None
    detail: str | None = None

    def public_dict(self) -> dict[str, Any]:
        return {
            "provider": self.provider,
            "status": self.status.value,
            "checks": list(self.checks),
            "http_status": self.http_status,
            "request_id": self.request_id,
            "provider_units": self.provider_units,
            "detail": self.detail,
        }
