#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
tmp_config="$(mktemp "${TMPDIR:-/tmp}/profit-engine-day12.XXXXXX.json")"
trap 'rm -f "$tmp_config"' EXIT

PYTHONPATH="$repo_root/profit-engine/runtime" python3 - "$tmp_config" <<'PY'
from pathlib import Path
import sys

from profit_engine_runtime.live_bootstrap import write_live_config

write_live_config(Path(sys.argv[1]), force=True)
PY

PYTHONPATH="$repo_root/profit-engine/runtime" \
  python3 -m profit_engine_runtime.day12_readiness_cli --config "$tmp_config"
