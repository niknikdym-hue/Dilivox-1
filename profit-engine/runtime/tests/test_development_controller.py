from __future__ import annotations

from datetime import datetime, timezone
import tempfile
from pathlib import Path
import unittest

from profit_engine_runtime.development_controller import (
    DevelopmentControlError,
    DevelopmentController,
)


class FakeAdapter:
    def __init__(self) -> None:
        self.sha = "a" * 40
        self.dispatches = []
        self.cancelled = []
        self.owner_decisions = []
        self.run_result = {
            "run_id": 100,
            "status": "queued",
            "conclusion": None,
            "head_sha": self.sha,
            "head_branch": "profit-engine",
            "url": "https://github.com/niknikdym-hue/Dilivox-1/actions/runs/100",
        }

    def canonical_sha(self):
        return self.sha

    def dispatch_start(self, **kwargs):
        self.dispatches.append(kwargs)
        run_id = 100 + len(self.dispatches)
        return {
            "state": "DISPATCHED",
            "workflow": "fixture.yml",
            "run_id": run_id,
            "status": "queued",
            "conclusion": None,
        }

    def run(self, run_id):
        return {**self.run_result, "run_id": run_id}

    def cancel_run(self, run_id):
        self.cancelled.append(run_id)

    def branch_sha(self, branch):
        return "b" * 40

    def dispatch_owner_decision(self, **kwargs):
        self.owner_decisions.append(kwargs)


def dev_status(**kwargs):
    return {
        "dev_ai_cost_usd": 0.0,
        "remaining_dev_envelope_usd": 10.0,
    }


class DevelopmentControllerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        self.adapter = FakeAdapter()
        self.controller = DevelopmentController(
            adapter=self.adapter,
            state_path=root / "state.json",
            gate_ledger_path=root / "owner-gates.jsonl",
            now=lambda: datetime(2026, 9, 12, 12, 0, tzinfo=timezone.utc),
            development_status_loader=dev_status,
        )

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_start_dispatches_exact_task_once_even_on_double_click(self) -> None:
        first = self.controller.start(
            task_id="TASK-020-G0-SMOKE",
            request_id="request-12345678",
            route_override="AUTO",
        )
        second = self.controller.start(
            task_id="TASK-020-G0-SMOKE",
            request_id="request-12345678",
            route_override="AUTO",
        )
        self.assertEqual(first, second)
        self.assertEqual(1, len(self.adapter.dispatches))
        self.assertEqual("TASK-020-G0-SMOKE", self.adapter.dispatches[0]["task_id"])
        self.assertEqual("G0", self.adapter.dispatches[0]["execution_route"])
        self.assertEqual("0.00", self.adapter.dispatches[0]["hard_cap_usd"])

    def test_g0_success_returns_zero_cost_zero_provider_call_result(self) -> None:
        self.controller.start(
            task_id="TASK-020-G0-SMOKE",
            request_id="request-12345678",
        )
        self.adapter.run_result.update({"status": "completed", "conclusion": "success", "jobs": []})
        result = self.controller.refresh()
        self.assertEqual("READY_FOR_REVIEW", result["state"])
        self.assertEqual("0.00", result["last_result"]["actual_cost_usd"])
        self.assertEqual(0, result["last_result"]["provider_call_count"])
        self.assertEqual("G0_READ_ONLY_PREFLIGHT", result["last_result"]["scope_result"])

    def test_request_id_cannot_be_reused_for_different_start(self) -> None:
        self.controller.start(
            task_id="TASK-020-G0-SMOKE",
            request_id="request-12345678",
        )
        with self.assertRaises(DevelopmentControlError) as caught:
            self.controller.start(
                task_id="TASK-020-OWNER-CONTROL-PANEL-V2",
                request_id="request-12345678",
            )
        self.assertEqual("IDEMPOTENCY_CONFLICT", caught.exception.code)

    def test_blocked_and_owner_gate_tasks_cannot_start(self) -> None:
        with self.assertRaises(DevelopmentControlError) as blocked:
            self.controller.start(
                task_id="TASK-015-FIRST-PARTY-EVENT-ENDPOINT",
                request_id="request-12345678",
            )
        self.assertEqual("TASK_BLOCKED", blocked.exception.code)
        with self.assertRaises(DevelopmentControlError) as gated:
            self.controller.start(
                task_id="TASK-013-PRODUCTION-SITE-INSTRUMENTATION-AND-GOALS",
                request_id="request-87654321",
            )
        self.assertEqual("OWNER_GATE_REQUIRED", gated.exception.code)
        self.assertEqual([], self.adapter.dispatches)

    def test_quality_floor_rejects_downward_override_and_astra_auto(self) -> None:
        with self.assertRaises(DevelopmentControlError) as downgrade:
            self.controller.start(
                task_id="TASK-020-OWNER-CONTROL-PANEL-V2",
                request_id="request-12345678",
                route_override="G2",
            )
        self.assertEqual("QUALITY_FLOOR_DOWNGRADE_BLOCKED", downgrade.exception.code)
        with self.assertRaises(DevelopmentControlError) as astra:
            self.controller.start(
                task_id="TASK-020-OWNER-CONTROL-PANEL-V2",
                request_id="request-87654321",
                route_override="G4",
            )
        self.assertEqual("ASTRA_OWNER_GATE", astra.exception.code)

    def test_package_pauses_after_current_step_and_resumes_from_checkpoint(self) -> None:
        started = self.controller.start_package(
            task_ids=["TASK-020-G0-SMOKE", "TASK-020-OWNER-CONTROL-PANEL-V2"],
            request_id="package-12345678",
        )
        self.assertEqual(2, len(started["package_plan"]))
        self.controller.pause(active_id="package-12345678", request_id="pause-12345678")
        self.adapter.run_result.update({"status": "completed", "conclusion": "success"})
        paused = self.controller.refresh()
        self.assertEqual("PAUSED", paused["state"])
        self.assertTrue(paused["active"]["checkpoint"]["valid"])
        self.assertEqual(["TASK-020-G0-SMOKE"], paused["active"]["completed_task_ids"])
        resumed = self.controller.resume(active_id="package-12345678", request_id="resume-12345678")
        self.assertEqual("RUNNING", resumed["state"])
        self.assertTrue(resumed["resumed_from_checkpoint"])
        self.assertEqual(2, len(self.adapter.dispatches))
        self.assertEqual("TASK-020-OWNER-CONTROL-PANEL-V2", self.adapter.dispatches[-1]["task_id"])

    def test_package_stops_on_first_failure_without_retry(self) -> None:
        self.controller.start_package(
            task_ids=["TASK-020-G0-SMOKE", "TASK-020-OWNER-CONTROL-PANEL-V2"],
            request_id="package-12345678",
        )
        self.adapter.run_result.update({"status": "completed", "conclusion": "failure"})
        result = self.controller.refresh()
        self.assertEqual("FAILED_CLOSED", result["state"])
        self.assertEqual(1, len(self.adapter.dispatches))
        self.assertEqual(0, result["active"]["automatic_retry_count"])

    def test_stop_targets_exact_active_run_only(self) -> None:
        started = self.controller.start(
            task_id="TASK-020-G0-SMOKE",
            request_id="request-12345678",
        )
        run_id = started["active"]["run"]["run_id"]
        with self.assertRaises(DevelopmentControlError):
            self.controller.stop(active_id="wrong-active", request_id="stop-11111111")
        stopped = self.controller.stop(active_id="request-12345678", request_id="stop-22222222")
        self.assertEqual("STOP_REQUESTED", stopped["state"])
        self.assertEqual([run_id], self.adapter.cancelled)

    def test_owner_decision_is_exact_sha_scope_and_hash_linked(self) -> None:
        result = self.controller.decide_owner_gate(
            gate_id="OWNER-GATE::TASK-013-PRODUCTION-SITE-INSTRUMENTATION-AND-GOALS",
            decision="DEFER",
            request_id="gate-12345678",
            evidence_note="Publication remains deferred.",
        )
        self.assertEqual("OWNER_DECISION_RECORDED", result["state"])
        self.assertFalse(result["generic_authority_granted"])
        self.assertEqual(self.adapter.sha, result["canonical_sha"])
        self.assertEqual(1, len(self.adapter.owner_decisions))
        self.assertEqual(result["scope_digest"], self.adapter.owner_decisions[0]["scope_digest"])

    def test_tampered_owner_gate_chain_fails_closed(self) -> None:
        self.controller.decide_owner_gate(
            gate_id="OWNER-GATE::TASK-013-PRODUCTION-SITE-INSTRUMENTATION-AND-GOALS",
            decision="APPROVE",
            request_id="gate-12345678",
            evidence_note="Exact fixture approval.",
        )
        text = self.controller.gate_ledger_path.read_text(encoding="utf-8")
        self.controller.gate_ledger_path.write_text(text.replace("Exact fixture approval.", "tampered"), encoding="utf-8")
        with self.assertRaises(DevelopmentControlError) as caught:
            self.controller.start(
                task_id="TASK-013-PRODUCTION-SITE-INSTRUMENTATION-AND-GOALS",
                request_id="request-99999999",
            )
        self.assertEqual("OWNER_GATE_REQUIRED", caught.exception.code)


if __name__ == "__main__":
    unittest.main()
