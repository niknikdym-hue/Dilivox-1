from __future__ import annotations

import argparse
from collections import defaultdict, deque
import json
import re
import secrets
import subprocess
import threading
import time
from http.server import ThreadingHTTPServer
from typing import Any
from urllib.parse import unquote, urlparse

from . import control_panel as legacy
from .development_controller import DevelopmentControlError, DevelopmentController
from .github_control import GitHubControlError
from .project_control import ProjectControlService
from .project_control_ui import render_project_html


MAX_COMMAND_BODY_BYTES = 64 * 1024
BURST_WINDOW_SECONDS = 5.0
BURST_MAX_COMMANDS = 10
TASK_PATH_RE = re.compile(r"^/api/project/task/([A-Z0-9:-][A-Z0-9._:-]{2,119})$")
GATE_PATH_RE = re.compile(r"^/api/owner-gates/([^/]{3,180})/decision$")


def _profit_html(csrf_token: str) -> str:
    html = legacy.HTML
    html = html.replace(
        '<meta name="viewport" content="width=device-width,initial-scale=1">',
        '<meta name="viewport" content="width=device-width,initial-scale=1"><meta name="pe-csrf" content="' + csrf_token + '">',
        1,
    )
    old = "headers:{'Content-Type':'application/json'},body:JSON.stringify(payload||{})"
    new = "headers:{'Content-Type':'application/json','X-Profit-Engine-CSRF':document.querySelector('meta[name=\"pe-csrf\"]').content},body:JSON.stringify(payload||{})"
    if old not in html:
        raise RuntimeError("legacy Profit refresh marker changed; fail closed")
    return html.replace(old, new, 1)


class BurstLimiter:
    def __init__(self, *, now: Any = time.monotonic):
        self.now = now
        self._events: dict[tuple[str, str], deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()

    def admit(self, client: str, path: str) -> bool:
        current = float(self.now())
        key = (client, path)
        with self._lock:
            events = self._events[key]
            while events and current - events[0] > BURST_WINDOW_SECONDS:
                events.popleft()
            if len(events) >= BURST_MAX_COMMANDS:
                return False
            events.append(current)
            return True


class Handler(legacy.Handler):
    server_version = "ProfitEngineOwnerControl/3.0"
    session_token = secrets.token_urlsafe(32)
    backend_instance_id = secrets.token_hex(12)
    limiter = BurstLimiter()
    project_service: ProjectControlService = ProjectControlService()

    def _headers(self, content_type: str, length: int) -> None:
        self.send_header("Content-Type", content_type)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Security-Policy", "default-src 'self'; connect-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Content-Length", str(length))

    def _json(self, value: dict[str, Any] | list[Any], status: int = 200) -> None:
        body = json.dumps(value, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self._headers("application/json; charset=utf-8", len(body))
        self.end_headers()
        self.wfile.write(body)

    def _html(self, value: str) -> None:
        body = value.encode("utf-8")
        self.send_response(200)
        self._headers("text/html; charset=utf-8", len(body))
        self.end_headers()
        self.wfile.write(body)

    def _redirect(self, target: str) -> None:
        self.send_response(303)
        self.send_header("Location", target)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", "0")
        self.end_headers()

    def _expected_origin(self) -> str:
        port = int(self.server.server_address[1])
        return f"http://{legacy.HOST}:{port}"

    def _authorize_command(self) -> None:
        origin = self.headers.get("Origin")
        if origin != self._expected_origin():
            raise DevelopmentControlError("ORIGIN_REJECTED", "State-changing requests require the exact localhost Origin.", 403)
        if self.headers.get("X-Profit-Engine-CSRF") != self.session_token:
            raise DevelopmentControlError("CSRF_REJECTED", "Per-launch session boundary failed.", 403)
        content_type = self.headers.get("Content-Type", "").split(";", 1)[0].strip().lower()
        if content_type != "application/json":
            raise DevelopmentControlError("JSON_ONLY", "State-changing requests accept application/json only.", 415)
        client = self.client_address[0] if self.client_address else ""
        if client != legacy.HOST:
            raise DevelopmentControlError("LOCALHOST_ONLY", "Project Control accepts local clients only.", 403)
        if not self.limiter.admit(client, self.path):
            raise DevelopmentControlError("COMMAND_RATE_LIMITED", "Too many repeated commands; wait before retrying.", 429)

    def _request_json(self) -> dict[str, Any]:
        raw_length = self.headers.get("Content-Length")
        try:
            length = int(raw_length or "0")
        except ValueError as exc:
            raise DevelopmentControlError("INVALID_CONTENT_LENGTH", "Invalid Content-Length.", 400) from exc
        if length <= 0 or length > MAX_COMMAND_BODY_BYTES:
            raise DevelopmentControlError("INVALID_COMMAND_SIZE", "JSON command must be within 1..65536 bytes.", 413)
        raw = self.rfile.read(length).decode("utf-8")
        try:
            value = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise DevelopmentControlError("INVALID_JSON", "Command body is not valid JSON.", 400) from exc
        if not isinstance(value, dict):
            raise DevelopmentControlError("INVALID_JSON_SHAPE", "Command body must be a JSON object.", 400)
        return value

    @staticmethod
    def _bounded_text(value: Any, field: str, *, maximum: int = 180) -> str:
        if not isinstance(value, str) or not value or len(value) > maximum:
            raise DevelopmentControlError("INVALID_COMMAND_FIELD", f"{field} is missing or out of bounds.", 400)
        return value

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path == "/":
            self._redirect("/profit")
            return
        if path == "/profit":
            self._html(_profit_html(self.session_token))
            return
        if path == "/project":
            self._html(render_project_html(self.session_token))
            return
        if path == "/api/health":
            self._json({
                "state": "READY",
                "backend_instance_id": self.backend_instance_id,
                "host": legacy.HOST,
                "profit_route": "/profit",
                "project_route": "/project",
                "one_backend": True,
                "provider_write_allowed": False,
            })
            return
        if path in {"/api/snapshot", "/api/profit/snapshot"}:
            self._json(legacy.load_snapshot())
            return
        if path == "/api/project/snapshot":
            # Read-only reconciliation advances queued/running/result lifecycle
            # in the visible panel without a manual GitHub visit.
            self._json(self.project_service.snapshot(fetch_remote=False, reconcile=True))
            return
        if path == "/api/project/tasks":
            self._json(self.project_service.tasks())
            return
        match = TASK_PATH_RE.fullmatch(path)
        if match:
            task = self.project_service.task(match.group(1))
            if task is None:
                self._json({"error": "not_found"}, 404)
            else:
                self._json(task)
            return
        self._json({"error": "not_found"}, 404)

    def _dispatch_post(self, path: str, request: dict[str, Any]) -> dict[str, Any]:
        controller: DevelopmentController = self.project_service.controller
        if path in {"/api/refresh", "/api/profit/refresh"}:
            return legacy.collect_snapshot(
                days=request.get("days"),
                date_from=request.get("date_from"),
                date_to=request.get("date_to"),
            )
        if path == "/api/project/refresh":
            return self.project_service.snapshot(fetch_remote=True, reconcile=True)
        if path == "/api/development/start":
            return controller.start(
                task_id=self._bounded_text(request.get("task_id"), "task_id"),
                request_id=self._bounded_text(request.get("request_id"), "request_id"),
                route_override=request.get("route_override"),
            )
        if path == "/api/development/package/start":
            task_ids = request.get("task_ids")
            if not isinstance(task_ids, list) or not all(isinstance(value, str) for value in task_ids):
                raise DevelopmentControlError("INVALID_PACKAGE", "task_ids must be an ordered JSON array.", 400)
            return controller.start_package(
                task_ids=task_ids,
                request_id=self._bounded_text(request.get("request_id"), "request_id"),
                route_override=request.get("route_override"),
            )
        if path in {"/api/development/pause", "/api/development/resume", "/api/development/stop"}:
            values = {
                "/api/development/pause": controller.pause,
                "/api/development/resume": controller.resume,
                "/api/development/stop": controller.stop,
            }
            return values[path](
                active_id=self._bounded_text(request.get("active_id"), "active_id"),
                request_id=self._bounded_text(request.get("request_id"), "request_id"),
            )
        gate_match = GATE_PATH_RE.fullmatch(path)
        if gate_match:
            gate_id = unquote(gate_match.group(1))
            return controller.decide_owner_gate(
                gate_id=gate_id,
                decision=self._bounded_text(request.get("decision"), "decision", maximum=12),
                request_id=self._bounded_text(request.get("request_id"), "request_id"),
                evidence_note=str(request.get("evidence_note") or ""),
            )
        raise DevelopmentControlError("COMMAND_NOT_ALLOWED", "No such allowlisted Project Control command.", 404)

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        try:
            self._authorize_command()
            request = self._request_json()
            self._json(self._dispatch_post(path, request))
        except DevelopmentControlError as exc:
            self._json({"state": "REJECTED", "code": exc.code, "detail": exc.detail}, exc.status)
        except GitHubControlError as exc:
            self._json({"state": "REJECTED", "code": exc.code, "detail": exc.detail}, 409)
        except (ValueError, json.JSONDecodeError) as exc:
            self._json({"state": "REJECTED", "code": "INVALID_REQUEST", "detail": str(exc)}, 400)
        except Exception:
            self._json({
                "state": "FAILED_CLOSED",
                "code": "INTERNAL_CONTROL_ERROR",
                "detail": "The bounded command failed without granting any broader authority.",
                "provider_write_allowed": False,
            }, 500)


def _open_two_windows() -> None:
    script = r'''
on ensureWindow(targetUrl)
  tell application "Safari"
    repeat with existingWindow in windows
      repeat with existingTab in tabs of existingWindow
        if URL of existingTab starts with targetUrl then
          set current tab of existingWindow to existingTab
          set index of existingWindow to 1
          return
        end if
      end repeat
    end repeat
    make new document with properties {URL:targetUrl}
  end tell
end ensureWindow
tell application "Safari"
  my ensureWindow("http://127.0.0.1:8765/profit")
  my ensureWindow("http://127.0.0.1:8765/project")
  activate
end tell
'''
    completed = subprocess.run(("/usr/bin/osascript", "-e", script), check=False, timeout=20)
    if completed.returncode != 0:
        subprocess.run(("/usr/bin/open", "http://127.0.0.1:8765/profit"), check=False)
        subprocess.run(("/usr/bin/open", "http://127.0.0.1:8765/project"), check=False)


def serve(*, port: int = legacy.PORT, open_two_windows: bool = False) -> None:
    if legacy.HOST != "127.0.0.1":
        raise RuntimeError("Owner Control must bind only 127.0.0.1")
    server = ThreadingHTTPServer((legacy.HOST, port), Handler)
    if open_two_windows:
        threading.Timer(0.5, _open_two_windows).start()
    print(f"Profit Engine backend: http://{legacy.HOST}:{port}")
    print("Windows: /profit + /project / one backend / provider writes: LOCKED / 0")
    server.serve_forever()


def main() -> int:
    parser = argparse.ArgumentParser(description="DILIVOX dual-window Owner Control")
    parser.add_argument("--port", type=int, default=legacy.PORT)
    parser.add_argument("--open", action="store_true", help="backward-compatible alias for --open-two")
    parser.add_argument("--open-two", action="store_true")
    parser.add_argument("--refresh-once", action="store_true")
    parser.add_argument("--project-snapshot", action="store_true")
    parser.add_argument("--days", type=int, default=legacy.DEFAULT_DAYS)
    parser.add_argument("--date-from")
    parser.add_argument("--date-to")
    args = parser.parse_args()
    if args.project_snapshot:
        print(json.dumps(Handler.project_service.snapshot(fetch_remote=False), ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    if args.refresh_once:
        print(json.dumps(legacy.collect_snapshot(
            days=None if args.date_from or args.date_to else args.days,
            date_from=args.date_from,
            date_to=args.date_to,
        ), ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    serve(port=args.port, open_two_windows=args.open or args.open_two)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
