from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import urllib.error
import urllib.request
from typing import Any

from .development_router import classify_task


GITHUB_REPOSITORY = "niknikdym-hue/Dilivox-1"
DEV_BRANCH = "profit-engine"
DEV_ENVELOPE_USD = 10.0
DEFAULT_PACKAGE_CAP_USD = 3.0
RUNS_URL = f"https://api.github.com/repos/{GITHUB_REPOSITORY}/actions/runs?per_page=30"
PREFLIGHT_WORKFLOW_PATH = ".github/workflows/profit-engine-dev-preflight.yml"
DEV_WORKFLOW_PATH = ".github/workflows/profit-engine-bounded-dev-task.yml"
PROFIT_ENGINE_ROOT = Path(__file__).resolve().parents[2]
COST_LEDGER_PATH = PROFIT_ENGINE_ROOT / "data" / "development-cost-ledger.json"
DEV_REQUEST_DIR = PROFIT_ENGINE_ROOT / "dev-requests"


def _fetch_json(url: str, timeout: float = 5.0) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "dilivox-profit-engine-owner-control",
        },
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def _compact_run(run: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": run.get("id"),
        "name": run.get("name"),
        "path": run.get("path"),
        "status": run.get("status"),
        "conclusion": run.get("conclusion"),
        "event": run.get("event"),
        "head_branch": run.get("head_branch"),
        "head_sha": run.get("head_sha"),
        "created_at": run.get("created_at"),
        "updated_at": run.get("updated_at"),
        "html_url": run.get("html_url"),
        "display_title": run.get("display_title"),
    }


def _latest_workflow_run(payload: dict[str, Any], workflow_path: str) -> dict[str, Any] | None:
    """Return latest workflow run by immutable workflow path, not UI run-name."""

    runs = payload.get("workflow_runs") or []
    for run in runs:
        if not isinstance(run, dict):
            continue
        if run.get("path") == workflow_path:
            return _compact_run(run)
    return None


def _api_state(preflight: dict[str, Any] | None) -> str:
    if not preflight:
        return "NOT_CHECKED"
    if preflight.get("status") != "completed":
        return "CHECKING"
    if preflight.get("conclusion") == "success":
        return "READY"
    return "PREFLIGHT_FAILED"


def _load_cost_ledger() -> tuple[float, str, int]:
    if not COST_LEDGER_PATH.exists():
        return 0.0, "LEDGER_MISSING", 0
    try:
        value = json.loads(COST_LEDGER_PATH.read_text(encoding="utf-8"))
        if value.get("schema_version") != "dilivox-dev-cost-ledger-v1":
            raise ValueError("unsupported development cost ledger version")
        entries = value.get("entries") or []
        if not isinstance(entries, list):
            raise ValueError("development cost entries must be a list")
        total = 0.0
        accepted = 0
        for entry in entries:
            if not isinstance(entry, dict):
                raise ValueError("development cost entry must be an object")
            if entry.get("accepted") is not True:
                continue
            amount = float(entry.get("dev_ai_cost_usd") or 0.0)
            if amount < 0:
                raise ValueError("negative development cost")
            total += amount
            accepted += 1
        return round(total, 6), "ACCEPTED_LEDGER", accepted
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        return 0.0, "LEDGER_INVALID", 0


def _source_path(path: Path) -> str:
    try:
        return path.relative_to(PROFIT_ENGINE_ROOT).as_posix()
    except ValueError:
        # Unit tests may inject a temporary request directory. Production still
        # uses the canonical DEV_REQUEST_DIR rooted below PROFIT_ENGINE_ROOT.
        return path.name


def _load_latest_request() -> dict[str, Any] | None:
    if not DEV_REQUEST_DIR.exists():
        return None
    rows: list[tuple[datetime, dict[str, Any]]] = []
    for path in DEV_REQUEST_DIR.glob("*.json"):
        try:
            req = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(req, dict) or req.get("execute") is not True:
                continue
            created = datetime.fromisoformat(str(req["created_at"]).replace("Z", "+00:00"))
            descriptor = dict(req.get("task_descriptor") or {})
            descriptor.setdefault("task_id", req.get("task_id"))
            route = classify_task(descriptor)
            rows.append((created, {
                "request_id": req.get("request_id"),
                "created_at": req.get("created_at"),
                "task_id": req.get("task_id"),
                "task_file": req.get("task_file"),
                "base_sha": req.get("base_sha"),
                "task_budget_usd": req.get("task_budget_usd"),
                "execution_route": route.execution_route,
                "model_route": route.model_route or "GitHub/Python",
                "quality_floor": route.quality_floor,
                "routing_reason": route.routing_reason,
                "why_not_cheaper": route.why_not_cheaper,
                "owner_approval_required": route.owner_approval_required,
                "source_path": _source_path(path),
            }))
        except (OSError, KeyError, ValueError, TypeError, json.JSONDecodeError):
            continue
    if not rows:
        return None
    rows.sort(key=lambda item: item[0], reverse=True)
    return rows[0][1]


def collect_development_status(*, fetch_remote: bool = True) -> dict[str, Any]:
    dev_cost, dev_cost_state, accepted_cost_entries = _load_cost_ledger()
    value: dict[str, Any] = {
        "state": "LOCAL_POLICY_READY",
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "repository": GITHUB_REPOSITORY,
        "authority_branch": DEV_BRANCH,
        "api_key_state": "NOT_CHECKED",
        "quality_policy": "QUALITY_FIRST_COST_AWARE",
        "initial_openai_dev_envelope_usd": DEV_ENVELOPE_USD,
        "default_package_hard_cap_usd": DEFAULT_PACKAGE_CAP_USD,
        "dev_ai_cost_usd": dev_cost,
        "dev_ai_cost_state": dev_cost_state,
        "accepted_cost_entries": accepted_cost_entries,
        "remaining_dev_envelope_usd": round(max(0.0, DEV_ENVELOPE_USD - dev_cost), 6),
        "current_request": _load_latest_request(),
        "routes": [
            {"route": "G0", "model": "GitHub/Python", "paid": False},
            {"route": "G1", "model": "gpt-5.6-luna", "paid": True},
            {"route": "G2", "model": "gpt-5.6-terra", "paid": True},
            {"route": "G3", "model": "gpt-5.6-sol", "paid": True},
            {"route": "G4", "model": "gpt-6-astra", "paid": True, "owner_opt_in": True},
        ],
        "preflight": None,
        "last_dev_run": None,
        "read_only": True,
        "provider_write_allowed": False,
        "auto_merge": False,
        "auto_deploy": False,
    }
    if not fetch_remote:
        return value

    try:
        payload = _fetch_json(RUNS_URL)
        preflight = _latest_workflow_run(payload, PREFLIGHT_WORKFLOW_PATH)
        dev_run = _latest_workflow_run(payload, DEV_WORKFLOW_PATH)
        value["preflight"] = preflight
        value["last_dev_run"] = dev_run
        value["api_key_state"] = _api_state(preflight)
        value["state"] = "REMOTE_STATUS_OK"
    except (OSError, urllib.error.URLError, json.JSONDecodeError, ValueError) as exc:
        value["state"] = "REMOTE_STATUS_UNAVAILABLE"
        value["remote_error"] = str(exc)
    return value
