from __future__ import annotations

from datetime import datetime, timezone
import json
import urllib.error
import urllib.request
from typing import Any


GITHUB_REPOSITORY = "niknikdym-hue/Dilivox-1"
DEV_BRANCH = "profit-engine"
DEV_ENVELOPE_USD = 10.0
DEFAULT_PACKAGE_CAP_USD = 3.0
RUNS_URL = f"https://api.github.com/repos/{GITHUB_REPOSITORY}/actions/runs?per_page=30"


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


def _latest_named_run(payload: dict[str, Any], workflow_name: str) -> dict[str, Any] | None:
    runs = payload.get("workflow_runs") or []
    for run in runs:
        if not isinstance(run, dict):
            continue
        if run.get("name") == workflow_name:
            return {
                "id": run.get("id"),
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
    return None


def _api_state(preflight: dict[str, Any] | None) -> str:
    if not preflight:
        return "NOT_CHECKED"
    if preflight.get("status") != "completed":
        return "CHECKING"
    if preflight.get("conclusion") == "success":
        return "READY"
    return "PREFLIGHT_FAILED"


def collect_development_status(*, fetch_remote: bool = True) -> dict[str, Any]:
    value: dict[str, Any] = {
        "state": "LOCAL_POLICY_READY",
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "repository": GITHUB_REPOSITORY,
        "authority_branch": DEV_BRANCH,
        "api_key_state": "NOT_CHECKED",
        "quality_policy": "QUALITY_FIRST_COST_AWARE",
        "initial_openai_dev_envelope_usd": DEV_ENVELOPE_USD,
        "default_package_hard_cap_usd": DEFAULT_PACKAGE_CAP_USD,
        "dev_ai_cost_usd": 0.0,
        "dev_ai_cost_state": "NO_PAID_DILIVOX_RUNS_RECORDED_YET",
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
        preflight = _latest_named_run(payload, "Profit Engine Dev Preflight")
        dev_run = _latest_named_run(payload, "Profit Engine Bounded Dev Task")
        value["preflight"] = preflight
        value["last_dev_run"] = dev_run
        value["api_key_state"] = _api_state(preflight)
        value["state"] = "REMOTE_STATUS_OK"
    except (OSError, urllib.error.URLError, json.JSONDecodeError, ValueError) as exc:
        value["state"] = "REMOTE_STATUS_UNAVAILABLE"
        value["remote_error"] = str(exc)
    return value
