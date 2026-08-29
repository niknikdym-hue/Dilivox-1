from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import stat
import tempfile


DEFAULT_OWNER_PERMISSION_PATH = Path(
    "~/.config/profit-engine/approvals/day12-direct-manager-editing.json"
).expanduser()
SCHEMA_VERSION = "profit-engine.day12.direct-manager-permission.v1"
SOURCE = "YANDEX_DIRECT_MANAGING_ACCOUNT_UI"
MAX_AGE = timedelta(hours=24)
MAX_FUTURE_SKEW = timedelta(minutes=5)


@dataclass(frozen=True)
class OwnerPermissionEvidence:
    schema_version: str
    permission: str
    operator_login: str
    target_login_sha256: str
    source: str
    owner_confirmed: bool
    confirmed_at: str
    evidence_digest: str


def target_login_sha256(login: str) -> str:
    return sha256(login.strip().casefold().encode("utf-8")).hexdigest()


def evidence_digest(payload: dict[str, object]) -> str:
    return sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def build_owner_permission_payload(
    *,
    operator_login: str,
    target_login: str,
    confirmed_at: datetime,
    owner_confirmed: bool,
) -> dict[str, object]:
    operator = operator_login.strip()
    target = target_login.strip()
    if not operator or not target:
        raise ValueError("exact Direct operator and managed target logins are required")
    if operator.casefold() == target.casefold():
        raise ValueError("Direct operator and managed target must differ")
    if owner_confirmed is not True:
        raise ValueError("explicit Owner confirmation of Editing is required")
    if confirmed_at.tzinfo is None:
        raise ValueError("confirmed_at must be timezone-aware")

    value: dict[str, object] = {
        "schema_version": SCHEMA_VERSION,
        "permission": "EDITING",
        "operator_login": operator,
        "target_login_sha256": target_login_sha256(target),
        "source": SOURCE,
        "owner_confirmed": True,
        "confirmed_at": confirmed_at.astimezone(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    return {**value, "evidence_digest": evidence_digest(value)}


def record_owner_permission_evidence(
    path: Path = DEFAULT_OWNER_PERMISSION_PATH,
    *,
    operator_login: str,
    target_login: str,
    confirmed_at: datetime | None = None,
    owner_confirmed: bool,
) -> Path:
    """Atomically record Owner-confirmed Direct Managing Account Editing evidence.

    This records local authority evidence only. It does not call Yandex and does not
    grant provider write authority. Plaintext managed-target login is never written.
    """
    payload = build_owner_permission_payload(
        operator_login=operator_login,
        target_login=target_login,
        confirmed_at=confirmed_at or datetime.now(timezone.utc),
        owner_confirmed=owner_confirmed,
    )
    path = path.expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent, text=True)
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(tmp_path, 0o600)
        os.replace(tmp_path, path)
        os.chmod(path, 0o600)
    finally:
        if tmp_path.exists():
            tmp_path.unlink()
    return path


def load_owner_permission_evidence(
    path: Path,
    *,
    operator_login: str,
    target_login: str,
    now: datetime | None = None,
) -> OwnerPermissionEvidence:
    if not path.exists():
        raise FileNotFoundError(path)
    mode = stat.S_IMODE(path.stat().st_mode)
    if mode & 0o077:
        raise ValueError(f"owner permission evidence permissions must be 0600, found {mode:04o}")

    data = json.loads(path.read_text(encoding="utf-8"))
    required = {
        "schema_version",
        "permission",
        "operator_login",
        "target_login_sha256",
        "source",
        "owner_confirmed",
        "confirmed_at",
        "evidence_digest",
    }
    if set(data) != required:
        raise ValueError("owner permission evidence has unexpected or missing fields")

    recorded_digest = str(data["evidence_digest"])
    digest_payload = {key: data[key] for key in sorted(required - {"evidence_digest"})}
    if recorded_digest != evidence_digest(digest_payload):
        raise ValueError("owner permission evidence digest mismatch")
    if data["schema_version"] != SCHEMA_VERSION:
        raise ValueError("unsupported owner permission evidence schema")
    if data["permission"] != "EDITING":
        raise ValueError("owner permission evidence must confirm EDITING")
    if data["source"] != SOURCE or data["owner_confirmed"] is not True:
        raise ValueError("owner permission evidence must be an explicit Owner confirmation from Direct UI")
    if str(data["operator_login"]).casefold() != operator_login.strip().casefold():
        raise ValueError("owner permission evidence operator mismatch")
    if str(data["target_login_sha256"]) != target_login_sha256(target_login):
        raise ValueError("owner permission evidence target mismatch")

    confirmed_at = datetime.fromisoformat(str(data["confirmed_at"]).replace("Z", "+00:00"))
    if confirmed_at.tzinfo is None:
        raise ValueError("owner permission evidence confirmed_at must be timezone-aware")
    current = now or datetime.now(timezone.utc)
    current = current.astimezone(timezone.utc)
    confirmed_at = confirmed_at.astimezone(timezone.utc)
    if confirmed_at > current + MAX_FUTURE_SKEW:
        raise ValueError("owner permission evidence timestamp is in the future")
    if current - confirmed_at > MAX_AGE:
        raise ValueError("owner permission evidence is stale")

    return OwnerPermissionEvidence(
        schema_version=str(data["schema_version"]),
        permission=str(data["permission"]),
        operator_login=str(data["operator_login"]),
        target_login_sha256=str(data["target_login_sha256"]),
        source=str(data["source"]),
        owner_confirmed=bool(data["owner_confirmed"]),
        confirmed_at=str(data["confirmed_at"]),
        evidence_digest=recorded_digest,
    )
