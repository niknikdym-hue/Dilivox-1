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

tmp_config="$(mktemp "${TMPDIR:-/tmp}/profit-engine-day12-metrica-compat.XXXXXX.json")"
trap 'rm -f "$tmp_config"' EXIT

PYTHONPATH="$repo_root/profit-engine/runtime" python3 - "$tmp_config" "$target" <<'PY'
from pathlib import Path
import sys
from profit_engine_runtime.live_bootstrap import write_live_config
write_live_config(Path(sys.argv[1]), direct_target_login=sys.argv[2], force=True)
PY

read -r date_from date_to < <(python3 - <<'PY'
from datetime import date, timedelta
end = date.today() - timedelta(days=1)
start = end - timedelta(days=29)
print(start.isoformat(), end.isoformat())
PY
)

printf 'DAY12_METRICA_COMPATIBILITY_WINDOW %s %s\n' "$date_from" "$date_to"
PYTHONPATH="$repo_root/profit-engine/runtime" \
  python3 -m profit_engine_runtime.day12_metrica_yan_compatibility_cli \
  --config "$tmp_config" \
  --date-from "$date_from" \
  --date-to "$date_to"
