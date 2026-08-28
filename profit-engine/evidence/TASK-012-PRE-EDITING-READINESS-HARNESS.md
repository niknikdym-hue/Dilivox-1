# TASK 012 — Pre-Editing Day-12 readiness harness

Status: CENTRAL BRAIN IMPLEMENTED / PRE-EDITING SAFE
Updated: 2026-08-28

## Purpose

Remove avoidable engineering delay from the Day-12 critical path before the Owner-only Direct permission transition.

The existing provider doctor remains read-only and is reused rather than duplicated. It checks:

- Yandex Direct via read-only `clients.get` and `campaigns.get`;
- Yandex Metrica counter visibility plus a YAN-monetization report probe;
- YAN Partner Statistics tree/report access.

Secrets remain outside Git and are resolved only through `env:` or macOS `keychain:` references.

## Added Day-12 readiness gate

`profit-engine/runtime/profit_engine_runtime/day12_readiness.py`

The gate produces only these states:

- `BLOCKED_CONTROLLER_ACCEPTANCE`;
- `BLOCKED_OWNER_PERMISSION`;
- `BLOCKED_PROVIDER_CERTIFICATION`;
- `READY_FOR_LIVE_CANDIDATE_SELECTION`.

It requires, in order:

1. exact accepted Task-011R controller SHA `a494d30b49c8d11687be56cdab870a5d83356e02`;
2. Owner-confirmed Direct permission `EDITING`;
3. PASS from `direct`, `metrica`, and `yan_statistics` doctors.

Missing provider results are treated as `NOT_ATTEMPTED` and fail closed.

Even when every readiness gate passes:

- `provider_write_allowed=false`;
- `REAL_PROVIDER_REQUESTS=0`;
- `ADVERTISING_SPEND=0`;
- `PRODUCTION_WRITER_ENABLED=false`.

Therefore this gate can never authorize the first production mutation. It only permits live candidate selection to begin under the separate accepted Day-12 controller/write contract.

## CLI

`profit-engine/runtime/profit_engine_runtime/day12_readiness_cli.py`

The CLI:

- runs the existing read-only provider doctor;
- accepts an Owner-confirmed permission state as data only and never changes Yandex permissions;
- binds the accepted controller SHA;
- prints a redacted public readiness result.

Example after Owner confirms Editing:

```bash
PYTHONPATH=profit-engine/runtime python3 -m profit_engine_runtime.day12_readiness_cli --direct-permission EDITING
```

Before Editing the same command may be run with `READING` or the default `UNKNOWN`; the readiness result must remain blocked and no write path exists.

## Tests

`profit-engine/runtime/tests/test_day12_readiness.py` covers:

- Reading blocks even when every doctor passes;
- unknown permission fails closed;
- wrong controller SHA blocks;
- missing provider result becomes `NOT_ATTEMPTED` and blocks;
- any Direct/Metrica/YAN doctor failure blocks;
- all gates may advance only to candidate selection, never write permission;
- readiness digest tampering is detected.

## Safety

This change performs no provider/site mutation, creates no advertising spend, requests no write credential, stores no secret/provider-private ID, and does not alter the accepted Day-11 controller or private ProfitAllocator.
