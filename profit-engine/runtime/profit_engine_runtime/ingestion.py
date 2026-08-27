from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any, Mapping, Protocol

from .contracts import JsonValue
from .data_quality import DATA_QUALITY_HOLD
from .raw_store import (
    DataState,
    LocalRawStore,
    RawSnapshotConflict,
    RawSnapshotEnvelope,
    RawSnapshotIntegrityError,
    SourceWindow,
    canonical_json_bytes,
    request_fingerprint,
    sha256_json,
)


class RunStatus(StrEnum):
    STARTED = "started"
    COMPLETE = "complete"
    FAILED = "failed"
    HELD = "held"


@dataclass(frozen=True)
class SourceResult:
    provider: str
    source_object_type: str
    captured_at: str
    window_start: str | None
    window_end: str | None
    request_identity: JsonValue
    payload: JsonValue
    provider_request_id: str | None = None
    data_state: DataState = DataState.ESTIMATED
    completeness: bool = True


@dataclass(frozen=True)
class NormalizedBatch:
    campaign_snapshots: tuple[Mapping[str, Any], ...] = ()
    traffic_facts: tuple[Mapping[str, Any], ...] = ()
    monetization_facts: tuple[Mapping[str, Any], ...] = ()
    hold_reasons: tuple[str, ...] = ()


class ReadCollector(Protocol):
    provider: str
    source_object_type: str

    def request_identity(self) -> JsonValue: ...
    def read(self) -> SourceResult: ...
    def validate(self, source: SourceResult) -> tuple[str, ...]: ...
    def normalize(self, source: SourceResult, raw_snapshot_id: str) -> NormalizedBatch: ...


@dataclass
class InMemoryRelationalStore:
    runs: dict[str, dict[str, Any]] = field(default_factory=dict)
    raw_snapshots: dict[str, dict[str, Any]] = field(default_factory=dict)
    campaign_snapshots: dict[str, Mapping[str, Any]] = field(default_factory=dict)
    traffic_facts: dict[str, Mapping[str, Any]] = field(default_factory=dict)
    monetization_facts: dict[str, Mapping[str, Any]] = field(default_factory=dict)
    quality_checks: list[dict[str, Any]] = field(default_factory=list)
    operation_log: list[str] = field(default_factory=list)

    def start(self, run_id: str, record: Mapping[str, Any]) -> None:
        self.runs.setdefault(run_id, dict(record))
        self.runs[run_id]["status"] = RunStatus.STARTED.value
        self.operation_log.append("run:started")

    def record_raw(self, raw_snapshot_id: str, record: Mapping[str, Any]) -> None:
        self.raw_snapshots.setdefault(raw_snapshot_id, dict(record))
        self.operation_log.append("raw:accepted")

    def record_batch(self, batch: NormalizedBatch) -> None:
        for destination, records in (
            (self.campaign_snapshots, batch.campaign_snapshots),
            (self.traffic_facts, batch.traffic_facts),
            (self.monetization_facts, batch.monetization_facts),
        ):
            for record in records:
                destination.setdefault(str(record["idempotency_key"]), record)
        self.operation_log.append("facts:normalized")

    def finish(self, run_id: str, status: RunStatus, reasons: tuple[str, ...] = ()) -> None:
        self.runs[run_id]["status"] = status.value
        self.runs[run_id]["hold_reasons"] = reasons
        self.quality_checks.append({
            "run_id": run_id,
            "status": DATA_QUALITY_HOLD if status == RunStatus.HELD else status.value,
            "optimizer_consumable": status == RunStatus.COMPLETE,
            "reasons": reasons,
        })
        self.operation_log.append(f"run:{status.value}")


@dataclass(frozen=True)
class IngestionOutcome:
    run_id: str
    status: RunStatus
    raw_snapshot_id: str | None
    raw_created: bool
    replay: bool
    campaign_snapshot_count: int
    traffic_fact_count: int
    monetization_fact_count: int
    hold_reasons: tuple[str, ...]

    @property
    def optimizer_consumable(self) -> bool:
        return self.status == RunStatus.COMPLETE


class IngestionOrchestrator:
    def __init__(self, raw_store: LocalRawStore, relational: InMemoryRelationalStore):
        self.raw_store = raw_store
        self.relational = relational

    def run(self, site_id: str, collector: ReadCollector) -> IngestionOutcome:
        source: SourceResult | None = None
        identity = collector.request_identity()
        fingerprint = request_fingerprint(identity)
        run_id = _stable_id({"site_id": site_id, "provider": collector.provider,
            "source": collector.source_object_type, "request_fingerprint": fingerprint})
        self.relational.start(run_id, {
            "site_id": site_id, "provider": collector.provider,
            "source_object_type": collector.source_object_type,
            "idempotency_key": fingerprint,
        })
        try:
            source = collector.read()
            if canonical_json_bytes(source.request_identity) != canonical_json_bytes(identity):
                raise ValueError("collector request identity changed during read")
            validation_holds = collector.validate(source)
            freshness_holds = _freshness_holds(source)
            envelope = RawSnapshotEnvelope(
                schema_version="1.0", site_id=site_id, provider=source.provider,
                source_object_type=source.source_object_type,
                captured_at=source.captured_at,
                source_window=SourceWindow(source.window_start, source.window_end),
                request_fingerprint=fingerprint, payload_sha256=sha256_json(source.payload),
                provider_request_id=source.provider_request_id,
                data_state=source.data_state, ingestion_run_id=run_id,
            )
            put = self.raw_store.put(envelope, source.payload)
            verified_envelope, verified_payload = self.raw_store.get(put.logical_key)
            if sha256_json(verified_payload) != verified_envelope.payload_sha256:
                raise RawSnapshotIntegrityError("post-write raw verification failed")
            raw_snapshot_id = _stable_id({"logical_key": put.logical_key, "sha256": verified_envelope.payload_sha256})
            self.relational.record_raw(raw_snapshot_id, {
                "site_id": site_id, "provider": source.provider,
                "logical_key": put.logical_key, "payload_sha256": verified_envelope.payload_sha256,
                "request_fingerprint": fingerprint,
            })
            batch = collector.normalize(source, raw_snapshot_id)
            holds = tuple(dict.fromkeys((*validation_holds, *freshness_holds, *batch.hold_reasons,
                *(() if source.completeness else ("incomplete_pagination",)))))
            self.relational.record_batch(batch)
            status = RunStatus.HELD if holds else RunStatus.COMPLETE
            self.relational.finish(run_id, status, holds)
            return _outcome(run_id, status, raw_snapshot_id, put.created, put.idempotent, batch, holds)
        except RawSnapshotConflict:
            self.relational.runs.setdefault(run_id, {"site_id": site_id, "provider": collector.provider})
            holds = ("raw_snapshot_conflict",)
            self.relational.finish(run_id, RunStatus.HELD, holds)
            return _outcome(run_id, RunStatus.HELD, None, False, False, NormalizedBatch(), holds)
        except (RawSnapshotIntegrityError, ValueError, TypeError, KeyError, RuntimeError) as error:
            self.relational.runs.setdefault(run_id, {"site_id": site_id, "provider": collector.provider})
            reason = f"malformed_or_integrity:{type(error).__name__}"
            self.relational.finish(run_id, RunStatus.FAILED, (reason,))
            return _outcome(run_id, RunStatus.FAILED, None, False, False, NormalizedBatch(), (reason,))


def fact_key(value: Mapping[str, Any]) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _freshness_holds(source: SourceResult) -> tuple[str, ...]:
    if not source.window_end:
        return ("missing_source",)
    captured = datetime.fromisoformat(source.captured_at.replace("Z", "+00:00"))
    window_end = datetime.fromisoformat(source.window_end.replace("Z", "+00:00"))
    if captured.tzinfo is None or window_end.tzinfo is None:
        raise ValueError("source timestamps must be timezone-aware")
    return ("stale_source_window",) if (captured - window_end).total_seconds() > 3 * 86400 else ()


def _stable_id(value: JsonValue) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def _outcome(run_id: str, status: RunStatus, raw_snapshot_id: str | None,
    created: bool, replay: bool, batch: NormalizedBatch, reasons: tuple[str, ...]) -> IngestionOutcome:
    return IngestionOutcome(run_id, status, raw_snapshot_id, created, replay,
        len(batch.campaign_snapshots), len(batch.traffic_facts),
        len(batch.monetization_facts), reasons)
