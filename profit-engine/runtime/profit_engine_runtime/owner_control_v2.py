from __future__ import annotations

import argparse
import json
import subprocess
import threading
from http.server import ThreadingHTTPServer
from typing import Any

from . import control_panel as legacy
from .development_status import collect_development_status


DEV_SECTION = r"""
<div class="section"><div class="sectionHead"><h2>Разработка · API Codex</h2><div class="hint">quality-first · расходы отдельно от экономики сайта</div></div>
 <div class="levers">
  <div class="lever"><div class="leverTitle">OpenAI API</div><div class="sideBig" id="devApiState">—</div><div class="leverText" id="devApiNote">Проверяется бесплатным GitHub preflight; ключ никогда не показывается в панели.</div></div>
  <div class="lever"><div class="leverTitle">Бюджет разработки</div><div class="sideBig"><span id="devSpent">$0.00</span> / <span id="devEnvelope">$10.00</span></div><div class="leverText">Hard cap одного платного пакета: <b id="devPackageCap">$3.00</b>. Astra — только отдельный Owner opt-in.</div></div>
  <div class="lever"><div class="leverTitle">Последний запуск</div><div class="sideBig" id="devRunState">Нет</div><div class="leverText" id="devRunDetail">Платный запуск ещё не выполнялся.</div></div>
 </div>
 <div class="rows" style="margin-top:11px">
  <div class="row"><b>G0 · GitHub/Python</b><span>$0</span><span>детерминированная работа</span><span class="pill ok">БЕСПЛАТНО</span></div>
  <div class="row"><b>G1 · Luna</b><span>малые задачи</span><span>только если достаточно качества</span><span class="pill neutral">API CODEX</span></div>
  <div class="row"><b>G2 · Terra</b><span>обычная разработка</span><span>основной платный маршрут</span><span class="pill warn">API CODEX</span></div>
  <div class="row"><b>G3 · Sol</b><span>сложное / money / security</span><span>без обязательной попытки слабее</span><span class="pill warn">API CODEX</span></div>
 </div>
</div>
"""

DEV_SCRIPT = r"""
function fmtUsd(x){let n=Number(x);return Number.isFinite(n)?'$'+n.toFixed(2):'—'}
function renderDevelopment(d){
 d=d||{};
 let api=document.getElementById('devApiState');
 if(!api)return;
 let state=d.api_key_state||'NOT_CHECKED';
 api.textContent=state;
 api.className='sideBig';
 document.getElementById('devEnvelope').textContent=fmtUsd(d.initial_openai_dev_envelope_usd);
 document.getElementById('devPackageCap').textContent=fmtUsd(d.default_package_hard_cap_usd);
 document.getElementById('devSpent').textContent=fmtUsd(d.dev_ai_cost_usd);
 let p=d.preflight||{};
 document.getElementById('devApiNote').textContent=state==='READY'?'GitHub preflight подтвердил: OPENAI_API_KEY настроен; значение секрета недоступно панели.':state==='PREFLIGHT_FAILED'?'Preflight не прошёл — платный запуск не разрешён до исправления.':'Ожидается подтверждённый GitHub preflight; платный запуск пока не считаем готовым.';
 let r=d.last_dev_run||{};
 document.getElementById('devRunState').textContent=r.status?(String(r.status).toUpperCase()+(r.conclusion?' / '+String(r.conclusion).toUpperCase():'')):'Нет платных запусков';
 document.getElementById('devRunDetail').textContent=r.display_title||'DEV_AI_COST = $0.00 до первого подтверждённого платного запуска.';
}
"""


def build_html() -> str:
    html = legacy.HTML
    if '<details class="diag">' not in html or 'function render(s){' not in html:
        raise RuntimeError("legacy control panel markers changed; fail closed")
    html = html.replace('<details class="diag">', DEV_SECTION + '\n<details class="diag">', 1)
    html = html.replace('function render(s){', DEV_SCRIPT + '\nfunction render(s){renderDevelopment(s.development||{});', 1)
    return html


HTML = build_html()


def _augment(snapshot: dict[str, Any]) -> dict[str, Any]:
    value = dict(snapshot)
    value["development"] = collect_development_status(fetch_remote=True)
    return value


class Handler(legacy.Handler):
    server_version = "ProfitEngineOwnerControl/2.0"

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
            self._json(_augment(legacy.load_snapshot()))
            return
        super().do_GET()

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/api/refresh":
            self._json({"error": "not_found"}, 404)
            return
        try:
            request = self._request_json()
            snapshot = legacy.collect_snapshot(
                days=request.get("days"),
                date_from=request.get("date_from"),
                date_to=request.get("date_to"),
            )
            self._json(_augment(snapshot))
        except (ValueError, json.JSONDecodeError) as exc:
            self._json({
                "state": "INVALID_WINDOW",
                "detail": str(exc),
                "provider_write_allowed": False,
                "writer_state": "LOCKED",
                "development": collect_development_status(fetch_remote=False),
            }, 400)
        except Exception as exc:
            self._json({
                "state": "REFRESH_FAILED",
                "detail": str(exc),
                "provider_write_allowed": False,
                "writer_state": "LOCKED",
                "development": collect_development_status(fetch_remote=False),
            }, 500)


def serve(*, port: int = legacy.PORT, open_browser: bool = False) -> None:
    server = ThreadingHTTPServer((legacy.HOST, port), Handler)
    if open_browser:
        threading.Timer(
            0.5,
            lambda: subprocess.run(["open", f"http://{legacy.HOST}:{port}"], check=False),
        ).start()
    print(f"Profit Engine Owner Control V2: http://{legacy.HOST}:{port}")
    print("Development visibility: ON / provider writes from panel: LOCKED / 0")
    server.serve_forever()


def main() -> int:
    parser = argparse.ArgumentParser(description="DILIVOX single Owner Control V2")
    parser.add_argument("--port", type=int, default=legacy.PORT)
    parser.add_argument("--open", action="store_true")
    parser.add_argument("--refresh-once", action="store_true")
    parser.add_argument("--days", type=int, default=legacy.DEFAULT_DAYS)
    parser.add_argument("--date-from")
    parser.add_argument("--date-to")
    args = parser.parse_args()
    if args.refresh_once:
        snapshot = legacy.collect_snapshot(
            days=None if args.date_from or args.date_to else args.days,
            date_from=args.date_from,
            date_to=args.date_to,
        )
        print(json.dumps(_augment(snapshot), ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    serve(port=args.port, open_browser=args.open)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
