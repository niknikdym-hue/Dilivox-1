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
apply_json="$(mktemp "${TMPDIR:-/tmp}/profit-engine-goals-apply.XXXXXX.json")"
trap 'rm -f "$goals_json" "$apply_json"' EXIT
set +e
python3 -m profit_engine_runtime.metrica_goals_cli --config "$config" > "$goals_json"
goals_rc=$?
set -e
cat "$goals_json"

goals_write_state="NOT_NEEDED"
if [[ $goals_rc -ne 0 ]]; then
  read -r missing_count invalid_count duplicate_count < <(python3 - "$goals_json" <<'PY'
import json, sys
v=json.load(open(sys.argv[1], encoding='utf-8'))
print(len(v.get('missing_identifiers', [])), len(v.get('invalid_identifiers', [])), len(v.get('duplicate_identifiers', [])))
PY
)

  if [[ "$invalid_count" != "0" || "$duplicate_count" != "0" ]]; then
    goals_write_state="BLOCKED_EXISTING_GOALS_INVALID"
    echo "METRICA GOALS: существующие канонические цели конфликтуют; запись не выполняется." >&2
  elif [[ "$missing_count" != "0" ]]; then
    if ! security find-generic-password -s "ProfitEngine-MetricaOAuth-Write" -a "profit-engine" -w >/dev/null 2>&1; then
      goals_write_state="BLOCKED_METRICA_WRITE_TOKEN_REQUIRED"
      echo "METRICA GOALS: нужен отдельный OAuth-токен с правом metrika:write. Повторный POST не выполняется." >&2
      echo "NEXT: bash profit-engine/scripts/install-metrica-write-token-mac.sh" >&2
    else
      apply="${PROFIT_ENGINE_APPLY_MISSING_GOALS:-}"
      if [[ "$apply" != "YES" ]] && command -v osascript >/dev/null 2>&1; then
        button="$(osascript -e 'button returned of (display dialog "Profit Engine нашёл отсутствующие цели Метрики. Создать только отсутствующие отдельным Metrica-write токеном?" buttons {"Не сейчас", "Создать отсутствующие"} default button "Создать отсутствующие" with icon caution)')"
        [[ "$button" == "Создать отсутствующие" ]] && apply="YES" || true
      fi
      if [[ "$apply" == "YES" ]]; then
        printf '\n=== P0: CREATE ONLY MISSING METRICA GOALS ===\n'
        set +e
        python3 -m profit_engine_runtime.metrica_goals_cli --config "$config" --apply-missing > "$apply_json"
        apply_rc=$?
        set -e
        cat "$apply_json"
        goals_write_state="$(python3 - "$apply_json" <<'PY'
import json, sys
try:
    print(json.load(open(sys.argv[1], encoding='utf-8')).get('state','UNKNOWN'))
except Exception:
    print('UNKNOWN')
PY
)"
        if [[ $apply_rc -ne 0 ]]; then
          echo "METRICA GOALS: gate не закрыт ($goals_write_state); остальные P0 read-only проверки продолжаются." >&2
        fi
      else
        goals_write_state="REWORK_PENDING"
      fi
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
  python3 - "$snapshot" "$site_rc" "$goals_write_state" <<'PY'
import json, sys
v=json.load(open(sys.argv[1], encoding='utf-8'))
site_rc=int(sys.argv[2]); goals=sys.argv[3]; state=v.get('state')
print('state=' + str(state))
print('writer_state=' + str(v.get('writer_state')))
print('provider_write_allowed=' + str(v.get('provider_write_allowed')))
print('site_instrumentation_live=' + ('true' if site_rc == 0 else 'false'))
print('metrica_goals_write_state=' + goals)
if goals == 'BLOCKED_METRICA_WRITE_TOKEN_REQUIRED':
    print('goals_next=Install separate metrika:write token; keep working Direct OAuth unchanged.')
if site_rc != 0:
    print('site_next=Publish the prepared Profit Engine block in Tilda site-wide HEAD and publish all pages.')
if state == 'WAITING_METRICA_YAN_PROPAGATION':
    print('next=YAN→Metrica monetization propagation is pending; other P0 work continues.')
elif state == 'METRICA_GOALS_REWORK':
    print('next=Close Metrica goals; other read-only diagnostics remain available.')
elif state == 'MONEY_PREFLIGHT_REWORK':
    print('next=Money attribution/reconciliation needs rework; no Direct mutation.')
elif state == 'READ_MODEL_READY':
    print('next=Central Brain may evaluate exact money evidence for first reversible Direct smoke.')
else:
    print('next=Use panel diagnostics; no Direct write is authorized by this bootstrap.')
PY
fi

/usr/bin/open "$HOME/Applications/Profit Engine.app" >/dev/null 2>&1 || true

cat <<EOF

P0_BOOTSTRAP_COMPLETE
control_panel=$HOME/Applications/Profit Engine.app
tilda_package=$HOME/.config/profit-engine/tilda/dilivox-profit-engine-head-v1.html
panel_exit_code=$panel_rc
site_probe_exit_code=$site_rc
metrica_goals_write_state=$goals_write_state
direct_provider_write_requests=0
direct_writer_authorized=false
EOF
