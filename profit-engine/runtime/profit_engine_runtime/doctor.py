from __future__ import annotations

import argparse
import json
from pathlib import Path

from .clients import YanPartnerStatsReadClient, YandexDirectReadClient, YandexMetricaReadClient
from .config import DEFAULT_CONFIG_PATH, load_site_config, resolve_secret
from .models import DiagnosticResult, DoctorStatus
from .redaction import redact
from .transport import UrllibTransport


def run(config_path: Path = DEFAULT_CONFIG_PATH) -> list[DiagnosticResult]:
    try:
        config, config_present = load_site_config(config_path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        detail = f"private config error: {type(exc).__name__}"
        return [DiagnosticResult(name, DoctorStatus.NOT_ATTEMPTED, detail=detail) for name in ("direct", "metrica", "yan_statistics")]

    transport = UrllibTransport()
    try:
        shared_token = resolve_secret(config.yandex_oauth_token_ref)
        yan_token = resolve_secret(config.yan_stats_token_ref)
    except ValueError as exc:
        detail = str(exc)
        return [DiagnosticResult(name, DoctorStatus.NOT_ATTEMPTED, detail=detail) for name in ("direct", "metrica", "yan_statistics")]

    results = [
        YandexDirectReadClient(transport, config).diagnose(shared_token),
        YandexMetricaReadClient(transport, config).diagnose(shared_token),
        YanPartnerStatsReadClient(transport, config).diagnose(yan_token),
    ]
    if not config_present:
        results = [
            DiagnosticResult(r.provider, r.status, r.checks, r.http_status, r.request_id, r.provider_units, (r.detail or "") + "; using defaults because private registry is absent")
            for r in results
        ]
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Profit Engine read-only provider doctor")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH)
    args = parser.parse_args()
    public = {"rollout_mode": "READ_ONLY", "results": [item.public_dict() for item in run(args.config)]}
    print(json.dumps(redact(public), ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
