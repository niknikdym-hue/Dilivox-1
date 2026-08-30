from __future__ import annotations

import argparse
import json
from pathlib import Path

from .config import DEFAULT_CONFIG_PATH, load_site_config
from .day12_readiness import (
    ACCEPTED_TASK_011R_SHA,
    Day12ReadinessState,
    build_day12_launch_readiness,
)
from .doctor import run as run_doctor
from .owner_permission import DEFAULT_OWNER_PERMISSION_PATH, load_owner_permission_evidence
from .redaction import redact


def readiness_exit_code(state: Day12ReadinessState) -> int:
    """Return success only for the exact candidate-selection-ready state."""
    return 0 if state == Day12ReadinessState.READY_FOR_LIVE_CANDIDATE_SELECTION else 2


def main() -> int:
    parser = argparse.ArgumentParser(description="Profit Engine Day-12 read-only launch readiness gate")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH)
    parser.add_argument(
        "--owner-permission-evidence",
        type=Path,
        default=DEFAULT_OWNER_PERMISSION_PATH,
        help="Fresh 0600 Owner confirmation of Managing Account Editing; never grants provider write authority",
    )
    parser.add_argument("--controller-sha", default=ACCEPTED_TASK_011R_SHA)
    args = parser.parse_args()

    diagnostics = run_doctor(args.config)
    owner_evidence = None
    owner_evidence_status = "NOT_APPLICABLE"
    try:
        config, _ = load_site_config(args.config)
        if config.direct_operator_login:
            owner_evidence_status = "MISSING"
            if config.direct_client_login:
                try:
                    owner_evidence = load_owner_permission_evidence(
                        args.owner_permission_evidence,
                        operator_login=config.direct_operator_login,
                        target_login=config.direct_client_login,
                    )
                    owner_evidence_status = "VALID"
                except FileNotFoundError:
                    owner_evidence_status = "MISSING"
                except (OSError, ValueError, json.JSONDecodeError):
                    owner_evidence_status = "INVALID"
    except (OSError, ValueError, json.JSONDecodeError):
        owner_evidence_status = "INVALID_CONFIG"

    readiness = build_day12_launch_readiness(
        diagnostics=diagnostics,
        owner_permission_evidence=owner_evidence,
        controller_sha=args.controller_sha,
    )
    public = {
        "mode": "DAY12_READ_ONLY_PREFLIGHT",
        "permission_source": readiness.direct_permission_source,
        "owner_permission_evidence": owner_evidence_status,
        "diagnostics": [item.public_dict() for item in diagnostics],
        "readiness": {
            "state": readiness.state.value,
            "reasons": list(readiness.reasons),
            "direct_permission": readiness.direct_permission.value,
            "direct_permission_source": readiness.direct_permission_source,
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
    return readiness_exit_code(readiness.state)


if __name__ == "__main__":
    raise SystemExit(main())
