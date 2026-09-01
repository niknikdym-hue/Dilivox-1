#!/usr/bin/env bash
set -euo pipefail

SERVICE="ProfitEngine-MetricaOAuth-Write"
ACCOUNT="profit-engine"
ROOT="$HOME/.local/share/profit-engine/Dilivox-1"
CONFIG="$HOME/.config/profit-engine/sites/dilivox.json"

if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "BLOCKED: этот установщик предназначен для macOS." >&2
  exit 2
fi
if ! command -v security >/dev/null 2>&1 || ! command -v osascript >/dev/null 2>&1; then
  echo "BLOCKED: нужны стандартные macOS security и osascript." >&2
  exit 2
fi

if security find-generic-password -s "$SERVICE" -a "$ACCOUNT" -w >/dev/null 2>&1; then
  button="$(osascript -e 'button returned of (display dialog "Отдельный Metrica-write токен уже есть в Keychain. Заменить его?" buttons {"Оставить", "Заменить"} default button "Оставить" with icon caution)')"
  if [[ "$button" != "Заменить" ]]; then
    echo "METRICA_WRITE_TOKEN: уже установлен; значение не выводится."
    exit 0
  fi
fi

client_id="$(osascript -e 'text returned of (display dialog "Введите Client ID ОТДЕЛЬНОГО Yandex OAuth API-приложения для Profit Engine Metrica. У приложения должны быть права metrika:read и metrika:write. Не используйте и не перенастраивайте рабочее Direct OAuth-приложение." default answer "" buttons {"Отмена", "Продолжить"} default button "Продолжить")')"
if [[ -z "$client_id" ]]; then
  echo "BLOCKED: Client ID не введён." >&2
  exit 2
fi

/usr/bin/open "https://oauth.yandex.ru/authorize?response_type=token&client_id=${client_id}&force_confirm=yes" >/dev/null 2>&1 || true
osascript -e 'display dialog "В браузере разрешите отдельному приложению доступ к Метрике. После выдачи OAuth-токена скопируйте его. Сам токен в ChatGPT/GitHub не отправляйте. Затем нажмите Продолжить." buttons {"Продолжить"} default button "Продолжить"' >/dev/null

token="$(osascript -e 'text returned of (display dialog "Вставьте OAuth-токен с правами metrika:read + metrika:write. Он будет сохранён только в macOS Keychain." default answer "" with hidden answer buttons {"Отмена", "Сохранить"} default button "Сохранить")')"
if [[ -z "$token" ]]; then
  echo "BLOCKED: токен не введён." >&2
  exit 2
fi

security add-generic-password -U -s "$SERVICE" -a "$ACCOUNT" -w "$token" >/dev/null
unset token

echo "METRICA_WRITE_TOKEN_STORED: Keychain $SERVICE/$ACCOUNT; значение не выводится."

if [[ -d "$ROOT/.git" && -f "$CONFIG" ]]; then
  export PYTHONPATH="$ROOT/profit-engine/runtime"
  printf '\n=== VERIFY BY BOUNDED MISSING-GOAL APPLY/READBACK ===\n'
  set +e
  python3 -m profit_engine_runtime.metrica_goals_cli --config "$CONFIG" --apply-missing
  rc=$?
  set -e
  if [[ $rc -eq 0 ]]; then
    echo "METRICA_WRITE_SCOPE_VERIFIED: канонические цели созданы/проверены."
  else
    echo "METRICA_WRITE_SCOPE_NOT_VERIFIED: проверьте, что отдельное OAuth-приложение имеет metrika:write. Повторных POST этот скрипт автоматически не делает." >&2
  fi
  exit "$rc"
fi

echo "METRICA_WRITE_TOKEN_STORED: runtime/config пока недоступны; проверка будет выполнена следующим P0 bootstrap."
