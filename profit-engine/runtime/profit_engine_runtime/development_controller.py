from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
import hashlib
import json
from pathlib import Path
import re
import threading
from typing import Any, Callable, Mapping

from .development_status import collect_development_status
from .github_control import GhCliControlAdapter, GitHubControlError, REQUEST_ID_RE
from .project_board import STATUS_VOCABULARY, TASK_BY_ID, build_project_board


CONTROL_HOME = Path("~/.config/profit-engine/control-panel").expanduser()
EXECUTION_STATE_PATH = CONTROL_HOME / "development-control-v1.json"
OWNER_GATE_LEDGER_PATH = CONTROL_HOME / "owner-gate-decisions-v1.jsonl"
MAX_PACKAGE_TASKS = 5
MAX_IDEMPOTENCY_RECORDS = 80
ROUTE_RANK = {"G0": 0, "G1": 1, "G2": 2, "G3": 3, "G4": 4}
ROUTE_MODEL = {
    "G0": "none",
    "G1": "gpt-5.6-luna",
    "G2": "gpt-5.6-terra",
    "G3": "gpt-5.6-sol",
    "G4": "gpt-6-astra",
}
ROUTE_CAP = {"G0": Decimal("0.00"), "G1": Decimal("0.50"), "G2": Decimal("1.50"), "G3": Decimal("3.00")}


class DevelopmentControlError(RuntimeError):
    def __init__(self, code: str, detail: str, status: int = 409):
        super().__init__(detail)
        self.code = code
        self.detail = detail
        self.status = status


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _money(value: Any) -> Decimal:
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise DevelopmentControlError("INVALID_DEVELOPMENT_BUDGET", "Development budget must be an exact decimal.", 400) from exc
    if not amount.is_finite() or amount < 0:
        raise DevelopmentControlError("INVALID_DEVELOPMENT_BUDGET", "Development budget must be finite and non-negative.", 400)
    return amount.quantize(Decimal("0.01"))


def _payload_digest(command: str, payload: Mapping[str, Any]) -> str:
    material = json.dumps({"command": command, "payload": payload}, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(material.encode("utf-8")).hexdigest()


def _default_state() -> dict[str, Any]:
    return {
        "schema_version": "dilivox-development-control-v1",
        "state": "IDLE",
        "active": None,
        "last_result": None,
        "idempotency": [],
        "updated_at": None,
        "provider_write_allowed": False,
        "auto_paid_retry": False,
        "auto_merge": False,
        "auto_deploy": False,
    }


class DevelopmentController:
    """Orchestrates exact bounded GitHub workflows; it is not a mutable task database."""

    def __init__(
        self,
        *,
        adapter: GhCliControlAdapter | Any | None = None,
        state_path: Path = EXECUTION_STATE_PATH,
        gate_ledger_path: Path = OWNER_GATE_LEDGER_PATH,
        now: Callable[[], datetime] = _utc_now,
        development_status_loader: Callable[..., dict[str, Any]] = collect_development_status,
    ):
        self.adapter = adapter or GhCliControlAdapter()
        self.state_path = state_path
        self.gate_ledger_path = gate_ledger_path
        self.now = now
        self.development_status_loader = development_status_loader
        self._lock = threading.RLock()

    def _read_state(self) -> dict[str, Any]:
        if not self.state_path.exists():
            return _default_state()
        try:
            value = json.loads(self.state_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise DevelopmentControlError("DEVELOPMENT_STATE_INVALID", "Local development checkpoint is unreadable.") from exc
        if value.get("schema_version") != "dilivox-development-control-v1":
            raise DevelopmentControlError("DEVELOPMENT_STATE_INVALID", "Unsupported local development checkpoint version.")
        if value.get("provider_write_allowed") is not False:
            raise DevelopmentControlError("DEVELOPMENT_STATE_INVALID", "Provider-write boundary was violated in local state.")
        return value

    def _write_state(self, value: Mapping[str, Any]) -> None:
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        self.state_path.parent.chmod(0o700)
        tmp = self.state_path.with_suffix(".tmp")
        tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        tmp.chmod(0o600)
        tmp.replace(self.state_path)

    def state(self) -> dict[str, Any]:
        with self._lock:
            return self._read_state()

    def _idempotent(self, command: str, request_id: str, payload: Mapping[str, Any], operation: Callable[[dict[str, Any]], dict[str, Any]]) -> dict[str, Any]:
        if not isinstance(request_id, str) or not REQUEST_ID_RE.fullmatch(request_id):
            raise DevelopmentControlError("INVALID_REQUEST_ID", "request_id must be a bounded opaque identifier.", 400)
        digest = _payload_digest(command, payload)
        with self._lock:
            state = self._read_state()
            for record in state.get("idempotency") or []:
                if record.get("request_id") != request_id:
                    continue
                if record.get("digest") != digest or record.get("command") != command:
                    raise DevelopmentControlError("IDEMPOTENCY_CONFLICT", "request_id was already used for another exact command.")
                return dict(record.get("response") or {})
            response = operation(state)
            records = list(state.get("idempotency") or [])
            records.append({
                "request_id": request_id,
                "command": command,
                "digest": digest,
                "created_at": self.now().isoformat(),
                "response": response,
            })
            state["idempotency"] = records[-MAX_IDEMPOTENCY_RECORDS:]
            state["updated_at"] = self.now().isoformat()
            self._write_state(state)
            return response

    @staticmethod
    def _route(task: Mapping[str, Any], override: str | None) -> tuple[str, str, Decimal]:
        floor = str(task["execution_route"])
        requested = "AUTO" if override is None else str(override).upper()
        if requested == "AUTO":
            route = floor
        else:
            if requested not in ROUTE_RANK:
                raise DevelopmentControlError("INVALID_ROUTE_OVERRIDE", "Route override is outside G0-G4.", 400)
            if requested == "G4":
                raise DevelopmentControlError("ASTRA_OWNER_GATE", "Astra requires a separately explicit Owner authorization.")
            if floor == "G0" or ROUTE_RANK[requested] < ROUTE_RANK[floor]:
                raise DevelopmentControlError("QUALITY_FLOOR_DOWNGRADE_BLOCKED", "Owner route selection cannot downgrade the task quality floor.")
            route = requested
        if route == "G4":
            raise DevelopmentControlError("ASTRA_OWNER_GATE", "Astra cannot be auto-selected by the panel.")
        task_cap = _money(task["hard_cap_usd"])
        return route, ROUTE_MODEL[route], min(task_cap if task_cap else ROUTE_CAP[route], ROUTE_CAP[route])

    @staticmethod
    def _task_map(runtime_tasks: Mapping[str, Mapping[str, Any]] | None = None) -> dict[str, dict[str, Any]]:
        board = build_project_board(runtime_tasks=runtime_tasks)
        return {task["task_id"]: task for task in board["tasks"]}

    def _approved_gate(self, task: Mapping[str, Any], canonical_sha: str) -> bool:
        if not task.get("owner_gate"):
            return True
        latest: dict[str, Any] | None = None
        try:
            for record in self._gate_records():
                if record.get("gate_id") == task.get("owner_gate_id"):
                    latest = record
        except DevelopmentControlError:
            return False
        return bool(
            latest
            and latest.get("decision") == "APPROVE"
            and latest.get("scope_digest") == task.get("owner_gate_scope_digest")
            and latest.get("canonical_sha") == canonical_sha
        )

    def _gate_records(self) -> list[dict[str, Any]]:
        if not self.gate_ledger_path.exists():
            return []
        expected_previous = "0" * 64
        records: list[dict[str, Any]] = []
        try:
            lines = [line for line in self.gate_ledger_path.read_text(encoding="utf-8").splitlines() if line]
            for line in lines:
                record = json.loads(line)
                if not isinstance(record, dict) or record.get("schema_version") != "dilivox-owner-gate-decision-v1":
                    raise ValueError("invalid Owner Gate record shape")
                claimed_hash = record.get("record_hash")
                if record.get("previous_hash") != expected_previous or not isinstance(claimed_hash, str):
                    raise ValueError("broken Owner Gate chain")
                material_record = dict(record)
                material_record.pop("record_hash", None)
                material = json.dumps(material_record, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
                computed = hashlib.sha256(material.encode("utf-8")).hexdigest()
                if not re.fullmatch(r"[0-9a-f]{64}", claimed_hash) or computed != claimed_hash:
                    raise ValueError("invalid Owner Gate record hash")
                records.append(record)
                expected_previous = claimed_hash
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            raise DevelopmentControlError("OWNER_GATE_LEDGER_INVALID", "Owner Gate audit chain is invalid.") from exc
        return records

    def _validate_task_start(self, task: Mapping[str, Any], tasks: Mapping[str, Mapping[str, Any]], canonical_sha: str, package_predecessors: set[str]) -> None:
        if task["task_id"] not in TASK_BY_ID:
            raise DevelopmentControlError("UNKNOWN_TASK", "Task is not present in the canonical projection.", 404)
        if task["status"] == "DONE":
            raise DevelopmentControlError("TASK_ALREADY_DONE", "Completed work cannot be restarted as new paid work.")
        if task["status"] in {"BLOCKED_EXTERNAL", "BLOCKED_DATA"}:
            raise DevelopmentControlError("TASK_BLOCKED", "The selected task has an unresolved external/data blocker.")
        if task.get("owner_gate") and not self._approved_gate(task, canonical_sha):
            raise DevelopmentControlError("OWNER_GATE_REQUIRED", "The exact Owner Gate has not been approved for this canonical SHA.")
        terminal = {"DONE", "CODE_READY", "LIVE_PROVIDER_VERIFIED", "LIVE_SITE_VERIFIED", "ECONOMICALLY_PROVEN"}
        unresolved = [
            dependency for dependency in task["dependencies"]
            if dependency not in package_predecessors and tasks[dependency]["status"] not in terminal
        ]
        if unresolved:
            raise DevelopmentControlError("DEPENDENCIES_NOT_READY", "Task dependencies are not technically accepted: " + ", ".join(unresolved))
        if not task.get("task_file") and task["task_id"] != "TASK-020-G0-SMOKE":
            raise DevelopmentControlError("TASK_NOT_EXECUTABLE", "Milestone cards cannot be dispatched as development tasks.")
        if task["task_id"] != "TASK-020-G0-SMOKE" and not task.get("allowed_paths"):
            raise DevelopmentControlError("TASK_SCOPE_NOT_BOUND", "Task has no canonical allowed-path boundary.")

    def _budget_status(self) -> tuple[Decimal, Decimal]:
        status = self.development_status_loader(fetch_remote=False)
        accepted = _money(status.get("dev_ai_cost_usd", 0))
        remaining = _money(status.get("remaining_dev_envelope_usd", 0))
        if accepted + remaining > Decimal("10.00"):
            raise DevelopmentControlError("DEVELOPMENT_LEDGER_CONFLICT", "Accepted cost and remaining envelope conflict.")
        return accepted, remaining

    def start(self, *, task_id: str, request_id: str, route_override: str | None = None) -> dict[str, Any]:
        payload = {"task_id": task_id, "route_override": route_override or "AUTO"}

        def operation(state: dict[str, Any]) -> dict[str, Any]:
            if state.get("state") in {"RUNNING", "PAUSE_REQUESTED", "STOP_REQUESTED"}:
                raise DevelopmentControlError("DEVELOPMENT_ALREADY_ACTIVE", "Another exact development task/package is active.")
            tasks = self._task_map()
            task = tasks.get(task_id)
            if not task:
                raise DevelopmentControlError("UNKNOWN_TASK", "Task is not present in the canonical projection.", 404)
            canonical_sha = self.adapter.canonical_sha()
            self._validate_task_start(task, tasks, canonical_sha, set())
            route, model, cap = self._route(task, route_override)
            accepted, remaining = self._budget_status()
            if cap > remaining:
                raise DevelopmentControlError("DEVELOPMENT_ENVELOPE_EXHAUSTED", "The exact task cap exceeds the remaining accepted development envelope.")
            dispatch = self.adapter.dispatch_start(
                task_id=task_id,
                request_id=request_id,
                base_sha=canonical_sha,
                execution_route=route,
                hard_cap_usd=f"{cap:.2f}",
            )
            active = {
                "kind": "SINGLE",
                "request_id": request_id,
                "package_id": None,
                "task_ids": [task_id],
                "current_index": 0,
                "current_task_id": task_id,
                "completed_task_ids": [],
                "authority_base_sha": canonical_sha,
                "current_base_sha": canonical_sha,
                "work_branch": None if task_id == "TASK-020-G0-SMOKE" else f"brain/project-control-{request_id.lower()}",
                "execution_route": route,
                "model": model,
                "quality_floor": task["quality_floor"],
                "routing_reason": task["routing_reason"],
                "why_not_cheaper": task["why_not_cheaper"],
                "reserved_maximum_usd": f"{cap:.2f}",
                "actual_cost_usd": None,
                "accepted_dev_ai_cost_before_usd": f"{accepted:.2f}",
                "remaining_envelope_before_usd": f"{remaining:.2f}",
                "run": dispatch,
                "pause_after_current": False,
                "automatic_retry_count": 0,
                "checkpoint": None,
                "started_at": self.now().isoformat(),
                "latest_completed_action": "GitHub workflow dispatch accepted.",
                "current_action": "Waiting for bounded GitHub workflow.",
            }
            state.update({"state": "RUNNING", "active": active, "last_result": None})
            return {"state": "RUNNING", "active": active, "duplicate_dispatch": False}

        return self._idempotent("start", request_id, payload, operation)

    def start_package(self, *, task_ids: list[str], request_id: str, route_override: str | None = None) -> dict[str, Any]:
        payload = {"task_ids": task_ids, "route_override": route_override or "AUTO"}

        def operation(state: dict[str, Any]) -> dict[str, Any]:
            if state.get("state") in {"RUNNING", "PAUSE_REQUESTED", "STOP_REQUESTED"}:
                raise DevelopmentControlError("DEVELOPMENT_ALREADY_ACTIVE", "Another exact development task/package is active.")
            if not isinstance(task_ids, list) or not 1 <= len(task_ids) <= MAX_PACKAGE_TASKS or len(task_ids) != len(set(task_ids)):
                raise DevelopmentControlError("INVALID_PACKAGE", "A package must contain 1-5 unique ordered tasks.", 400)
            tasks = self._task_map()
            canonical_sha = self.adapter.canonical_sha()
            predecessors: set[str] = set()
            plan: list[dict[str, Any]] = []
            total_cap = Decimal("0")
            for task_id in task_ids:
                task = tasks.get(task_id)
                if not task:
                    raise DevelopmentControlError("UNKNOWN_TASK", f"Unknown task in package: {task_id}", 404)
                self._validate_task_start(task, tasks, canonical_sha, predecessors)
                route, model, cap = self._route(task, route_override)
                total_cap += cap
                plan.append({"task_id": task_id, "execution_route": route, "model": model, "hard_cap_usd": f"{cap:.2f}", "quality_floor": task["quality_floor"]})
                predecessors.add(task_id)
            accepted, remaining = self._budget_status()
            if total_cap > Decimal("3.00") or total_cap > remaining:
                raise DevelopmentControlError("PACKAGE_BUDGET_EXCEEDED", "Package reserved maximum exceeds its $3.00 or remaining-envelope bound.")
            first = plan[0]
            dispatch = self.adapter.dispatch_start(
                task_id=first["task_id"], request_id=request_id, base_sha=canonical_sha,
                execution_route=first["execution_route"], hard_cap_usd=first["hard_cap_usd"], package_id=request_id,
            )
            active = {
                "kind": "PACKAGE", "request_id": request_id, "package_id": request_id,
                "task_ids": list(task_ids), "plan": plan, "current_index": 0,
                "current_task_id": first["task_id"], "completed_task_ids": [],
                "authority_base_sha": canonical_sha, "current_base_sha": canonical_sha,
                "work_branch": f"brain/project-control-{request_id.lower()}",
                "execution_route": first["execution_route"], "model": first["model"],
                "quality_floor": first["quality_floor"], "reserved_maximum_usd": f"{total_cap:.2f}",
                "actual_cost_usd": None, "accepted_dev_ai_cost_before_usd": f"{accepted:.2f}",
                "remaining_envelope_before_usd": f"{remaining:.2f}", "run": dispatch,
                "pause_after_current": False, "automatic_retry_count": 0, "checkpoint": None,
                "started_at": self.now().isoformat(), "latest_completed_action": "First package task dispatched.",
                "current_action": "Waiting for the current bounded task before any next task.",
            }
            state.update({"state": "RUNNING", "active": active, "last_result": None})
            return {"state": "RUNNING", "active": active, "package_plan": plan, "duplicate_dispatch": False}

        return self._idempotent("start_package", request_id, payload, operation)

    def pause(self, *, active_id: str, request_id: str) -> dict[str, Any]:
        payload = {"active_id": active_id}

        def operation(state: dict[str, Any]) -> dict[str, Any]:
            active = state.get("active") or {}
            expected = active.get("package_id") or active.get("request_id")
            if state.get("state") != "RUNNING" or active_id != expected:
                raise DevelopmentControlError("ACTIVE_EXECUTION_MISMATCH", "Pause applies only to the exact active task/package.")
            active["pause_after_current"] = True
            active["current_action"] = "Pause requested; current bounded step may finish, no next task will start."
            state["state"] = "PAUSE_REQUESTED"
            return {"state": "PAUSE_REQUESTED", "active_id": expected, "run_id": (active.get("run") or {}).get("run_id")}

        return self._idempotent("pause", request_id, payload, operation)

    def stop(self, *, active_id: str, request_id: str) -> dict[str, Any]:
        payload = {"active_id": active_id}

        def operation(state: dict[str, Any]) -> dict[str, Any]:
            active = state.get("active") or {}
            expected = active.get("package_id") or active.get("request_id")
            if state.get("state") not in {"RUNNING", "PAUSE_REQUESTED", "PAUSED"} or active_id != expected:
                raise DevelopmentControlError("ACTIVE_EXECUTION_MISMATCH", "Stop applies only to the exact active task/package.")
            run_id = (active.get("run") or {}).get("run_id")
            if state.get("state") != "PAUSED" and isinstance(run_id, int):
                self.adapter.cancel_run(run_id)
                state["state"] = "STOP_REQUESTED"
                active["current_action"] = "Exact active GitHub run cancellation requested; no retry."
            else:
                state["state"] = "STOPPED"
                active["current_action"] = "Package stopped at its proven checkpoint."
            return {"state": state["state"], "active_id": expected, "run_id": run_id, "automatic_retry_count": 0}

        return self._idempotent("stop", request_id, payload, operation)

    def resume(self, *, active_id: str, request_id: str) -> dict[str, Any]:
        payload = {"active_id": active_id}

        def operation(state: dict[str, Any]) -> dict[str, Any]:
            active = state.get("active") or {}
            expected = active.get("package_id") or active.get("request_id")
            checkpoint = active.get("checkpoint") or {}
            if state.get("state") != "PAUSED" or active_id != expected:
                raise DevelopmentControlError("ACTIVE_EXECUTION_MISMATCH", "Resume applies only to the exact paused package.")
            if checkpoint.get("valid") is not True or checkpoint.get("completed_task_ids") != active.get("completed_task_ids"):
                raise DevelopmentControlError("VALID_CHECKPOINT_REQUIRED", "Resume requires an exact proven checkpoint.")
            if self.adapter.canonical_sha() != active.get("authority_base_sha"):
                raise DevelopmentControlError("AUTHORITY_BASE_MOVED", "Canonical authority moved; package cannot resume.")
            next_index = len(active.get("completed_task_ids") or [])
            if active.get("kind") != "PACKAGE" or next_index >= len(active.get("task_ids") or []):
                raise DevelopmentControlError("NOTHING_TO_RESUME", "No pending package task remains.")
            plan = active["plan"][next_index]
            base_sha = active.get("current_base_sha") or active["authority_base_sha"]
            dispatch = self.adapter.dispatch_start(
                task_id=plan["task_id"], request_id=f"{active['request_id']}:step{next_index + 1}",
                base_sha=base_sha, execution_route=plan["execution_route"], hard_cap_usd=plan["hard_cap_usd"], package_id=active["package_id"],
            )
            active.update({
                "current_index": next_index, "current_task_id": plan["task_id"], "execution_route": plan["execution_route"],
                "model": plan["model"], "quality_floor": plan["quality_floor"], "run": dispatch,
                "pause_after_current": False, "current_action": "Resumed from exact proven checkpoint.",
            })
            state["state"] = "RUNNING"
            return {"state": "RUNNING", "active": active, "resumed_from_checkpoint": True}

        return self._idempotent("resume", request_id, payload, operation)

    def refresh(self) -> dict[str, Any]:
        with self._lock:
            state = self._read_state()
            active = state.get("active") or {}
            if state.get("state") not in {"RUNNING", "PAUSE_REQUESTED", "STOP_REQUESTED"}:
                return state
            run_id = (active.get("run") or {}).get("run_id")
            if not isinstance(run_id, int):
                pending = active.get("run") or {}
                discovered = self.adapter.discover_dispatched_run(
                    workflow=str(pending.get("workflow") or ""),
                    request_id=str(pending.get("request_id") or active.get("request_id") or ""),
                    not_before=str(pending.get("not_before") or pending.get("created_at") or ""),
                    baseline_run_ids=pending.get("baseline_run_ids") or [],
                )
                if not discovered:
                    active["current_action"] = "GitHub accepted dispatch; run ID discovery is pending."
                    state["updated_at"] = self.now().isoformat()
                    self._write_state(state)
                    return state
                active["run"] = {"state": "DISPATCHED", "workflow": pending.get("workflow"), **discovered}
                run_id = discovered["run_id"]
            run = self.adapter.run(run_id)
            active["run"] = run
            if run.get("status") != "completed":
                active["current_action"] = "GitHub bounded step is " + str(run.get("status") or "running") + "."
                state["updated_at"] = self.now().isoformat()
                self._write_state(state)
                return state

            conclusion = str(run.get("conclusion") or "").lower()
            if state.get("state") == "STOP_REQUESTED" or conclusion == "cancelled":
                state["state"] = "STOPPED"
                active["current_action"] = "Exact run stopped; automatic retry remains disabled."
            elif conclusion != "success":
                state["state"] = "FAILED_CLOSED"
                active["current_action"] = "Bounded step failed; package stopped on first failure."
                state["last_result"] = {"state": "FAILED_CLOSED", "task_id": active.get("current_task_id"), "run": run}
            else:
                completed = list(active.get("completed_task_ids") or [])
                if active.get("current_task_id") not in completed:
                    completed.append(active.get("current_task_id"))
                active["completed_task_ids"] = completed
                active["latest_completed_action"] = f"{active.get('current_task_id')} technical workflow PASS."
                active["checkpoint"] = {
                    "valid": True,
                    "completed_task_ids": completed,
                    "run_id": run_id,
                    "authority_base_sha": active.get("authority_base_sha"),
                    "created_at": self.now().isoformat(),
                }
                review = None
                if active.get("work_branch") and hasattr(self.adapter, "review_result"):
                    try:
                        review = self.adapter.review_result(active["work_branch"])
                    except GitHubControlError as exc:
                        review = {"state": "PR_STATUS_UNAVAILABLE", "error": exc.code}
                active["review"] = review
                if active.get("kind") == "PACKAGE" and active.get("work_branch"):
                    try:
                        active["current_base_sha"] = self.adapter.branch_sha(active["work_branch"])
                    except GitHubControlError:
                        active["current_base_sha"] = active.get("current_base_sha")
                has_next = len(completed) < len(active.get("task_ids") or [])
                if active.get("pause_after_current") and has_next:
                    state["state"] = "PAUSED"
                    active["current_action"] = "Paused at a proven checkpoint before the next task."
                elif has_next:
                    if self.adapter.canonical_sha() != active.get("authority_base_sha"):
                        state["state"] = "AUTHORITY_MOVED_STOPPED"
                        active["current_action"] = "Canonical authority moved; package stopped before next spend."
                    else:
                        next_index = len(completed)
                        plan = active["plan"][next_index]
                        next_request_id = f"{active['request_id']}:step{next_index + 1}"
                        dispatch = self.adapter.dispatch_start(
                            task_id=plan["task_id"], request_id=next_request_id,
                            base_sha=active.get("current_base_sha") or active["authority_base_sha"],
                            execution_route=plan["execution_route"], hard_cap_usd=plan["hard_cap_usd"], package_id=active["package_id"],
                        )
                        active.update({
                            "current_index": next_index, "current_task_id": plan["task_id"], "execution_route": plan["execution_route"],
                            "model": plan["model"], "quality_floor": plan["quality_floor"], "run": dispatch,
                            "current_action": "Next package task dispatched after technical PASS.",
                        })
                        state["state"] = "RUNNING"
                else:
                    state["state"] = "READY_FOR_REVIEW"
                    active["current_action"] = "All bounded steps passed; result awaits Central Brain acceptance."
                    is_g0 = active.get("current_task_id") == "TASK-020-G0-SMOKE"
                    if is_g0:
                        active["actual_cost_usd"] = "0.00"
                    state["last_result"] = {
                        "state": "READY_FOR_REVIEW", "task_ids": active.get("task_ids"), "run": run,
                        "reserved_maximum_usd": active.get("reserved_maximum_usd"), "actual_cost_usd": active.get("actual_cost_usd"),
                        "provider_call_count": 0 if is_g0 else None,
                        "files_changed": [] if is_g0 else ((review or {}).get("files_changed") if isinstance(review, dict) else None),
                        "tests": run.get("jobs") or [],
                        "scope_result": "G0_READ_ONLY_PREFLIGHT" if is_g0 else "BOUNDED_WORKFLOW_PASS",
                        "draft_pr": review,
                        "unresolved_issues": ["Central Brain acceptance remains required."],
                        "automatic_retry_count": 0, "auto_merge": False, "auto_deploy": False,
                    }
            state["updated_at"] = self.now().isoformat()
            self._write_state(state)
            return state

    def decide_owner_gate(
        self,
        *,
        gate_id: str,
        decision: str,
        request_id: str,
        evidence_note: str = "",
    ) -> dict[str, Any]:
        payload = {"gate_id": gate_id, "decision": decision, "evidence_note": evidence_note}
        decision = str(decision).upper()

        def operation(state: dict[str, Any]) -> dict[str, Any]:
            if decision not in {"APPROVE", "REJECT", "DEFER"}:
                raise DevelopmentControlError("INVALID_OWNER_DECISION", "Owner decision must be APPROVE, REJECT or DEFER.", 400)
            if not isinstance(evidence_note, str) or len(evidence_note) > 1000:
                raise DevelopmentControlError("INVALID_EVIDENCE_NOTE", "Evidence note exceeds its bounded text limit.", 400)
            board = build_project_board()
            task = next((row for row in board["owner_gates"] if row.get("owner_gate_id") == gate_id), None)
            if not task:
                raise DevelopmentControlError("UNKNOWN_OWNER_GATE", "Owner Gate is not present in the canonical projection.", 404)
            canonical_sha = self.adapter.canonical_sha()
            previous_hash = "0" * 64
            records = self._gate_records()
            if records:
                previous_hash = records[-1]["record_hash"]
            record = {
                "schema_version": "dilivox-owner-gate-decision-v1",
                "gate_id": gate_id,
                "task_id": task["task_id"],
                "decision": decision,
                "scope_digest": task["owner_gate_scope_digest"],
                "canonical_sha": canonical_sha,
                "evidence_note": evidence_note.strip(),
                "request_id": request_id,
                "decided_at": self.now().isoformat(),
                "previous_hash": previous_hash,
            }
            material = json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
            record["record_hash"] = hashlib.sha256(material.encode("utf-8")).hexdigest()
            self.adapter.dispatch_owner_decision(
                gate_id=gate_id,
                task_id=task["task_id"],
                decision=decision,
                scope_digest=task["owner_gate_scope_digest"],
                canonical_sha=canonical_sha,
                request_id=request_id,
            )
            self.gate_ledger_path.parent.mkdir(parents=True, exist_ok=True)
            self.gate_ledger_path.parent.chmod(0o700)
            with self.gate_ledger_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
            self.gate_ledger_path.chmod(0o600)
            return {
                "state": "OWNER_DECISION_RECORDED",
                "gate_id": gate_id,
                "task_id": task["task_id"],
                "decision": decision,
                "scope_digest": task["owner_gate_scope_digest"],
                "canonical_sha": canonical_sha,
                "record_hash": record["record_hash"],
                "generic_authority_granted": False,
            }

        return self._idempotent("owner_gate_decision", request_id, payload, operation)
