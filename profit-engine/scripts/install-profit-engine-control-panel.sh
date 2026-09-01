#!/usr/bin/env bash
set -euo pipefail

REPO_URL="https://github.com/niknikdym-hue/Dilivox-1.git"
INSTALL_ROOT="$HOME/.local/share/profit-engine"
INSTALL_REPO="$INSTALL_ROOT/Dilivox-1"
APP="$HOME/Applications/Profit Engine.app"
CONFIG="$HOME/.config/profit-engine/sites/dilivox.json"

mkdir -p "$INSTALL_ROOT" "$HOME/Applications"

staging="$INSTALL_ROOT/Dilivox-1.new"
rm -rf "$staging"
git clone --depth 1 --branch profit-engine "$REPO_URL" "$staging"
rm -rf "$INSTALL_REPO.old"
if [[ -d "$INSTALL_REPO" ]]; then mv "$INSTALL_REPO" "$INSTALL_REPO.old"; fi
mv "$staging" "$INSTALL_REPO"
rm -rf "$INSTALL_REPO.old"

if [[ ! -f "$CONFIG" ]]; then
  if ! command -v osascript >/dev/null 2>&1; then
    echo "BLOCKED: macOS osascript is required to install the private Direct target binding." >&2
    exit 2
  fi
  target="$(osascript -e 'text returned of (display dialog "Profit Engine: введите точный логин рекламного аккаунта Dilivox, которым управляет reklamadymova. Логин будет сохранён только локально в приватном config 0600." default answer "" buttons {"Отмена", "OK"} default button "OK")')"
  if [[ -z "$target" ]]; then
    echo "BLOCKED: exact managed advertiser login is required." >&2
    exit 2
  fi
  if [[ "$(printf '%s' "$target" | tr '[:upper:]' '[:lower:]')" == "reklamadymova" ]]; then
    echo "BLOCKED: reklamadymova is the Managing Account/operator, not the advertiser target." >&2
    exit 2
  fi
  PYTHONPATH="$INSTALL_REPO/profit-engine/runtime" \
    python3 -m profit_engine_runtime.live_bootstrap \
    --direct-target-login "$target"
fi
chmod 600 "$CONFIG"

rm -rf "$APP"
mkdir -p "$APP/Contents/MacOS" "$APP/Contents/Resources"
cat > "$APP/Contents/Info.plist" <<'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
<key>CFBundleName</key><string>Profit Engine</string>
<key>CFBundleDisplayName</key><string>Profit Engine</string>
<key>CFBundleIdentifier</key><string>ru.dilivox.profit-engine</string>
<key>CFBundleVersion</key><string>1</string>
<key>CFBundleShortVersionString</key><string>0.1</string>
<key>CFBundlePackageType</key><string>APPL</string>
<key>CFBundleExecutable</key><string>ProfitEngine</string>
<key>LSMinimumSystemVersion</key><string>12.0</string>
</dict></plist>
PLIST

cat > "$APP/Contents/MacOS/ProfitEngine" <<'SH'
#!/usr/bin/env bash
set -euo pipefail
ROOT="$HOME/.local/share/profit-engine/Dilivox-1"
URL="http://127.0.0.1:8765"
if /usr/bin/curl -fsS "$URL/api/snapshot" >/dev/null 2>&1; then
  /usr/bin/open "$URL"
  exit 0
fi
cd "$ROOT"
export PYTHONPATH="$ROOT/profit-engine/runtime"
exec /usr/bin/env python3 -m profit_engine_runtime.control_panel --open
SH
chmod 755 "$APP/Contents/MacOS/ProfitEngine"

# Fail before Finder/open if the bundle contract is broken. This guards the exact
# defect that previously produced "application cannot be opened because its executable is missing".
if [[ ! -x "$APP/Contents/MacOS/ProfitEngine" ]]; then
  echo "BLOCKED_CONTROL_PANEL_BUNDLE: executable is missing or not executable." >&2
  exit 2
fi
if command -v /usr/libexec/PlistBuddy >/dev/null 2>&1; then
  executable_name="$(/usr/libexec/PlistBuddy -c 'Print :CFBundleExecutable' "$APP/Contents/Info.plist" 2>/dev/null || true)"
  if [[ "$executable_name" != "ProfitEngine" ]]; then
    echo "BLOCKED_CONTROL_PANEL_BUNDLE: CFBundleExecutable is not bound to ProfitEngine." >&2
    exit 2
  fi
fi

printf '\nINSTALLED: %s\n' "$APP"
printf 'LOCAL URL: http://127.0.0.1:8765\n'
printf 'PROVIDER WRITES FROM PANEL: LOCKED / 0\n'

# Opening the UI is convenience, not an installation/analytics gate. A Finder/open
# problem must not abort the rest of the P0 bootstrap after the bundle itself passed validation.
if ! /usr/bin/open "$APP" >/dev/null 2>&1; then
  echo "WARN_CONTROL_PANEL_OPEN: bundle is installed and validated, but macOS open returned nonzero; P0 bootstrap will continue." >&2
fi
