from __future__ import annotations

import argparse
import json
from pathlib import Path

from .owner_permission import DEFAULT_OWNER_PERMISSION_PATH, record_owner_permission_evidence


DIRECT_OPERATOR_LOGIN = "reklamadymova"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Record explicit Owner confirmation that Direct Managing Account access is EDITING"
    )
    parser.add_argument("--target-login", required=True, help="Exact managed owner advertiser login")
    parser.add_argument("--output", type=Path, default=DEFAULT_OWNER_PERMISSION_PATH)
    parser.add_argument(
        "--confirm-editing",
        action="store_true",
        help="Required explicit assertion that Owner has already changed the Direct UI relationship to Editing",
    )
    args = parser.parse_args()
    if not args.confirm_editing:
        parser.error("--confirm-editing is required; this command must never infer the UI permission")

    path = record_owner_permission_evidence(
        args.output,
        operator_login=DIRECT_OPERATOR_LOGIN,
        target_login=args.target_login,
        owner_confirmed=True,
    )
    print(json.dumps({
        "status": "RECORDED",
        "permission": "EDITING",
        "source": "YANDEX_DIRECT_MANAGING_ACCOUNT_UI",
        "operator_login": DIRECT_OPERATOR_LOGIN,
        "target_login_plaintext_written": False,
        "provider_write_authorized": False,
        "evidence_path": str(path),
    }, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
