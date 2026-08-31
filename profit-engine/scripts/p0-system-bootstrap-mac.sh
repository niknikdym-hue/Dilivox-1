#!/usr/bin/env bash
set -euo pipefail

source_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

# 1) Install/update the permanent localhost control panel and private Dilivox config.
bash "$source_root/profit-engine/scripts/install-profit-engine-control-panel.sh"

root="$HOME/.local/share/profit-engine/Dilivox-1"
config="$HOME/.config/profit-engine/sites/dilivox.json"
export PYTHONPATH="$root/profit-engine/runtime"

printf '\n=== P0: METRICA GOALS AUDIT ===\n'
goals_json="$(mktemp "${TMPDIR:-/tmp}/profit-engine-goals.XXXXXX.json")"
trap 'rm -f "$goals_json"' EXIT
set +e
python3 -m profit_engine_runtime.metrica_goals_cli --config "$config" > "$goals_json"
goals_rc=$?
set -e
cat "$goals_json"

if [[ $goals_rc -ne 0 ]]; then
  read -r missing_count invalid_count duplicate_count < <(python3 - "$goals_json" <<'PY'
import json, sys
v=json.load(open(sys.argv[1], encoding='utf-8'))
print(len(v.get('missing_identifiers', [])), len(v.get('invalid_identifiers', [])), len(v.get('duplicate_identifiers', [])))
PY
)

  if [[ "$invalid_count" != "0" || "$duplicate_count" != "0" ]]; then
    echo "BLOCKED_METRICA_GOALS: existing canonical identifiers are invalid/duplicated; no goal writes sent." >&2
  elif [[ "$missing_count" != "0" ]]; then
    apply="${PROFIT_ENGINE_APPLY_MISSING_GOALS:-}"
    if [[ "$apply" != "YES" ]] && command -v osascript >/dev/null 2>&1; then
      button="$(osascript -e 'button returned of (display dialog "Profit Engine нашёл отсутствующие канонические цели Метрики. Создать ТОЛЬКО отсутствующие цели? Существующие цели не изменяются и не удаляются." buttons {"Не сейчас", "Создать отсутствующие"} default button "Создать отсутствующие" with icon caution)')"
      [[ "$button" == "Создать отсутствующие" ]] && apply="YES" || true
    fi
    if [[ "$apply" == "YES" ]]; then
      printf '\n=== P0: CREATE ONLY MISSING METRICA GOALS ===\n'
      python3 -m profit_engine_runtime.metrica_goals_cli --config "$config" --apply-missing
    else
      echo "METRICA_GOALS_REWORK_PENDING: missing goals were not created."
    fi
  fi
fi

printf '\n=== P0: LIVE READ MODEL / MONEY / PANEL SNAPSHOT ===\n'
set +e
python3 -m profit_engine_runtime.control_panel --refresh-once
panel_rc=$?
set -e

printf '\n=== P0: CURRENT DILIVOX PRODUCTION SITE CHECK ===\n'
set +e
python3 -m profit_engine_runtime.site_live_probe_cli
site_rc=$?
set -e

printf '\n=== P0: PREPARE ONE-PASTE TILDA PRODUCTION PACKAGE ===\n'
bash "$root/profit-engine/scripts/prepare-dilivox-tilda-production-head.sh"

snapshot="$HOME/.config/profit-engine/control-panel/snapshot.json"
if [[ -f "$snapshot" ]]; then
  printf '\n=== P0: RESOLVED NEXT STATE ===\n'
  python3 - "$snapshot" "$site_rc" <<'PY'
import json, sys
v=json.load(open(sys.argv[1], encoding='utf-8'))
site_rc=int(sys.argv[2])
state=v.get('state')
print('state=' + str(state))
print('writer_state=' + str(v.get('writer_state')))
print('provider_write_allowed=' + str(v.get('provider_write_allowed')))
print('site_instrumentation_live=' + ('true' if site_rc == 0 else 'false'))
if site_rc != 0:
    print('site_next=Paste the prepared Profit Engine v1 block into Tilda site-wide HEAD and publish all pages; rerun this bootstrap for automatic live verification.')
if state == 'WAITING_METRICA_YAN_PROPAGATION':
    print('next=Provider monetization propagation is still pending; keep Direct fail-closed. Site instrumentation may be published in parallel.')
elif state == 'METRICA_GOALS_REWORK':
    print('next=Close Metrica goal audit/readback, then refresh panel.')
elif state == 'MONEY_PREFLIGHT_REWORK':
    print('next=Money attribution/reconciliation needs rework; no Direct mutation.')
elif state == 'READ_MODEL_READY':
    print('next=Central Brain may evaluate exact Dilivox money evidence for first reversible Direct smoke.')
else:
    print('next=Use the panel diagnostics; no Direct write is authorized by this bootstrap.')
PY
fi

/usr/bin/open "$HOME/Applications/Profit Engine.app" >/dev/null 2>&1 || true

cat <<EOF

P0_BOOTSTRAP_COMPLETE
control_panel=$HOME/Applications/Profit Engine.app
tilda_package=$HOME/.config/profit-engine/tilda/dilivox-profit-engine-head-v1.html
panel_exit_code=$panel_rc
site_probe_exit_code=$site_rc
direct_provider_write_requests=0
direct_writer_authorized=false

The Tilda package is in the clipboard when pbcopy is available. Publication is the only external site-UI step not executable by the current project tools.
EOF
