from __future__ import annotations

import json
import unittest

from profit_engine_runtime.github_control import (
    BOUNDED_WORKFLOW,
    CANONICAL_BRANCH,
    G0_SMOKE_WORKFLOW,
    GITHUB_REPOSITORY,
    CommandResult,
    GhCliControlAdapter,
    GitHubControlError,
)


class FakeRunner:
    def __init__(self) -> None:
        self.commands: list[tuple[str, ...]] = []
        self.run_list_count = 0

    def __call__(self, args):
        command = tuple(args)
        self.commands.append(command)
        if command[:3] == ("gh", "api", "user"):
            return CommandResult(0, "niknikdym-hue\n", "")
        if command[:3] == ("gh", "workflow", "run"):
            return CommandResult(0, "", "")
        if command[:3] == ("gh", "run", "list"):
            self.run_list_count += 1
            if self.run_list_count == 1:
                return CommandResult(0, "[]", "")
            payload = [{
                "databaseId": 123,
                "status": "queued",
                "conclusion": None,
                "headSha": "a" * 40,
                "headBranch": "profit-engine",
                "createdAt": "2099-01-01T00:00:00Z",
                "updatedAt": "2099-01-01T00:00:00Z",
                "url": "https://github.com/niknikdym-hue/Dilivox-1/actions/runs/123",
                "displayTitle": "DILIVOX bounded dev · request-12345678",
                "event": "workflow_dispatch",
                "workflowName": "Profit Engine",
            }]
            return CommandResult(0, json.dumps(payload), "")
        if command[:3] == ("gh", "run", "cancel"):
            return CommandResult(0, "", "")
        if command[:3] == ("gh", "run", "view"):
            return CommandResult(0, json.dumps({
                "databaseId": 123, "status": "completed", "conclusion": "success",
                "headSha": "a" * 40, "headBranch": "profit-engine",
                "createdAt": "2099-01-01T00:00:00Z", "updatedAt": "2099-01-01T00:01:00Z",
                "url": "https://github.com/niknikdym-hue/Dilivox-1/actions/runs/123",
                "displayTitle": "bounded", "event": "workflow_dispatch",
                "workflowName": "Profit Engine", "jobs": [],
            }), "")
        if command[:3] == ("gh", "pr", "list"):
            return CommandResult(0, json.dumps([{
                "number": 42, "url": "https://github.com/niknikdym-hue/Dilivox-1/pull/42",
                "state": "OPEN", "isDraft": True, "title": "bounded result",
                "headRefName": "brain/project-control-request-12345678", "baseRefName": "profit-engine",
            }]), "")
        if command[:3] == ("gh", "pr", "view"):
            return CommandResult(0, json.dumps({
                "headRefOid": "b" * 40,
                "files": [{"path": "profit-engine/runtime/example.py"}],
                "statusCheckRollup": [{"name": "test", "status": "COMPLETED", "conclusion": "SUCCESS"}],
                "reviewDecision": "", "mergeStateStatus": "CLEAN",
            }), "")
        if command[:2] == ("gh", "api") and "git/ref/heads/profit-engine" in command[2]:
            return CommandResult(0, "a" * 40 + "\n", "")
        return CommandResult(1, "", "unexpected command")

class GitHubControlAdapterTests(unittest.TestCase):
    def test_paid_dispatch_uses_only_fixed_repo_branch_workflow_and_fields(self) -> None:
        runner = FakeRunner()
        adapter = GhCliControlAdapter(runner=runner, sleep=lambda _: None)
        result = adapter.dispatch_start(
            task_id="TASK-017-NEXT-CONTENT-DECISION-CORE",
            request_id="request-12345678",
            base_sha="a" * 40,
            execution_route="G2",
            hard_cap_usd="1.50",
            package_id="package-12345678",
        )
        self.assertEqual("DISPATCHED", result["state"])
        dispatch = next(command for command in runner.commands if command[:3] == ("gh", "workflow", "run"))
        self.assertIn(BOUNDED_WORKFLOW, dispatch)
        self.assertIn(GITHUB_REPOSITORY, dispatch)
        self.assertIn(CANONICAL_BRANCH, dispatch)
        self.assertNotIn("main", dispatch)
        self.assertFalse(any("token" in part.lower() for part in dispatch))

    def test_g0_smoke_uses_only_existing_free_preflight(self) -> None:
        runner = FakeRunner()
        adapter = GhCliControlAdapter(runner=runner, sleep=lambda _: None)
        adapter.dispatch_start(
            task_id="TASK-020-G0-SMOKE",
            request_id="request-12345678",
            base_sha="a" * 40,
            execution_route="G0",
            hard_cap_usd="0.00",
        )
        dispatch = next(command for command in runner.commands if command[:3] == ("gh", "workflow", "run"))
        self.assertIn(G0_SMOKE_WORKFLOW, dispatch)
        self.assertNotIn(BOUNDED_WORKFLOW, dispatch)
        self.assertFalse(any(part.startswith("hard_cap_usd=") for part in dispatch))

    def test_arbitrary_workflow_branch_and_bad_identity_fail_closed(self) -> None:
        adapter = GhCliControlAdapter(runner=FakeRunner(), sleep=lambda _: None)
        with self.assertRaises(GitHubControlError):
            adapter.workflow_runs("attacker.yml")
        with self.assertRaises(GitHubControlError):
            adapter.branch_sha("main")
        with self.assertRaises(GitHubControlError):
            adapter.dispatch_start(
                task_id="../../shell",
                request_id="request-12345678",
                base_sha="a" * 40,
                execution_route="G2",
                hard_cap_usd="1.00",
            )

    def test_stop_cancels_exact_positive_run_only(self) -> None:
        runner = FakeRunner()
        adapter = GhCliControlAdapter(runner=runner)
        adapter.cancel_run(123)
        self.assertIn(("gh", "run", "cancel", "123", "--repo", GITHUB_REPOSITORY), runner.commands)
        with self.assertRaises(GitHubControlError):
            adapter.cancel_run(0)

    def test_auth_failure_is_redacted_and_never_returns_credentials(self) -> None:
        def failed(args):
            return CommandResult(1, "", "Authorization: Bearer secret-value token=abc")
        adapter = GhCliControlAdapter(runner=failed)
        with self.assertRaises(GitHubControlError) as caught:
            adapter.actor()
        self.assertNotIn("secret-value", caught.exception.detail)
        self.assertNotIn("token=abc", caught.exception.detail)

    def test_review_result_is_exact_branch_base_and_redacted_summary(self) -> None:
        adapter = GhCliControlAdapter(runner=FakeRunner())
        value = adapter.review_result("brain/project-control-request-12345678")
        self.assertEqual(42, value["number"])
        self.assertTrue(value["is_draft"])
        self.assertEqual(["profit-engine/runtime/example.py"], value["files_changed"])
        self.assertFalse(value["auto_merge"])


if __name__ == "__main__":
    unittest.main()
