from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any, Mapping, Sequence


TARGET_K5 = Decimal("5")
STRONG_K5 = Decimal("6")
WEAK_K5 = Decimal("3")


def build_owner_advice(
    *,
    money: Sequence[Mapping[str, Any]],
    monetization_ready: bool,
    campaigns: Sequence[Mapping[str, Any]],
    manual_search_state: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Translate read-only system truth into a small owner decision surface.

    This function never authorizes or performs provider writes. It only turns
    already-collected money/evidence states into plain-language priorities.
    """
    actions: list[dict[str, Any]] = []
    valid_money: list[dict[str, Any]] = []
    data_blocked = False

    if not monetization_ready:
        actions.append(_action(
            priority=1,
            severity="STOP",
            title="Не менять рекламу: сначала восстановить денежную атрибуцию",
            evidence="Доход РСЯ по кампаниям сейчас нельзя надёжно сопоставить расходам Директа.",
            do_now="Не менять ставки и бюджет. Восстановить чтение дохода РСЯ в Метрике и повторить денежную проверку.",
            expected_effect="После восстановления станет видно, какие кампании реально приближают K5 к 5,00×.",
            prohibited="Не масштабировать рекламу по CTR, CPC или поведенческим целям без денежного K5.",
        ))
        data_blocked = True

    for item in money:
        row = dict(item)
        state = str(row.get("state") or "")
        label = str(row.get("label") or row.get("campaign_id") or "Кампания")
        spend = _decimal(row.get("direct_spend_rub"))
        revenue = _decimal(row.get("metrica_attributed_yan_revenue_rub"))
        k5 = _decimal(row.get("k5_observed"))

        if state == "ERROR" or state == "HOLD_DATA_QUALITY":
            data_blocked = True
            actions.append(_action(
                priority=1,
                severity="STOP",
                title=f"{label}: не принимать рекламных решений до исправления данных",
                evidence=_hold_text(row),
                do_now="Исправить источник/сверку данных и повторить money preflight. До этого не менять ставки и бюджет по этой кампании.",
                expected_effect="Убираем риск оптимизировать рекламу по неверной выручке.",
                prohibited="Не трактовать отсутствующий или несверенный K5 как прибыль или убыток.",
            ))
            continue

        if state == "NO_DIRECT_SPEND":
            valid_money.append({"label": label, "state": state, "spend": spend or Decimal("0"), "revenue": revenue or Decimal("0"), "k5": None})
            continue

        if state == "READY_FOR_CANDIDATE_EVALUATION" and spend is not None and revenue is not None and k5 is not None:
            valid_money.append({"label": label, "state": state, "spend": spend, "revenue": revenue, "k5": k5})
            actions.append(_campaign_action(label=label, k5=k5, spend=spend))

    portfolio = _portfolio(valid_money, data_blocked=data_blocked, monetization_ready=monetization_ready)

    if not data_blocked and monetization_ready:
        portfolio_k5 = _decimal(portfolio.get("k5"))
        if portfolio_k5 is None:
            actions.append(_action(
                priority=2,
                severity="LEARN",
                title="Накопить расход: K5 пока нельзя посчитать",
                evidence="По точным Dilivox-кампаниям в выбранном окне нет достаточного расхода Директа.",
                do_now="Не увеличивать бюджет только ради статистики. Подготовить отдельную Search-кампанию с фиксированным недельным лимитом.",
                expected_effect="Получим контролируемую выборку для сравнения расхода и дохода РСЯ.",
                prohibited="Не считать K5 бесконечным при нулевом расходе.",
            ))
        elif portfolio_k5 < TARGET_K5:
            actions.append(_action(
                priority=1,
                severity="ACT",
                title="Главная задача: снизить стоимость привлечения, а не увеличивать бюджет",
                evidence=f"Совокупный K5 = {_fmt(portfolio_k5)}× при цели 5,00×.",
                do_now="Довести ручной Search-контур: видеть запрос/ключ → расход → доход → рекомендацию по ставке. Сначала снижать/отсекать убыточный трафик.",
                expected_effect="Снижение CPC и исключение слабых запросов повышают доход РСЯ на 1 ₽ расхода.",
                prohibited="Недельный бюджет не увеличивать, пока совокупный K5 ниже 5,00×.",
            ))
        else:
            actions.append(_action(
                priority=1,
                severity="HOLD",
                title="Цель K5 достигнута: удерживать экономику и масштабировать только доказанное",
                evidence=f"Совокупный K5 = {_fmt(portfolio_k5)}× при цели 5,00×.",
                do_now="Не менять всё сразу. Выделить прибыльные запросы/кампании и накапливать подтверждение перед увеличением ставок или бюджета.",
                expected_effect="Сохраняем положительную экономику и выявляем безопасный источник роста.",
                prohibited="Не увеличивать недельный бюджет >20% без явного подтверждения владельца.",
            ))

    manual = dict(manual_search_state or {})
    if str(manual.get("state") or "") == "BUILD_FIRST":
        actions.append(_action(
            priority=2,
            severity="BUILD",
            title="Следующий рычаг прибыли: управляемый Яндекс Поиск",
            evidence="Теневой контроллер ставок уже спроектирован, но отдельная Search-кампания ещё не создана.",
            do_now="Показать в панели рекомендации по ключам (MS4), затем создать DILIVOX | SEARCH | PROFIT ENGINE с фиксированным недельным лимитом.",
            expected_effect="Получим управляемый рычаг снижения CPC и отключения запросов с плохим K5.",
            prohibited="Ставки и бюджет пока не меняются автоматически; writer остаётся LOCKED.",
        ))

    if not actions:
        actions.append(_action(
            priority=1,
            severity="LEARN",
            title="Обновить данные и определить следующий денежный рычаг",
            evidence="Свежей достаточной денежной выборки пока нет.",
            do_now="Обновить панель после завершённого дня и использовать только точный K5.",
            expected_effect="Панель выберет действие по фактической экономике.",
            prohibited="Не принимать решения по неполным данным.",
        ))

    actions.sort(key=lambda row: (int(row["priority"]), _severity_order(str(row["severity"]))))
    return {
        "target_k5": "5.00",
        "portfolio": portfolio,
        "primary_action": actions[0],
        "actions": actions[:5],
        "campaign_count": len(campaigns),
        "provider_write_allowed": False,
        "writer_state": "LOCKED",
    }


def _portfolio(rows: Sequence[Mapping[str, Any]], *, data_blocked: bool, monetization_ready: bool) -> dict[str, Any]:
    spend = sum((_decimal(row.get("spend")) or Decimal("0") for row in rows), Decimal("0"))
    revenue = sum((_decimal(row.get("revenue")) or Decimal("0") for row in rows), Decimal("0"))
    k5 = revenue / spend if spend > 0 and not data_blocked and monetization_ready else None
    gap = (TARGET_K5 - k5) if k5 is not None else None
    if data_blocked or not monetization_ready:
        status = "DATA_HOLD"
    elif k5 is None:
        status = "LEARNING"
    elif k5 >= TARGET_K5:
        status = "TARGET_MET"
    else:
        status = "BELOW_TARGET"
    return {
        "status": status,
        "spend_rub": _fmt_money(spend),
        "revenue_rub": _fmt_money(revenue),
        "k5": _fmt(k5) if k5 is not None else None,
        "gap_to_target": _fmt(gap) if gap is not None else None,
    }


def _campaign_action(*, label: str, k5: Decimal, spend: Decimal) -> dict[str, Any]:
    if k5 >= STRONG_K5:
        return _action(
            priority=3,
            severity="HOLD",
            title=f"{label}: сохранить как кандидат на осторожное масштабирование",
            evidence=f"K5 {_fmt(k5)}× на расходе {_fmt_money(spend)} ₽.",
            do_now="Сохранять настройки и накапливать подтверждение; сравнить с другими источниками трафика.",
            expected_effect="Не теряем уже работающую экономику.",
            prohibited="Не повышать бюджет автоматически только из-за одного удачного окна.",
        )
    if k5 >= TARGET_K5:
        return _action(
            priority=3,
            severity="HOLD",
            title=f"{label}: цель выполняется — не раскачивать кампанию",
            evidence=f"K5 {_fmt(k5)}× на расходе {_fmt_money(spend)} ₽.",
            do_now="Держать и наблюдать; искать внутри кампании более прибыльные сегменты.",
            expected_effect="Сохраняем K5 ≥ 5 без лишних изменений.",
            prohibited="Не увеличивать бюджет до подтверждения устойчивости.",
        )
    if k5 >= WEAK_K5:
        return _action(
            priority=2,
            severity="ACT",
            title=f"{label}: снижать стоимость трафика",
            evidence=f"K5 {_fmt(k5)}× ниже цели 5,00×.",
            do_now="Не увеличивать бюджет. В ручном Search-контуре снижать ставки слабых запросов и удерживать сильные.",
            expected_effect="Цель — поднять K5 за счёт меньшего расхода на тот же доход РСЯ.",
            prohibited="Не масштабировать кампанию до K5 ≥ 5.",
        )
    return _action(
        priority=1,
        severity="ACT",
        title=f"{label}: экономика слабая — остановить масштабирование",
        evidence=f"K5 {_fmt(k5)}× существенно ниже цели 5,00×.",
        do_now="Не увеличивать бюджет. При достаточной выборке — снижать ставки/отсекать слабые запросы в отдельном ручном Search-контуре.",
        expected_effect="Ограничиваем расход, который не возвращается доходом РСЯ.",
        prohibited="Не пытаться компенсировать низкий K5 дополнительным бюджетом.",
    )


def _action(*, priority: int, severity: str, title: str, evidence: str, do_now: str, expected_effect: str, prohibited: str) -> dict[str, Any]:
    return {
        "priority": priority,
        "severity": severity,
        "title": title,
        "evidence": evidence,
        "do_now": do_now,
        "expected_effect": expected_effect,
        "prohibited": prohibited,
    }


def _hold_text(row: Mapping[str, Any]) -> str:
    holds = row.get("holds")
    if isinstance(holds, list) and holds:
        return "Проверка данных остановлена: " + ", ".join(str(item) for item in holds[:3])
    detail = row.get("detail")
    return str(detail) if detail else "Денежные данные не прошли контроль качества."


def _decimal(value: Any) -> Decimal | None:
    if value is None or value == "":
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None


def _fmt(value: Decimal) -> str:
    return format(value.quantize(Decimal("0.01")), "f")


def _fmt_money(value: Decimal) -> str:
    return format(value.quantize(Decimal("0.01")), "f")


def _severity_order(value: str) -> int:
    return {"STOP": 0, "ACT": 1, "BUILD": 2, "HOLD": 3, "LEARN": 4}.get(value, 9)
