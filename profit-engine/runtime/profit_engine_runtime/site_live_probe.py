from __future__ import annotations

from dataclasses import dataclass
import hashlib
import urllib.error
import urllib.request
from typing import Callable


URLS = (
    "https://dilivox.ru/",
    "https://dilivox.ru/istorii/",
)
MARKERS = {
    "package_v1": "PROFIT ENGINE DILIVOX PRODUCTION INSTRUMENTATION v1",
    "existing_ux_event_source": "DILIVOX_SYSTEM_V1",
    "metrica_goals": "ProfitEngineMetricaGoals",
    "canonical_normalizer": "__DILIVOX_CANONICAL_METRICA_V2__",
    "metrica_counter": "110349067",
}
Fetcher = Callable[[str], str]


@dataclass(frozen=True)
class SitePageProbe:
    url: str
    http_ok: bool
    markers: dict[str, bool]
    html_sha256: str | None
    bytes: int | None
    error: str | None = None


def _fetch(url: str) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": "Dilivox-Profit-Engine-Live-Probe/1.0"})
    with urllib.request.urlopen(request, timeout=30) as response:
        if not 200 <= response.status < 300:
            raise RuntimeError(f"HTTP {response.status}")
        return response.read().decode("utf-8", errors="replace")


def inspect_html(url: str, html: str) -> SitePageProbe:
    markers = {name: marker in html for name, marker in MARKERS.items()}
    encoded = html.encode("utf-8")
    return SitePageProbe(
        url=url,
        http_ok=True,
        markers=markers,
        html_sha256=hashlib.sha256(encoded).hexdigest(),
        bytes=len(encoded),
    )


def probe_site(*, fetcher: Fetcher = _fetch) -> dict[str, object]:
    pages: list[SitePageProbe] = []
    for url in URLS:
        try:
            pages.append(inspect_html(url, fetcher(url)))
        except (urllib.error.URLError, TimeoutError, RuntimeError) as exc:
            pages.append(SitePageProbe(url, False, {name: False for name in MARKERS}, None, None, type(exc).__name__))

    all_http = all(page.http_ok for page in pages)
    all_markers = all(all(page.markers.values()) for page in pages)
    if all_http and all_markers:
        state = "PRODUCTION_INSTRUMENTATION_PRESENT"
    elif all_http:
        state = "PRODUCTION_INSTRUMENTATION_MISSING_OR_PARTIAL"
    else:
        state = "SITE_PROBE_ERROR"

    return {
        "mode": "DILIVOX_LIVE_SITE_INSTRUMENTATION_READ_ONLY",
        "state": state,
        "pages": [
            {
                "url": page.url,
                "http_ok": page.http_ok,
                "markers": page.markers,
                "html_sha256": page.html_sha256,
                "bytes": page.bytes,
                "error": page.error,
            }
            for page in pages
        ],
        "provider_write_allowed": False,
        "provider_write_requests": 0,
    }
