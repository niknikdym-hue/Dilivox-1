from __future__ import annotations

from datetime import datetime, timezone
import subprocess
import threading
import time
from typing import Any

from .development_controller import DevelopmentController
from .development_status import collect_development_status
from .github_control import GhCliControlAdapter, GitHubControlError
from .project_board import PROFIT_ENGINE_ROOT, build_project_board, derive_truth_state


def _local_origin_sha() -> str | None:
    try:
        value = subprocess.run(
            ("git", "rev-parse", "origin/profit-engine"),
            cwd=PROFIT_ENGINE_ROOT.parent,
            check=True,
            capture_output=True,
            text=True,
            timeout=5,
        ).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return None
    return value if len(value) == 40 else None


class ProjectControlService:
    def __init__(
        self,
        *,
        adapter: GhCliControlAdapter | Any | None = None,
        controller: DevelopmentController | None = None,
    ):
        self.adapter = adapter or GhCliControlAdapter()
        self.controller = controller or DevelopmentController(adapter=self.adapter)
        self._remote_cache: dict[str, Any] | None = None
        self._remote_cache_lock = threading.Lock()

    @staticmethod
    def _runtime_tasks(control_state: dict[str, Any]) -> dict[str, dict[str, Any]]:
        active = control_state.get("active") or {}
        rows: dict[str, dict[str, Any]] = {}
        task_id = active.get("current_task_id")
        if task_id:
            review = active.get("review") or {}
            rows[task_id] = {
                "branch": active.get("work_branch"),
                "pr": review.get("url"),
                "sha": active.get("current_base_sha"),
                "ci_state": (active.get("run") or {}).get("conclusion") or (active.get("run") or {}).get("status") or "NOT_CHECKED",
                "current_action": active.get("current_action"),
                "actual_cost_usd": active.get("actual_cost_usd"),
            }
            if control_state.get("state") == "READY_FOR_REVIEW":
                rows[task_id]["status"] = "CODE_READY"
        for completed in active.get("completed_task_ids") or []:
            rows.setdefault(completed, {})["ci_state"] = "SUCCESS"
            rows[completed]["current_action"] = "Technical PASS recorded; Central Brain acceptance remains separate."
            if completed == "TASK-020-G0-SMOKE":
                rows[completed]["status"] = "CODE_READY"
        return rows

    def snapshot(self, *, fetch_remote: bool = True, reconcile: bool = False) -> dict[str, Any]:
        control_state = self.controller.refresh() if reconcile else self.controller.state()
        board = build_project_board(runtime_tasks=self._runtime_tasks(control_state))
        local_sha = _local_origin_sha()
        remote_sha: str | None = None
        remote_available = False
        github_state = "GITHUB_CONTROL_NOT_CHECKED"
        github_actor = None
        ci: dict[str, Any] | None = None
        github_error = None
        if fetch_remote:
            try:
                github_actor = self.adapter.actor()
                remote_sha = self.adapter.canonical_sha()
                remote_available = True
                github_state = "READY"
                try:
                    runs = self.adapter.workflow_runs("profit-engine-ci.yml", limit=5)
                    ci = runs[0] if runs else None
                except GitHubControlError:
                    ci = None
                with self._remote_cache_lock:
                    self._remote_cache = {
                        "cached_monotonic": time.monotonic(), "remote_sha": remote_sha,
                        "github_actor": github_actor, "ci": ci,
                    }
            except GitHubControlError as exc:
                github_state = exc.code
                github_error = exc.detail
        else:
            with self._remote_cache_lock:
                cached = dict(self._remote_cache or {})
            if cached and time.monotonic() - float(cached.get("cached_monotonic", 0)) <= 60:
                remote_sha = cached.get("remote_sha")
                github_actor = cached.get("github_actor")
                ci = cached.get("ci")
                remote_available = bool(remote_sha)
                github_state = "READY_CACHED_60S"

        critical_blockers = sum(
            bool(task.get("blockers")) or task.get("status") in {"OWNER_GATE", "BLOCKED_EXTERNAL", "BLOCKED_DATA"}
            for task in board["critical_path"]
        )
        truth = derive_truth_state(
            canonical_sha=local_sha,
            remote_sha=remote_sha,
            remote_available=remote_available,
            source_conflict=False,
            critical_blocker_count=critical_blockers,
        )
        development = collect_development_status(fetch_remote=False)
        development["controller"] = control_state
        development["reserved_maximum_usd"] = (control_state.get("active") or {}).get("reserved_maximum_usd")
        development["actual_cost_usd"] = (control_state.get("active") or {}).get("actual_cost_usd")
        development["current_task"] = (control_state.get("active") or {}).get("current_task_id")
        development["current_package"] = (control_state.get("active") or {}).get("task_ids")
        development["execution_route"] = (control_state.get("active") or {}).get("execution_route")
        development["model"] = (control_state.get("active") or {}).get("model")
        development["run_state"] = control_state.get("state")
        development["warning_80_percent"] = development.get("dev_ai_cost_usd", 0) >= development.get("initial_openai_dev_envelope_usd", 10) * 0.8
        development["astra_enabled"] = False

        total = len(board["tasks"])
        complete = sum(task["status"] == "DONE" for task in board["tasks"])
        owner_gate_count = len(board["owner_gates"])
        result = {
            "schema_version": "dilivox-project-control-snapshot-v1",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "truth_state": truth,
            "canonical_profit_engine_sha": remote_sha or local_sha,
            "local_origin_sha": local_sha,
            "remote_origin_sha": remote_sha,
            "github_control_state": github_state,
            "github_actor": github_actor,
            "github_error": github_error,
            "ci": ci,
            "current_milestone": board["current_milestone"],
            "current_stage": board["current_stage"],
            "completed_tasks": complete,
            "required_tasks": total,
            "critical_blocker_count": critical_blockers,
            "owner_gate_count": owner_gate_count,
            "stages": board["stages"],
            "critical_path": board["critical_path"],
            "tasks": board["tasks"],
            "owner_gates": board["owner_gates"],
            "history": board["history"],
            "adaptive_funnel": {
                "packages": [
                    {"package": "AF-0", "state": "BLOCKED_EXTERNAL", "dependencies": ["TASK-013-PRODUCTION-SITE-INSTRUMENTATION-AND-GOALS", "TASK-015-FIRST-PARTY-EVENT-ENDPOINT"], "policy": "MEASUREMENT_TRUTH", "experiment": None, "kill_switch": "NOT_APPLICABLE", "fallback": "STATIC_EDITORIAL_FALLBACK", "evidence": "PARTIAL_PROVIDER_ONLY", "feature_roi": None},
                    {"package": "AF-1", "state": "NOT_STARTED", "dependencies": [], "policy": "DETERMINISTIC_CONTENT_GRAPH", "experiment": None, "kill_switch": "NOT_APPLICABLE", "fallback": "STATIC_EDITORIAL", "evidence": "NO_DATA", "feature_roi": None},
                    {"package": "AF-2", "state": "NOT_STARTED", "dependencies": ["AF-1"], "policy": "RULE_POLICY_V0.1", "experiment": None, "kill_switch": "REQUIRED_BEFORE_LIVE", "fallback": "STATIC_EDITORIAL_FALLBACK", "evidence": "NO_DATA", "feature_roi": None},
                    {"package": "AF-3", "state": "BLOCKED_EXTERNAL", "dependencies": ["AF-0", "AF-2"], "policy": "CONTROL_VS_RULE_BASED", "experiment": "NOT_STARTED", "kill_switch": "REQUIRED", "fallback": "STATIC_EDITORIAL_FALLBACK", "evidence": "NO_DATA", "feature_roi": None},
                    {"package": "AF-4", "state": "BLOCKED_DATA", "dependencies": ["AF-3"], "policy": "FEATURE_PROFIT_GATE", "experiment": "NOT_STARTED", "kill_switch": "PRESERVE", "fallback": "STATIC_EDITORIAL_FALLBACK", "evidence": "NOT_YET_PROVEN", "feature_roi": None},
                ],
                "production_ai": "OFF",
                "recommendation": "HOLD_UNTIL_AF0_TRUTH",
            },
            "content": {
                "catalog_count": "~50",
                "current_gate": "50_MEASUREMENT_LAB",
                "next_gate": "150_GENRE_ECONOMICS",
                "clusters": "AWAITING_TASK_016",
                "series": "AWAITING_TASK_016",
                "wave_state": "NOT_AUTHORIZED",
                "wave_cost": None,
                "incremental_revenue": None,
                "feature_roi": None,
                "next_wave_recommendation": "HOLD_UNTIL_AF4_EVIDENCE",
            },
            "providers_compliance": {
                "direct": "RECORDED_LIVE_READ_PASS",
                "metrica": "RECORDED_LIVE_PROVIDER_PASS",
                "yan": "RECORDED_LIVE_TECHNICAL_PASS",
                "tilda_instrumentation": "NOT_LIVE_VERIFIED",
                "privacy": "OWNER_GATE",
                "first_party_endpoint": "NOT_DEPLOYED",
                "reconciliation": "REVIEW_REQUIRED",
                "compliance": "YAN_CLARIFICATION_BLOCKING_SCALE",
            },
            "development": development,
            "provider_write_allowed": False,
            "auto_paid_retry": False,
            "auto_merge": False,
            "auto_deploy": False,
            "mutable_task_database": False,
        }
        return result

    def tasks(self) -> list[dict[str, Any]]:
        return self.snapshot(fetch_remote=False)["tasks"]

    def task(self, task_id: str) -> dict[str, Any] | None:
        return next((task for task in self.tasks() if task["task_id"] == task_id), None)
