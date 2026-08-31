from __future__ import annotations

import argparse
import json
from pathlib import Path

from .manual_search_campaign_preview import build_manual_search_preview


DEFAULT_REGISTRY = Path(__file__).resolve().parents[2] / "sites" / "dilivox" / "content-registry.json"


def main() -> int:
    parser = argparse.ArgumentParser(description="Non-executable dry-run for DILIVOX | SEARCH | PROFIT ENGINE")
    parser.add_argument("--weekly-budget-rub", required=True)
    parser.add_argument("--keyword", action="append", dest="keywords", required=True)
    parser.add_argument("--landing-content-id")
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    args = parser.parse_args()
    output = build_manual_search_preview(
        registry_path=args.registry,
        weekly_budget_rub=args.weekly_budget_rub,
        keywords=args.keywords,
        landing_content_id=args.landing_content_id,
    )
    print(json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if output["factory_preview"]["state"] == "PREVIEW_VALID" else 2


if __name__ == "__main__":
    raise SystemExit(main())
