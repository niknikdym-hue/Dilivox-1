# TASK 006 — FIRST-PARTY EVENTS + SITE SAFETY — EVIDENCE

## Identity and scope

- Accepted Task 005: `ec3590f9a4daee08fcbdac957269fd77d78c9a15`.
- Central Brain baseline/current origin: `2bfb83f7fa20ca03f2ded4fb898122fddfdcc3e8`.
- Safe fetch + fast-forward used; final evidence commit SHA is reported in the
  final response.
- Separate Dilivox workspace remained read-only. No Tilda/production/provider
  mutation, Direct write, budget/spend, Cloud apply, or YAN code change.

## Event taxonomy and schema

Schema: `event-envelope.schema.json`, version `1.0`, strict additional-property
rejection. Exact implemented types:

`page_view_site`, `story_open`, `story_progress_25`, `story_progress_50`,
`story_progress_75`, `version_section_seen`, `version_selected`,
`reveal_opened`, `story_completed`, `next_story_seen`, `next_story_clicked`,
`catalog_opened`, `return_visit`, `session_end_summary`,
`experiment_exposure`, `experiment_conversion`.

Property allowlists exist only for choice ref/correctness, bounded session
summary, and approved experiment conversion evidence. Answer/free text, query
strings, PII, fingerprints, Metrica ID, raw URL/stack, secrets and unknown
properties are rejected.

## Browser semantics

Successor artifact: `sites/dilivox/tilda/dilivox-event-layer-task006.js`.

- Same controller covers text and comic content.
- Page/story events are singleton.
- 25/50/75 derive only from `[data-dv-story-text]` geometry.
- Choice-section exposure requires >=50% visibility.
- Selection requires trusted activation and never captures answer text.
- Reveal transition and completion are distinct; completion requires reveal open
  plus >=50% genuine reveal/final visibility.
- Next-story events resolve stable source/destination IDs; approved catalog hooks
  emit catalog navigation.
- Return event requires the Task-005 privacy-gated return reference.
- Experiment exposure requires actual rendered signal; conversion requires an
  explicitly approved mapping and source event.
- Passive scroll/click, IntersectionObserver and best-effort pagehide hooks never
  block navigation.

## Queue, identity and transport

- Random opaque `event_id`; deterministic logical `idempotency_key` from schema,
  site, session, content, type and instance key.
- Client singleton suppression; server/ingestor dedupe authoritative.
- Queue maximum 50; event maximum 8 KiB; batch maximum 64 KiB; TTL 24h;
  normal retry maximum 3.
- Async injectable transport only. No endpoint and no default transport.
- Dispatch kill switch prevents event construction/queueing.
- Overflow/drop, depth, retry failures, created/sent/acked/rejected/duplicate
  counts are health signals.
- No synchronous XHR or third-party dependency.

## Raw-first ingestion

`runtime/profit_engine_runtime/site_events.py` implements atomic local fixture
ingestion:

`outer validation -> immutable raw batch put -> raw get/SHA verification -> strict event validation -> dedupe -> site_events`.

Operation-log test proves `raw:verified` precedes `events:normalized`. Malformed
batches write no normalized events; conflicting batch identity becomes
`raw_batch_conflict`; retry/replay produces one fact plus duplicate count.
Fixture normalized count: 1 accepted `site_event`; replay count: 1 duplicate;
atomic malformed fixture normalized count: 0.

## Health, performance and data quality

Privacy-minimal health supports unresolved identity; created/sent/acked/rejected/
dropped/duplicate counts; queue depth/overflow; delivery/instrumentation errors;
SiteAgent/kill state; coarse error type + hashed signature; navigation, LCP, CLS
and long-task values. No raw stack, URL or text.

`DATA_QUALITY_HOLD` fixture coverage: unresolved content, stale endpoint, queue
overflow, impossible sequence, duplicate anomaly, lost paid acquisition,
experiment join failure, schema incompatibility and instrumentation failure.
Every hold has `optimizer_consumable=false`. DOM placement never becomes a YAN
impression/revenue fact.

## Coverage and checks

- Node browser suites: 22/22 PASS (Task 005 + Task 006).
- Python suites: 44/44 PASS (all previous 38 + 6 event-ingestion tests).
- Text/comic and mobile/desktop representative semantics: PASS.
- Queue caps/TTL/retry/overflow/fail-open: PASS.
- Raw-first/dedupe/conflict/atomic reject: PASS.
- Privacy, schema allowlist, reveal/completion, navigation, experiment gates: PASS.
- Artifact contains no real HTTP endpoint, synchronous XHR, `Ya.Context`, or YAN
  render mutation: PASS.
- `git diff --check`, secret/private-data scan and optimizer-code scan: PASS.
- Live dispatch: `DISABLED_NOT_CONFIGURED`; real requests: 0.

## Files changed

- `profit-engine/sites/dilivox/event-envelope.schema.json`
- `profit-engine/sites/dilivox/tilda/dilivox-event-layer-task006.js`
- `profit-engine/sites/dilivox/tilda/INSTALLATION.md`
- `profit-engine/sites/dilivox/tests/event-layer.test.cjs`
- `profit-engine/runtime/profit_engine_runtime/site_events.py`
- `profit-engine/runtime/tests/test_site_events.py`
- `profit-engine/evidence/TASK-006-FIRST-PARTY-EVENTS.md`

Unrelated untracked Task-001 evidence was preserved and excluded.

## Blockers and Task 007

Engineering foundation is complete. Production endpoint, privacy/deployment
review and controlled Tilda publication remain deliberately unapproved. External
provider OAuth certification remains a parallel blocker.

Recommended Task 007: reconciliation-ready event/provider joining, attribution
ledger and K5 measurement foundation using immutable facts; define freshness,
late-arrival and estimated/final/reconciled rules before any optimizer or write
controller consumes the data.
