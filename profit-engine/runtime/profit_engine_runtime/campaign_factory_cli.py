from __future__ import annotations
import argparse
from dataclasses import asdict
import json
from pathlib import Path
from .campaign_factory import synthetic_fixture

def main() -> int:
    parser = argparse.ArgumentParser(description="Build a credential-free Campaign Factory dry-run preview")
    parser.add_argument("scenario", choices=("valid", "missing-content", "invalid-tracking", "invalid-capability"))
    parser.add_argument("--registry", type=Path, required=True)
    args = parser.parse_args()
    preview = synthetic_fixture(args.registry, args.scenario)
    print(json.dumps(asdict(preview), ensure_ascii=False, sort_keys=True, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
