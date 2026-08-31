#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
target="${PROFIT_ENGINE_DIRECT_TARGET_LOGIN:-}"

if [[ -z "$target" ]]; then
  if ! command -v osascript >/dev/null 2>&1; then
    echo "BLOCKED: set PROFIT_ENGINE_DIRECT_TARGET_LOGIN to the exact managed owner advertiser login." >&2
    exit 2
  fi
  target="$(osascript -e 'text returned of (display dialog "Введите точный логин рекламного аккаунта Dilivox, которым управляет reklamadymova" default answer "" buttons {"Отмена", "OK"} default button "OK")')"
fi

if [[ -z "$target" ]]; then
  echo "BLOCKED: exact managed owner advertiser login is required." >&2
  exit 2
fi
if [[ "$(printf '%s' "$target" | tr '[:upper:]' '[:lower:]')" == "reklamadymova" ]]; then
  echo "BLOCKED: reklamadymova is the Managing Account/operator, not the managed advertiser target." >&2
  exit 2
fi

tmp_config="$(mktemp "${TMPDIR:-/tmp}/profit-engine-day12-money.XXXXXX.json")"
trap 'rm -f "$tmp_config"' EXIT

PYTHONPATH="$repo_root/profit-engine/runtime" python3 - "$tmp_config" "$target" <<'PY'
from pathlib import Path
import sys
from profit_engine_runtime.live_bootstrap import write_live_config

write_live_config(
    Path(sys.argv[1]),
    direct_target_login=sys.argv[2],
    force=True,
)
PY

if [[ -n "${PROFIT_ENGINE_DATE_FROM:-}" && -n "${PROFIT_ENGINE_DATE_TO:-}" ]]; then
  date_from="$PROFIT_ENGINE_DATE_FROM"
  date_to="$PROFIT_ENGINE_DATE_TO"
elif [[ -n "${PROFIT_ENGINE_DATE_FROM:-}" || -n "${PROFIT_ENGINE_DATE_TO:-}" ]]; then
  echo "BLOCKED: set both PROFIT_ENGINE_DATE_FROM and PROFIT_ENGINE_DATE_TO, or neither." >&2
  exit 2
else
  read -r date_from date_to < <(python3 - <<'PY'
from datetime import date, timedelta
end = date.today() - timedelta(days=1)
start = end - timedelta(days=29)
print(start.isoformat(), end.isoformat())
PY
)
fi

printf 'DAY12_DILIVOX_MONEY_WINDOW %s %s\n' "$date_from" "$date_to"
printf '\n=== METRICA YAN MONETIZATION LINK GATE ===\n'
set +e
compatibility_output="$(
  PYTHONPATH="$repo_root/profit-engine/runtime" \
    python3 -m profit_engine_runtime.day12_metrica_yan_compatibility_cli \
    --config "$tmp_config" \
    --date-from "$date_from" \
    --date-to "$date_to" 2>&1
)"
compatibility_status=$?
set -e
printf '%s\n' "$compatibility_output"

if [[ $compatibility_status -ne 0 ]]; then
  echo "BLOCKED_METRICA_YAN_NOT_ENABLED: no Direct/YAN money attribution will run until the YAN site dilivox.ru is linked to Metrica tag 110349067 via 'Show YAN reports in Yandex Metrica'." >&2
  echo "Provider documentation says monetization data can appear within 24 hours after enabling the tag." >&2
  echo "PROVIDER_WRITE_REQUESTS=0" >&2
  exit 2
fi

for campaign_id in 712203524 712791195; do
  printf '\n=== DILIVOX MONEY PREFLIGHT campaign_id=%s ===\n' "$campaign_id"
  PYTHONPATH="$repo_root/profit-engine/runtime" \
    python3 -m profit_engine_runtime.day12_money_preflight_cli \
    --config "$tmp_config" \
    --campaign-id "$campaign_id" \
    --date-from "$date_from" \
    --date-to "$date_to"
done
