from __future__ import annotations

import argparse
import json
from pathlib import Path

from .config import DEFAULT_CONFIG_PATH
from .day12_readiness import (
    ACCEPTED_TASK_011R_SHA,
    DirectPermissionState,
    build_day12_launch_readiness,
)
from .doctor import run as run_doctor
from .redaction import redact


def main() -> int:
    parser = argparse.ArgumentParser(description="Profit Engine Day-12 read-only launch readiness gate")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH)
    parser.add_argument(
        "--direct-permission",
        choices=[item.value for item in DirectPermissionState],
        default=DirectPermissionState.UNKNOWN.value,
        help="Owner-confirmed Direct permission state; this flag never changes provider permissions",
    )
    parser.add_argument("--controller-sha", default=ACCEPTED_TASK_011R_SHA)
    args = parser.parse_args()

    diagnostics = run_doctor(args.config)
    readiness = build_day12_launch_readiness(
        direct_permission=DirectPermissionState(args.direct_permission),
        diagnostics=diagnostics,
        controller_sha=args.controller_sha,
    )
    public = {
        "mode": "DAY12_READ_ONLY_PREFLIGHT",
        "diagnostics": [item.public_dict() for item in diagnostics],
        "readiness": {
            "state": readiness.state.value,
            "reasons": list(readiness.reasons),
            "direct_permission": readiness.direct_permission.value,
            "controller_sha": readiness.controller_sha,
            "provider_statuses": [list(item) for item in readiness.provider_statuses],
            "real_provider_requests": readiness.real_provider_requests,
            "advertising_spend": readiness.advertising_spend,
            "production_writer_enabled": readiness.production_writer_enabled,
            "provider_write_allowed": readiness.provider_write_allowed,
            "readiness_digest": readiness.readiness_digest,
        },
    }
    print(json.dumps(redact(public), ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
