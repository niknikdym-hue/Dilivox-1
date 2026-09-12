from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
import re
import subprocess
import time
from typing import Any, Callable, Mapping, Sequence


GITHUB_REPOSITORY = "niknikdym-hue/Dilivox-1"
OWNER_ACTOR = "niknikdym-hue"
CANONICAL_BRANCH = "profit-engine"
BOUNDED_WORKFLOW = "profit-engine-bounded-dev-task.yml"
G0_SMOKE_WORKFLOW = "profit-engine-dev-preflight.yml"
OWNER_GATE_WORKFLOW = "profit-engine-owner-gate-evidence.yml"
STATUS_WORKFLOWS = frozenset({BOUNDED_WORKFLOW, G0_SMOKE_WORKFLOW, OWNER_GATE_WORKFLOW, "profit-engine-ci.yml"})
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
REQUEST_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{7,79}$")
TASK_ID_RE = re.compile(r"^(?:TASK|MILESTONE)-[A-Z0-9][A-Z0-9-]{2,79}$")


class GitHubControlError(RuntimeError):
    def __init__(self, code: str, detail: str):
        super().__init__(detail)
        self.code = code
        self.detail = detail


@dataclass(frozen=True)
class CommandResult:
    returncode: int
    stdout: str
    stderr: str


Runner = Callable[[Sequence[str]], CommandResult]


def _default_runner(args: Sequence[str]) -> CommandResult:
    completed = subprocess.run(
        list(args),
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )
    return CommandResult(completed.returncode, completed.stdout, completed.stderr)


def _safe_detail(value: str) -> str:
    compact = " ".join(value.replace("\x00", "").split())
    compact = re.sub(r"(?i)authorization\s*[:=]\s*(?:bearer\s+)?\S+", "authorization=[REDACTED]", compact)
    compact = re.sub(r"(?i)(token|password|secret)\s*[:=]\s*\S+", r"\1=[REDACTED]", compact)
    return compact[:500]


class GhCliControlAdapter:
    """Fixed-scope server-side adapter; no token or arbitrary command reaches the browser."""

    def __init__(self, *, runner: Runner = _default_runner, sleep: Callable[[float], None] = time.sleep):
        self._runner = runner
        self._sleep = sleep

    def _run(self, args: Sequence[str], *, error_code: str = "GITHUB_CONTROL_FAILED") -> str:
        result = self._runner(args)
        if result.returncode != 0:
            detail = _safe_detail(result.stderr or result.stdout or "GitHub CLI command failed")
            if "auth" in detail.lower() or "login" in detail.lower() or "credential" in detail.lower():
                raise GitHubControlError("GITHUB_CONTROL_NOT_CONFIGURED", detail)
            raise GitHubControlError(error_code, detail)
        return result.stdout

    def actor(self) -> str:
        value = self._run(
            ("gh", "api", "user", "--jq", ".login"),
            error_code="GITHUB_CONTROL_NOT_CONFIGURED",
        ).strip()
        if value != OWNER_ACTOR:
            raise GitHubControlError("GITHUB_OWNER_ACTOR_REQUIRED", "Authenticated GitHub actor is not the repository Owner.")
        return value

    def canonical_sha(self) -> str:
        value = self._run((
            "gh", "api", f"repos/{GITHUB_REPOSITORY}/git/ref/heads/{CANONICAL_BRANCH}", "--jq", ".object.sha",
        )).strip()
        if not SHA_RE.fullmatch(value):
            raise GitHubControlError("GITHUB_INVALID_SHA", "GitHub returned an invalid canonical SHA.")
        return value

    def workflow_runs(self, workflow: str = BOUNDED_WORKFLOW, *, limit: int = 30) -> list[dict[str, Any]]:
        if workflow not in STATUS_WORKFLOWS:
            raise GitHubControlError("GITHUB_WORKFLOW_NOT_ALLOWED", "Workflow is outside the fixed allowlist.")
        raw = self._run((
            "gh", "run", "list", "--repo", GITHUB_REPOSITORY,
            "--workflow", workflow, "--branch", CANONICAL_BRANCH,
            "--limit", str(min(max(limit, 1), 50)),
            "--json", "databaseId,status,conclusion,headSha,headBranch,createdAt,updatedAt,url,displayTitle,event,workflowName",
        ))
        try:
            rows = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise GitHubControlError("GITHUB_INVALID_RESPONSE", "GitHub run list was not valid JSON.") from exc
        if not isinstance(rows, list):
            raise GitHubControlError("GITHUB_INVALID_RESPONSE", "GitHub run list had an unexpected shape.")
        return [self._safe_run(row) for row in rows if isinstance(row, dict)]

    @staticmethod
    def _safe_run(row: Mapping[str, Any]) -> dict[str, Any]:
        return {
            "run_id": row.get("databaseId"),
            "status": row.get("status"),
            "conclusion": row.get("conclusion"),
            "head_sha": row.get("headSha"),
            "head_branch": row.get("headBranch"),
            "created_at": row.get("createdAt"),
            "updated_at": row.get("updatedAt"),
            "url": row.get("url"),
            "display_title": row.get("displayTitle"),
            "event": row.get("event"),
            "workflow_name": row.get("workflowName"),
        }

    def run(self, run_id: int) -> dict[str, Any]:
        if not isinstance(run_id, int) or run_id <= 0:
            raise GitHubControlError("GITHUB_INVALID_RUN_ID", "Run ID must be a positive integer.")
        raw = self._run((
            "gh", "run", "view", str(run_id), "--repo", GITHUB_REPOSITORY,
            "--json", "databaseId,status,conclusion,headSha,headBranch,createdAt,updatedAt,url,displayTitle,event,workflowName,jobs",
        ))
        try:
            row = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise GitHubControlError("GITHUB_INVALID_RESPONSE", "GitHub run response was not valid JSON.") from exc
        safe = self._safe_run(row)
        safe["jobs"] = [
            {
                "name": job.get("name"),
                "status": job.get("status"),
                "conclusion": job.get("conclusion"),
                "started_at": job.get("startedAt"),
                "completed_at": job.get("completedAt"),
            }
            for job in (row.get("jobs") or [])
            if isinstance(job, dict)
        ]
        return safe

    def dispatch_start(
        self,
        *,
        task_id: str,
        request_id: str,
        base_sha: str,
        execution_route: str,
        hard_cap_usd: str,
        package_id: str | None = None,
    ) -> dict[str, Any]:
        self.actor()
        if not TASK_ID_RE.fullmatch(task_id):
            raise GitHubControlError("GITHUB_TASK_NOT_ALLOWED", "Task ID failed the canonical allowlist.")
        if not REQUEST_ID_RE.fullmatch(request_id):
            raise GitHubControlError("GITHUB_INVALID_REQUEST_ID", "Request ID failed validation.")
        if package_id is not None and not REQUEST_ID_RE.fullmatch(package_id):
            raise GitHubControlError("GITHUB_INVALID_PACKAGE_ID", "Package ID failed validation.")
        if not SHA_RE.fullmatch(base_sha):
            raise GitHubControlError("GITHUB_INVALID_SHA", "Base SHA failed validation.")
        if execution_route not in {"G0", "G1", "G2", "G3", "G4"}:
            raise GitHubControlError("GITHUB_ROUTE_NOT_ALLOWED", "Execution route failed validation.")
        try:
            hard_cap = float(hard_cap_usd)
        except (TypeError, ValueError) as exc:
            raise GitHubControlError("GITHUB_INVALID_CAP", "Hard cap must be numeric.") from exc
        if hard_cap < 0 or hard_cap > 3:
            raise GitHubControlError("GITHUB_INVALID_CAP", "Hard cap must be within the accepted $0..$3 package bound.")

        started = datetime.now(timezone.utc)
        if task_id == "TASK-020-G0-SMOKE":
            workflow = G0_SMOKE_WORKFLOW
            args = (
                "gh", "workflow", "run", workflow, "--repo", GITHUB_REPOSITORY,
                "--ref", CANONICAL_BRANCH,
            )
        else:
            workflow = BOUNDED_WORKFLOW
            args = (
                "gh", "workflow", "run", workflow, "--repo", GITHUB_REPOSITORY,
                "--ref", CANONICAL_BRANCH,
                "-f", f"task_id={task_id}",
                "-f", f"request_id={request_id}",
                "-f", f"base_sha={base_sha}",
                "-f", f"execution_route={execution_route}",
                "-f", f"hard_cap_usd={hard_cap_usd}",
                "-f", f"package_id={package_id or request_id}",
            )
        baseline_ids = {
            row["run_id"] for row in self.workflow_runs(workflow, limit=10)
            if isinstance(row.get("run_id"), int)
        }
        self._run(args, error_code="GITHUB_DISPATCH_FAILED")

        for _ in range(4):
            discovered = self.discover_dispatched_run(
                workflow=workflow,
                request_id=request_id,
                not_before=started.isoformat(),
                baseline_run_ids=baseline_ids,
            )
            if discovered:
                return {"state": "DISPATCHED", "workflow": workflow, **discovered}
            self._sleep(0.5)
        return {
            "state": "DISPATCHED_RUN_PENDING_DISCOVERY",
            "workflow": workflow,
            "request_id": request_id,
            "not_before": started.isoformat(),
            "baseline_run_ids": sorted(baseline_ids),
            "run_id": None,
            "status": "queued",
            "conclusion": None,
            "created_at": started.isoformat(),
        }

    def discover_dispatched_run(
        self,
        *,
        workflow: str,
        request_id: str,
        not_before: str,
        baseline_run_ids: set[int] | list[int] | tuple[int, ...],
    ) -> dict[str, Any] | None:
        if workflow not in {BOUNDED_WORKFLOW, G0_SMOKE_WORKFLOW}:
            raise GitHubControlError("GITHUB_WORKFLOW_NOT_ALLOWED", "Dispatch discovery workflow is outside the fixed allowlist.")
        if not REQUEST_ID_RE.fullmatch(request_id):
            raise GitHubControlError("GITHUB_INVALID_REQUEST_ID", "Dispatch discovery request ID failed validation.")
        try:
            threshold = datetime.fromisoformat(not_before.replace("Z", "+00:00"))
        except (AttributeError, ValueError) as exc:
            raise GitHubControlError("GITHUB_INVALID_RESPONSE", "Dispatch discovery timestamp is invalid.") from exc
        if threshold.tzinfo is None:
            threshold = threshold.replace(tzinfo=timezone.utc)
        excluded = {value for value in baseline_run_ids if isinstance(value, int) and value > 0}
        candidates: list[dict[str, Any]] = []
        for row in self.workflow_runs(workflow, limit=10):
            run_id = row.get("run_id")
            created_raw = row.get("created_at")
            if not isinstance(run_id, int) or run_id in excluded or not isinstance(created_raw, str):
                continue
            try:
                created = datetime.fromisoformat(created_raw.replace("Z", "+00:00"))
            except ValueError:
                continue
            if created < threshold.replace(microsecond=0):
                continue
            if workflow == BOUNDED_WORKFLOW and request_id not in str(row.get("display_title") or ""):
                continue
            candidates.append(row)
        if not candidates:
            return None
        candidates.sort(key=lambda row: str(row.get("created_at")), reverse=True)
        return candidates[0]

    def cancel_run(self, run_id: int) -> None:
        if not isinstance(run_id, int) or run_id <= 0:
            raise GitHubControlError("GITHUB_INVALID_RUN_ID", "Run ID must be a positive integer.")
        self.actor()
        self._run(("gh", "run", "cancel", str(run_id), "--repo", GITHUB_REPOSITORY), error_code="GITHUB_CANCEL_FAILED")

    def dispatch_owner_decision(
        self,
        *,
        gate_id: str,
        task_id: str,
        decision: str,
        scope_digest: str,
        canonical_sha: str,
        request_id: str,
    ) -> None:
        self.actor()
        if not re.fullmatch(r"OWNER-GATE::(?:TASK|MILESTONE)-[A-Z0-9-]{3,100}", gate_id):
            raise GitHubControlError("GITHUB_GATE_NOT_ALLOWED", "Owner Gate ID failed validation.")
        if not TASK_ID_RE.fullmatch(task_id) or decision not in {"APPROVE", "REJECT", "DEFER"}:
            raise GitHubControlError("GITHUB_GATE_NOT_ALLOWED", "Owner Gate task/decision failed validation.")
        if not re.fullmatch(r"[0-9a-f]{64}", scope_digest) or not SHA_RE.fullmatch(canonical_sha):
            raise GitHubControlError("GITHUB_GATE_NOT_ALLOWED", "Owner Gate binding failed validation.")
        if not REQUEST_ID_RE.fullmatch(request_id):
            raise GitHubControlError("GITHUB_INVALID_REQUEST_ID", "Owner Gate request ID failed validation.")
        self._run((
            "gh", "workflow", "run", OWNER_GATE_WORKFLOW, "--repo", GITHUB_REPOSITORY,
            "--ref", CANONICAL_BRANCH,
            "-f", f"gate_id={gate_id}", "-f", f"task_id={task_id}", "-f", f"decision={decision}",
            "-f", f"scope_digest={scope_digest}", "-f", f"canonical_sha={canonical_sha}", "-f", f"request_id={request_id}",
        ), error_code="GITHUB_OWNER_GATE_EVIDENCE_FAILED")

    def branch_sha(self, branch: str) -> str:
        self._validate_work_branch(branch)
        value = self._run(("gh", "api", f"repos/{GITHUB_REPOSITORY}/git/ref/heads/{branch}", "--jq", ".object.sha")).strip()
        if not SHA_RE.fullmatch(value):
            raise GitHubControlError("GITHUB_INVALID_SHA", "GitHub returned an invalid work-branch SHA.")
        return value

    @staticmethod
    def _validate_work_branch(branch: str) -> None:
        expected_prefix = "brain/project-control-"
        if not isinstance(branch, str) or not branch.startswith(expected_prefix) or not re.fullmatch(r"[A-Za-z0-9._/-]{10,120}", branch):
            raise GitHubControlError("GITHUB_BRANCH_NOT_ALLOWED", "Work branch is outside the derived project-control namespace.")

    def review_result(self, branch: str) -> dict[str, Any] | None:
        """Return a redacted Draft-PR result for one derived control branch."""

        self._validate_work_branch(branch)
        raw = self._run((
            "gh", "pr", "list", "--repo", GITHUB_REPOSITORY,
            "--head", branch, "--base", CANONICAL_BRANCH, "--state", "all", "--limit", "1",
            "--json", "number,url,state,isDraft,title,headRefName,baseRefName",
        ))
        try:
            rows = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise GitHubControlError("GITHUB_INVALID_RESPONSE", "GitHub PR list was not valid JSON.") from exc
        if not isinstance(rows, list) or not rows:
            return None
        summary = rows[0]
        if not isinstance(summary, dict) or summary.get("headRefName") != branch or summary.get("baseRefName") != CANONICAL_BRANCH:
            raise GitHubControlError("GITHUB_INVALID_RESPONSE", "GitHub PR identity did not match the exact control branch.")
        number = summary.get("number")
        if not isinstance(number, int) or number <= 0:
            raise GitHubControlError("GITHUB_INVALID_RESPONSE", "GitHub PR number was invalid.")
        detail_raw = self._run((
            "gh", "pr", "view", str(number), "--repo", GITHUB_REPOSITORY,
            "--json", "headRefOid,files,statusCheckRollup,reviewDecision,mergeStateStatus",
        ))
        try:
            detail = json.loads(detail_raw)
        except json.JSONDecodeError as exc:
            raise GitHubControlError("GITHUB_INVALID_RESPONSE", "GitHub PR detail was not valid JSON.") from exc
        files = [
            str(row.get("path")) for row in (detail.get("files") or [])
            if isinstance(row, dict) and isinstance(row.get("path"), str)
        ]
        checks = [
            {
                "name": row.get("name") or row.get("context"),
                "status": row.get("status") or row.get("state"),
                "conclusion": row.get("conclusion"),
            }
            for row in (detail.get("statusCheckRollup") or []) if isinstance(row, dict)
        ]
        return {
            "number": number,
            "url": summary.get("url"),
            "title": summary.get("title"),
            "state": summary.get("state"),
            "is_draft": summary.get("isDraft"),
            "head_sha": detail.get("headRefOid"),
            "files_changed": files,
            "checks": checks,
            "review_decision": detail.get("reviewDecision"),
            "merge_state": detail.get("mergeStateStatus"),
            "auto_merge": False,
            "auto_deploy": False,
        }
