from __future__ import annotations

import json
import os
import stat
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DEFAULT_CONFIG_PATH = Path("~/.config/profit-engine/sites/dilivox.json").expanduser()


@dataclass(frozen=True)
class SiteConfig:
    site_id: str = "dilivox"
    canonical_domain: str = "dilivox.ru"
    rollout_mode: str = "READ_ONLY"
    yandex_oauth_token_ref: str = "env:PROFIT_ENGINE_YANDEX_OAUTH_TOKEN"
    yan_stats_token_ref: str = "env:PROFIT_ENGINE_YAN_STATS_TOKEN"
    direct_client_login: str | None = None
    metrica_counter_id: str | None = None
    metrica_dimensions: tuple[str, ...] = ("ym:s:date",)
    yan_resource_id: str | None = None
    yan_revenue_field: str | None = None
    yan_currency: str | None = None
    yan_timezone: str | None = None
    yan_vat_basis: str | None = None
    direct_endpoint: str = "https://api.direct.yandex.com/json/v5"
    metrica_management_endpoint: str = "https://api-metrika.yandex.net/management/v1"
    metrica_reports_endpoint: str = "https://api-metrika.yandex.net/stat/v1/data"
    yan_stats_endpoint: str = "https://partner.yandex.ru/api/statistics2"


def load_site_config(path: Path = DEFAULT_CONFIG_PATH) -> tuple[SiteConfig, bool]:
    if not path.exists():
        return SiteConfig(), False
    mode = stat.S_IMODE(path.stat().st_mode)
    if mode & 0o077:
        raise ValueError(f"private config permissions must be 0600, found {mode:04o}")
    data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    if data.get("rollout_mode") != "READ_ONLY":
        raise ValueError("rollout_mode must be READ_ONLY")
    providers = data.get("providers", {})
    direct = providers.get("direct", {})
    metrica = providers.get("metrica", {})
    yan = providers.get("yan_statistics", {})
    return SiteConfig(
        site_id=data.get("site_id", "dilivox"),
        canonical_domain=data.get("canonical_domain", "dilivox.ru"),
        rollout_mode=data["rollout_mode"],
        yandex_oauth_token_ref=direct.get("token_source_ref", "env:PROFIT_ENGINE_YANDEX_OAUTH_TOKEN"),
        yan_stats_token_ref=yan.get("token_source_ref", "env:PROFIT_ENGINE_YAN_STATS_TOKEN"),
        direct_client_login=_private_value(direct.get("client_login_ref")),
        metrica_counter_id=_private_value(metrica.get("counter_ref")),
        metrica_dimensions=tuple(metrica.get("dimensions", ("ym:s:date",))),
        yan_resource_id=_private_value(yan.get("resource_ref")),
        yan_revenue_field=_private_value(yan.get("revenue_field_ref")),
        yan_currency=_private_value(yan.get("currency")),
        yan_timezone=_private_value(yan.get("timezone")),
        yan_vat_basis=_private_value(yan.get("vat_basis")),
        direct_endpoint=direct.get("endpoint", SiteConfig.direct_endpoint),
        metrica_management_endpoint=metrica.get("management_endpoint", SiteConfig.metrica_management_endpoint),
        metrica_reports_endpoint=metrica.get("reports_endpoint", SiteConfig.metrica_reports_endpoint),
        yan_stats_endpoint=yan.get("endpoint", SiteConfig.yan_stats_endpoint),
    ), True


def resolve_secret(reference: str) -> str | None:
    if reference.startswith("env:"):
        return os.environ.get(reference.removeprefix("env:")) or None
    if reference.startswith("keychain:"):
        service_account = reference.removeprefix("keychain:")
        if "/" not in service_account:
            raise ValueError("keychain reference must be keychain:<service>/<account>")
        service, account = service_account.split("/", 1)
        completed = subprocess.run(
            ["security", "find-generic-password", "-s", service, "-a", account, "-w"],
            check=False,
            capture_output=True,
            text=True,
        )
        return completed.stdout.rstrip("\n") if completed.returncode == 0 else None
    raise ValueError("unsupported secret reference; use env: or keychain:")


def _private_value(value: Any) -> str | None:
    if value in (None, "", "PRIVATE_LOCAL_VALUE"):
        return None
    return str(value)
