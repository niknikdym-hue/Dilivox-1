#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
event_js="$repo_root/profit-engine/sites/dilivox/tilda/dilivox-event-layer-task006.js"
goals_js="$repo_root/profit-engine/sites/dilivox/tilda/dilivox-metrica-goals-v1.js"
out_dir="$HOME/.config/profit-engine/tilda"
out="$out_dir/dilivox-profit-engine-head-v1.html"

mkdir -p "$out_dir"
chmod 700 "$out_dir"

{
  printf '%s\n' '<!-- PROFIT ENGINE DILIVOX PRODUCTION INSTRUMENTATION v1 -->'
  printf '%s\n' '<!-- SiteAgent + event controller: no production transport; Metrica goals only. -->'
  printf '%s\n' '<script>'
  cat "$event_js"
  printf '\n%s\n' '</script>'
  printf '%s\n' '<script>'
  cat <<'BOOT'
(function (w, d) {
  "use strict";
  function start() {
    if (w.DilivoxProfitEngineEventController || !w.ProfitEngineEvents) return;
    try {
      w.DilivoxProfitEngineEventController = w.ProfitEngineEvents.install(w, {
        autoStart: true,
        // Intentionally NO transport: Task 013 records/queues in-memory only.
        // First-party network dispatch remains blocked until Task 015 endpoint acceptance.
        transport: null,
        dispatchKillSwitch: false
      });
    } catch (_) {}
  }
  if (d.readyState === "loading") d.addEventListener("DOMContentLoaded", start, { once: true });
  else setTimeout(start, 0);
})(window, document);
BOOT
  printf '%s\n' '</script>'
  printf '%s\n' '<script>'
  cat "$goals_js"
  printf '\n%s\n' '</script>'
  printf '%s\n' '<!-- /PROFIT ENGINE DILIVOX PRODUCTION INSTRUMENTATION v1 -->'
} > "$out"
chmod 600 "$out"

sha="$(shasum -a 256 "$out" | awk '{print $1}')"
bytes="$(wc -c < "$out" | tr -d ' ')"

if command -v pbcopy >/dev/null 2>&1; then
  pbcopy < "$out"
  copied=true
else
  copied=false
fi

cat <<EOF
TILDA_PRODUCTION_PACKAGE_READY
path=$out
sha256=$sha
bytes=$bytes
clipboard=$copied
provider_write_requests=0
direct_write_allowed=false
yan_block_mutation=false
first_party_network_transport=false

TILDA STEP:
1. Settings сайта -> More/Ещё -> HTML code for the HEAD section.
2. Replace only the Profit Engine block between its v1 comments if one already exists; otherwise paste once.
3. Save and Publish all pages.
4. Do not alter existing YAN blocks or story T123 blocks.
EOF
