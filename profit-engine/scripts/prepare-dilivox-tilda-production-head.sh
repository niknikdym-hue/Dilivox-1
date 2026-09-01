#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
goals_js="$repo_root/profit-engine/sites/dilivox/tilda/dilivox-metrica-goals-v1.js"
out_dir="$HOME/.config/profit-engine/tilda"
out="$out_dir/dilivox-profit-engine-head-v1.html"

mkdir -p "$out_dir"
chmod 700 "$out_dir"

{
  printf '%s\n' '<!-- PROFIT ENGINE DILIVOX PRODUCTION INSTRUMENTATION v1 -->'
  printf '%s\n' '<!-- Existing DILIVOX_SYSTEM_V1 remains the sole UX/event source. -->'
  printf '%s\n' '<!-- This bridge initializes no counter and installs no second progress/navigation controller. -->'
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
2. Keep the existing Metrica counter 110349067 and existing DILIVOX_SYSTEM_V1 UX block exactly once.
3. Replace only the Profit Engine block between its v1 comments if one exists; otherwise paste this block once immediately after DILIVOX_SYSTEM_V1.
4. Save and Publish all pages only after Central Brain acceptance.
5. Do not add dilivox-event-layer-task006.js separately; do not alter YAN blocks or story T123 blocks.
EOF
