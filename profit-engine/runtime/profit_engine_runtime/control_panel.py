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


HOST = "127.0.0.1"
PORT = 8765
CONTROL_DIR = Path("~/.config/profit-engine/control-panel").expanduser()
SNAPSHOT_PATH = CONTROL_DIR / "snapshot.json"
DILIVOX_CAMPAIGNS = {
    "712203524": "Dilivox",
    "712791195": "dilivox.ru",
}


def completed_window(days: int = 30) -> tuple[str, str]:
    end = date.today() - timedelta(days=1)
    start = end - timedelta(days=days - 1)
    return start.isoformat(), end.isoformat()


def _safe_write_snapshot(value: dict[str, Any]) -> None:
    CONTROL_DIR.mkdir(parents=True, exist_ok=True)
    CONTROL_DIR.chmod(0o700)
    tmp = SNAPSHOT_PATH.with_suffix(".tmp")
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.chmod(0o600)
    tmp.replace(SNAPSHOT_PATH)


def load_snapshot() -> dict[str, Any]:
    if not SNAPSHOT_PATH.exists():
        return {
            "state": "NOT_REFRESHED",
            "updated_at": None,
            "provider_write_allowed": False,
            "writer_state": "LOCKED",
        }
    return json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))


def collect_snapshot(config_path: Path = DEFAULT_CONFIG_PATH) -> dict[str, Any]:
    now = datetime.now(timezone.utc).isoformat()
    date_from, date_to = completed_window()
    snapshot: dict[str, Any] = {
        "state": "REFRESHING",
        "updated_at": now,
        "window": {"date_from": date_from, "date_to": date_to},
        "site_id": "dilivox",
        "domain": "dilivox.ru",
        "target_k5": "5.0",
        "provider_write_allowed": False,
        "writer_state": "LOCKED",
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
        _safe_write_snapshot(snapshot)
        return snapshot

    try:
        goals = audit_goals(config_path=config_path, goals_path=Path(__file__).resolve().parents[2] / "sites" / "dilivox" / "metrica-goals.json")
        snapshot["metrica_goals"] = goals
    except Exception as exc:  # fail closed; no provider write exists in this collector
        snapshot["metrica_goals"] = {"state": "ERROR", "detail": str(exc)}
        snapshot["errors"].append(f"Metrica goals: {exc}")

    try:
        compatibility = run_metrica_yan_probe(config_path=config_path, date_from=date_from, date_to=date_to)
        snapshot["metrica_yan"] = compatibility
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

    monetization_ready = False
    compatibility_results = snapshot.get("metrica_yan", {}).get("results", []) if isinstance(snapshot.get("metrica_yan"), dict) else []
    if compatibility_results:
        monetization_ready = any(
            row.get("probe") == "yan_total_by_date" and row.get("status") == "PASS"
            for row in compatibility_results if isinstance(row, dict)
        )
    snapshot["metrica_yan_monetization_ready"] = monetization_ready

    money: list[dict[str, Any]] = []
    if monetization_ready:
        for campaign_id, label in DILIVOX_CAMPAIGNS.items():
            try:
                value = run_money_preflight(
                    config_path=config_path,
                    campaign_id=campaign_id,
                    date_from=date_from,
                    date_to=date_to,
                )
                value["label"] = label
                money.append(value)
            except Exception as exc:
                money.append({"label": label, "state": "ERROR", "detail": str(exc)})
                snapshot["errors"].append(f"Money preflight {label}: {exc}")
    snapshot["money"] = money

    goal_state = snapshot.get("metrica_goals", {}).get("state") if isinstance(snapshot.get("metrica_goals"), dict) else None
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

    snapshot["updated_at"] = datetime.now(timezone.utc).isoformat()
    _safe_write_snapshot(snapshot)
    return snapshot


HTML = r"""<!doctype html>
<html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Profit Engine — Dilivox</title>
<style>
:root{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;background:#f5f5f7;color:#161617}body{margin:0}.wrap{max-width:1180px;margin:auto;padding:28px}.top{display:flex;justify-content:space-between;gap:20px;align-items:flex-start}.eyebrow{font-size:12px;letter-spacing:.12em;text-transform:uppercase;color:#68686d}.title{font-size:34px;font-weight:760;margin:5px 0}.sub{color:#666;max-width:760px}.btn{border:0;background:#111;color:white;padding:11px 16px;border-radius:10px;font-weight:650;cursor:pointer}.btn:disabled{opacity:.45;cursor:not-allowed}.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:24px 0}.card{background:white;border:1px solid #e5e5e7;border-radius:14px;padding:17px;box-shadow:0 1px 2px rgba(0,0,0,.025)}.label{font-size:12px;color:#777}.value{font-size:25px;font-weight:730;margin-top:7px}.state{font-size:12px;font-weight:700;margin-top:8px}.section{margin:18px 0}.section h2{font-size:18px;margin:0 0 10px}.rows{background:white;border:1px solid #e5e5e7;border-radius:14px;overflow:hidden}.row{display:grid;grid-template-columns:1.4fr 1fr 1fr 1fr;gap:12px;padding:13px 16px;border-bottom:1px solid #eee;align-items:center}.row:last-child{border:0}.muted{color:#777;font-size:13px}.pill{display:inline-block;padding:4px 8px;border-radius:99px;background:#eee;font-size:11px;font-weight:700}.ok{background:#e8f8ec}.warn{background:#fff3d7}.bad{background:#ffe7e7}.locked{background:#eee}.footer{font-size:12px;color:#777;margin-top:25px}@media(max-width:800px){.grid{grid-template-columns:1fr 1fr}.row{grid-template-columns:1fr 1fr}.top{display:block}.btn{margin-top:14px}}@media(max-width:500px){.grid{grid-template-columns:1fr}}
</style></head>
<body><div class="wrap">
<div class="top"><div><div class="eyebrow">DILIVOX · PROFIT ENGINE</div><div class="title">Панель управления</div><div class="sub">Главная цель: 1 ₽ расходов в Директе → 5 ₽ дохода РСЯ. Панель работает только на этом Mac. Боевые изменения заблокированы до отдельного защищённого разрешения на одну конкретную операцию.</div></div><button class="btn" id="refresh">Обновить данные</button></div>
<div class="grid">
<div class="card"><div class="label">Состояние системы</div><div class="value" id="system">—</div><div class="state" id="updated">—</div></div>
<div class="card"><div class="label">Цель K5</div><div class="value">5,00×</div><div class="state">Доход РСЯ / расход Директа</div></div>
<div class="card"><div class="label">РСЯ → Метрика</div><div class="value" id="yanlink">—</div><div class="state" id="yanlinkState">—</div></div>
<div class="card"><div class="label">Боевые действия</div><div class="value">ЗАБЛОКИРОВАНО</div><div class="state">Только через защитные проверки</div></div>
</div>
<div class="section"><h2>Экономика Dilivox</h2><div class="rows" id="money"><div class="row"><span>Данные ещё не обновлены</span></div></div></div>
<div class="section"><h2>Кампании Dilivox</h2><div class="rows" id="campaigns"></div></div>
<div class="section"><h2>Цели Метрики</h2><div class="rows" id="goals"></div></div>
<div class="section"><h2>P0 · Ручное управление поисковой рекламой</h2><div class="rows"><div class="row"><b>DILIVOX | SEARCH | PROFIT ENGINE</b><span>Только Поиск</span><span>Недельный лимит задаёт владелец</span><span class="pill warn">В РАЗРАБОТКЕ</span></div><div class="row"><span>Ставки по ключевым фразам</span><span>Теневой контроллер → защищённая запись</span><span>K5 — главный критерий</span><span class="pill locked">ЗАПИСЬ ЗАБЛОКИРОВАНА</span></div></div></div>
<div class="footer">Секреты: macOS Keychain · доступ только с этого Mac: 127.0.0.1 · записей в рекламные системы из панели: 0</div>
</div><script>
const RU={
 NOT_REFRESHED:'Ещё не обновлялась',REFRESHING:'Обновление…',REFRESH_FAILED:'Ошибка обновления',
 BLOCKED_LOCAL_CONFIG:'Нет локальной конфигурации',WAITING_METRICA_YAN_PROPAGATION:'Ожидаем данные РСЯ в Метрике',
 METRICA_GOALS_REWORK:'Нужно настроить цели Метрики',DIRECT_IDENTITY_REWORK:'Нужно перепроверить кампании Директа',
 MONEY_PREFLIGHT_REWORK:'Нужно перепроверить денежные данные',READ_MODEL_READY:'Данные готовы',
 PASS:'Готово',ACTIVE:'Активна',SUSPENDED:'Приостановлена',ARCHIVED:'В архиве',ACCEPTED:'Принята',MODERATION:'На модерации',
 MISSING:'Отсутствует',DUPLICATE:'Дубликат',WRONG_TYPE:'Неверный тип',REWORK_REQUIRED:'Требует настройки',
 READY_FOR_CANDIDATE_EVALUATION:'Готово к оценке',NO_DIRECT_SPEND:'Нет расходов Директа',HOLD_DATA_QUALITY:'Стоп: качество данных',
 ERROR:'Ошибка',LOCKED:'Заблокировано',BUILD_FIRST:'В разработке',ON:'Активна',OFF:'Выключена'
};
const ROLE={engagement_proxy:'Дочитал до 75%',interaction_proxy:'Сделал выбор',high_value_proxy:'Завершил историю',recirculation_proxy:'Перешёл к следующей истории',return_value_proxy:'Вернулся на сайт'};
function ru(x){let k=String(x??'');return RU[k]||k||'—'}
function role(x){let k=String(x??'');return ROLE[k]||k||'—'}
function p(state){if(state==='PASS'||state==='ACTIVE'||state==='READ_MODEL_READY'||state==='READY_FOR_CANDIDATE_EVALUATION'||state==='ACCEPTED')return 'ok';if(String(state).includes('ERROR')||String(state).includes('REWORK')||state==='WRONG_TYPE'||state==='DUPLICATE')return 'bad';return 'warn'}
function pill(s){return `<span class="pill ${p(s)}" title="${esc(s)}">${esc(ru(s))}</span>`}
function esc(x){return String(x??'—').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
function render(s){
 document.getElementById('system').textContent=ru(s.state); document.getElementById('system').title=s.state||''; document.getElementById('updated').textContent=s.updated_at?'Обновлено: '+new Date(s.updated_at).toLocaleString('ru-RU'):'Ещё не обновлялось';
 document.getElementById('yanlink').textContent=s.metrica_yan_monetization_ready?'ГОТОВО':'ОЖИДАНИЕ'; document.getElementById('yanlinkState').textContent=s.metrica_yan_monetization_ready?'Доход РСЯ читается в Метрике':'Ожидаем активацию или поступление данных';
 let money=s.money||[]; document.getElementById('money').innerHTML=money.length?money.map(m=>`<div class="row"><b>${esc(m.label)}</b><span>Расход: ${esc(m.direct_spend_rub)} ₽</span><span>Доход РСЯ: ${esc(m.metrica_attributed_yan_revenue_rub)} ₽</span><span>K5: ${esc(m.k5_observed)} ${pill(m.state)}</span></div>`).join(''):'<div class="row"><span>Расчёт экономики пока недоступен</span><span></span><span></span><span></span></div>';
 let campaigns=s.campaigns||[]; document.getElementById('campaigns').innerHTML=campaigns.length?campaigns.map(c=>`<div class="row"><b>${esc(c.label)}</b><span>Кампания ${esc(c.campaign_id)}</span><span>${pill(c.state)}</span><span>${esc(ru(c.status))}</span></div>`).join(''):'<div class="row"><span>Нет свежих данных о кампаниях</span></div>';
 let gs=(s.metrica_goals&&s.metrica_goals.goals)||[]; document.getElementById('goals').innerHTML=gs.length?gs.map(g=>`<div class="row"><b>${esc(g.name)}</b><span class="muted">${esc(g.identifier)}</span><span>${pill(g.state)}</span><span>${esc(role(g.role))}</span></div>`).join(''):'<div class="row"><span>Цели ещё не проверены</span></div>';
}
async function load(){let r=await fetch('/api/snapshot');render(await r.json())}
document.getElementById('refresh').onclick=async function(){this.disabled=true;this.textContent='Проверяю…';try{let r=await fetch('/api/refresh',{method:'POST'});render(await r.json())}finally{this.disabled=false;this.textContent='Обновить данные'}};load();
</script></body></html>"""


class Handler(BaseHTTPRequestHandler):
    server_version = "ProfitEngineLocal/1.0"

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

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/api/refresh":
            self._json({"error": "not_found"}, 404)
            return
        try:
            self._json(collect_snapshot())
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
    parser = argparse.ArgumentParser(description="Localhost-only Profit Engine control panel")
    parser.add_argument("--port", type=int, default=PORT)
    parser.add_argument("--open", action="store_true")
    parser.add_argument("--refresh-once", action="store_true")
    args = parser.parse_args()
    if args.refresh_once:
        print(json.dumps(collect_snapshot(), ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    serve(port=args.port, open_browser=args.open)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
