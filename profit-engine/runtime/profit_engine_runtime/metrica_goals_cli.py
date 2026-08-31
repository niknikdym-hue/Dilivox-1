from __future__ import annotations

import argparse
import json
from pathlib import Path
import urllib.error
import urllib.request
from typing import Any

from .config import DEFAULT_CONFIG_PATH, load_site_config, resolve_secret
from .redaction import redact


DEFAULT_GOALS_PATH = Path(__file__).resolve().parents[2] / "sites" / "dilivox" / "metrica-goals.json"


def _load_registry(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    goals = value.get("goals")
    if not isinstance(goals, list) or not goals:
        raise ValueError("Metrica goal registry must contain a non-empty goals list")
    identifiers: set[str] = set()
    for goal in goals:
        identifier = str(goal.get("identifier", ""))
        if not identifier or identifier in identifiers:
            raise ValueError("Metrica goal identifiers must be unique and non-empty")
        identifiers.add(identifier)
        if goal.get("metrica_type") != "action" or goal.get("condition_type") != "exact":
            raise ValueError("P0 Dilivox goals must be exact JavaScript-event goals")
    return value


def _request_json(request: urllib.request.Request) -> tuple[int, dict[str, Any]]:
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            raw = response.read().decode("utf-8")
            return response.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            body = json.loads(raw) if raw else {}
        except json.JSONDecodeError:
            body = {}
        message = None
        if isinstance(body, dict):
            errors = body.get("errors")
            if isinstance(errors, list) and errors and isinstance(errors[0], dict):
                message = errors[0].get("message")
        raise RuntimeError(f"Metrica HTTP {exc.code}: {message or 'provider error'}") from None


def _goal_identifiers(goal: dict[str, Any]) -> set[str]:
    values: set[str] = set()
    for condition in goal.get("conditions") or []:
        if isinstance(condition, dict) and condition.get("url") is not None:
            values.add(str(condition["url"]))
    return values


def audit_goals(*, config_path: Path, goals_path: Path) -> dict[str, Any]:
    config, present = load_site_config(config_path)
    if not present:
        raise FileNotFoundError(f"private Dilivox config not found at {config_path}")
    if not config.metrica_counter_id:
        raise ValueError("exact Metrica counter binding is required")
    token = resolve_secret(config.yandex_oauth_token_ref)
    if not token:
        raise ValueError("Metrica OAuth credential is unavailable")

    registry = _load_registry(goals_path)
    request = urllib.request.Request(
        f"{config.metrica_management_endpoint}/counter/{config.metrica_counter_id}/goals",
        headers={"Authorization": f"OAuth {token}", "Accept": "application/json"},
        method="GET",
    )
    status, body = _request_json(request)
    current = body.get("goals") if isinstance(body, dict) else []
    current = current if isinstance(current, list) else []

    expected = {str(item["identifier"]): item for item in registry["goals"]}
    matches: dict[str, list[dict[str, Any]]] = {key: [] for key in expected}
    for goal in current:
        if not isinstance(goal, dict):
            continue
        for identifier in _goal_identifiers(goal):
            if identifier in matches:
                matches[identifier].append(goal)

    items: list[dict[str, Any]] = []
    missing: list[str] = []
    invalid: list[str] = []
    duplicates: list[str] = []
    for identifier, spec in expected.items():
        found = matches[identifier]
        if not found:
            state = "MISSING"
            missing.append(identifier)
        elif len(found) > 1:
            state = "DUPLICATE"
            duplicates.append(identifier)
        elif found[0].get("type") != "action":
            state = "WRONG_TYPE"
            invalid.append(identifier)
        else:
            state = "PASS"
        items.append({
            "key": spec["key"],
            "identifier": identifier,
            "name": spec["name"],
            "role": spec["role"],
            "native_bidding_eligible": bool(spec.get("native_bidding_eligible", False)),
            "state": state,
        })

    overall = "PASS" if not (missing or invalid or duplicates) else "REWORK_REQUIRED"
    public = {
        "mode": "DILIVOX_METRICA_GOALS_AUDIT_READ_ONLY",
        "http_status": status,
        "state": overall,
        "expected_goal_count": len(expected),
        "provider_goal_count": len(current),
        "missing_identifiers": missing,
        "invalid_identifiers": invalid,
        "duplicate_identifiers": duplicates,
        "goals": items,
        "provider_write_allowed": False,
        "provider_write_requests": 0,
        "credential_values_printed": False,
    }
    return redact(public, (token,))


def apply_missing_goals(*, config_path: Path, goals_path: Path) -> dict[str, Any]:
    """Create only registry goals that are missing. No update/delete and no retry."""
    before = audit_goals(config_path=config_path, goals_path=goals_path)
    if before["invalid_identifiers"] or before["duplicate_identifiers"]:
        raise ValueError("refusing goal writes while existing canonical identifiers are invalid or duplicated")
    missing = set(before["missing_identifiers"])
    if not missing:
        return {
            "mode": "DILIVOX_METRICA_GOALS_APPLY",
            "state": "NO_CHANGES_NEEDED",
            "created": [],
            "provider_write_requests": 0,
            "readback": before,
        }

    config, _ = load_site_config(config_path)
    token = resolve_secret(config.yandex_oauth_token_ref)
    if not token:
        raise ValueError("Metrica OAuth credential is unavailable")
    registry = _load_registry(goals_path)

    created: list[str] = []
    requests_sent = 0
    for spec in registry["goals"]:
        identifier = str(spec["identifier"])
        if identifier not in missing:
            continue
        body = json.dumps({
            "goal": {
                "name": spec["name"],
                "type": "action",
                "conditions": [{"type": "exact", "url": identifier}],
                "is_favorite": False,
            }
        }, ensure_ascii=False).encode("utf-8")
        request = urllib.request.Request(
            f"{config.metrica_management_endpoint}/counter/{config.metrica_counter_id}/goals",
            data=body,
            headers={
                "Authorization": f"OAuth {token}",
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        _request_json(request)
        requests_sent += 1
        created.append(identifier)

    readback = audit_goals(config_path=config_path, goals_path=goals_path)
    state = "APPLIED_AND_VERIFIED" if readback["state"] == "PASS" else "APPLIED_BUT_READBACK_NOT_PASS"
    return redact({
        "mode": "DILIVOX_METRICA_GOALS_APPLY",
        "state": state,
        "created": created,
        "provider_write_requests": requests_sent,
        "blind_retry": False,
        "readback": readback,
        "credential_values_printed": False,
    }, (token,))


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit or explicitly create canonical Dilivox Metrica JS goals")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH)
    parser.add_argument("--goals", type=Path, default=DEFAULT_GOALS_PATH)
    parser.add_argument("--apply-missing", action="store_true", help="Create only missing canonical goals; this is a Metrica configuration write")
    args = parser.parse_args()
    if args.apply_missing:
        output = apply_missing_goals(config_path=args.config, goals_path=args.goals)
    else:
        output = audit_goals(config_path=args.config, goals_path=args.goals)
    print(json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if output.get("state") in {"PASS", "NO_CHANGES_NEEDED", "APPLIED_AND_VERIFIED"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
