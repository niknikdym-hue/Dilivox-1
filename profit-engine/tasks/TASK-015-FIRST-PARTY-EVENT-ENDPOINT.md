# TASK 015 — DILIVOX FIRST-PARTY EVENT ENDPOINT

Status: P0 / REQUIRED FOR COMPLETE SITE LOOP
Current executor: Central Brain
Depends on: Task 013 production instrumentation

## Objective

Turn the accepted browser event layer from an in-memory instrumentation surface into a durable, bounded, privacy-safe production event stream for Profit Engine.

This task is required for the complete first-site ecosystem but must not block safe Metrica goal instrumentation or the Day-12 money/Direct smoke.

## Existing accepted contract

Browser event schema:
`profit-engine/sites/dilivox/event-schema.json`

Server validation/normalization:
`profit-engine/runtime/profit_engine_runtime/site_events.py`

Existing properties:

- strict event type allowlist;
- strict top-level/property allowlist;
- max 8 KB event / 64 KB batch on client;
- max 64 KB batch server-side;
- idempotency keys;
- raw-first validation design;
- attribution/content/session linkage;
- no ad-click instrumentation;
- no fingerprints or arbitrary user payloads.

## Production endpoint contract

Required route:

`POST /v1/sites/dilivox/events`

Required behavior:

- HTTPS only;
- JSON only;
- body <= 64 KB;
- exact schema version allowlist;
- site_id must equal `dilivox`;
- rate limited;
- no browser credential/secrets;
- no query-string payload;
- CORS allow only canonical Dilivox origins;
- validate complete batch before optimizer consumption;
- raw immutable append before normalized materialization;
- idempotent duplicate acceptance;
- reject/hold malformed or unknown properties;
- server timestamp + request ID;
- no provider write side effects;
- no synchronous Direct/YAN/Metrica calls in request path.

## Persistence

Production cannot use `InMemorySiteEventStore` as authority.

Required durable layers:

1. immutable raw batch store with payload SHA-256;
2. normalized event table keyed by idempotency key/event ID;
3. ingestion audit table;
4. bounded retention policy for raw operational records;
5. derived cohort/behavior aggregates separated from raw events.

Provider-neutral storage interface is required; first deployment may use a Yandex Cloud stack if it remains replaceable.

## Client transport

Only after endpoint acceptance, the Tilda event layer may receive a transport that:

- POSTs bounded batches;
- treats only explicit 2xx acknowledgment as success;
- has bounded retry/backoff already defined by Task-006;
- never includes OAuth/provider secrets;
- fails open for the reader experience;
- can be killed independently of Metrica goals and ads.

## Privacy / compliance

Current public `/privacy/` already discloses Yandex Metrica, cookies, source of visit and actions on pages. That is sufficient for the Task-013 Metrica `reachGoal` layer currently being prepared.

Before Task-015 network dispatch is enabled, publish the prepared first-party analytics delta:

`profit-engine/sites/dilivox/privacy-policy-profit-engine-v2.md`

It must be merged into the public privacy page, publication date updated, Tilda page republished, and live text verified. **No first-party network dispatch is authorized before this privacy publication gate passes.**

Do not collect:

- email/phone/name;
- free-form text typed by users;
- fingerprinting data;
- ad-click identities;
- Yandex cookies copied into Profit Engine payloads;
- secrets/tokens.

Identifiers remain first-party pseudonymous/session/acquisition references as already accepted.

## Acceptance

Task 015 is accepted only after:

1. Privacy v2 first-party analytics disclosure is live and verified;
2. durable endpoint deployed;
3. CORS/rate/size/schema negative tests pass;
4. live one-batch browser smoke accepted;
5. exact raw SHA + normalized event materialization verified;
6. duplicate replay is idempotent;
7. malformed replay is held/rejected;
8. site reader flow remains unaffected on endpoint failure;
9. kill switch tested;
10. no Direct/YAN/provider mutation occurs from ingestion;
11. production evidence is recorded.

Terminal state:
`DILIVOX_FIRST_PARTY_EVENT_ENDPOINT_ACCEPTED`.
