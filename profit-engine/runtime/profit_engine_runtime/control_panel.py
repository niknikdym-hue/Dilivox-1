from __future__ import annotations

import argparse
from datetime import date, datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import subprocess
import threading
from typing import Any

from .config import DEFAULT_CONFIG_PATH
from .day12_campaign_inventory_cli import run_campaign_inventory
from .day12_metrica_yan_compatibility_cli import run_probe as run_metrica_yan_probe
from .day12_money_preflight_cli import run_money_preflight
from .metrica_goals_cli import audit_goals
from .owner_advisor import build_owner_advice


HOST = "127.0.0.1"
PORT = 8765
DEFAULT_DAYS = 7
MAX_WINDOW_DAYS = 365
CONTROL_DIR = Path("~/.config/profit-engine/control-panel").expanduser()
SNAPSHOT_PATH = CONTROL_DIR / "snapshot.json"
DILIVOX_CAMPAIGNS = {
    "712203524": "Dilivox",
    "712791195": "dilivox.ru",
}


def completed_window(days: int = DEFAULT_DAYS) -> tuple[str, str]:
    if days < 1 or days > MAX_WINDOW_DAYS:
        raise ValueError(f"period must be within 1..{MAX_WINDOW_DAYS} completed days")
    end = date.today() - timedelta(days=1)
    start = end - timedelta(days=days - 1)
    return start.isoformat(), end.isoformat()


def resolve_window(
    *,
    days: int | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
) -> dict[str, Any]:
    if date_from or date_to:
        if not date_from or not date_to:
            raise ValueError("для своего периода нужны обе даты")
        try:
            start = date.fromisoformat(date_from)
            end = date.fromisoformat(date_to)
        except ValueError as exc:
            raise ValueError("даты должны быть в формате YYYY-MM-DD") from exc
        if start > end:
            raise ValueError("начало периода не может быть позже конца")
        if end >= date.today():
            raise ValueError("используем только завершённые дни; сегодняшний день не включается")
        length = (end - start).days + 1
        if length > MAX_WINDOW_DAYS:
            raise ValueError(f"максимальный период панели — {MAX_WINDOW_DAYS} дней")
        return {
            "date_from": start.isoformat(),
            "date_to": end.isoformat(),
            "days": length,
            "preset_days": None,
            "mode": "CUSTOM",
        }

    selected = DEFAULT_DAYS if days is None else int(days)
    start, end = completed_window(selected)
    return {
        "date_from": start,
        "date_to": end,
        "days": selected,
        "preset_days": selected,
        "mode": "PRESET",
    }


def _safe_write_snapshot(value: dict[str, Any]) -> None:
    CONTROL_DIR.mkdir(parents=True, exist_ok=True)
    CONTROL_DIR.chmod(0o700)
    tmp = SNAPSHOT_PATH.with_suffix(".tmp")
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.chmod(0o600)
    tmp.replace(SNAPSHOT_PATH)


def load_snapshot() -> dict[str, Any]:
    if not SNAPSHOT_PATH.exists():
        window = resolve_window(days=DEFAULT_DAYS)
        return {
            "state": "NOT_REFRESHED",
            "updated_at": None,
            "window": window,
            "provider_write_allowed": False,
            "writer_state": "LOCKED",
            "owner_advice": {
                "portfolio": {
                    "status": "LEARNING",
                    "spend_rub": "0.00",
                    "revenue_rub": "0.00",
                    "k5": None,
                    "gap_to_target": None,
                },
                "primary_action": {
                    "priority": 1,
                    "severity": "LEARN",
                    "title": "Обновить данные",
                    "evidence": "Панель ещё не получила свежие денежные данные.",
                    "do_now": "Выбрать период и нажать «Обновить».",
                    "expected_effect": "Появится конкретное следующее действие по K5.",
                    "prohibited": "Не менять рекламу до свежей проверки.",
                },
                "actions": [],
            },
        }
    value = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
    if "window" not in value:
        value["window"] = resolve_window(days=DEFAULT_DAYS)
    return value


def collect_snapshot(
    config_path: Path = DEFAULT_CONFIG_PATH,
    *,
    days: int | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
) -> dict[str, Any]:
    now = datetime.now(timezone.utc).isoformat()
    window = resolve_window(days=days, date_from=date_from, date_to=date_to)
    window_from = str(window["date_from"])
    window_to = str(window["date_to"])
    snapshot: dict[str, Any] = {
        "state": "REFRESHING",
        "updated_at": now,
        "window": window,
        "site_id": "dilivox",
        "domain": "dilivox.ru",
        "target_k5": "5.0",
        "provider_write_allowed": False,
        "writer_state": "LOCKED",
        "money_basis": {
            "direct": "Cost, IncludeVAT=YES, IncludeDiscount=YES",
            "yan": "ym:s:yanPartnerPrice, RUB, without VAT",
        },
        "manual_search_p0": {
            "state": "BUILD_FIRST",
            "campaign_name": "DILIVOX | SEARCH | PROFIT ENGINE",
            "network": "OFF",
            "budget_control": "OWNER_FIXED_WEEKLY_LIMIT_FIRST",
            "bid_writer": "SHADOW_ONLY_UNTIL_SEPARATE_ACCEPTANCE",
        },
        "errors": [],
    }
    if not config_path.exists():
        snapshot["state"] = "BLOCKED_LOCAL_CONFIG"
        snapshot["errors"].append("Private Dilivox config is not installed on this Mac")
        snapshot["owner_advice"] = build_owner_advice(
            money=(),
            monetization_ready=False,
            campaigns=(),
            manual_search_state=snapshot["manual_search_p0"],
        )
        _safe_write_snapshot(snapshot)
        return snapshot

    try:
        snapshot["metrica_goals"] = audit_goals(
            config_path=config_path,
            goals_path=Path(__file__).resolve().parents[2] / "sites" / "dilivox" / "metrica-goals.json",
        )
    except Exception as exc:
        snapshot["metrica_goals"] = {"state": "ERROR", "detail": str(exc)}
        snapshot["errors"].append(f"Metrica goals: {exc}")

    try:
        snapshot["metrica_yan"] = run_metrica_yan_probe(
            config_path=config_path,
            date_from=window_from,
            date_to=window_to,
        )
    except Exception as exc:
        snapshot["metrica_yan"] = {"state": "ERROR", "detail": str(exc)}
        snapshot["errors"].append(f"Metrica/YAN: {exc}")

    try:
        inventory = run_campaign_inventory(config_path=config_path)
        selected = []
        for campaign in inventory.get("campaigns", []):
            campaign_id = str(campaign.get("campaign_id"))
            if campaign_id in DILIVOX_CAMPAIGNS:
                selected.append({
                    "label": DILIVOX_CAMPAIGNS[campaign_id],
                    "campaign_id": campaign_id,
                    "state": campaign.get("state"),
                    "provider_state": campaign.get("provider_state"),
                    "status": campaign.get("status"),
                    "type": campaign.get("type"),
                })
        snapshot["campaigns"] = selected
        snapshot["campaign_inventory_digest"] = inventory.get("inventory_digest")
    except Exception as exc:
        snapshot["campaigns"] = []
        snapshot["errors"].append(f"Direct campaign inventory: {exc}")

    compatibility_results = (
        snapshot.get("metrica_yan", {}).get("results", [])
        if isinstance(snapshot.get("metrica_yan"), dict)
        else []
    )
    monetization_ready = bool(compatibility_results) and any(
        row.get("probe") == "yan_total_by_date" and row.get("status") == "PASS"
        for row in compatibility_results
        if isinstance(row, dict)
    )
    snapshot["metrica_yan_monetization_ready"] = monetization_ready

    money: list[dict[str, Any]] = []
    if monetization_ready:
        for campaign_id, label in DILIVOX_CAMPAIGNS.items():
            try:
                value = run_money_preflight(
                    config_path=config_path,
                    campaign_id=campaign_id,
                    date_from=window_from,
                    date_to=window_to,
                )
                value["label"] = label
                money.append(value)
            except Exception as exc:
                money.append({
                    "label": label,
                    "campaign_id": campaign_id,
                    "state": "ERROR",
                    "detail": str(exc),
                })
                snapshot["errors"].append(f"Money preflight {label}: {exc}")
    snapshot["money"] = money

    goal_state = (
        snapshot.get("metrica_goals", {}).get("state")
        if isinstance(snapshot.get("metrica_goals"), dict)
        else None
    )
    campaigns_ok = len(snapshot.get("campaigns", [])) == 2
    if not monetization_ready:
        snapshot["state"] = "WAITING_METRICA_YAN_PROPAGATION"
    elif goal_state != "PASS":
        snapshot["state"] = "METRICA_GOALS_REWORK"
    elif not campaigns_ok:
        snapshot["state"] = "DIRECT_IDENTITY_REWORK"
    elif any(item.get("state") == "ERROR" for item in money):
        snapshot["state"] = "MONEY_PREFLIGHT_REWORK"
    else:
        snapshot["state"] = "READ_MODEL_READY"

    snapshot["owner_advice"] = build_owner_advice(
        money=money,
        monetization_ready=monetization_ready,
        campaigns=snapshot.get("campaigns", []),
        manual_search_state=snapshot.get("manual_search_p0", {}),
    )
    snapshot["updated_at"] = datetime.now(timezone.utc).isoformat()
    _safe_write_snapshot(snapshot)
    return snapshot


HTML = r"""<!doctype html>
<html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Profit Engine — Dilivox</title>
<style>
:root{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;background:#f4f4f6;color:#171719}*{box-sizing:border-box}body{margin:0}.wrap{max-width:1220px;margin:auto;padding:30px}.top{display:flex;justify-content:space-between;gap:22px;align-items:flex-start}.eyebrow{font-size:12px;letter-spacing:.13em;text-transform:uppercase;color:#6c6c72}.title{font-size:34px;font-weight:780;margin:5px 0 7px}.sub{color:#666;max-width:820px;line-height:1.45}.btn{border:0;background:#111;color:#fff;padding:11px 17px;border-radius:11px;font-weight:700;cursor:pointer}.btn:disabled{opacity:.5;cursor:not-allowed}.period{margin:20px 0;background:#fff;border:1px solid #e4e4e8;border-radius:16px;padding:16px}.periodTop{display:flex;gap:9px;align-items:center;flex-wrap:wrap}.preset{border:1px solid #d7d7dc;background:#fff;padding:8px 12px;border-radius:10px;cursor:pointer;font-weight:700}.preset.active{background:#111;color:#fff;border-color:#111}.custom{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-left:auto}.custom input{border:1px solid #d7d7dc;border-radius:9px;padding:8px 10px;font:inherit}.periodLabel{margin-top:11px;font-size:13px;color:#555}.periodNote{font-size:12px;color:#888;margin-left:6px}.hero{display:grid;grid-template-columns:1.25fr .75fr;gap:14px;margin:18px 0 24px}.heroMain,.heroSide,.action,.rows,.lever{background:#fff;border:1px solid #e4e4e8;border-radius:16px;box-shadow:0 1px 2px rgba(0,0,0,.025)}.heroMain{padding:24px}.heroSide{padding:22px}.label{font-size:12px;color:#777}.k5line{display:flex;align-items:flex-end;gap:13px;margin-top:8px}.k5{font-size:48px;font-weight:820;line-height:1}.target{font-size:15px;color:#777;padding-bottom:7px}.status{display:inline-flex;margin-top:13px;padding:6px 10px;border-radius:999px;font-size:12px;font-weight:800}.ok{background:#e8f8ec;color:#215e2d}.warn{background:#fff2d8;color:#76520a}.bad{background:#ffe8e8;color:#8a2727}.neutral{background:#ececf0;color:#555}.moneyline{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:15px}.moneybox{padding:12px;border-radius:12px;background:#f7f7f9}.moneyval{font-size:22px;font-weight:760;margin-top:4px}.sideTitle{font-size:16px;font-weight:760}.sideBig{font-size:23px;font-weight:790;margin:8px 0}.sideText{font-size:13px;line-height:1.45;color:#64646a}.section{margin:22px 0}.sectionHead{display:flex;justify-content:space-between;gap:15px;align-items:end;margin-bottom:10px}.section h2{font-size:19px;margin:0}.hint{font-size:12px;color:#777}.action{padding:19px;margin-bottom:10px;display:grid;grid-template-columns:52px 1fr;gap:15px}.num{width:38px;height:38px;display:flex;align-items:center;justify-content:center;border-radius:12px;background:#111;color:#fff;font-weight:800}.actionTitle{font-size:18px;font-weight:780;margin:0 0 8px}.actionGrid{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:12px}.mini{background:#f7f7f9;border-radius:12px;padding:12px;font-size:13px;line-height:1.42}.mini b{display:block;margin-bottom:4px;font-size:12px}.danger{background:#fff0f0}.rows{overflow:hidden}.row{display:grid;grid-template-columns:1.25fr .9fr .9fr 1.4fr;gap:12px;padding:14px 16px;border-bottom:1px solid #eee;align-items:center}.row:last-child{border:0}.muted{color:#777;font-size:13px}.pill{display:inline-block;padding:5px 8px;border-radius:999px;font-size:11px;font-weight:800}.levers{display:grid;grid-template-columns:repeat(3,1fr);gap:11px}.lever{padding:16px}.leverTitle{font-size:15px;font-weight:770}.leverText{font-size:13px;line-height:1.43;color:#666;margin-top:7px}.diag{margin-top:22px;background:#fff;border:1px solid #e4e4e8;border-radius:14px;padding:14px}.diag summary{cursor:pointer;font-weight:700}.diagGrid{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-top:12px}.diagItem{background:#f7f7f9;padding:11px;border-radius:10px;font-size:12px}.footer{font-size:12px;color:#777;margin:24px 0 4px}@media(max-width:900px){.hero{grid-template-columns:1fr}.custom{margin-left:0}.actionGrid,.levers,.diagGrid{grid-template-columns:1fr}.row{grid-template-columns:1fr 1fr}.top{display:block}.btn{margin-top:14px}}@media(max-width:520px){.wrap{padding:18px}.row{grid-template-columns:1fr}.moneyline{grid-template-columns:1fr}.k5{font-size:42px}}
</style></head>
<body><div class="wrap">
<div class="top"><div><div class="eyebrow">DILIVOX · PROFIT ENGINE</div><div class="title">Пульт прибыли</div><div class="sub">Показывает не только цифры, а следующий денежный шаг к цели <b>1 ₽ Директа → 5 ₽ дохода РСЯ</b>. Период выбираешь ты; сегодняшний незавершённый день в расчёт не попадает.</div></div><button class="btn" id="refresh">Обновить</button></div>

<div class="period">
 <div class="periodTop">
  <b>Период:</b>
  <button class="preset" data-days="1">1 день</button>
  <button class="preset" data-days="3">3 дня</button>
  <button class="preset" data-days="7">7 дней</button>
  <button class="preset" data-days="14">14 дней</button>
  <button class="preset" data-days="30">30 дней</button>
  <div class="custom"><span>или</span><input type="date" id="dateFrom"><span>—</span><input type="date" id="dateTo"><button class="preset" id="applyCustom">Применить</button></div>
 </div>
 <div class="periodLabel" id="periodLabel">— <span class="periodNote">только завершённые дни</span></div>
</div>

<div class="hero">
 <div class="heroMain">
  <div class="label">Фактический K5 за выбранный период</div>
  <div class="k5line"><div class="k5" id="portfolioK5">—</div><div class="target">цель 5,00×</div></div>
  <div id="portfolioStatus" class="status neutral">Нет свежих данных</div>
  <div class="moneyline">
   <div class="moneybox"><div class="label">Расход Директа</div><div class="moneyval" id="portfolioSpend">—</div></div>
   <div class="moneybox"><div class="label">Доход РСЯ</div><div class="moneyval" id="portfolioRevenue">—</div></div>
  </div>
 </div>
 <div class="heroSide">
  <div class="sideTitle">Что делать сейчас</div>
  <div class="sideBig" id="primaryTitle">Обновить данные</div>
  <div class="sideText" id="primaryDo">После обновления здесь будет одно главное действие.</div>
  <div id="primarySeverity" class="status neutral">READ ONLY</div>
 </div>
</div>

<div class="section"><div class="sectionHead"><h2>Приоритетные действия</h2><div class="hint">в порядке влияния на K5</div></div><div id="actions"></div></div>
<div class="section"><div class="sectionHead"><h2>Экономика по кампаниям</h2><div class="hint">расход → доход РСЯ → решение</div></div><div class="rows" id="money"></div></div>

<div class="section"><div class="sectionHead"><h2>Три рычага прибыли</h2><div class="hint">что реально может поднять K5</div></div><div class="levers">
 <div class="lever"><div class="leverTitle">1. Дешевле покупать трафик</div><div class="leverText">Снижать ставки слабых запросов, удерживать прибыльные, не раздувать недельный бюджет.</div></div>
 <div class="lever"><div class="leverTitle">2. Больше дохода с читателя</div><div class="leverText">Улучшать глубину чтения, переходы между историями и рекламную монетизацию только через измеряемые эксперименты.</div></div>
 <div class="lever"><div class="leverTitle">3. Масштабировать доказанное</div><div class="leverText">K5 ≥ 5 должен быть устойчивым на выбранных окнах. Рост недельного бюджета >20% всегда требует твоего подтверждения.</div></div>
</div></div>

<div class="section"><div class="sectionHead"><h2>Ручной Яндекс Поиск</h2><div class="hint">следующий управляемый контур</div></div><div class="rows">
 <div class="row"><b>DILIVOX | SEARCH | PROFIT ENGINE</b><span>Только Поиск</span><span>Сеть выключена</span><span class="pill warn">ГОТОВИМ</span></div>
 <div class="row"><b>Ставки по ключам</b><span>Shadow-рекомендации</span><span>Недельный бюджет фиксирован владельцем</span><span class="pill neutral">WRITER LOCKED</span></div>
</div></div>

<details class="diag"><summary>Техническая диагностика</summary><div class="diagGrid">
 <div class="diagItem"><b>Система</b><div id="system">—</div></div>
 <div class="diagItem"><b>РСЯ → Метрика</b><div id="yanlink">—</div></div>
 <div class="diagItem"><b>Боевые действия</b><div>ЗАБЛОКИРОВАНЫ</div></div>
 <div class="diagItem"><b>Цели Метрики</b><div>Используем существующие dv_*; Profit Engine ими не управляет</div></div>
 <div class="diagItem"><b>Денежная база</b><div>Direct: Cost с НДС; РСЯ: доход в RUB без НДС</div></div>
 <div class="diagItem"><b>Обновлено</b><div id="updated">—</div></div>
 <div class="diagItem"><b>Ошибки</b><div id="errors">нет</div></div>
</div></details>
<div class="footer">Локально: 127.0.0.1 · секреты: macOS Keychain · provider-write endpoint в панели отсутствует</div>
</div>
<script>
let lastSnapshot=null;
function esc(x){return String(x??'—').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
function num(x){let n=Number(x);return Number.isFinite(n)?n:null}
function fmtK5(x){let n=num(x);return n===null?'—':n.toLocaleString('ru-RU',{minimumFractionDigits:2,maximumFractionDigits:2})+'×'}
function fmtMoney(x){let n=num(x);return n===null?'—':n.toLocaleString('ru-RU',{minimumFractionDigits:2,maximumFractionDigits:2})+' ₽'}
function sevClass(s){return s==='STOP'||s==='ACT'?'bad':s==='HOLD'?'ok':s==='BUILD'||s==='LEARN'?'warn':'neutral'}
function statusText(s){return {TARGET_MET:'ЦЕЛЬ ВЫПОЛНЯЕТСЯ',BELOW_TARGET:'НИЖЕ ЦЕЛИ',DATA_HOLD:'СТОП: ПРОВЕРИТЬ ДАННЫЕ',LEARNING:'НУЖНА ВЫБОРКА'}[s]||s||'—'}
function stateRu(s){return {READ_MODEL_READY:'Данные готовы',WAITING_METRICA_YAN_PROPAGATION:'Ожидаем денежные данные РСЯ',MONEY_PREFLIGHT_REWORK:'Нужно исправить денежные данные',DIRECT_IDENTITY_REWORK:'Нужно перепроверить кампании',METRICA_GOALS_REWORK:'Проверить конфигурацию Метрики',BLOCKED_LOCAL_CONFIG:'Нет локальной конфигурации'}[s]||s||'—'}
function moneyAction(m){let k=num(m.k5_observed);if(m.state==='ERROR'||m.state==='HOLD_DATA_QUALITY')return 'Не менять рекламу до исправления данных';if(m.state==='NO_DIRECT_SPEND')return 'Нет расхода — K5 не считаем';if(k===null)return 'Накопить корректные данные';if(k<3)return 'Не масштабировать; снижать стоимость трафика';if(k<5)return 'Снижать CPC; бюджет не увеличивать';if(k<6)return 'Держать и подтверждать результат';return 'Кандидат на осторожное масштабирование'}
function moneyStateClass(m){if(m.state==='ERROR'||m.state==='HOLD_DATA_QUALITY')return 'bad';let k=num(m.k5_observed);if(k!==null&&k>=5)return 'ok';return 'warn'}
function fmtDate(v){if(!v)return '—';let [y,m,d]=v.split('-');return `${d}.${m}.${y}`}
function renderWindow(w){w=w||{};document.getElementById('dateFrom').value=w.date_from||'';document.getElementById('dateTo').value=w.date_to||'';document.getElementById('periodLabel').innerHTML=`<b>${fmtDate(w.date_from)} — ${fmtDate(w.date_to)}</b> · ${esc(w.days||'—')} завершённых дн. <span class="periodNote">сегодня не включён</span>`;document.querySelectorAll('.preset[data-days]').forEach(b=>b.classList.toggle('active',Number(b.dataset.days)===Number(w.preset_days)))}
function render(s){lastSnapshot=s;renderWindow(s.window);let a=s.owner_advice||{};let p=a.portfolio||{};let primary=a.primary_action||{};document.getElementById('portfolioK5').textContent=fmtK5(p.k5);document.getElementById('portfolioSpend').textContent=fmtMoney(p.spend_rub);document.getElementById('portfolioRevenue').textContent=fmtMoney(p.revenue_rub);let ps=document.getElementById('portfolioStatus');ps.textContent=statusText(p.status);ps.className='status '+(p.status==='TARGET_MET'?'ok':p.status==='BELOW_TARGET'||p.status==='DATA_HOLD'?'bad':'warn');document.getElementById('primaryTitle').textContent=primary.title||'Обновить данные';document.getElementById('primaryDo').textContent=primary.do_now||'—';let pv=document.getElementById('primarySeverity');pv.textContent=primary.severity||'READ ONLY';pv.className='status '+sevClass(primary.severity);let actions=a.actions||[];document.getElementById('actions').innerHTML=actions.length?actions.map((x,i)=>`<div class="action"><div class="num">${i+1}</div><div><div class="actionTitle">${esc(x.title)}</div><div class="muted">${esc(x.evidence)}</div><div class="actionGrid"><div class="mini"><b>Сделать</b>${esc(x.do_now)}</div><div class="mini"><b>Зачем</b>${esc(x.expected_effect)}</div><div class="mini danger" style="grid-column:1/-1"><b>Не делать</b>${esc(x.prohibited)}</div></div></div></div>`).join(''):'<div class="action"><div class="num">1</div><div><div class="actionTitle">Обновить данные</div></div></div>';let money=s.money||[];document.getElementById('money').innerHTML=money.length?money.map(m=>`<div class="row"><div><b>${esc(m.label)}</b><div class="muted">кампания ${esc(m.campaign_id)}</div></div><span>Расход: ${fmtMoney(m.direct_spend_rub)}<br><span class="muted">Доход: ${fmtMoney(m.metrica_attributed_yan_revenue_rub)}</span></span><span><b>K5 ${fmtK5(m.k5_observed)}</b><br><span class="pill ${moneyStateClass(m)}">${esc(m.state)}</span></span><span>${esc(moneyAction(m))}</span></div>`).join(''):'<div class="row"><span>Денежная выборка пока недоступна</span></div>';document.getElementById('system').textContent=stateRu(s.state);document.getElementById('yanlink').textContent=s.metrica_yan_monetization_ready?'Доход РСЯ читается':'Нет подтверждения';document.getElementById('updated').textContent=s.updated_at?new Date(s.updated_at).toLocaleString('ru-RU'):'—';document.getElementById('errors').textContent=(s.errors||[]).length?(s.errors||[]).slice(0,2).join(' · '):'нет'}
async function load(){let r=await fetch('/api/snapshot');render(await r.json())}
async function refresh(payload){let b=document.getElementById('refresh');b.disabled=true;b.textContent='Проверяю…';try{let r=await fetch('/api/refresh',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload||{})});let data=await r.json();if(!r.ok){alert(data.detail||'Не удалось обновить данные');return}render(data)}finally{b.disabled=false;b.textContent='Обновить'}}
document.getElementById('refresh').onclick=()=>refresh(lastSnapshot&&lastSnapshot.window&&lastSnapshot.window.mode==='CUSTOM'?{date_from:lastSnapshot.window.date_from,date_to:lastSnapshot.window.date_to}:{days:(lastSnapshot&&lastSnapshot.window&&lastSnapshot.window.preset_days)||7});document.querySelectorAll('.preset[data-days]').forEach(b=>b.onclick=()=>refresh({days:Number(b.dataset.days)}));document.getElementById('applyCustom').onclick=()=>refresh({date_from:document.getElementById('dateFrom').value,date_to:document.getElementById('dateTo').value});load();
</script></body></html>"""


class Handler(BaseHTTPRequestHandler):
    server_version = "ProfitEngineLocal/1.1"

    def _json(self, value: dict[str, Any], status: int = 200) -> None:
        body = json.dumps(value, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/":
            body = HTML.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if self.path == "/api/snapshot":
            self._json(load_snapshot())
            return
        self._json({"error": "not_found"}, 404)

    def _request_json(self) -> dict[str, Any]:
        try:
            length = int(self.headers.get("Content-Length", "0") or "0")
        except ValueError:
            length = 0
        if length <= 0:
            return {}
        raw = self.rfile.read(min(length, 4096)).decode("utf-8")
        value = json.loads(raw)
        if not isinstance(value, dict):
            raise ValueError("invalid refresh request")
        return value

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/api/refresh":
            self._json({"error": "not_found"}, 404)
            return
        try:
            request = self._request_json()
            self._json(collect_snapshot(
                days=request.get("days"),
                date_from=request.get("date_from"),
                date_to=request.get("date_to"),
            ))
        except (ValueError, json.JSONDecodeError) as exc:
            self._json({
                "state": "INVALID_WINDOW",
                "detail": str(exc),
                "provider_write_allowed": False,
                "writer_state": "LOCKED",
            }, 400)
        except Exception as exc:
            self._json({
                "state": "REFRESH_FAILED",
                "detail": str(exc),
                "provider_write_allowed": False,
                "writer_state": "LOCKED",
            }, 500)

    def log_message(self, format: str, *args: object) -> None:
        return


def serve(*, port: int = PORT, open_browser: bool = False) -> None:
    server = ThreadingHTTPServer((HOST, port), Handler)
    if open_browser:
        threading.Timer(0.5, lambda: subprocess.run(["open", f"http://{HOST}:{port}"], check=False)).start()
    print(f"Profit Engine control panel: http://{HOST}:{port}")
    print("Provider writes from panel: LOCKED / 0")
    server.serve_forever()


def main() -> int:
    parser = argparse.ArgumentParser(description="Localhost-only Profit Engine owner action console")
    parser.add_argument("--port", type=int, default=PORT)
    parser.add_argument("--open", action="store_true")
    parser.add_argument("--refresh-once", action="store_true")
    parser.add_argument("--days", type=int, default=DEFAULT_DAYS)
    parser.add_argument("--date-from")
    parser.add_argument("--date-to")
    args = parser.parse_args()
    if args.refresh_once:
        print(json.dumps(collect_snapshot(
            days=None if args.date_from or args.date_to else args.days,
            date_from=args.date_from,
            date_to=args.date_to,
        ), ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    serve(port=args.port, open_browser=args.open)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
