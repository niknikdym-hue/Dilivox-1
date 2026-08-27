# TASK-002 — Read Foundation and Provider Certification Evidence

- Timestamp: 2026-08-27 17:41:27 MSK
- Local path: `/Users/elenadymova/Documents/New project/Profit Engine/Dilivox-1`
- Branch: `profit-engine`
- Baseline origin before Task 001 sync: `1af8b80d305a8ec67a5439f632609bf0375c5959`
- Task 001 evidence commit after safe rebase: `38a72ccd26f2016e9fdca1092fca8905e7d2dcb7`
- Origin after Task 001 fast-forward push: `38a72ccd26f2016e9fdca1092fca8905e7d2dcb7`
- Runtime implementation HEAD before this evidence commit: `4aa0486acffcbfd82aa72330a0288c4b0ed57d22`
- Final evidence-bearing HEAD: reported by the final Git verification because a commit cannot contain its own SHA

## Step 0 — Task 001 evidence synchronization

The original local evidence commit `dd0f302...` was rechecked and contained only
`profit-engine/evidence/TASK-001-M0-INVENTORY.md`. Secret-pattern checks found no
secret value or suspicious assignment. It was rebased mechanically onto Central
Brain HEAD `1af8b80...`, producing `38a72cc...`. No authority/state conflict
occurred. A normal fast-forward push advanced `origin/profit-engine` from
`1af8b80...` to `38a72cc...`; no force push was used. Task 001 evidence is now
visible on origin.

## Secret hygiene

The new root `.gitignore` was verified to ignore:

- `.env`, `.env.local`, and other local environment variants;
- Profit Engine private/runtime/config/evidence state;
- credential/token-named files;
- PEM/key/certificate files;
- Python virtual environments, caches, and bytecode;
- Node dependencies and caches;
- macOS junk;
- Terraform state and local logs/caches.

Tracked-file and staged-diff scans found no secret-bearing file or credential
assignment. Public examples contain placeholders only. No real provider account,
campaign, counter, resource, placement, client-login, token, or secret was added.

## Runtime architecture

The Python 3.12+ runtime under `profit-engine/runtime/` uses no third-party
dependencies and provides:

- provider-neutral `ProviderReadClient` interface;
- `YandexDirectReadClient`;
- `YandexMetricaReadClient`;
- `YanPartnerStatsReadClient`;
- explicit `READ_ONLY = True` capability;
- common immutable request, response, diagnostic, and status models;
- injectable HTTP transport for fixture tests;
- production `urllib` transport with per-request timeout and at most three
  bounded attempts for transient 429/5xx/network failures;
- structured request/response logging that redacts authorization, token,
  private mapping keys, and secret values;
- request ID, HTTP status, attempt count, and Direct unit header capture without
  response body logging;
- one doctor CLI with statuses `PASS`, `BLOCKED_MISSING_CREDENTIAL`,
  `BLOCKED_ACCESS`, `PROVIDER_ERROR`, and `NOT_ATTEMPTED`;
- no provider add/update/delete/suspend/resume method.

Direct read calls use HTTP POST only because Yandex Direct JSON API v5 encodes
the read RPC as body method `get`; no write RPC exists in this runtime.

## Public/private configuration boundary

Public files:

- `profit-engine/config/site-registry.schema.json`
- `profit-engine/config/sites/dilivox.example.json`
- `profit-engine/runtime/README.md`

Private default path (outside Git):

`~/.config/profit-engine/sites/dilivox.json`

The runtime rejects a present registry if its permissions grant group/other
access; expected mode is `0600`. The registry holds only private mapping
references and endpoint selection, never tokens. Rollout mode must be
`READ_ONLY`.

Approved token source references:

- `env:PROFIT_ENGINE_YANDEX_OAUTH_TOKEN` for the shared Direct/Metrica OAuth
  read token with `direct:api` and `metrika:read` scopes;
- `env:PROFIT_ENGINE_YAN_STATS_TOKEN` for the distinct YAN Statistics API token;
- alternatively `keychain:<service>/<account>` for macOS Keychain retrieval.

Keychain output and environment values are consumed in memory and never logged.

## Provider diagnostics

### Direct

- Status: `BLOCKED_MISSING_CREDENTIAL`
- Live request: not attempted because the shared Yandex OAuth read token is not
  securely available.
- Implemented live sequence: `clients.get` minimal identity metadata, then
  `campaigns.get` with minimal fields and limit 1 against Direct API v5.
- Optional `Client-Login` is read only from private config.
- Authorization shape: `Bearer`, always redacted from logs.

### Metrica

- Status: `BLOCKED_MISSING_CREDENTIAL`
- Live request: not attempted because the shared Yandex OAuth read token is not
  securely available.
- Implemented live sequence: counters list, Dilivox selection via private
  mapping or canonical domain, permission capture, then a one-day minimal report
  probe using visits plus YAN partner revenue metric.
- Authorization shape: `OAuth`, always redacted from logs.

### YAN Partner Statistics

- Status: `BLOCKED_MISSING_CREDENTIAL`
- Live request: not attempted because the YAN Statistics-specific OAuth token is
  not securely available.
- Implemented live sequence: statistics tree discovery and a yesterday/limit-1
  basic report. A private resource filter is applied when configured.
- The Block Configuration API token is explicitly not accepted as a substitute.

No live provider endpoint was called without credentials. No provider write,
campaign operation, budget change, spend, Tilda publication, production-site
mutation, or Yandex Cloud resource creation occurred.

## Tests and checks

- `python3 -m unittest discover -s profit-engine/runtime/tests -v`: **11 passed**
- Direct request method/path/header/body shape: passed
- Metrica request shape and YAN monetization probe: passed
- YAN tree/report request shape: passed
- authorization/token redaction from logs and snapshots: passed
- missing credentials classification: passed
- HTTP 401/403 access classification: passed
- retry bound (three attempts): passed
- no provider write methods/RPC verbs: passed
- private registry outside repository and `0600` enforcement: passed
- public placeholder-only example: passed
- Python compile check: passed
- `.gitignore` fixture paths: all ignored
- `git diff --check`: passed
- tracked/staged secret-pattern scans: passed

## Exact Owner actions required

1. Shared Direct/Metrica token: authorize the existing Profit Engine OAuth app
   under the technical Yandex identity with both `direct:api` and
   `metrika:read`, then store the resulting token in macOS Keychain or inject it
   ephemerally as `PROFIT_ENGINE_YANDEX_OAUTH_TOKEN`. Do not send it in chat or
   commit it. If Direct production API approval is still pending, complete that
   provider approval first.
2. YAN token: in the YAN interface for an identity that can read Dilivox, choose
   API → receive an OAuth token specifically for the Statistics API, then store
   it in Keychain or inject it ephemerally as
   `PROFIT_ENGINE_YAN_STATS_TOKEN`. Do not use the separate block-configuration
   token.
3. Copy the public Dilivox registry example to
   `~/.config/profit-engine/sites/dilivox.json`, add actual provider mappings
   locally, and set mode `0600`. Tokens do not belong in that file.
4. Rerun the doctor. A 401/403 will be reported as `BLOCKED_ACCESS`; other
   provider/transport failures as `PROVIDER_ERROR`.

## Files changed

- `profit-engine/config/site-registry.schema.json`
- `profit-engine/config/sites/dilivox.example.json`
- `profit-engine/runtime/README.md`
- `profit-engine/runtime/profit_engine_runtime/__init__.py`
- `profit-engine/runtime/profit_engine_runtime/models.py`
- `profit-engine/runtime/profit_engine_runtime/redaction.py`
- `profit-engine/runtime/profit_engine_runtime/transport.py`
- `profit-engine/runtime/profit_engine_runtime/config.py`
- `profit-engine/runtime/profit_engine_runtime/clients.py`
- `profit-engine/runtime/profit_engine_runtime/doctor.py`
- `profit-engine/runtime/tests/test_runtime.py`
- `profit-engine/evidence/TASK-002-READ-FOUNDATION.md`

## Recommended Task 003 boundary

Proceed with the Day 3 minimal private/cloud data foundation while provider
credentials are supplied in parallel: decide the private-core boundary, define
immutable raw snapshot envelopes, add PostgreSQL/data schema foundations,
secret-manager/Lockbox adapter contracts, runtime health/logging, and deployment
structure. Keep all provider operations read-only and rerun certification as
soon as tokens are securely available. Do not enable Direct writes.

Central Brain remains the acceptance authority.
