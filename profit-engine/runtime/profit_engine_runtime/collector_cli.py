from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from datetime import date, timedelta
from pathlib import Path

from .collectors import DirectCollector, MetricaCollector, YanCollector
from .config import DEFAULT_CONFIG_PATH, load_site_config, resolve_secret
from .doctor import run as doctor_run
from .fixtures import DIRECT, FIXTURE_CAPTURED_AT, METRICA, YAN
from .ingestion import InMemoryRelationalStore, IngestionOrchestrator
from .models import DoctorStatus
from .raw_store import LocalRawStore
from .redaction import redact
from .transport import UrllibTransport


def execute(provider: str, *, fixture: bool, config_path: Path,
    raw_root: Path | None, day: str) -> dict[str, object]:
    config, _ = load_site_config(config_path)
    selected = ("direct", "metrica", "yan") if provider == "all" else (provider,)
    statuses: dict[str, str] = {}
    direct_token = metrica_token = yan_token = None
    if not fixture:
        doctor = {item.provider: item for item in doctor_run(config_path)}
        aliases = {"direct": "direct", "metrica": "metrica", "yan": "yan_statistics"}
        for name in selected:
            result = doctor[aliases[name]]
            statuses[name] = result.status.value
        if any(statuses[name] != DoctorStatus.PASS.value for name in selected):
            return {"mode": "live", "status": "BLOCKED_MISSING_CREDENTIAL", "providers": statuses}
        direct_token = resolve_secret(config.yandex_oauth_token_ref)
        metrica_token = resolve_secret(config.metrica_oauth_token_ref)
        yan_token = resolve_secret(config.yan_stats_token_ref)

    relational = InMemoryRelationalStore()
    orchestrator = IngestionOrchestrator(LocalRawStore(raw_root), relational)
    transport = None if fixture else UrllibTransport(max_attempts=3)
    collectors = {
        "direct": DirectCollector(transport, config, direct_token, day,
            fixture_payload=DIRECT if fixture else None, captured_at=FIXTURE_CAPTURED_AT if fixture else None),
        "metrica": MetricaCollector(transport, config, metrica_token, day,
            counter_id=config.metrica_counter_id, dimensions=config.metrica_dimensions,
            fixture_payload=METRICA if fixture else None,
            captured_at=FIXTURE_CAPTURED_AT if fixture else None),
        "yan": YanCollector(transport, config, yan_token, day,
            revenue_field="fixture_revenue" if fixture else config.yan_revenue_field,
            currency="RUB" if fixture else config.yan_currency,
            timezone_name="Europe/Moscow" if fixture else config.yan_timezone,
            vat_basis="fixture-explicit" if fixture else config.yan_vat_basis,
            fixture_payload=YAN if fixture else None, captured_at=FIXTURE_CAPTURED_AT if fixture else None),
    }
    outcomes = [orchestrator.run(config.site_id, collectors[name]) for name in selected]
    return {"mode": "fixture" if fixture else "live", "status": "COMPLETE",
        "providers": {name: asdict(outcome) for name, outcome in zip(selected, outcomes)},
        "counts": {"campaign_snapshots": len(relational.campaign_snapshots),
            "traffic_facts": len(relational.traffic_facts),
            "monetization_facts": len(relational.monetization_facts)}}


def main() -> int:
    parser = argparse.ArgumentParser(description="Profit Engine READ_ONLY ingestion")
    parser.add_argument("provider", choices=("direct", "metrica", "yan", "all"))
    parser.add_argument("--fixture", action="store_true", help="use deterministic synthetic fixtures")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH)
    parser.add_argument("--raw-root", type=Path)
    parser.add_argument("--day", default=(date.today() - timedelta(days=1)).isoformat())
    args = parser.parse_args()
    try:
        result = execute(args.provider, fixture=args.fixture, config_path=args.config,
            raw_root=args.raw_root, day=args.day)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        result = {"mode": "fixture" if args.fixture else "live", "status": "FAILED",
            "error": type(error).__name__}
    print(json.dumps(redact(result), ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if result["status"] in {"COMPLETE", "BLOCKED_MISSING_CREDENTIAL"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
