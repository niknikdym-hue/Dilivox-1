from __future__ import annotations

import argparse
import json
from pathlib import Path
import urllib.error
import urllib.parse
import urllib.request

from .config import DEFAULT_CONFIG_PATH, load_site_config, resolve_secret
from .redaction import redact

YAN_METRICS = "ym:s:yanPartnerPrice,ym:s:yanRequests,ym:s:yanRenders,ym:s:yanShows"
DIRECT_DIM = "ym:s:last_yandex_direct_clickDirectClickOrder"
YAN_SOURCE_DIMS = "ym:s:last_yandex_direct_clickTrafficSource,ym:s:last_yandex_direct_clickSourceEngine"
DILIVOX_CAMPAIGNS = ("712203524", "712791195")


def build_probe_queries(*, counter_id: str, date_from: str, date_to: str) -> list[tuple[str, dict[str, str]]]:
    base = {
        "ids": counter_id,
        "date1": date_from,
        "date2": date_to,
        "accuracy": "full",
        "limit": "100000",
    }
    probes: list[tuple[str, dict[str, str]]] = [
        ("yan_total_by_date", {**base, "dimensions": "ym:s:date", "metrics": YAN_METRICS}),
        ("yan_sources_supported_preset_shape", {**base, "dimensions": YAN_SOURCE_DIMS, "metrics": YAN_METRICS}),
        ("direct_campaign_dimension_visits", {**base, "dimensions": f"ym:s:date,{DIRECT_DIM}", "metrics": "ym:s:visits"}),
        ("direct_campaign_dimension_yan", {**base, "dimensions": f"ym:s:date,{DIRECT_DIM}", "metrics": YAN_METRICS}),
    ]
    for index, campaign_id in enumerate(DILIVOX_CAMPAIGNS, start=1):
        probes.append((
            f"direct_campaign_filter_yan_{index}",
            {
                **base,
                "dimensions": "ym:s:date",
                "metrics": YAN_METRICS,
                "filters": f"{DIRECT_DIM}=='{campaign_id}'",
            },
        ))
    return probes


def _provider_error(body: bytes) -> tuple[str | None, str | None, str | None]:
    try:
        parsed = json.loads(body.decode("utf-8")) if body else {}
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None, None, None
    if not isinstance(parsed, dict):
        return None, None, None
    errors = parsed.get("errors")
    first = errors[0] if isinstance(errors, list) and errors and isinstance(errors[0], dict) else {}
    return (
        str(first.get("error_type")) if first.get("error_type") is not None else None,
        str(first.get("code")) if first.get("code") is not None else None,
        str(first.get("message")) if first.get("message") is not None else None,
    )


def run_probe(*, config_path: Path, date_from: str, date_to: str) -> dict[str, object]:
    config, present = load_site_config(config_path)
    if not present:
        raise FileNotFoundError(f"private Dilivox config not found at {config_path}")
    if not config.metrica_counter_id:
        raise ValueError("exact Metrica counter binding is required")
    token = resolve_secret(config.yandex_oauth_token_ref)
    if not token:
        raise ValueError("shared Metrica OAuth credential is unavailable")

    results: list[dict[str, object]] = []
    for name, query in build_probe_queries(
        counter_id=config.metrica_counter_id,
        date_from=date_from,
        date_to=date_to,
    ):
        url = f"{config.metrica_reports_endpoint}?{urllib.parse.urlencode(query)}"
        request = urllib.request.Request(
            url,
            headers={"Authorization": f"OAuth {token}", "Accept": "application/json"},
            method="GET",
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as raw:
                body = json.loads(raw.read().decode("utf-8"))
                data = body.get("data") if isinstance(body, dict) else None
                results.append({
                    "probe": name,
                    "status": "PASS",
                    "http_status": raw.status,
                    "row_count": len(data) if isinstance(data, list) else None,
                    "sampled": bool(body.get("sampled", False)) if isinstance(body, dict) else None,
                    "contains_sensitive_data": bool(body.get("contains_sensitive_data", False)) if isinstance(body, dict) else None,
                    "currency": body.get("currency") if isinstance(body, dict) else None,
                })
        except urllib.error.HTTPError as exc:
            error_type, error_code, message = _provider_error(exc.read())
            results.append({
                "probe": name,
                "status": "HTTP_ERROR",
                "http_status": exc.code,
                "error_type": error_type,
                "error_code": error_code,
                "error_message": message,
            })
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            results.append({
                "probe": name,
                "status": "TRANSPORT_ERROR",
                "error_type": type(exc).__name__,
            })

    public = {
        "mode": "DAY12_METRICA_YAN_COMPATIBILITY_READ_ONLY",
        "date_from": date_from,
        "date_to": date_to,
        "read_requests_attempted": len(results),
        "provider_write_requests": 0,
        "provider_write_allowed": False,
        "credential_values_printed": False,
        "results": results,
    }
    return redact(public, (token,))


def main() -> int:
    parser = argparse.ArgumentParser(description="Read-only compatibility probe for Metrica YAN revenue attribution")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG_PATH)
    parser.add_argument("--date-from", required=True)
    parser.add_argument("--date-to", required=True)
    args = parser.parse_args()
    print(json.dumps(run_probe(config_path=args.config, date_from=args.date_from, date_to=args.date_to), ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
