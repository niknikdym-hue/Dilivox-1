from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from functools import lru_cache
import hashlib
from pathlib import Path
import re
from typing import Any, Iterable, Mapping


PROFIT_ENGINE_ROOT = Path(__file__).resolve().parents[2]
TASKS_ROOT = PROFIT_ENGINE_ROOT / "tasks"
EVIDENCE_ROOT = PROFIT_ENGINE_ROOT / "evidence"

STATUS_VOCABULARY = frozenset({
    "NOT_STARTED",
    "DESIGNED",
    "CODE_READY",
    "LIVE_PROVIDER_VERIFIED",
    "LIVE_SITE_VERIFIED",
    "ECONOMICALLY_PROVEN",
    "BLOCKED_EXTERNAL",
    "BLOCKED_DATA",
    "OWNER_GATE",
    "DONE",
})
TRUTH_STATES = frozenset({"CURRENT", "STALE", "CONFLICT", "BLOCKED"})


@dataclass(frozen=True)
class StageDefinition:
    stage_id: str
    title_ru: str
    scope_ru: str
    next_milestone_ru: str


STAGES = (
    StageDefinition("A", "Измерение и соответствие", "Метрика, РСЯ, деньги, Privacy и first-party truth", "Живая проверка сайта и privacy-safe endpoint"),
    StageDefinition("B", "Живое управление Profit Engine", "Direct, поиск, советы владельцу и защита капитала", "Закрыть критический путь без обхода Owner Gates"),
    StageDefinition("C", "Adaptive Funnel MVP", "AF-0…AF-4: измерение, routing, эксперимент и экономика", "Получить AF-0 measurement truth"),
    StageDefinition("D", "Масштаб контента", "50 → 150 → 300, серии, кластеры и ROI волн", "Доказать экономику первой волны 50 → 150"),
    StageDefinition("E", "Коммерческий масштаб", "300 → 400–600, новые провайдеры и profit-gated AI", "Открывается только после доказанной экономики этапа D"),
)


@dataclass(frozen=True)
class TaskDefinition:
    task_id: str
    task_file: str | None
    title_ru: str
    outcome_ru: str
    stage: str
    workstream: str
    status: str
    target_state: str
    dependencies: tuple[str, ...] = ()
    blockers: tuple[str, ...] = ()
    owner_gate: bool = False
    executor: str = "Central Brain / Codex"
    execution_route: str = "G0"
    model: str = "none"
    routing_reason: str = "Детерминированная проверка или уже принятая работа."
    why_not_cheaper: str | None = None
    quality_floor: str = "exact"
    hard_cap_usd: str = "0.00"
    actual_cost_usd: str = "0.00"
    current_action: str = ""
    next_action: str = ""
    critical_order: int | None = None
    live_provider_state: str = "NOT_CLAIMED"
    live_site_state: str = "NOT_CLAIMED"
    economic_state: str = "NOT_PROVEN"
    source_ref: str | None = None
    allowed_paths: tuple[str, ...] = ()
    check_profiles: tuple[str, ...] = ("runtime_unit", "node_tests", "json_validate", "diff_check")
    deterministic: bool = False
    free_quality_equivalent: bool = False
    new_code: bool = False
    cross_module: bool = False
    high_risk: bool = False


def _task(
    task_id: str,
    title_ru: str,
    outcome_ru: str,
    stage: str,
    workstream: str,
    status: str,
    target_state: str,
    **kwargs: Any,
) -> TaskDefinition:
    filename = task_id + ".md" if task_id.startswith("TASK-") and task_id != "TASK-020-G0-SMOKE" else None
    return TaskDefinition(
        task_id=task_id,
        task_file=filename,
        title_ru=title_ru,
        outcome_ru=outcome_ru,
        stage=stage,
        workstream=workstream,
        status=status,
        target_state=target_state,
        **kwargs,
    )


TASK_DEFINITIONS = (
    _task("TASK-001-LOCAL-BOOTSTRAP-M0", "Локальный запуск и инвентаризация", "Зафиксировать реальную исходную систему без изменения сайта.", "A", "foundation", "DONE", "DONE"),
    _task("TASK-002-READ-FOUNDATION-PROVIDER-CERTIFICATION", "Read-only фундамент провайдеров", "Безопасно читать Direct, Метрику и РСЯ.", "A", "providers", "DONE", "DONE", dependencies=("TASK-001-LOCAL-BOOTSTRAP-M0",)),
    _task("TASK-003-DATA-FOUNDATION-PRIVATE-CORE-BOUNDARY", "Фундамент данных", "Сохранить raw truth, relational facts и границу private core.", "A", "data", "DONE", "DONE", dependencies=("TASK-002-READ-FOUNDATION-PROVIDER-CERTIFICATION",)),
    _task("TASK-004-READ-ONLY-INGESTION", "Read-only ingestion", "Доставлять provider responses через RAW FIRST в проверенные facts.", "A", "data", "DONE", "DONE", dependencies=("TASK-003-DATA-FOUNDATION-PRIVATE-CORE-BOUNDARY",)),
    _task("TASK-005-DILIVOX-IDENTITY-ATTRIBUTION-SITE-AGENT", "Identity и attribution", "Связать стабильный контент и разрешённую paid-attribution identity.", "A", "measurement", "DONE", "DONE", dependencies=("TASK-004-READ-ONLY-INGESTION",)),
    _task("TASK-006-FIRST-PARTY-EVENTS-SITE-SAFETY", "First-party события", "Собирать безопасные поведенческие события без поломки сайта.", "A", "measurement", "DONE", "DONE", dependencies=("TASK-005-DILIVOX-IDENTITY-ATTRIBUTION-SITE-AGENT",)),
    _task("TASK-007-MONEY-LEDGER-RECONCILIATION", "Денежный ledger и K5", "Считать деньги Decimal-only с явной атрибуцией и reconciliation.", "A", "money", "DONE", "DONE", dependencies=("TASK-006-FIRST-PARTY-EVENTS-SITE-SAFETY",), economic_state="CONTRACT_ACCEPTED"),
    _task("TASK-008-CAMPAIGN-CREATIVE-FACTORY-DRY-RUN", "Фабрика кампаний dry-run", "Строить только inert preview кампаний и креативов.", "B", "acquisition", "DONE", "DONE", dependencies=("TASK-007-MONEY-LEDGER-RECONCILIATION",)),
    _task("TASK-009-ACQUISITION-STRATEGY-LAB-PUBLIC-CONTRACTS", "Acquisition Strategy Lab", "Формировать публично-безопасные experiments без выбора победителя.", "B", "strategy", "DONE", "DONE", dependencies=("TASK-008-CAMPAIGN-CREATIVE-FACTORY-DRY-RUN",)),
    _task("TASK-010-TWO-REPO-PROFIT-ALLOCATOR", "Profit Allocator", "Связать public evidence с proposal-only private decision core.", "B", "allocation", "DONE", "DONE", dependencies=("TASK-009-ACQUISITION-STRATEGY-LAB-PUBLIC-CONTRACTS",)),
    _task("TASK-010-REWORK-COHORT-MATERIALIZATION", "Rework cohort materialization", "Не выдавать period revenue за доказанный acquisition cohort.", "B", "allocation", "DONE", "DONE", dependencies=("TASK-010-TWO-REPO-PROFIT-ALLOCATOR",)),
    _task("TASK-011-GUARDED-DIRECT-CONTROLLER-DRY-RUN", "Guarded Direct Controller", "Подготовить fail-closed controller без реальных provider writes.", "B", "direct-control", "DONE", "DONE", dependencies=("TASK-010-REWORK-COHORT-MATERIALIZATION",)),
    _task("TASK-011-REWORK-EXECUTION-BINDINGS", "Rework execution bindings", "Закрыть lock, TOCTOU, request и owner-authority bypasses.", "B", "direct-control", "DONE", "DONE", dependencies=("TASK-011-GUARDED-DIRECT-CONTROLLER-DRY-RUN",)),
    _task("TASK-011R-EXECUTION-BINDINGS-HANDOFF", "Handoff Task 011R", "Сохранить discoverability принятого rework-контракта.", "B", "history", "DONE", "DONE", dependencies=("TASK-011-REWORK-EXECUTION-BINDINGS",)),
    _task(
        "TASK-012-LIVE-GUARDED-PRODUCTION-LAUNCH", "Первый guarded Direct smoke", "Провести ровно одно разрешённое действие только после свежих money и Owner gates.", "B", "direct-control", "OWNER_GATE", "LIVE_PROVIDER_VERIFIED",
        dependencies=("TASK-011-REWORK-EXECUTION-BINDINGS",), blockers=("Нужны свежий money review и точечное Owner approval для exact action.",), owner_gate=True,
        live_provider_state="RECORDED_READ_PASS_WRITE_NOT_EXECUTED", current_action="Боевой write не разрешён этой задачей панели.", next_action="Собрать свежий exact plan и отдельное Owner approval.", critical_order=30,
    ),
    _task(
        "TASK-013-PRODUCTION-SITE-INSTRUMENTATION-AND-GOALS", "Production instrumentation", "Доставить уже принятые цели на реальный Dilivox и проверить arrivals.", "A", "measurement", "OWNER_GATE", "LIVE_SITE_VERIFIED",
        dependencies=("TASK-006-FIRST-PARTY-EVENTS-SITE-SAFETY",), blockers=("Требуются Owner-controlled Tilda publication и live-site verification.",), owner_gate=True,
        live_provider_state="LIVE_PROVIDER_VERIFIED", live_site_state="NOT_VERIFIED", current_action="Provider goals подтверждены; production browser instrumentation не доказана.", next_action="Owner публикует точный принятый Tilda block, затем выполняется live probe.", critical_order=10,
    ),
    _task(
        "TASK-014-MANUAL-SEARCH-PROFIT-CONTROLLER", "Manual Search Profit Control", "Управлять поисковыми ставками по K5, сохраняя weekly capital.", "B", "manual-search", "CODE_READY", "LIVE_PROVIDER_VERIFIED",
        dependencies=("TASK-007-MONEY-LEDGER-RECONCILIATION",), blockers=("MS4 panel integration и последующая отдельная write acceptance.",), live_provider_state="READ_MODEL_ACCEPTED", next_action="Интегрировать shadow output без включения writer.", critical_order=40,
    ),
    _task(
        "TASK-015-FIRST-PARTY-EVENT-ENDPOINT", "Privacy-safe event endpoint", "Сделать first-party event truth долговечным и fail-open для чтения.", "A", "measurement", "BLOCKED_EXTERNAL", "LIVE_SITE_VERIFIED",
        dependencies=("TASK-013-PRODUCTION-SITE-INSTRUMENTATION-AND-GOALS",), blockers=("Privacy v2 и production endpoint ещё не приняты/развёрнуты.",), owner_gate=True,
        execution_route="G3", model="gpt-5.6-sol", routing_reason="Security/privacy/idempotency требуют Sol-class review.", why_not_cheaper="SECURITY_OR_PRIVACY_SENSITIVE", quality_floor="privacy-safe-production", hard_cap_usd="3.00",
        current_action="Можно продолжать только code slices, не production deploy.", next_action="Согласовать Privacy v2 и реализовать bounded endpoint.", critical_order=20,
        allowed_paths=("profit-engine/runtime", "profit-engine/data", "profit-engine/sites/dilivox", "profit-engine/evidence"), new_code=True, cross_module=True, high_risk=True,
    ),
    _task(
        "TASK-016-ADAPTIVE-BASELINE-CONTENT-MAP", "AF-1: карта текущего контента", "Построить проверенный граф примерно 50 историй без AI guesses.", "C", "adaptive-funnel", "NOT_STARTED", "CODE_READY",
        execution_route="G1", model="gpt-5.6-luna", routing_reason="Нужны новые generator/validator artifacts; после их появления повторные projection checks станут G0.", why_not_cheaper="NEW_BOUNDED_CODE_SYNTHESIS", quality_floor="exact-registry", hard_cap_usd="0.50",
        next_action="Запустить bounded implementation, затем повторять projection бесплатно.", critical_order=50,
        allowed_paths=("profit-engine/sites/dilivox", "profit-engine/runtime", "profit-engine/evidence"), new_code=True,
    ),
    _task(
        "TASK-017-NEXT-CONTENT-DECISION-CORE", "AF-2: NextContentDecision core", "Создать прозрачный rule-based routing с static fallback.", "C", "adaptive-funnel", "NOT_STARTED", "CODE_READY",
        dependencies=("TASK-016-ADAPTIVE-BASELINE-CONTENT-MAP",), execution_route="G2", model="gpt-5.6-terra", routing_reason="Новый multi-file decision core требует нормального engineering route.", why_not_cheaper="MULTIFILE_REASONING_REQUIRED", quality_floor="production-shaped-offline", hard_cap_usd="1.50",
        next_action="После принятой Task 016 запустить bounded Terra implementation.", critical_order=60,
        allowed_paths=("profit-engine/runtime", "profit-engine/sites/dilivox", "profit-engine/evidence"), new_code=True, cross_module=True,
    ),
    _task(
        "TASK-018-RULE-BASED-ADAPTIVE-EXPERIMENT", "AF-3: rule-based experiment", "Сравнить static control и treatment без AI и без риска для чтения.", "C", "adaptive-funnel", "BLOCKED_EXTERNAL", "LIVE_SITE_VERIFIED",
        dependencies=("TASK-017-NEXT-CONTENT-DECISION-CORE", "TASK-013-PRODUCTION-SITE-INSTRUMENTATION-AND-GOALS", "TASK-015-FIRST-PARTY-EVENT-ENDPOINT"), blockers=("AF-0 live instrumentation/privacy gates не закрыты.",), owner_gate=True,
        execution_route="G2", model="gpt-5.6-terra", routing_reason="Production-shaped experiment integration требует multi-file engineering.", why_not_cheaper="MULTIFILE_REASONING_REQUIRED", quality_floor="fail-safe-experiment", hard_cap_usd="1.50",
        next_action="Не запускать treatment до AF-0 live acceptance.", critical_order=70,
        allowed_paths=("profit-engine/runtime", "profit-engine/sites/dilivox", "profit-engine/evidence"), new_code=True, cross_module=True,
    ),
    _task(
        "TASK-019-ADAPTIVE-PROFIT-EVALUATION", "AF-4: экономическая оценка", "Решить TEST/KEEP/HOLD/KILL/SCALE по reconciled FEATURE_ROI.", "C", "adaptive-funnel", "BLOCKED_DATA", "ECONOMICALLY_PROVEN",
        dependencies=("TASK-018-RULE-BASED-ADAPTIVE-EXPERIMENT",), blockers=("Нет реального Task 018 experiment evidence и reconciled money.",),
        execution_route="G3", model="gpt-5.6-sol", routing_reason="Money attribution and reconciliation are high consequence.", why_not_cheaper="SECURITY_OR_MONEY_SENSITIVE", quality_floor="money-truth", hard_cap_usd="3.00",
        next_action="Ждать совместимые реальные control/treatment money windows.", critical_order=80,
        allowed_paths=("profit-engine/runtime", "profit-engine/data", "profit-engine/evidence"), new_code=True, cross_module=True, high_risk=True,
    ),
    _task(
        "TASK-020-OWNER-CONTROL-PANEL-V2", "Полное управление проектом", "Дать владельцу управление разработкой без обычного посещения GitHub.", "B", "owner-control", "DESIGNED", "CODE_READY",
        dependencies=("TASK-021-CODEX-DEVELOPMENT-EXECUTOR",), execution_route="G3", model="gpt-5.6-sol", routing_reason="Dual-window, security, idempotency and workflow control require Sol-class reasoning.", why_not_cheaper="SECURITY_AND_CROSS_CONTROL_INTEGRATION", quality_floor="owner-safe-control-plane", hard_cap_usd="3.00",
        current_action="Bounded Task 020 implementation branch.", next_action="Draft PR, exact-head CI and Central Brain acceptance.",
        allowed_paths=("profit-engine/runtime", "profit-engine/scripts", "profit-engine/tasks", "profit-engine/evidence", ".github/workflows", "profit-engine/DILIVOX_OWNER_CONTROL_PANEL_REQUIREMENTS.md"), new_code=True, cross_module=True, high_risk=True,
    ),
    _task(
        "TASK-021-CODEX-DEVELOPMENT-EXECUTOR", "Bounded development executor", "Маршрутизировать G0–G4 с budget/scope gates без merge/deploy.", "B", "development", "DONE", "DONE",
        execution_route="G0", model="none", routing_reason="Принятая реализация и acceptance не использовали OpenAI provider call.", quality_floor="accepted-control-plane", hard_cap_usd="0.00", actual_cost_usd="0.00",
        source_ref="profit-engine/evidence/TASK-021-DEVELOPMENT-CONTROL-PLANE-ACCEPTED-2026-09-12.md",
    ),
    _task(
        "TASK-020-G0-SMOKE", "Бесплатная проверка Project Control", "Доказать путь кнопка → backend → GitHub Action → результат без OpenAI cost.", "B", "owner-control", "NOT_STARTED", "DONE",
        dependencies=("TASK-021-CODEX-DEVELOPMENT-EXECUTOR",), executor="GitHub-native", execution_route="G0", model="none",
        routing_reason="Детерминированный preflight полностью достаточен для end-to-end control smoke.", quality_floor="exact-control-path", hard_cap_usd="0.00", actual_cost_usd="0.00",
        next_action="Запустить из Project Control после локальной проверки.", allowed_paths=("profit-engine/evidence",), check_profiles=("router_tests", "diff_check"), deterministic=True, free_quality_equivalent=True,
        source_ref="profit-engine/tasks/TASK-020-OWNER-CONTROL-PANEL-V2.md",
    ),
    _task(
        "MILESTONE-D-050-150", "Контент 50 → 150", "Производить только измеренными волнами 25–50 после AF-4 evidence.", "D", "content-scale", "BLOCKED_DATA", "ECONOMICALLY_PROVEN",
        dependencies=("TASK-019-ADAPTIVE-PROFIT-EVALUATION",), blockers=("AF-4 FEATURE_ROI ещё не доказан.",), owner_gate=True, source_ref="profit-engine/PROFIT_ENGINE_AUTHORITY.md#A-011",
    ),
    _task(
        "MILESTONE-D-150-300", "Контент 150 → 300", "Углублять winners по фактической экономике, сохраняя exploration bound.", "D", "content-scale", "NOT_STARTED", "ECONOMICALLY_PROVEN",
        dependencies=("MILESTONE-D-050-150",), source_ref="profit-engine/PROFIT_ENGINE_AUTHORITY.md#A-011",
    ),
    _task(
        "MILESTONE-E-300-600", "Коммерческий масштаб 300 → 400–600", "Расширять каталог только после доказанного content-wave ROI.", "E", "commercial-scale", "NOT_STARTED", "ECONOMICALLY_PROVEN",
        dependencies=("MILESTONE-D-150-300",), owner_gate=True, source_ref="profit-engine/PROFIT_ENGINE_AUTHORITY.md#A-011",
    ),
    _task(
        "MILESTONE-E-OPTIONAL-AI-PROVIDERS", "Optional AI и новые провайдеры", "Добавлять только provider-neutral и FEATURE_ROI-gated возможности.", "E", "expansion", "NOT_STARTED", "ECONOMICALLY_PROVEN",
        dependencies=("MILESTONE-E-300-600",), owner_gate=True, source_ref="profit-engine/PROFIT_ENGINE_AUTHORITY.md#A-009",
    ),
)


TASK_BY_ID = {task.task_id: task for task in TASK_DEFINITIONS}


@lru_cache(maxsize=64)
def _title_from_task(path: Path) -> str:
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    raise ValueError(f"task has no H1 title: {path}")


@lru_cache(maxsize=64)
def _evidence_refs_cached(task_id: str) -> tuple[str, ...]:
    match = re.match(r"TASK-(\d{3})", task_id)
    if not match or not EVIDENCE_ROOT.exists():
        return ()
    prefix = f"TASK-{match.group(1)}"
    return tuple(sorted(
        str(path.relative_to(PROFIT_ENGINE_ROOT.parent))
        for path in EVIDENCE_ROOT.glob(prefix + "*.md")
        if " " not in path.name
    ))


def _evidence_refs(task_id: str) -> list[str]:
    return list(_evidence_refs_cached(task_id))


def validate_projection() -> None:
    ids = [task.task_id for task in TASK_DEFINITIONS]
    if len(ids) != len(set(ids)):
        raise ValueError("project projection contains duplicate task IDs")
    stage_ids = {stage.stage_id for stage in STAGES}
    unknown_statuses = sorted({task.status for task in TASK_DEFINITIONS} - STATUS_VOCABULARY)
    if unknown_statuses:
        raise ValueError(f"unsupported task statuses: {unknown_statuses}")
    unknown_stages = sorted({task.stage for task in TASK_DEFINITIONS} - stage_ids)
    if unknown_stages:
        raise ValueError(f"unsupported task stages: {unknown_stages}")
    for task in TASK_DEFINITIONS:
        missing = sorted(set(task.dependencies) - set(ids))
        if missing:
            raise ValueError(f"{task.task_id} has unknown dependencies: {missing}")
        if task.task_file:
            path = TASKS_ROOT / task.task_file
            if not path.exists():
                raise ValueError(f"projection source missing: {path}")
            _title_from_task(path)
    projected_files = {task.task_file for task in TASK_DEFINITIONS if task.task_file}
    actual_files = {path.name for path in TASKS_ROOT.glob("TASK-*.md")}
    if projected_files != actual_files:
        raise ValueError(
            "task projection mismatch; missing="
            + repr(sorted(actual_files - projected_files))
            + " extra="
            + repr(sorted(projected_files - actual_files))
        )
    if {task.stage for task in TASK_DEFINITIONS} != stage_ids:
        raise ValueError("all five project stages must contain projected work")


def _task_payload(task: TaskDefinition, runtime: Mapping[str, Any] | None = None) -> dict[str, Any]:
    payload = asdict(task)
    payload["dependencies"] = list(task.dependencies)
    payload["blockers"] = list(task.blockers)
    payload["allowed_paths"] = list(task.allowed_paths)
    payload["check_profiles"] = list(task.check_profiles)
    payload["canonical_title"] = _title_from_task(TASKS_ROOT / task.task_file) if task.task_file else task.title_ru
    payload["task_file"] = f"profit-engine/tasks/{task.task_file}" if task.task_file else None
    payload["evidence_refs"] = _evidence_refs(task.task_id)
    payload["branch"] = None
    payload["pr"] = None
    payload["sha"] = None
    payload["ci_state"] = "NOT_CHECKED"
    payload["last_evidence_time"] = None
    if runtime:
        for field in (
            "status", "branch", "pr", "sha", "ci_state", "current_action", "next_action",
            "last_evidence_time", "actual_cost_usd", "live_provider_state", "live_site_state", "economic_state",
        ):
            if runtime.get(field) is not None:
                payload[field] = runtime[field]
    if payload["status"] not in STATUS_VOCABULARY:
        raise ValueError(f"runtime attempted unsupported status for {task.task_id}")
    payload["owner_gate_id"] = f"OWNER-GATE::{task.task_id}" if task.owner_gate else None
    scope_material = "|".join((task.task_id, task.target_state, ",".join(task.blockers)))
    payload["owner_gate_scope_digest"] = hashlib.sha256(scope_material.encode("utf-8")).hexdigest() if task.owner_gate else None
    return payload


def _dependency_ready(task: Mapping[str, Any], by_id: Mapping[str, Mapping[str, Any]]) -> bool:
    terminal = {"DONE", "CODE_READY", "LIVE_PROVIDER_VERIFIED", "LIVE_SITE_VERIFIED", "ECONOMICALLY_PROVEN"}
    return all(by_id[dependency]["status"] in terminal for dependency in task["dependencies"])


def _stage_status(tasks: Iterable[Mapping[str, Any]]) -> str:
    values = [task["status"] for task in tasks]
    if any(value == "OWNER_GATE" for value in values):
        return "OWNER_GATE"
    if any(value == "BLOCKED_EXTERNAL" for value in values):
        return "BLOCKED_EXTERNAL"
    if any(value == "BLOCKED_DATA" for value in values):
        return "BLOCKED_DATA"
    if values and all(value == "DONE" for value in values):
        return "DONE"
    if any(value in {"CODE_READY", "LIVE_PROVIDER_VERIFIED", "LIVE_SITE_VERIFIED", "ECONOMICALLY_PROVEN"} for value in values):
        return "CODE_READY"
    if any(value == "DESIGNED" for value in values):
        return "DESIGNED"
    return "NOT_STARTED"


def build_project_board(*, runtime_tasks: Mapping[str, Mapping[str, Any]] | None = None) -> dict[str, Any]:
    validate_projection()
    runtime_tasks = runtime_tasks or {}
    tasks = [_task_payload(task, runtime_tasks.get(task.task_id)) for task in TASK_DEFINITIONS]
    by_id = {task["task_id"]: task for task in tasks}
    for task in tasks:
        task["dependencies_ready"] = _dependency_ready(task, by_id)
        task["start_eligible"] = (
            task["status"] in {"NOT_STARTED", "DESIGNED", "CODE_READY"}
            and task["dependencies_ready"]
            and not task["blockers"]
            and not task["owner_gate"]
            and bool(task["task_file"] or task["task_id"] == "TASK-020-G0-SMOKE")
        )

    stages: list[dict[str, Any]] = []
    for stage in STAGES:
        members = [task for task in tasks if task["stage"] == stage.stage_id]
        complete = sum(task["status"] == "DONE" for task in members)
        blockers = sum(bool(task["blockers"]) or task["status"] in {"BLOCKED_EXTERNAL", "BLOCKED_DATA"} for task in members)
        owner_gates = sum(task["owner_gate"] and task["status"] != "DONE" for task in members)
        stages.append({
            **asdict(stage),
            "status": _stage_status(members),
            "completed_tasks": complete,
            "required_tasks": len(members),
            "blocker_count": blockers,
            "owner_gate_count": owner_gates,
            "accepted_evidence_state": "PARTIAL" if complete else "NONE",
        })

    critical_path = [
        task for task in tasks
        if task["critical_order"] is not None and task["status"] != "DONE"
    ]
    critical_path.sort(key=lambda item: (item["critical_order"], item["task_id"]))
    owner_gates = [task for task in tasks if task["owner_gate"] and task["status"] != "DONE"]
    history = [task for task in tasks if task["status"] == "DONE"]
    history.sort(key=lambda item: item["task_id"])
    return {
        "schema_version": "dilivox-whole-project-projection-v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_model": "CANONICAL_DOCS_TASKS_EVIDENCE_PROJECTION",
        "mutable_task_database": False,
        "status_vocabulary": sorted(STATUS_VOCABULARY),
        "stages": stages,
        "tasks": tasks,
        "critical_path": critical_path,
        "owner_gates": owner_gates,
        "history": history,
        "current_stage": critical_path[0]["stage"] if critical_path else "E",
        "current_milestone": critical_path[0]["title_ru"] if critical_path else "Критический путь закрыт",
    }


def derive_truth_state(
    *,
    canonical_sha: str | None,
    remote_sha: str | None,
    remote_available: bool,
    source_conflict: bool,
    critical_blocker_count: int,
) -> str:
    if source_conflict or (canonical_sha and remote_sha and canonical_sha != remote_sha):
        return "CONFLICT"
    if not remote_available or not canonical_sha or not remote_sha:
        return "STALE"
    if critical_blocker_count:
        return "BLOCKED"
    return "CURRENT"


def assert_truth_non_upgrade(
    *,
    ci_state: str,
    live_provider_state: str,
    live_site_state: str,
    economic_state: str,
) -> None:
    if ci_state not in {"NOT_CHECKED", "QUEUED", "IN_PROGRESS", "SUCCESS", "FAILURE"}:
        raise ValueError("unknown CI state")
    if economic_state == "ECONOMICALLY_PROVEN" and (
        live_provider_state != "LIVE_PROVIDER_VERIFIED" or live_site_state != "LIVE_SITE_VERIFIED"
    ):
        raise ValueError("economic proof cannot be inferred without compatible live truth")
