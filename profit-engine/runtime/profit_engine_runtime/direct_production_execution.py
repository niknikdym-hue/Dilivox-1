"""Guarded Day-12 production execution for one reversible Direct mutation."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import StrEnum
from typing import Mapping, Sequence

from .config import SiteConfig
from .direct_controller import (
    AuditChain,
    ControllerPlan,
    ExecutionLockRegistry,
    KillSwitch,
    ProviderPreflightSnapshot,
    build_preflight,
    derive_expected_readback,
    pre_dispatch_snapshot_matches,
)
from .direct_production_writer import ProductionWriterArm, YandexDirectProductionWriter
from .models import HttpRequest
from .transport import HttpTransport, TransportError


class ProductionTerminalState(StrEnum):
    GUARDED_PRODUCTION_LAUNCHED = "GUARDED_PRODUCTION_LAUNCHED"
    PRODUCTION_WRITE_BLOCKED = "PRODUCTION_WRITE_BLOCKED"
    PRODUCTION_EXECUTION_UNCERTAIN = "PRODUCTION_EXECUTION_UNCERTAIN"


@dataclass(frozen=True)
class ProductionExecutionOutcome:
    state: ProductionTerminalState
    dispatch_attempts: int
    provider_read_attempts: int
    request_id: str | None
    units: str | None
    recovered_from_uncertain_transport: bool
    audit_valid: bool


class YandexDirectLiveStateReader:
    """Exact read-only state reader for the already bound Direct target."""

    def __init__(self, *, transport: HttpTransport, config: SiteConfig):
        self.transport = transport
        self.config = config
        self.read_count = 0

    def preflight(
        self,
        *,
        plan: ControllerPlan,
        token: str,
        now: datetime,
        ttl: timedelta = timedelta(minutes=2),
    ) -> ProviderPreflightSnapshot:
        self.read_count += 1
        item, request_id, units = self._read_exact(plan=plan, token=token)
        return build_preflight(
            target=plan.target,
            normalized_state=str(item.get("State", "UNKNOWN")),
            status=str(item.get("Status", "UNKNOWN")),
            current_provider_daily_budget=None,
            currency=None,
            strategy_subtype="not-required-for-suspend-resume",
            fetched_at=now,
            ttl=ttl,
            source_ref=f"direct:v501:{plan.target.entity_type}:get",
            request_id=request_id,
            units=_units_int(units),
        )

    def readback(self, *, plan: ControllerPlan, token: str) -> Mapping[str, str]:
        self.read_count += 1
        item, _, _ = self._read_exact(plan=plan, token=token)
        return {
            "provider_entity_id": str(item["Id"]),
            "normalized_state": str(item.get("State", "UNKNOWN")),
            "status": str(item.get("Status", "UNKNOWN")),
        }

    def _read_exact(self, *, plan: ControllerPlan, token: str):
        if not token:
            raise ValueError("Direct OAuth token required")
        if not self.config.direct_client_login:
            raise ValueError("exact managed Direct target login required")
        service = "campaigns" if plan.target.entity_type == "campaign" else "ads"
        collection = "Campaigns" if service == "campaigns" else "Ads"
        try:
            provider_id = int(plan.target.provider_entity_id)
        except (TypeError, ValueError) as exc:
            raise ValueError("provider entity id must be integer Direct id") from exc
        response = self.transport.send(HttpRequest(
            "POST",
            f"{self.config.direct_endpoint}/{service}",
            {
                "Authorization": f"Bearer {token}",
                "Client-Login": self.config.direct_client_login,
                "Accept-Language": "en",
                "Content-Type": "application/json; charset=utf-8",
            },
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
            raise TransportError("Direct exact-state read returned non-success status", status_code=response.status_code)
        body = response.json_body if isinstance(response.json_body, dict) else {}
        if body.get("error"):
            raise TransportError("Direct exact-state read returned top-level error", status_code=response.status_code)
        items = body.get("result", {}).get(collection, [])
        exact = next((item for item in items if item.get("Id") == provider_id), None)
        if exact is None:
            raise TransportError("Direct exact-state read did not return bound object")
        return exact, response.request_id, _header(response.headers, "Units")


def execute_guarded_production_once(
    *,
    arm: ProductionWriterArm,
    plan: ControllerPlan,
    expected_preflight: ProviderPreflightSnapshot,
    writer: YandexDirectProductionWriter,
    state_reader: YandexDirectLiveStateReader,
    token: str,
    audit: AuditChain,
    locks: ExecutionLockRegistry,
    now: datetime,
    runtime_kill_switches: Sequence[KillSwitch] = (),
    lock_ttl: timedelta = timedelta(minutes=2),
) -> ProductionExecutionOutcome:
    if not arm.integrity_valid or not plan.integrity_valid:
        audit.append("BLOCKED", now, {"state": "INVALID_ARM_OR_PLAN"})
        return _outcome(ProductionTerminalState.PRODUCTION_WRITE_BLOCKED, writer, state_reader, None, None, False, audit)
    if arm.controller_plan_digest != plan.plan_digest or expected_preflight.snapshot_digest != plan.preflight_digest:
        audit.append("BLOCKED", now, {"state": "PLAN_PREFLIGHT_BINDING_MISMATCH"})
        return _outcome(ProductionTerminalState.PRODUCTION_WRITE_BLOCKED, writer, state_reader, None, None, False, audit)
    if not locks.acquire(plan.target.lock_key, now, lock_ttl):
        audit.append("BLOCKED", now, {"state": "BLOCKED_EXECUTION_LOCK"})
        return _outcome(ProductionTerminalState.PRODUCTION_WRITE_BLOCKED, writer, state_reader, None, None, False, audit)

    audit.append("EXECUTION_LOCK_ACQUIRED", now, {"lock_key": plan.target.lock_key})
    terminal = ProductionTerminalState.PRODUCTION_WRITE_BLOCKED
    request_id: str | None = None
    units: str | None = None
    uncertain_transport = False
    mutation_success: bool | None = None

    try:
        try:
            fresh = state_reader.preflight(plan=plan, token=token, now=now)
        except (TransportError, ValueError):
            audit.append("BLOCKED", now, {"state": "LIVE_PREFLIGHT_UNAVAILABLE"})
        else:
            audit.append("PREFLIGHT_RECHECKED", now, {"snapshot_digest": fresh.snapshot_digest})
            if not pre_dispatch_snapshot_matches(expected_preflight, fresh, now):
                audit.append("BLOCKED", now, {"state": "BLOCKED_STALE_PROVIDER_STATE"})
            elif any(_kill_switch_applies(item, plan) for item in runtime_kill_switches):
                audit.append("BLOCKED", now, {"state": "BLOCKED_KILL_SWITCH"})
            else:
                audit.append("DISPATCH_STARTED", now, {
                    "method": plan.method,
                    "object_count": 1,
                    "arm_digest": arm.arm_digest,
                    "plan_digest": plan.plan_digest,
                })
                try:
                    result = writer.dispatch_once(arm=arm, plan=plan, token=token, now=now)
                    mutation_success = result.object_success
                    request_id = result.request_id
                    units = result.units
                    audit.append("PROVIDER_RESPONSE_RECEIVED", now, {
                        "http_status": result.http_status,
                        "object_success": result.object_success,
                        "warnings": result.warnings,
                        "errors": result.errors,
                        "RequestId": result.request_id,
                        "Units": result.units,
                    })
                except TransportError:
                    uncertain_transport = True
                    audit.append("PROVIDER_RESPONSE_UNCERTAIN", now, {
                        "reason": "transport_error_after_single_attempt"
                    })

                try:
                    readback = state_reader.readback(plan=plan, token=token)
                    audit.append("READBACK_CAPTURED", now, readback)
                except (TransportError, ValueError):
                    terminal = ProductionTerminalState.PRODUCTION_EXECUTION_UNCERTAIN
                    audit.append("EXECUTION_UNCERTAIN", now, {"state": "READBACK_UNAVAILABLE"})
                else:
                    expected = derive_expected_readback(plan)
                    if _readback_matches_expected(readback, expected):
                        terminal = ProductionTerminalState.GUARDED_PRODUCTION_LAUNCHED
                        audit.append("READBACK_VERIFIED", now, {"state": "DESIRED_STATE_PRESENT"})
                        audit.append("COMPLETED", now, {"state": terminal.value})
                    elif mutation_success is False and readback.get("normalized_state") == expected_preflight.normalized_state:
                        terminal = ProductionTerminalState.PRODUCTION_WRITE_BLOCKED
                        audit.append("BLOCKED", now, {"state": "PROVIDER_REJECTED_UNCHANGED"})
                    else:
                        terminal = ProductionTerminalState.PRODUCTION_EXECUTION_UNCERTAIN
                        audit.append("EXECUTION_UNCERTAIN", now, {
                            "state": "READBACK_NOT_DESIRED",
                            "transport_uncertain": uncertain_transport,
                        })
    finally:
        locks.release(plan.target.lock_key)
        audit.append("EXECUTION_LOCK_RELEASED", now, {"lock_key": plan.target.lock_key})

    return _outcome(
        terminal,
        writer,
        state_reader,
        request_id,
        units,
        uncertain_transport and terminal == ProductionTerminalState.GUARDED_PRODUCTION_LAUNCHED,
        audit,
    )


def _readback_matches_expected(readback: Mapping[str, str], expected: Mapping[str, object]) -> bool:
    return (
        str(readback.get("provider_entity_id")) == str(expected.get("provider_entity_id"))
        and readback.get("normalized_state") == expected.get("normalized_state")
    )


def _kill_switch_applies(switch: KillSwitch, plan: ControllerPlan) -> bool:
    refs = {
        "global": {"*", "profit-engine"},
        "site": {plan.target.site_id},
        "provider": {plan.target.provider},
        "advertiser": {plan.target.advertiser_ref},
        "target": {plan.target.target_ref, plan.target.provider_entity_id},
        "experiment": {plan.proposal_id, plan.method},
        "action": {plan.proposal_id, plan.method},
    }
    return switch.active and switch.scope_ref in refs.get(switch.scope, set())


def _units_int(value: str | None) -> int | None:
    if not value:
        return None
    head = value.split("/", 1)[0]
    try:
        return int(head)
    except ValueError:
        return None


def _header(headers: Mapping[str, str], name: str) -> str | None:
    return next((value for key, value in headers.items() if key.lower() == name.lower()), None)


def _outcome(
    state: ProductionTerminalState,
    writer: YandexDirectProductionWriter,
    state_reader: YandexDirectLiveStateReader,
    request_id: str | None,
    units: str | None,
    recovered: bool,
    audit: AuditChain,
) -> ProductionExecutionOutcome:
    return ProductionExecutionOutcome(
        state=state,
        dispatch_attempts=writer.dispatch_count,
        provider_read_attempts=state_reader.read_count,
        request_id=request_id,
        units=units,
        recovered_from_uncertain_transport=recovered,
        audit_valid=audit.valid(),
    )
