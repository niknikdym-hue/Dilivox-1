from __future__ import annotations

import argparse
from decimal import Decimal
import json
from pathlib import Path
from typing import Callable

from .config import DEFAULT_CONFIG_PATH, load_site_config, resolve_secret
from .day12_money_preflight import Day12MoneyProbe
from .redaction import redact
from .transport import HttpTransport, UrllibTransport


SecretResolver = Callable[[str], str | None]


def run_money_preflight(
    *,
    config_path: Path,
    campaign_id: str,
    date_from: str,
    date_to: str,
    transport: HttpTransport | None = None,
    secret_resolver: SecretResolver = resolve_secret,
) -> dict[str, object]:
    config, config_present = load_site_config(config_path)
    if not config_present:
        raise FileNotFoundError(
            f"private Dilivox config not found at {config_path}; run the canonical live bootstrap/readiness flow first"
        )
    if not config.direct_operator_login or not config.direct_client_login:
        raise ValueError("exact Direct operator and managed target bindings are required")
    if config.direct_operator_login.casefold() == config.direct_client_login.casefold():
        raise ValueError("Direct operator and managed target must differ")
    if not config.metrica_counter_id:
        raise ValueError("exact Metrica counter binding is required")

    direct_token = secret_resolver(config.yandex_oauth_token_ref)
    metrica_token = secret_resolver(config.metrica_oauth_token_ref)
    yan_token = secret_resolver(config.yan_stats_token_ref)
    if not direct_token:
        raise ValueError("Direct OAuth credential is unavailable")
    if not metrica_token:
        raise ValueError("Metrica read OAuth credential is unavailable")
    if not yan_token:
        raise ValueError("YAN Statistics OAuth credential is unavailable")

    probe = Day12MoneyProbe(
        transport=transport or UrllibTransport(max_attempts=3, backoff_seconds=0.2),
        config=config,
    )
    result = probe.run(
        campaign_id=campaign_id,
        date_from=date_from,
        date_to=date_to,
        direct_token=direct_token,
        metrica_token=metrica_token,
        yan_token=yan_token,
    )
    public = {
        "mode": "DAY12_MONEY_PREFLIGHT_READ_ONLY",
        "site_id": result.site_id,
        "campaign_id": result.campaign_id,
        "date_from": result.date_from,
        "date_to": result.date_to,
        "state": result.state.value,
        "holds": list(result.holds),
        "direct_spend_rub": _decimal_text(result.direct_spend_rub),
        "metrica_attributed_yan_revenue_rub": _decimal_text(
            result.metrica_attributed_yan_revenue_rub
        ),
        "yan_control_revenue_rub": _decimal_text(result.yan_control_revenue_rub),
        "k5_observed": _decimal_text(result.k5_observed),
        "attributed_share_of_yan_control": _decimal_text(
            result.attributed_share_of_yan_control
        ),
        "direct_request_id": result.direct_request_id,
        "direct_units": result.direct_units,
        "provider_write_allowed": result.provider_write_allowed,
        "preflight_digest": result.preflight_digest,
        "credential_values_printed": False,
    }
    return redact(public, (direct_token, metrica_token, yan_token))


def _decimal_text(value: Decimal | None) -> str | None:
    return format(value, "f") if value is not None else None


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Profit Engine Day-12 read-only live money preflight"
    )
    parser.add_argument("--campaign-id", required=True)
    parser.add_argument("--date-from", required=True)
    parser.add_argument("--date-to", required=True)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH)
    args = parser.parse_args()

    public = run_money_preflight(
        config_path=args.config,
        campaign_id=args.campaign_id,
        date_from=args.date_from,
        date_to=args.date_to,
    )
    print(json.dumps(public, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
