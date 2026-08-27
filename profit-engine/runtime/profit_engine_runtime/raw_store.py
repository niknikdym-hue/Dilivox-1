from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import StrEnum
from pathlib import Path
from typing import Any

from .contracts import JsonValue

SHA256_RE = re.compile(r"^[a-f0-9]{64}$")
SEGMENT_RE = re.compile(r"^[a-z0-9][a-z0-9_-]*$")
DEFAULT_RAW_ROOT = Path("~/.local/share/profit-engine/raw").expanduser()

class RawStoreError(RuntimeError): pass
class RawSnapshotConflict(RawStoreError): pass
class RawSnapshotIntegrityError(RawStoreError): pass

class DataState(StrEnum):
    ESTIMATED = "estimated"
    FINAL = "final"
    RECONCILED = "reconciled"

@dataclass(frozen=True)
class SourceWindow:
    start: str | None = None
    end: str | None = None

@dataclass(frozen=True)
class RawSnapshotEnvelope:
    schema_version: str
    site_id: str
    provider: str
    source_object_type: str
    captured_at: str
    source_window: SourceWindow
    request_fingerprint: str
    payload_sha256: str
    provider_request_id: str | None
    data_state: DataState
    ingestion_run_id: str

    def __post_init__(self) -> None:
        if self.schema_version != "1.0": raise ValueError("unsupported raw snapshot schema version")
        for name in ("site_id", "provider", "source_object_type"):
            if not SEGMENT_RE.fullmatch(getattr(self, name)): raise ValueError(f"invalid {name}")
        for name in ("request_fingerprint", "payload_sha256"):
            if not SHA256_RE.fullmatch(getattr(self, name)): raise ValueError(f"invalid {name}")
        captured = datetime.fromisoformat(self.captured_at.replace("Z", "+00:00"))
        if captured.tzinfo is None: raise ValueError("captured_at must be timezone-aware")
        if not self.ingestion_run_id: raise ValueError("ingestion_run_id is required")

    @property
    def logical_key(self) -> str:
        captured = datetime.fromisoformat(self.captured_at.replace("Z", "+00:00")).astimezone(timezone.utc)
        return "/".join(("raw", self.site_id, self.provider, f"{captured.year:04d}",
            f"{captured.month:02d}", f"{captured.day:02d}", self.source_object_type,
            f"{self.request_fingerprint}.json"))

@dataclass(frozen=True)
class PutResult:
    logical_key: str
    created: bool
    idempotent: bool

def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()

def sha256_json(payload: JsonValue) -> str:
    return hashlib.sha256(canonical_json_bytes(payload)).hexdigest()

def request_fingerprint(request_identity: JsonValue) -> str:
    return sha256_json(request_identity)

class LocalRawStore:
    def __init__(self, root: Path | None = None) -> None:
        configured = os.environ.get("PROFIT_ENGINE_LOCAL_RAW_ROOT")
        self.root = Path(configured).expanduser() if configured and root is None else (root or DEFAULT_RAW_ROOT)

    def put(self, envelope: RawSnapshotEnvelope, payload: JsonValue) -> PutResult:
        if sha256_json(payload) != envelope.payload_sha256:
            raise RawSnapshotIntegrityError("payload SHA-256 does not match envelope")
        encoded = canonical_json_bytes({"envelope": _envelope_dict(envelope), "payload": payload})
        target = self._target(envelope.logical_key)
        target.parent.mkdir(parents=True, exist_ok=True)
        descriptor, temporary_name = tempfile.mkstemp(prefix=".raw-", dir=target.parent)
        temporary = Path(temporary_name)
        try:
            with os.fdopen(descriptor, "wb") as stream:
                stream.write(encoded); stream.flush(); os.fsync(stream.fileno())
            os.chmod(temporary, 0o600)
            try:
                os.link(temporary, target)
            except FileExistsError:
                old_envelope, old_payload = self.get(envelope.logical_key)
                old = canonical_json_bytes({"envelope": _envelope_dict(old_envelope), "payload": old_payload})
                if old == encoded: return PutResult(envelope.logical_key, False, True)
                raise RawSnapshotConflict("immutable raw snapshot identity already contains different content")
            return PutResult(envelope.logical_key, True, False)
        finally:
            temporary.unlink(missing_ok=True)

    def get(self, logical_key: str) -> tuple[RawSnapshotEnvelope, JsonValue]:
        try:
            document = json.loads(self._target(logical_key).read_text(encoding="utf-8"))
            envelope = _envelope_from_dict(document["envelope"]); payload = document["payload"]
        except (OSError, KeyError, TypeError, json.JSONDecodeError, ValueError) as error:
            raise RawSnapshotIntegrityError("raw snapshot is missing or malformed") from error
        if envelope.logical_key != logical_key:
            raise RawSnapshotIntegrityError("raw snapshot logical key does not match envelope")
        if sha256_json(payload) != envelope.payload_sha256:
            raise RawSnapshotIntegrityError("stored payload SHA-256 verification failed")
        return envelope, payload

    def _target(self, logical_key: str) -> Path:
        parts = Path(logical_key).parts
        if len(parts) != 8 or parts[0] != "raw" or any(p in ("", ".", "..") for p in parts):
            raise ValueError("invalid raw snapshot logical key")
        target = (self.root.parent / Path(*parts)).resolve()
        if not target.is_relative_to(self.root.resolve()):
            raise ValueError("raw snapshot path escapes store root")
        return target

def _envelope_dict(envelope: RawSnapshotEnvelope) -> dict[str, Any]:
    value = asdict(envelope); value["data_state"] = envelope.data_state.value
    return value

def _envelope_from_dict(value: dict[str, Any]) -> RawSnapshotEnvelope:
    data = dict(value)
    data["source_window"] = SourceWindow(**data["source_window"])
    data["data_state"] = DataState(data["data_state"])
    return RawSnapshotEnvelope(**data)
