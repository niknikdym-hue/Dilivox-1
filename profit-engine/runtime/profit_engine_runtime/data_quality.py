from dataclasses import dataclass
from enum import StrEnum

DATA_QUALITY_HOLD = "DATA_QUALITY_HOLD"

class FreshnessState(StrEnum):
    FRESH = "FRESH"
    STALE = "STALE"
    UNKNOWN = "UNKNOWN"
class MissingSourceState(StrEnum):
    PRESENT = "PRESENT"
    MISSING = "MISSING"
class DuplicateState(StrEnum):
    UNIQUE = "UNIQUE"
    IDEMPOTENT_REPLAY = "IDEMPOTENT_REPLAY"
    CONFLICT = "CONFLICT"
class SnapshotShapeState(StrEnum):
    VALID = "VALID"
    MALFORMED = "MALFORMED"
class ReconciliationState(StrEnum):
    READY = "READY"
    NOT_READY = "NOT_READY"
    RECONCILED = "RECONCILED"

@dataclass(frozen=True)
class DataQualityAssessment:
    freshness: FreshnessState
    missing_source: MissingSourceState
    duplicate: DuplicateState
    snapshot_shape: SnapshotShapeState
    reconciliation: ReconciliationState
    explicit_hold: bool = False
    @property
    def hold_reasons(self) -> tuple[str, ...]:
        reasons = []
        if self.explicit_hold: reasons.append("explicit_hold")
        if self.freshness != FreshnessState.FRESH: reasons.append(f"freshness:{self.freshness.value}")
        if self.missing_source == MissingSourceState.MISSING: reasons.append("missing_source")
        if self.duplicate == DuplicateState.CONFLICT: reasons.append("duplicate_conflict")
        if self.snapshot_shape == SnapshotShapeState.MALFORMED: reasons.append("malformed_snapshot")
        if self.reconciliation == ReconciliationState.NOT_READY: reasons.append("reconciliation_not_ready")
        return tuple(reasons)
    @property
    def status(self) -> str:
        return DATA_QUALITY_HOLD if self.hold_reasons else "READY"
    @property
    def optimizer_consumable(self) -> bool:
        return self.status == "READY"
