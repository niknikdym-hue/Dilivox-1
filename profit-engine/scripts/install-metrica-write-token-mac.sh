#!/usr/bin/env bash
set -euo pipefail

SERVICE="ProfitEngine-MetricaOAuth-Write"
ACCOUNT="profit-engine"
SOURCE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
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

choice="$(osascript -e 'button returned of (display dialog "Нужно отдельное Yandex OAuth приложение только для администрирования Метрики.\n\nТип: Для доступа к API или отладки\nНазвание: Profit Engine — Metrica Admin\nДоступы: metrika:read и metrika:write\n\nРабочее Direct OAuth-приложение НЕ меняйте.\n\nЕсли такого приложения ещё нет, нажмите Создать — откроется официальный Yandex OAuth." buttons {"Уже создано", "Создать"} default button "Создать")')"
if [[ "$choice" == "Создать" ]]; then
  /usr/bin/open "https://oauth.yandex.ru/client/new/" >/dev/null 2>&1 || true
  osascript -e 'display dialog "Создайте приложение «Для доступа к API или отладки», укажите доступы metrika:read и metrika:write, затем скопируйте Client ID. После этого нажмите Продолжить." buttons {"Продолжить"} default button "Продолжить"' >/dev/null
fi

client_id="$(osascript -e 'text returned of (display dialog "Вставьте Client ID отдельного приложения Profit Engine — Metrica Admin. Client ID не является OAuth-токеном; он нужен только для открытия страницы выдачи токена." default answer "" buttons {"Отмена", "Продолжить"} default button "Продолжить")')"
if [[ -z "$client_id" ]]; then
  echo "BLOCKED: Client ID не введён." >&2
  exit 2
fi

/usr/bin/open "https://oauth.yandex.ru/authorize?response_type=token&client_id=${client_id}&force_confirm=yes" >/dev/null 2>&1 || true
osascript -e 'display dialog "В браузере нажмите Разрешить. На странице verification_code скопируйте access_token. Сам токен в ChatGPT/GitHub не отправляйте. Затем нажмите Продолжить." buttons {"Продолжить"} default button "Продолжить"' >/dev/null

token="$(osascript -e 'text returned of (display dialog "Вставьте OAuth-токен с правами metrika:read + metrika:write. Он будет сохранён только в macOS Keychain." default answer "" with hidden answer buttons {"Отмена", "Сохранить"} default button "Сохранить")')"
if [[ -z "$token" ]]; then
  echo "BLOCKED: токен не введён." >&2
  exit 2
fi

security add-generic-password -U -s "$SERVICE" -a "$ACCOUNT" -w "$token" >/dev/null
unset token

echo "METRICA_WRITE_TOKEN_STORED: Keychain $SERVICE/$ACCOUNT; значение не выводится."

if [[ -f "$CONFIG" ]]; then
  export PYTHONPATH="$SOURCE_ROOT/profit-engine/runtime"
  printf '\n=== VERIFY BY FRESH-RUNTIME BOUNDED MISSING-GOAL APPLY/READBACK ===\n'
  set +e
  python3 -m profit_engine_runtime.metrica_goals_cli --config "$CONFIG" --apply-missing
  rc=$?
  set -e
  if [[ $rc -eq 0 ]]; then
    echo "METRICA_WRITE_SCOPE_VERIFIED: канонические цели созданы/проверены."
  else
    echo "METRICA_WRITE_SCOPE_NOT_VERIFIED: отдельное OAuth-приложение должно иметь metrika:write; автоматического повторного POST нет." >&2
  fi
  exit "$rc"
fi

echo "METRICA_WRITE_TOKEN_STORED: private config пока недоступен; проверка будет выполнена следующим P0 bootstrap."
