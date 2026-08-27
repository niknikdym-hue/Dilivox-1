from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping

from .data_quality import DATA_QUALITY_HOLD
from .ingestion import fact_key
from .raw_store import DataState, LocalRawStore, RawSnapshotConflict, RawSnapshotEnvelope, SourceWindow, request_fingerprint, sha256_json

EVENT_TYPES = frozenset({"page_view_site","story_open","story_progress_25","story_progress_50","story_progress_75","version_section_seen","version_selected","reveal_opened","story_completed","next_story_seen","next_story_clicked","catalog_opened","return_visit","session_end_summary","experiment_exposure","experiment_conversion"})
COMMON_FIELDS = frozenset({"schema_version","event_id","idempotency_key","event_type","occurred_at","site_id","content_id","content_type","session_id","acquisition_id","cohort_ref","experiment_id","variant_id","placement_id","source_content_id","destination_content_id","deployment_version","properties"})
PROPERTY_FIELDS = {"version_selected": frozenset({"choice_ref","is_correct"}), "session_end_summary": frozenset({"duration_bucket","event_count"}), "experiment_conversion": frozenset({"source_event_id","conversion_key"})}

@dataclass
class InMemorySiteEventStore:
    events: dict[str, Mapping[str, Any]] = field(default_factory=dict)
    operation_log: list[str] = field(default_factory=list)
    duplicates: int = 0

@dataclass(frozen=True)
class EventIngestionOutcome:
    status: str
    raw_snapshot_id: str | None
    accepted: int
    duplicates: int
    rejected: int
    hold_reasons: tuple[str, ...] = ()
    @property
    def optimizer_consumable(self) -> bool: return self.status == "complete"

class EventBatchIngestor:
    def __init__(self, raw: LocalRawStore, relational: InMemorySiteEventStore):
        self.raw, self.relational = raw, relational

    def ingest(self, batch: Mapping[str, Any]) -> EventIngestionOutcome:
        if set(batch) != {"schema_version","batch_id","site_id","captured_at","events"} or batch.get("schema_version") != "1.0" or not isinstance(batch.get("events"), list):
            return EventIngestionOutcome("held",None,0,0,len(batch.get("events",[])) if isinstance(batch.get("events"),list) else 1,("schema_incompatibility",))
        if len(str(batch).encode()) > 65536: return EventIngestionOutcome("held",None,0,0,len(batch["events"]),("batch_size_exceeded",))
        identity={"site_id":batch["site_id"],"batch_id":batch["batch_id"]}
        fp=request_fingerprint(identity); payload=dict(batch)
        envelope=RawSnapshotEnvelope("1.0",str(batch["site_id"]),"first-party-site","event-batch",str(batch["captured_at"]),SourceWindow(None,None),fp,sha256_json(payload),None,DataState.FINAL,str(batch["batch_id"]))
        try:
            put=self.raw.put(envelope,payload); checked,stored=self.raw.get(put.logical_key)
            if sha256_json(stored)!=checked.payload_sha256: raise ValueError("raw hash mismatch")
        except RawSnapshotConflict:
            return EventIngestionOutcome("held",None,0,0,len(batch["events"]),("raw_batch_conflict",))
        raw_id=fact_key({"logical_key":put.logical_key,"sha256":checked.payload_sha256})
        self.relational.operation_log.append("raw:verified")
        errors=[reason for event in batch["events"] for reason in validate_event(event)]
        if errors:
            return EventIngestionOutcome("held",raw_id,0,0,len(batch["events"]),tuple(sorted(set(errors))))
        accepted=duplicates=0
        pending={}
        for event in batch["events"]:
            key=event["idempotency_key"]
            if key in self.relational.events or key in pending: duplicates+=1
            else:
                pending[key]={"event_id":event["event_id"],"site_id":event["site_id"],"occurred_at":event["occurred_at"],"event_type":event["event_type"],"stable_content_id":event["content_id"],"attribution":{"acquisition_id":event["acquisition_id"],"cohort_ref":event["cohort_ref"]},"properties":event["properties"],"idempotency_key":key,"raw_snapshot_id":raw_id}; accepted+=1
        self.relational.events.update(pending); self.relational.duplicates+=duplicates
        self.relational.operation_log.append("events:normalized")
        return EventIngestionOutcome("complete",raw_id,accepted,duplicates,0)

def validate_event(event: Any) -> tuple[str,...]:
    if not isinstance(event,dict) or set(event)!=COMMON_FIELDS: return ("schema_incompatibility",)
    if event.get("schema_version")!="1.0" or event.get("event_type") not in EVENT_TYPES: return ("schema_incompatibility",)
    props=event.get("properties")
    if not isinstance(props,dict) or not set(props).issubset(PROPERTY_FIELDS.get(event["event_type"],frozenset())): return ("property_allowlist_rejection",)
    try:
        ts=datetime.fromisoformat(str(event["occurred_at"]).replace("Z","+00:00"))
        if ts.tzinfo is None: raise ValueError
    except ValueError: return ("schema_incompatibility",)
    if event["event_type"]=="experiment_conversion" and not props.get("source_event_id"): return ("unapproved_experiment_conversion",)
    return ()

def assess_event_quality(**signals: Any) -> dict[str,Any]:
    reasons=tuple(name for name,value in signals.items() if value)
    return {"status":DATA_QUALITY_HOLD if reasons else "READY","optimizer_consumable":not reasons,"reasons":reasons}
