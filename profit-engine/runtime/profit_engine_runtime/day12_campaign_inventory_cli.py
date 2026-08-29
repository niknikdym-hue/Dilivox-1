from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Callable

from .config import DEFAULT_CONFIG_PATH, load_site_config, resolve_secret
from .day12_campaign_inventory import YandexDirectCampaignInventory
from .redaction import redact
from .transport import HttpTransport, UrllibTransport


SecretResolver = Callable[[str], str | None]


def run_campaign_inventory(
    *,
    config_path: Path,
    transport: HttpTransport | None = None,
    secret_resolver: SecretResolver = resolve_secret,
) -> dict[str, object]:
    config, present = load_site_config(config_path)
    if not present:
        raise FileNotFoundError(
            f"private Dilivox config not found at {config_path}; run the canonical live bootstrap/readiness flow first"
        )
    if not config.direct_operator_login or not config.direct_client_login:
        raise ValueError("exact Direct operator and managed target bindings are required")
    if config.direct_operator_login.casefold() == config.direct_client_login.casefold():
        raise ValueError("Direct operator and managed target must differ")
    token = secret_resolver(config.yandex_oauth_token_ref)
    if not token:
        raise ValueError("Direct OAuth credential is unavailable")

    inventory = YandexDirectCampaignInventory(
        transport=transport or UrllibTransport(max_attempts=3, backoff_seconds=0.2),
        config=config,
    ).read_all(token=token)

    public = {
        "mode": "DAY12_DIRECT_CAMPAIGN_INVENTORY_READ_ONLY",
        "site_id": inventory.site_id,
        "total_campaigns": inventory.total_campaigns,
        "page_count": inventory.page_count,
        "campaigns": [
            {
                "campaign_id": item.campaign_id,
                "name": item.name,
                "type": item.campaign_type,
                "state": item.normalized_state,
                "provider_state": item.provider_state,
                "status": item.status,
            }
            for item in inventory.items
        ],
        "request_ids": list(inventory.request_ids),
        "units": list(inventory.units),
        "provider_write_allowed": inventory.provider_write_allowed,
        "candidate_selected": inventory.candidate_selected,
        "inventory_digest": inventory.inventory_digest,
        "credential_values_printed": False,
    }
    return redact(public, (token,))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Profit Engine Day-12 read-only exact Direct campaign inventory"
    )
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH)
    args = parser.parse_args()
    print(json.dumps(
        run_campaign_inventory(config_path=args.config),
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
