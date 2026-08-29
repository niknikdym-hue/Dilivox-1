from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from .config import DEFAULT_CONFIG_PATH


DIRECT_OPERATOR_LOGIN = "reklamadymova"


def build_live_config(direct_target_login: str) -> dict[str, object]:
    target = direct_target_login.strip()
    if not target:
        raise ValueError("direct_target_login is required")
    if target.casefold() == DIRECT_OPERATOR_LOGIN.casefold():
        raise ValueError("managed Direct target login must differ from the technical manager/operator login")
    return {
        "site_id": "dilivox",
        "canonical_domain": "dilivox.ru",
        "rollout_mode": "READ_ONLY",
        "providers": {
            "direct": {
                "endpoint": "https://api.direct.yandex.com/json/v501",
                "token_source_ref": "keychain:ProfitEngine-YandexOAuth-Read/profit-engine",
                "operator_login_ref": DIRECT_OPERATOR_LOGIN,
                "client_login_ref": target,
            },
            "metrica": {
                "management_endpoint": "https://api-metrika.yandex.net/management/v1",
                "reports_endpoint": "https://api-metrika.yandex.net/stat/v1/data",
                "token_source_ref": "keychain:ProfitEngine-YandexOAuth-Read/profit-engine",
                "counter_ref": "110349067",
                "dimensions": ["ym:s:date"],
            },
            "yan_statistics": {
                "endpoint": "https://partner.yandex.ru/api/statistics2",
                "token_source_ref": "keychain:ProfitEngine-YAN-Statistics/profit-engine",
                "revenue_field_ref": "partner_wo_nds",
                "currency": "RUB",
                "timezone": "Europe/Moscow",
            },
        },
    }


def write_live_config(
    path: Path = DEFAULT_CONFIG_PATH,
    *,
    direct_target_login: str,
    force: bool = False,
) -> Path:
    config = build_live_config(direct_target_login)
    if path.exists() and not force:
        existing = json.loads(path.read_text(encoding="utf-8"))
        if existing == config:
            os.chmod(path, 0o600)
            return path
        raise FileExistsError(f"config already exists at {path}; rerun with --force only after reviewing it")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.chmod(path, 0o600)
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description="Install the Dilivox live read configuration using existing macOS Keychain tokens")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH)
    parser.add_argument(
        "--direct-target-login",
        default=os.environ.get("PROFIT_ENGINE_DIRECT_TARGET_LOGIN"),
        help="Exact managed owner advertiser login; never use the technical manager/operator login",
    )
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    if not args.direct_target_login:
        parser.error("--direct-target-login or PROFIT_ENGINE_DIRECT_TARGET_LOGIN is required")
    path = write_live_config(
        args.config,
        direct_target_login=args.direct_target_login,
        force=args.force,
    )
    print(json.dumps({
        "status": "READY",
        "site_id": "dilivox",
        "domain": "dilivox.ru",
        "direct_operator_login": DIRECT_OPERATOR_LOGIN,
        "direct_target_login_configured": True,
        "direct_target_login_printed": False,
        "metrica_counter_id": "110349067",
        "token_values_written": False,
        "config_path": str(path),
        "mode": "READ_ONLY",
    }, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
