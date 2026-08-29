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
target_lower="$(printf '%s' "$target" | tr '[:upper:]' '[:lower:]')"
if [[ "$target_lower" == "reklamadymova" ]]; then
  echo "BLOCKED: reklamadymova is the Managing Account/operator, not the managed advertiser target." >&2
  exit 2
fi

confirmed="${PROFIT_ENGINE_CONFIRM_EDITING:-}"
if [[ "$confirmed" != "YES" ]]; then
  if ! command -v osascript >/dev/null 2>&1; then
    echo "BLOCKED: set PROFIT_ENGINE_CONFIRM_EDITING=YES only after you actually changed Direct Managing Account access to Editing." >&2
    exit 2
  fi
  button="$(osascript -e 'button returned of (display dialog "Подтвердите: в Яндекс.Директе для этого рекламного аккаунта доступ управляющего аккаунта reklamadymova уже изменён с «Чтение» на «Редактирование»." buttons {"Нет", "Да, изменён"} default button "Да, изменён" with icon caution)')"
  if [[ "$button" != "Да, изменён" ]]; then
    echo "BLOCKED: Owner Editing confirmation not given." >&2
    exit 2
  fi
fi

PYTHONPATH="$repo_root/profit-engine/runtime" \
  python3 -m profit_engine_runtime.owner_permission_cli \
  --target-login "$target" \
  --confirm-editing

PROFIT_ENGINE_DIRECT_TARGET_LOGIN="$target" \
  bash "$repo_root/profit-engine/scripts/day12-live-readiness.sh"
