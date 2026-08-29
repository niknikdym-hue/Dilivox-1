"""Day-12 production Direct writer.

This module is intentionally narrow. It can only perform one-object suspend/resume
mutations after the already accepted Day-12 readiness, candidate-selection and
controller-plan gates have passed. Budget writes are deliberately unavailable in
this production path: current Direct API budget control is strategy-aware and uses
WeeklySpendLimit rather than the legacy DailyBudget model.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from hashlib import sha256
import json
from typing import Any, Mapping

from .config import SiteConfig
from .day12_launch_gate import LiveCandidateSelection
from .day12_readiness import Day12LaunchReadiness, Day12ReadinessState, DirectPermissionState
from .direct_controller import ControllerPlan, ControllerState
from .models import HttpRequest, HttpResponse
from .transport import HttpTransport, TransportError, UrllibTransport


PRODUCTION_WRITER_DEFAULT_ENABLED = False
LIVE_WRITE_METHODS = frozenset({
    "campaign.suspend",
    "campaign.resume",
    "ad.suspend",
    "ad.resume",
})


def _digest(value: object) -> str:
    return sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    ).hexdigest()


@dataclass(frozen=True)
class ProductionWriterArm:
    arm_version: str
    readiness_digest: str
    selection_digest: str
    controller_plan_digest: str
    site_id: str
    provider: str
    target_ref: str
    provider_entity_id: str
    method: str
    max_dispatch_attempts: int
    prepared_at: str
    expires_at: str
    executable: bool
    armed: bool
    arm_digest: str

    @property
    def integrity_valid(self) -> bool:
        value = asdict(self)
        recorded = value.pop("arm_digest")
        return recorded == _digest(value)

    def live_at(self, now: datetime) -> bool:
        try:
            prepared = datetime.fromisoformat(self.prepared_at)
            expires = datetime.fromisoformat(self.expires_at)
        except ValueError:
            return False
        return prepared <= now < expires


def build_production_writer_arm(
    *,
    readiness: Day12LaunchReadiness,
    selection: LiveCandidateSelection,
    plan: ControllerPlan,
    prepared_at: datetime,
    expires_at: datetime,
    explicit_enable: bool = False,
) -> ProductionWriterArm:
    if not explicit_enable:
        raise ValueError("production writer requires explicit one-shot enable")
    if not readiness.integrity_valid:
        raise ValueError("day12 readiness integrity invalid")
    if readiness.state != Day12ReadinessState.READY_FOR_LIVE_CANDIDATE_SELECTION:
        raise ValueError("day12 readiness is not live-candidate ready")
    if readiness.direct_permission != DirectPermissionState.EDITING:
        raise ValueError("Direct Editing permission is required")
    if not selection.integrity_valid:
        raise ValueError("candidate selection integrity invalid")
    if not plan.integrity_valid or plan.state != ControllerState.READY_FOR_DAY12_EXECUTION:
        raise ValueError("controller plan is not Day12-ready")
    if selection.controller_plan_digest != plan.plan_digest:
        raise ValueError("candidate/plan digest mismatch")
    if selection.selection_digest == "" or selection.site_id != plan.target.site_id:
        raise ValueError("candidate is not bound to exact plan/site")
    if (
        selection.target_ref != plan.target.target_ref
        or selection.provider_entity_id != plan.target.provider_entity_id
        or selection.method != plan.method
    ):
        raise ValueError("candidate is not bound to exact target/method")
    if plan.method not in LIVE_WRITE_METHODS:
        raise ValueError("method is not enabled for first production write")
    if expires_at <= prepared_at:
        raise ValueError("production writer arm expiry must be after preparation")

    core = {
        "arm_version": "1.0",
        "readiness_digest": readiness.readiness_digest,
        "selection_digest": selection.selection_digest,
        "controller_plan_digest": plan.plan_digest,
        "site_id": plan.target.site_id,
        "provider": plan.target.provider,
        "target_ref": plan.target.target_ref,
        "provider_entity_id": plan.target.provider_entity_id,
        "method": plan.method,
        "max_dispatch_attempts": 1,
        "prepared_at": prepared_at.isoformat(),
        "expires_at": expires_at.isoformat(),
        "executable": True,
        "armed": True,
    }
    return ProductionWriterArm(**core, arm_digest=_digest(core))


@dataclass
class SingleAttemptDirectWriteTransport:
    """HTTP transport for mutations: exactly one network attempt, never a retry."""

    _transport: UrllibTransport = field(
        default_factory=lambda: UrllibTransport(max_attempts=1, backoff_seconds=0)
    )

    def send(self, request: HttpRequest) -> HttpResponse:
        if request.method != "POST":
            raise TransportError("Direct production writer permits POST only")
        if not request.url.startswith("https://api.direct.yandex.com/json/v501/"):
            raise TransportError("Direct production writer requires canonical v501 endpoint")
        return self._transport.send(request)


@dataclass(frozen=True)
class DirectMutationResult:
    method: str
    provider_entity_id: str
    http_status: int
    request_id: str | None
    units: str | None
    object_success: bool
    warnings: tuple[str, ...]
    errors: tuple[str, ...]


class YandexDirectProductionWriter:
    """One-object Direct suspend/resume writer with exact arm/plan binding."""

    def __init__(self, *, transport: HttpTransport, config: SiteConfig, enabled: bool = False):
        self.transport = transport
        self.config = config
        self.enabled = enabled
        self.dispatch_count = 0

    def dispatch_once(
        self,
        *,
        arm: ProductionWriterArm,
        plan: ControllerPlan,
        token: str,
        now: datetime,
    ) -> DirectMutationResult:
        self._validate_execution(arm=arm, plan=plan, token=token, now=now)
        if self.dispatch_count != 0:
            raise RuntimeError("production writer arm is one-shot and already consumed")

        service, method = _service_and_method(plan.method)
        provider_id = _provider_id(plan.target.provider_entity_id)
        request = HttpRequest(
            "POST",
            f"{self.config.direct_endpoint}/{service}",
            _headers(token, self.config),
            json_body={
                "method": method,
                "params": {"SelectionCriteria": {"Ids": [provider_id]}},
            },
        )
        self.dispatch_count += 1
        response = self.transport.send(request)
        return _parse_mutation_response(response, plan.method, provider_id)

    def read_back(
        self,
        *,
        plan: ControllerPlan,
        token: str,
        transport: HttpTransport,
    ) -> Mapping[str, Any]:
        if not token:
            raise ValueError("Direct OAuth token required")
        service, _ = _service_and_method(plan.method)
        provider_id = _provider_id(plan.target.provider_entity_id)
        collection = "Campaigns" if service == "campaigns" else "Ads"
        response = transport.send(HttpRequest(
            "POST",
            f"{self.config.direct_endpoint}/{service}",
            _headers(token, self.config),
            json_body={
                "method": "get",
                "params": {
                    "SelectionCriteria": {"Ids": [provider_id]},
                    "FieldNames": ["Id", "State", "Status"],
                    "Page": {"Limit": 1},
                },
            },
        ))
        if not 200 <= response.status_code < 300:
            raise TransportError("Direct read-back returned non-success status", status_code=response.status_code)
        body = response.json_body if isinstance(response.json_body, dict) else {}
        if body.get("error"):
            raise TransportError("Direct read-back returned top-level error", status_code=response.status_code)
        items = body.get("result", {}).get(collection, [])
        exact = next((item for item in items if item.get("Id") == provider_id), None)
        if exact is None:
            raise TransportError("Direct read-back did not return exact provider object")
        return {
            "provider_entity_id": str(provider_id),
            "normalized_state": str(exact.get("State", "UNKNOWN")),
            "status": str(exact.get("Status", "UNKNOWN")),
        }

    def _validate_execution(
        self,
        *,
        arm: ProductionWriterArm,
        plan: ControllerPlan,
        token: str,
        now: datetime,
    ) -> None:
        if not self.enabled:
            raise RuntimeError("production writer is disabled")
        if not token:
            raise ValueError("Direct OAuth token required")
        if not self.config.direct_client_login:
            raise ValueError("exact managed Direct target login required")
        if self.config.direct_operator_login and (
            self.config.direct_operator_login.casefold() == self.config.direct_client_login.casefold()
        ):
            raise ValueError("Direct operator and managed target must differ")
        if not arm.integrity_valid or not arm.armed or not arm.executable or not arm.live_at(now):
            raise ValueError("production writer arm invalid, inactive or expired")
        if arm.max_dispatch_attempts != 1:
            raise ValueError("production writer must be bounded to one dispatch attempt")
        if not plan.integrity_valid or plan.state != ControllerState.READY_FOR_DAY12_EXECUTION:
            raise ValueError("controller plan is not Day12-ready")
        if plan.method not in LIVE_WRITE_METHODS:
            raise ValueError("production writer does not permit this method")
        if (
            arm.controller_plan_digest != plan.plan_digest
            or arm.site_id != plan.target.site_id
            or arm.provider != plan.target.provider
            or arm.target_ref != plan.target.target_ref
            or arm.provider_entity_id != plan.target.provider_entity_id
            or arm.method != plan.method
        ):
            raise ValueError("production writer arm is not exactly bound to controller plan")


def _service_and_method(method: str) -> tuple[str, str]:
    if method not in LIVE_WRITE_METHODS:
        raise ValueError("unsupported live Direct mutation method")
    entity, action = method.split(".", 1)
    return ("campaigns" if entity == "campaign" else "ads", action)


def _provider_id(value: str) -> int:
    try:
        result = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("provider entity id must be an integer Direct id") from exc
    if result <= 0:
        raise ValueError("provider entity id must be positive")
    return result


def _headers(token: str, config: SiteConfig) -> dict[str, str]:
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept-Language": "en",
        "Content-Type": "application/json; charset=utf-8",
    }
    if config.direct_client_login:
        headers["Client-Login"] = config.direct_client_login
    return headers


def _parse_mutation_response(
    response: HttpResponse,
    method: str,
    provider_id: int,
) -> DirectMutationResult:
    body = response.json_body if isinstance(response.json_body, dict) else {}
    top_error = body.get("error")
    if top_error:
        return DirectMutationResult(
            method, str(provider_id), response.status_code, response.request_id,
            _header(response, "Units"), False, (), ("top_level_error",),
        )
    _, action = _service_and_method(method)
    result_key = "SuspendResults" if action == "suspend" else "ResumeResults"
    objects = body.get("result", {}).get(result_key, [])
    exact = next((item for item in objects if item.get("Id") == provider_id), None)
    if exact is None:
        return DirectMutationResult(
            method, str(provider_id), response.status_code, response.request_id,
            _header(response, "Units"), False, (), ("exact_object_result_missing",),
        )
    warnings = tuple(str(item.get("Code", "warning")) for item in (exact.get("Warnings") or []))
    errors = tuple(str(item.get("Code", "error")) for item in (exact.get("Errors") or []))
    success = 200 <= response.status_code < 300 and not errors
    return DirectMutationResult(
        method, str(provider_id), response.status_code, response.request_id,
        _header(response, "Units"), success, warnings, errors,
    )


def _header(response: HttpResponse, name: str) -> str | None:
    return next((value for key, value in response.headers.items() if key.lower() == name.lower()), None)
