from __future__ import annotations

from pathlib import Path
import unittest


class ProjectControlWorkflowContractTests(unittest.TestCase):
    def setUp(self) -> None:
        root = Path(__file__).resolve().parents[3]
        self.bounded = (root / ".github/workflows/profit-engine-bounded-dev-task.yml").read_text(encoding="utf-8")
        self.owner_gate = (root / ".github/workflows/profit-engine-owner-gate-evidence.yml").read_text(encoding="utf-8")
        self.ui = (root / "profit-engine/runtime/profit_engine_runtime/project_control_ui.py").read_text(encoding="utf-8")
        self.adapter = (root / "profit-engine/runtime/profit_engine_runtime/github_control.py").read_text(encoding="utf-8")

    def test_workflow_dispatch_is_exact_task_sha_route_and_package_bound(self) -> None:
        for field in ("task_id:", "request_id:", "base_sha:", "execution_route:", "hard_cap_usd:", "package_id:"):
            self.assertIn(field, self.bounded)
        self.assertIn("TASK_BY_ID", self.bounded)
        self.assertIn("build_project_board", self.bounded)
        self.assertIn("route would violate task quality floor", self.bounded)
        self.assertIn("brain/project-control-", self.bounded)
        self.assertIn("Cumulative work branch moved", self.bounded)

    def test_result_is_draft_review_only(self) -> None:
        self.assertIn("gh pr create", self.bounded)
        self.assertIn("--draft", self.bounded)
        self.assertNotIn("gh pr merge", self.bounded)
        self.assertNotIn("gh release", self.bounded)
        self.assertNotIn("deploy-pages", self.bounded)
        self.assertIn("auto_merge", self.bounded)
        self.assertIn("auto_deploy", self.bounded)

    def test_owner_gate_is_exact_scope_evidence_not_generic_authority(self) -> None:
        self.assertIn("scope_digest", self.owner_gate)
        self.assertIn("canonical_sha", self.owner_gate)
        self.assertIn("generic_authority_granted", self.owner_gate)
        self.assertIn("provider_write_allowed", self.owner_gate)
        self.assertIn("test \"$GITHUB_ACTOR\" = 'niknikdym-hue'", self.owner_gate)
        self.assertIn("build_project_board", self.owner_gate)
        self.assertIn("scope digest does not match canonical task", self.owner_gate)

    def test_browser_has_no_repo_workflow_or_shell_inputs(self) -> None:
        self.assertNotIn("repository:", self.ui)
        self.assertNotIn("workflow:", self.ui)
        self.assertNotIn("shell", self.ui.lower())
        self.assertIn("GITHUB_REPOSITORY = \"niknikdym-hue/Dilivox-1\"", self.adapter)
        self.assertIn("CANONICAL_BRANCH = \"profit-engine\"", self.adapter)
        self.assertIn("GITHUB_WORKFLOW_NOT_ALLOWED", self.adapter)


if __name__ == "__main__":
    unittest.main()
