from __future__ import annotations

from dataclasses import asdict, dataclass
from decimal import Decimal
import argparse
import json
from pathlib import Path
from typing import Any, Mapping


INITIAL_OPENAI_DEV_ENVELOPE_USD = Decimal("10.00")
DEFAULT_PACKAGE_HARD_CAP_USD = Decimal("3.00")

ROUTES: dict[str, dict[str, Any]] = {
    "G0": {"model": None, "soft_cap_usd": Decimal("0.00"), "hard_cap_usd": Decimal("0.00")},
    "G1": {"model": "gpt-5.6-luna", "soft_cap_usd": Decimal("0.15"), "hard_cap_usd": Decimal("0.50")},
    "G2": {"model": "gpt-5.6-terra", "soft_cap_usd": Decimal("0.75"), "hard_cap_usd": Decimal("1.50")},
    "G3": {"model": "gpt-5.6-sol", "soft_cap_usd": Decimal("1.50"), "hard_cap_usd": Decimal("3.00")},
    "G4": {"model": "gpt-6-astra", "soft_cap_usd": None, "hard_cap_usd": None},
}

MODEL_TO_ROUTE = {
    "none": "G0",
    "github_native": "G0",
    "luna": "G1",
    "gpt-5.6-luna": "G1",
    "terra": "G2",
    "gpt-5.6-terra": "G2",
    "sol": "G3",
    "gpt-5.6-sol": "G3",
    "astra": "G4",
    "gpt-6-astra": "G4",
}


@dataclass(frozen=True)
class DevelopmentRoute:
    execution_route: str
    model_route: str | None
    quality_floor: str
    routing_reason: str
    why_not_cheaper: str | None
    soft_cap_usd: str | None
    hard_cap_usd: str | None
    owner_approval_required: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _text(task: Mapping[str, Any]) -> str:
    keys = ("task_id", "title", "objective", "scope", "risk", "workstream", "acceptance")
    return " ".join(str(task.get(k) or "") for k in keys).lower()


def _bool(task: Mapping[str, Any], key: str) -> bool:
    value = task.get(key)
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    return str(value).strip().lower() in {"1", "true", "yes", "y", "on"}


def _explicit_route(task: Mapping[str, Any]) -> str | None:
    explicit = str(task.get("execution_route") or task.get("model_route") or "").strip().lower()
    if not explicit or explicit == "auto":
        return None
    if explicit.upper() in ROUTES:
        return explicit.upper()
    if explicit in MODEL_TO_ROUTE:
        return MODEL_TO_ROUTE[explicit]
    raise ValueError(f"unsupported explicit route/model: {explicit}")


def classify_task(task: Mapping[str, Any]) -> DevelopmentRoute:
    """Choose the least expensive route that is confidently sufficient.

    The classifier is intentionally conservative about quality: there is no
    requirement to attempt G0/G1 before G2/G3 when the task clearly needs more
    capability. G4/Astra is never auto-authorized.
    """

    quality_floor = str(task.get("quality_floor") or "production-grade").strip()
    explicit = _explicit_route(task)
    text = _text(task)

    deterministic = _bool(task, "deterministic") or _bool(task, "github_native")
    quality_equivalent = _bool(task, "free_quality_equivalent")
    new_code = _bool(task, "new_code") or _bool(task, "code_synthesis")
    cross_module = _bool(task, "cross_module")
    high_risk = _bool(task, "high_risk") or any(
        token in text
        for token in (
            "security",
            "privacy",
            "money",
            "reconciliation",
            "provider write",
            "budget",
            "idempot",
            "exactly-once",
            "payment",
            "rollback",
            "cross-module",
        )
    )
    architecture = _bool(task, "architecture") or _bool(task, "authority_change")
    simple = _bool(task, "simple") or any(
        token in text for token in ("fixture", "small test", "rename", "wording", "metadata-only")
    )

    if explicit:
        route = explicit
        reason = f"Explicit task route {route} was selected by the approved task contract."
    elif architecture and _bool(task, "astra_justified"):
        route = "G4"
        reason = "Task explicitly requires exceptional architecture/authority review."
    elif high_risk:
        route = "G3"
        reason = "High consequence or sensitive engineering requires Sol-class reasoning."
    elif new_code or cross_module:
        route = "G2"
        reason = "Non-trivial code synthesis or multi-module work requires the normal Terra development route."
    elif deterministic and quality_equivalent:
        route = "G0"
        reason = "The task is deterministic and the free route is quality-equivalent to a model-assisted implementation."
    elif simple:
        route = "G1"
        reason = "Small bounded reasoning/code task is suitable for Luna without lowering the quality floor."
    else:
        route = "G2"
        reason = "Default to Terra because capability sufficiency is more important than forcing a cheaper uncertain route."

    route_info = ROUTES[route]
    owner_approval_required = route == "G4" and not _bool(task, "astra_authorized")
    if owner_approval_required:
        reason += " Astra use remains blocked until explicit Owner authorization."

    cheaper = {
        "G0": None,
        "G1": "G0 would not provide the required bounded reasoning/code synthesis.",
        "G2": "G0/G1 are not confidently sufficient for the required implementation quality.",
        "G3": "G0-G2 are not confidently sufficient for the task risk/complexity.",
        "G4": "G0-G3 are insufficient only because an exceptional architecture/authority review was explicitly justified.",
    }[route]

    soft = route_info["soft_cap_usd"]
    hard = route_info["hard_cap_usd"]
    return DevelopmentRoute(
        execution_route=route,
        model_route=route_info["model"],
        quality_floor=quality_floor,
        routing_reason=reason,
        why_not_cheaper=cheaper,
        soft_cap_usd=None if soft is None else f"{soft:.2f}",
        hard_cap_usd=None if hard is None else f"{min(hard, DEFAULT_PACKAGE_HARD_CAP_USD):.2f}",
        owner_approval_required=owner_approval_required,
    )


def route_manifest(task: Mapping[str, Any]) -> dict[str, Any]:
    route = classify_task(task)
    return {
        "schema_version": "dilivox-dev-route-v1",
        "task_id": str(task.get("task_id") or "UNKNOWN"),
        "route": route.to_dict(),
        "initial_openai_dev_envelope_usd": f"{INITIAL_OPENAI_DEV_ENVELOPE_USD:.2f}",
        "default_package_hard_cap_usd": f"{DEFAULT_PACKAGE_HARD_CAP_USD:.2f}",
        "quality_first": True,
        "free_first": False,
        "auto_paid_retry": False,
        "auto_merge": False,
        "auto_deploy": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Route a bounded DILIVOX development task")
    parser.add_argument("task_json", type=Path)
    args = parser.parse_args()
    task = json.loads(args.task_json.read_text(encoding="utf-8"))
    print(json.dumps(route_manifest(task), ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
