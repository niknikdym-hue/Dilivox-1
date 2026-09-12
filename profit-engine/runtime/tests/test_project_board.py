from __future__ import annotations

import unittest

from profit_engine_runtime.project_board import (
    STATUS_VOCABULARY,
    build_project_board,
    derive_truth_state,
    validate_projection,
)


class ProjectBoardTests(unittest.TestCase):
    def test_projection_covers_every_canonical_task_with_unique_ids(self) -> None:
        validate_projection()
        board = build_project_board()
        ids = [task["task_id"] for task in board["tasks"]]
        self.assertEqual(len(ids), len(set(ids)))
        task_files = [task["task_file"] for task in board["tasks"] if task["task_file"]]
        self.assertEqual(24, len(task_files))
        self.assertEqual(24, len(set(task_files)))
        self.assertFalse(board["mutable_task_database"])

    def test_all_stages_and_status_vocabulary_are_complete(self) -> None:
        board = build_project_board()
        self.assertEqual(["A", "B", "C", "D", "E"], [stage["stage_id"] for stage in board["stages"]])
        self.assertTrue(all(stage["required_tasks"] > 0 for stage in board["stages"]))
        self.assertTrue(all(task["status"] in STATUS_VOCABULARY for task in board["tasks"]))
        self.assertEqual(sorted(STATUS_VOCABULARY), board["status_vocabulary"])

    def test_completed_work_remains_visible_in_history(self) -> None:
        board = build_project_board()
        history = {task["task_id"] for task in board["history"]}
        self.assertIn("TASK-001-LOCAL-BOOTSTRAP-M0", history)
        self.assertIn("TASK-021-CODEX-DEVELOPMENT-EXECUTOR", history)
        self.assertGreaterEqual(len(history), 15)

    def test_critical_path_is_dependency_ordered_and_honest(self) -> None:
        board = build_project_board()
        orders = [task["critical_order"] for task in board["critical_path"]]
        self.assertEqual(orders, sorted(orders))
        self.assertEqual("TASK-013-PRODUCTION-SITE-INSTRUMENTATION-AND-GOALS", board["critical_path"][0]["task_id"])
        self.assertEqual("OWNER_GATE", board["critical_path"][0]["status"])
        self.assertFalse(board["critical_path"][0]["start_eligible"])

    def test_ci_does_not_upgrade_live_or_economic_truth(self) -> None:
        runtime = {
            "TASK-016-ADAPTIVE-BASELINE-CONTENT-MAP": {
                "ci_state": "SUCCESS",
                "status": "CODE_READY",
            }
        }
        task = next(
            task for task in build_project_board(runtime_tasks=runtime)["tasks"]
            if task["task_id"] == "TASK-016-ADAPTIVE-BASELINE-CONTENT-MAP"
        )
        self.assertEqual("CODE_READY", task["status"])
        self.assertEqual("NOT_CLAIMED", task["live_provider_state"])
        self.assertEqual("NOT_CLAIMED", task["live_site_state"])
        self.assertEqual("NOT_PROVEN", task["economic_state"])

    def test_truth_state_fails_closed_for_stale_conflict_and_blocker(self) -> None:
        sha = "a" * 40
        self.assertEqual("CURRENT", derive_truth_state(
            canonical_sha=sha, remote_sha=sha, remote_available=True,
            source_conflict=False, critical_blocker_count=0,
        ))
        self.assertEqual("STALE", derive_truth_state(
            canonical_sha=sha, remote_sha=None, remote_available=False,
            source_conflict=False, critical_blocker_count=0,
        ))
        self.assertEqual("CONFLICT", derive_truth_state(
            canonical_sha=sha, remote_sha="b" * 40, remote_available=True,
            source_conflict=False, critical_blocker_count=0,
        ))
        self.assertEqual("BLOCKED", derive_truth_state(
            canonical_sha=sha, remote_sha=sha, remote_available=True,
            source_conflict=False, critical_blocker_count=1,
        ))

    def test_g0_smoke_is_free_but_nontrivial_tasks_respect_quality_floor(self) -> None:
        tasks = {task["task_id"]: task for task in build_project_board()["tasks"]}
        smoke = tasks["TASK-020-G0-SMOKE"]
        self.assertEqual("G0", smoke["execution_route"])
        self.assertEqual("0.00", smoke["hard_cap_usd"])
        self.assertTrue(smoke["start_eligible"])
        self.assertEqual("G1", tasks["TASK-016-ADAPTIVE-BASELINE-CONTENT-MAP"]["execution_route"])
        self.assertEqual("G2", tasks["TASK-017-NEXT-CONTENT-DECISION-CORE"]["execution_route"])
        self.assertEqual("G3", tasks["TASK-020-OWNER-CONTROL-PANEL-V2"]["execution_route"])


if __name__ == "__main__":
    unittest.main()
