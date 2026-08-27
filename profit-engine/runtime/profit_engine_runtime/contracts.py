from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import Any, Mapping, Protocol, Sequence

JsonValue = None | bool | int | float | str | list["JsonValue"] | dict[str, "JsonValue"]

class ReadinessStatus(StrEnum):
    READY = "READY"
    NOT_READY = "NOT_READY"
    DEGRADED = "DEGRADED"

@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency_code: str
    def __post_init__(self) -> None:
        if not isinstance(self.amount, Decimal):
            raise TypeError("money amount must be decimal.Decimal")
        if len(self.currency_code) != 3:
            raise ValueError("currency_code must be ISO-4217 shaped")

@dataclass(frozen=True)
class HealthReport:
    component: str
    status: ReadinessStatus
    checked_at: datetime
    checks: tuple[str, ...] = ()

@dataclass(frozen=True)
class AuditEvent:
    site_id: str
    occurred_at: datetime
    actor_type: str
    action_type: str
    outcome: str
    correlation_id: str
    redacted_detail: Mapping[str, Any]

class RelationalStore(Protocol):
    def record_ingestion_run(self, record: Mapping[str, Any]) -> None: ...
    def record_snapshot_metadata(self, record: Mapping[str, Any]) -> None: ...
    def fetch_ready_facts(self, site_id: str, through: datetime) -> Sequence[Mapping[str, Any]]: ...

class RawObjectStore(Protocol):
    def put(self, envelope: Any, payload: JsonValue) -> Any: ...
    def get(self, logical_key: str) -> tuple[Any, JsonValue]: ...

class SecretStore(Protocol):
    def resolve(self, reference: str) -> str | None: ...

class HealthReporter(Protocol):
    def report(self, report: HealthReport) -> None: ...

class AuditEventSink(Protocol):
    def emit(self, event: AuditEvent) -> None: ...

@dataclass(frozen=True)
class LockboxAdapterConfig:
    endpoint: str
    secret_reference: str
    service_identity_reference: str
    def __post_init__(self) -> None:
        if not self.secret_reference.startswith("lockbox-ref:"):
            raise ValueError("secret_reference must be an opaque lockbox-ref")
        if not self.service_identity_reference.startswith("identity-ref:"):
            raise ValueError("service identity must be an opaque identity-ref")
