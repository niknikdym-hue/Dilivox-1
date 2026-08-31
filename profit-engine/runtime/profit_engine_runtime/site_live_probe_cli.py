from __future__ import annotations

import json

from .site_live_probe import probe_site


def main() -> int:
    result = probe_site()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result.get("state") == "PRODUCTION_INSTRUMENTATION_PRESENT" else 2


if __name__ == "__main__":
    raise SystemExit(main())
