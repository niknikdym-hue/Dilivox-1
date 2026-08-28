from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import StrEnum
from hashlib import sha256
import json
from typing import Sequence

from .direct_controller import PRODUCTION_WRITER_ENABLED, REAL_PROVIDER_REQUESTS
from .models import DiagnosticResult, DoctorStatus


ACCEPTED_TASK_011R_SHA = "a494d30b49c8d11687be56cdab870a5d83356e02"
ADVERTISING_SPEND = 0
REQUIRED_PROVIDERS = ("direct", "metrica", "yan_statistics")


class DirectPermissionState(StrEnum):
    UNKNOWN = "UNKNOWN"
    READING = "READING"
    EDITING = "EDITING"


class Day12ReadinessState(StrEnum):
    BLOCKED_CONTROLLER_ACCEPTANCE = "BLOCKED_CONTROLLER_ACCEPTANCE"
    BLOCKED_OWNER_PERMISSION = "BLOCKED_OWNER_PERMISSION"
    BLOCKED_PROVIDER_CERTIFICATION = "BLOCKED_PROVIDER_CERTIFICATION"
    READY_FOR_LIVE_CANDIDATE_SELECTION = "READY_FOR_LIVE_CANDIDATE_SELECTION"


def _digest(value: object) -> str:
    return sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    ).hexdigest()


@dataclass(frozen=True)
class Day12LaunchReadiness:
    readiness_version: str
    state: Day12ReadinessState
    reasons: tuple[str, ...]
    direct_permission: DirectPermissionState
    controller_sha: str
    provider_statuses: tuple[tuple[str, str], ...]
    real_provider_requests: int
    advertising_spend: int
    production_writer_enabled: bool
    provider_write_allowed: bool
    readiness_digest: str

    @property
    def integrity_valid(self) -> bool:
        value = asdict(self)
        recorded = value.pop("readiness_digest")
        return recorded == _digest(value)


def build_day12_launch_readiness(
    *,
    direct_permission: DirectPermissionState,
    diagnostics: Sequence[DiagnosticResult],
    controller_sha: str = ACCEPTED_TASK_011R_SHA,
) -> Day12LaunchReadiness:
    by_provider = {item.provider: item for item in diagnostics}
    statuses = tuple(
        (name, by_provider[name].status.value if name in by_provider else DoctorStatus.NOT_ATTEMPTED.value)
        for name in REQUIRED_PROVIDERS
    )

    reasons: list[str] = []
    if controller_sha != ACCEPTED_TASK_011R_SHA:
        state = Day12ReadinessState.BLOCKED_CONTROLLER_ACCEPTANCE
        reasons.append("accepted_task_011r_sha_mismatch")
    elif direct_permission != DirectPermissionState.EDITING:
        state = Day12ReadinessState.BLOCKED_OWNER_PERMISSION
        reasons.append("direct_editing_permission_not_confirmed")
    elif any(status != DoctorStatus.PASS.value for _, status in statuses):
        state = Day12ReadinessState.BLOCKED_PROVIDER_CERTIFICATION
        for provider, status in statuses:
            if status != DoctorStatus.PASS.value:
                reasons.append(f"{provider}:{status}")
    else:
        state = Day12ReadinessState.READY_FOR_LIVE_CANDIDATE_SELECTION

    core = {
        "readiness_version": "1.0",
        "state": state,
        "reasons": tuple(reasons),
        "direct_permission": direct_permission,
        "controller_sha": controller_sha,
        "provider_statuses": statuses,
        "real_provider_requests": REAL_PROVIDER_REQUESTS,
        "advertising_spend": ADVERTISING_SPEND,
        "production_writer_enabled": PRODUCTION_WRITER_ENABLED,
        "provider_write_allowed": False,
    }
    return Day12LaunchReadiness(**core, readiness_digest=_digest(core))
