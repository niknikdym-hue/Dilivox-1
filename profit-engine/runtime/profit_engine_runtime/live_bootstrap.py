from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from .config import DEFAULT_CONFIG_PATH


DILIVOX_LIVE_CONFIG = {
    "site_id": "dilivox",
    "canonical_domain": "dilivox.ru",
    "rollout_mode": "READ_ONLY",
    "providers": {
        "direct": {
            "endpoint": "https://api.direct.yandex.com/json/v5",
            "token_source_ref": "keychain:ProfitEngine-YandexOAuth-Read/profit-engine",
            "client_login_ref": "reklamadymova",
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


def write_live_config(path: Path = DEFAULT_CONFIG_PATH, *, force: bool = False) -> Path:
    if path.exists() and not force:
        existing = json.loads(path.read_text(encoding="utf-8"))
        if existing == DILIVOX_LIVE_CONFIG:
            os.chmod(path, 0o600)
            return path
        raise FileExistsError(f"config already exists at {path}; rerun with --force only after reviewing it")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(DILIVOX_LIVE_CONFIG, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.chmod(path, 0o600)
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description="Install the Dilivox live read configuration using existing macOS Keychain tokens")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    path = write_live_config(args.config, force=args.force)
    print(json.dumps({
        "status": "READY",
        "site_id": "dilivox",
        "domain": "dilivox.ru",
        "direct_client_login": "reklamadymova",
        "metrica_counter_id": "110349067",
        "token_values_written": False,
        "config_path": str(path),
        "mode": "READ_ONLY",
    }, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
