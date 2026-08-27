from __future__ import annotations

import json
import logging
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Protocol

from .models import HttpRequest, HttpResponse
from .redaction import safe_json


LOGGER = logging.getLogger("profit_engine.provider_http")


class TransportError(RuntimeError):
    def __init__(self, message: str, *, status_code: int | None = None, attempts: int = 1):
        super().__init__(message)
        self.status_code = status_code
        self.attempts = attempts


class HttpTransport(Protocol):
    def send(self, request: HttpRequest) -> HttpResponse: ...


@dataclass
class UrllibTransport:
    max_attempts: int = 3
    backoff_seconds: float = 0.2

    def send(self, request: HttpRequest) -> HttpResponse:
        if request.method not in {"GET", "POST"}:
            raise TransportError("runtime permits only GET and read-RPC POST")

        query = urllib.parse.urlencode(request.query, doseq=True)
        url = request.url + (("&" if "?" in request.url else "?") + query if query else "")
        body = None
        headers = dict(request.headers)
        if request.json_body is not None:
            body = json.dumps(request.json_body).encode("utf-8")
            headers.setdefault("Content-Type", "application/json")

        LOGGER.info(public_request_log(request))

        for attempt in range(1, self.max_attempts + 1):
            try:
                raw_request = urllib.request.Request(url, data=body, headers=headers, method=request.method)
                with urllib.request.urlopen(raw_request, timeout=request.timeout_seconds) as raw:
                    raw_body = raw.read()
                    response_headers = dict(raw.headers.items())
                    decoded = raw_body.decode("utf-8") if raw_body else ""
                    content_type = _header(response_headers, "Content-Type") or ""
                    if not decoded:
                        parsed = None
                    elif "json" in content_type.lower():
                        parsed = json.loads(decoded)
                    else:
                        try:
                            parsed = json.loads(decoded)
                        except json.JSONDecodeError:
                            parsed = decoded
                    request_id = _header(response_headers, "RequestId", "Request-Id", "X-Request-Id")
                    response = HttpResponse(
                        status_code=raw.status,
                        headers=response_headers,
                        json_body=parsed,
                        request_id=request_id,
                        attempts=attempt,
                    )
                    LOGGER.info(public_response_log(response))
                    return response
            except urllib.error.HTTPError as exc:
                if exc.code in {429, 500, 502, 503, 504} and attempt < self.max_attempts:
                    time.sleep(self.backoff_seconds * attempt)
                    continue
                raise TransportError(
                    f"provider HTTP error {exc.code}", status_code=exc.code, attempts=attempt
                ) from None
            except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
                if attempt < self.max_attempts:
                    time.sleep(self.backoff_seconds * attempt)
                    continue
                raise TransportError(
                    f"provider transport error: {type(exc).__name__}", attempts=attempt
                ) from None
        raise AssertionError("unreachable")


def _header(headers: dict[str, str], *names: str) -> str | None:
    lowered = {key.lower(): value for key, value in headers.items()}
    return next((lowered[name.lower()] for name in names if name.lower() in lowered), None)


def public_request_log(request: HttpRequest) -> str:
    """Return structured request metadata without query values or payload data."""
    return safe_json({
        "event": "provider_http_request",
        "method": request.method,
        "url": request.url,
        "headers": dict(request.headers),
        "has_query": bool(request.query),
        "has_json_body": request.json_body is not None,
    })


def public_response_log(response: HttpResponse) -> str:
    return safe_json({
        "event": "provider_http_response",
        "status_code": response.status_code,
        "request_id": response.request_id,
        "attempts": response.attempts,
    })
