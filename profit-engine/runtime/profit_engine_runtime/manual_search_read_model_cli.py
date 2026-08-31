from __future__ import annotations

import argparse
from datetime import date, timedelta
import json
from pathlib import Path

from .config import DEFAULT_CONFIG_PATH
from .manual_search_read_model import public_result, run_manual_search_read


def default_window(days: int = 30) -> tuple[str, str]:
    end = date.today() - timedelta(days=1)
    start = end - timedelta(days=days - 1)
    return start.isoformat(), end.isoformat()


def main() -> int:
    parser = argparse.ArgumentParser(description="Read-only P0 manual-search campaign/keyword/bid/cost model")
    parser.add_argument("--campaign-id", required=True)
    parser.add_argument("--date-from")
    parser.add_argument("--date-to")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH)
    args = parser.parse_args()
    if bool(args.date_from) != bool(args.date_to):
        parser.error("set both --date-from and --date-to, or neither")
    date_from, date_to = (args.date_from, args.date_to) if args.date_from else default_window()
    output = public_result(run_manual_search_read(
        campaign_id=args.campaign_id,
        date_from=date_from,
        date_to=date_to,
        config_path=args.config,
    ))
    print(json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if output["manual_search_shape_ready"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
