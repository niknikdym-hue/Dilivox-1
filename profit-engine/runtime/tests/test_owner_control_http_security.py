from __future__ import annotations

import http.client
import json
import threading
import unittest

from profit_engine_runtime.owner_control_v2 import BurstLimiter, Handler
from http.server import ThreadingHTTPServer


class StubController:
    def __init__(self) -> None:
        self.calls = []

    def start(self, **kwargs):
        self.calls.append(("start", kwargs))
        return {"state": "RUNNING", "provider_write_allowed": False}

    def start_package(self, **kwargs):
        self.calls.append(("package", kwargs))
        return {"state": "RUNNING"}

    def pause(self, **kwargs):
        return {"state": "PAUSE_REQUESTED"}

    def resume(self, **kwargs):
        return {"state": "RUNNING"}

    def stop(self, **kwargs):
        return {"state": "STOP_REQUESTED"}

    def decide_owner_gate(self, **kwargs):
        return {"state": "OWNER_DECISION_RECORDED"}


class StubService:
    def __init__(self) -> None:
        self.controller = StubController()
        self.last_snapshot_args = None

    def snapshot(self, **kwargs):
        self.last_snapshot_args = kwargs
        return {
            "truth_state": "CURRENT",
            "tasks": [],
            "provider_write_allowed": False,
            "auto_merge": False,
            "auto_deploy": False,
        }

    def tasks(self):
        return []

    def task(self, task_id):
        return None


class OwnerControlHttpSecurityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.original_service = Handler.project_service
        self.original_limiter = Handler.limiter
        self.original_token = Handler.session_token
        Handler.project_service = StubService()
        Handler.limiter = BurstLimiter()
        Handler.session_token = "unit-test-csrf-token"
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.port = self.server.server_address[1]

    def tearDown(self) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)
        Handler.project_service = self.original_service
        Handler.limiter = self.original_limiter
        Handler.session_token = self.original_token

    def request(self, method, path, body=None, headers=None):
        connection = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        encoded = None if body is None else json.dumps(body)
        connection.request(method, path, body=encoded, headers=headers or {})
        response = connection.getresponse()
        raw = response.read()
        content_type = response.getheader("Content-Type") or ""
        value = json.loads(raw) if "application/json" in content_type else raw.decode("utf-8")
        connection.close()
        return response.status, value

    def auth_headers(self):
        return {
            "Origin": f"http://127.0.0.1:{self.port}",
            "X-Profit-Engine-CSRF": "unit-test-csrf-token",
            "Content-Type": "application/json",
        }

    def test_dual_routes_share_one_backend_health_identity(self) -> None:
        profit_status, profit = self.request("GET", "/profit")
        project_status, project = self.request("GET", "/project")
        health_status, health = self.request("GET", "/api/health")
        self.assertEqual((200, 200, 200), (profit_status, project_status, health_status))
        self.assertIn("Пульт прибыли", profit)
        self.assertIn("DILIVOX — Управление проектом", project)
        self.assertTrue(health["one_backend"])
        self.assertEqual("/profit", health["profit_route"])
        self.assertEqual("/project", health["project_route"])

    def test_project_snapshot_reconciles_lifecycle_without_remote_truth_refresh(self) -> None:
        status, _value = self.request("GET", "/api/project/snapshot")
        self.assertEqual(200, status)
        self.assertEqual(
            {"fetch_remote": False, "reconcile": True},
            Handler.project_service.last_snapshot_args,
        )

    def test_missing_and_foreign_origin_are_rejected(self) -> None:
        body = {"request_id": "request-12345678", "task_id": "TASK-020-G0-SMOKE"}
        status, value = self.request("POST", "/api/development/start", body, {
            "X-Profit-Engine-CSRF": "unit-test-csrf-token",
            "Content-Type": "application/json",
        })
        self.assertEqual(403, status)
        self.assertEqual("ORIGIN_REJECTED", value["code"])
        status, value = self.request("POST", "/api/development/start", body, {
            **self.auth_headers(),
            "Origin": "https://evil.example",
        })
        self.assertEqual(403, status)
        self.assertEqual("ORIGIN_REJECTED", value["code"])
        self.assertEqual([], Handler.project_service.controller.calls)

    def test_missing_csrf_and_non_json_are_rejected(self) -> None:
        headers = self.auth_headers()
        del headers["X-Profit-Engine-CSRF"]
        status, value = self.request("POST", "/api/project/refresh", {"request_id": "refresh-12345678"}, headers)
        self.assertEqual(403, status)
        self.assertEqual("CSRF_REJECTED", value["code"])
        headers = self.auth_headers()
        headers["Content-Type"] = "text/plain"
        status, value = self.request("POST", "/api/project/refresh", {"request_id": "refresh-87654321"}, headers)
        self.assertEqual(415, status)
        self.assertEqual("JSON_ONLY", value["code"])

    def test_valid_start_reaches_only_explicit_controller_method(self) -> None:
        status, value = self.request("POST", "/api/development/start", {
            "request_id": "request-12345678",
            "task_id": "TASK-020-G0-SMOKE",
            "route_override": "AUTO",
        }, self.auth_headers())
        self.assertEqual(200, status)
        self.assertEqual("RUNNING", value["state"])
        self.assertEqual("start", Handler.project_service.controller.calls[0][0])
        self.assertEqual("TASK-020-G0-SMOKE", Handler.project_service.controller.calls[0][1]["task_id"])

    def test_arbitrary_command_endpoint_is_absent(self) -> None:
        status, value = self.request("POST", "/api/command", {
            "request_id": "request-12345678",
            "command": "shell",
            "repository": "attacker/repo",
            "workflow": "evil.yml",
        }, self.auth_headers())
        self.assertEqual(404, status)
        self.assertEqual("COMMAND_NOT_ALLOWED", value["code"])

    def test_browser_payloads_never_contain_server_credentials(self) -> None:
        status, project = self.request("GET", "/project")
        self.assertEqual(200, status)
        for forbidden in ("OPENAI_API_KEY", "GITHUB_TOKEN", "ghp_", "github_pat_"):
            self.assertNotIn(forbidden, project)
        status, snapshot = self.request("GET", "/api/project/snapshot")
        self.assertEqual(200, status)
        material = json.dumps(snapshot)
        self.assertNotIn("unit-test-csrf-token", material)


if __name__ == "__main__":
    unittest.main()
