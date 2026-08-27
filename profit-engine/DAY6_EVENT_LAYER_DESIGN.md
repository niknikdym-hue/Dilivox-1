# PROFIT ENGINE — DAY 6 FIRST-PARTY EVENT LAYER DESIGN

Status: CANONICAL / CENTRAL BRAIN ACCEPTED DESIGN
Updated: 2026-08-27
Depends on accepted Task 005 HEAD: `ec3590f9a4daee08fcbdac957269fd77d78c9a15`

## Mission

Turn the accepted `DilivoxSiteAgent` identity/attribution context into reliable first-party behavioral evidence without breaking Dilivox, modifying YAN rendering, collecting unnecessary personal data, or treating telemetry as money truth.

Closed data path:

`Dilivox DOM -> SiteAgent context -> event semantics -> bounded browser queue -> first-party event batch -> immutable raw event batch -> dedupe/validation -> site_events -> data-quality state`.

The event layer is a measurement instrument. Reconciled Direct/YAN money remains the economic source of truth.

## Existing accepted source contract

Task 005 established stable content IDs, attribution persistence, placement registry, experiment identity hooks and a generic SiteAgent.

Current text stories and comics expose a compatible DOM contract:

- `[data-dv-page="story"]`;
- `data-dv-story-slug`;
- `[data-dv-story-text]`;
- `[data-dv-choice]`;
- `data-dv-correct`;
- `[data-dv-reveal]`;
- `data-dv-goal` navigation hooks;
- `[data-dv-ad-block]`.

One generic event layer must handle text and comic stories through SiteAgent. Do not fork separate business logic by story format.

## Event envelope v1

Strict common fields:

- `schema_version`;
- `event_id` — random opaque transport identity;
- `idempotency_key` — deterministic logical event identity;
- `event_type`;
- `occurred_at` UTC;
- `site_id`;
- `content_id` where resolved;
- `page_type` / `content_type`;
- pseudonymous `session_id`/reference;
- `acquisition_id` / cohort reference where active;
- `experiment_id` / `variant_id` only when applicable;
- `placement_id` only when specifically relevant;
- `source_content_id` / `destination_content_id` for navigation;
- deployment/event-layer version;
- approved event properties only.

Forbidden in event payloads:

- arbitrary/full query strings;
- free text/answer text;
- name/email/phone/form values;
- fingerprints;
- raw Metrica ClientID;
- raw secrets/private provider mappings;
- raw JS error stacks/URLs that may carry sensitive query data.

## Canonical behavior event semantics

### `page_view_site`

Emit once per document/page-load identity after SiteAgent resolves context. DOM mutations and tab visibility changes do not create additional page views.

### `story_open`

Emit once when page resolves to a story/comic content ID and `[data-dv-story-text]` exists.

### `story_progress_25`, `story_progress_50`, `story_progress_75`

Measure progress against the actual `[data-dv-story-text]` content geometry, not total document scroll. Header/footer/ads must not distort thresholds.

Use generated internal sentinels or equivalent `IntersectionObserver`/geometry logic. Each threshold emits once per `session × content`.

### `version_section_seen`

Emit once when the choice section becomes genuinely visible. DOM existence alone is not exposure. Recommended visibility threshold: >=50% where practical.

### `version_selected`

Emit on the first trusted user activation of `[data-dv-choice]` in the story attempt.

Allowed properties:
- choice index/reference;
- `is_correct` boolean if authoritative DOM already contains it.

Never send answer text.

### `reveal_opened`

Emit once when `[data-dv-reveal]` actually transitions from hidden/non-visible to revealed state. Do not infer reveal merely because a choice was clicked.

### `story_completed`

Completion is NOT synonymous with choice click or reveal state change.

Emit only when:
1. reveal is open; and
2. user genuinely views the reveal/final section (recommended completion sentinel or >=50% visibility of the relevant reveal block).

This prevents users who choose and immediately leave from being mislabeled as completed readers.

### `next_story_seen`

Emit once when an eligible next-story control/recommendation is genuinely visible. Current text stories may expose `data-dv-goal="next-story"`; SiteAgent abstraction remains authoritative.

### `next_story_clicked`

Emit on trusted user activation of next-story navigation. Must resolve both stable source and destination content IDs.

### `catalog_opened`

Emit on approved catalog navigation hooks such as `back-to-stories` / `home-to-stories` and equivalent SiteAgent-resolved actions.

### `return_visit`

No fingerprinting.

Only available when Task 005 first-party anonymous return identity is enabled AND privacy review is approved. A return means a new session after a prior session. Reporting later buckets it into 1d/7d/30d windows.

Initial session inactivity boundary for testing: 30 minutes. This is an operational default, not a permanent business invariant.

### `session_end_summary`

Best-effort diagnostic event only. May include bounded counters/duration summaries, not text content. Trigger via `pagehide` and/or `visibilitychange -> hidden`; never block navigation.

### `experiment_exposure`

Emit only when an eligible assigned variant is actually rendered/experienced. Assignment alone is not exposure. Deduplicate by `session × content × experiment × variant`.

### `experiment_conversion`

Only emitted from an explicitly approved proxy-conversion rule. It must reference the underlying source event/evidence. No arbitrary click becomes a conversion.

## Idempotency

Every event has:

- random `event_id`;
- deterministic `idempotency_key`.

Minimum logical key:

`schema_version + site_id + session_id + content_id + event_type + instance_key`.

Examples:
- page-load identity;
- progress threshold;
- choice index;
- destination content ID;
- experiment/variant pair.

Server/event ingestion must ignore duplicate logical events without double-counting.

## Browser queue and delivery safety

Event instrumentation must fail open for the product and fail closed for telemetry.

Required:

- first-party endpoint only;
- no third-party dependency;
- bounded queue and payload sizes;
- asynchronous/non-blocking delivery;
- bounded retry with jitter;
- queue TTL; never retry forever;
- `sendBeacon` or `fetch(..., keepalive:true)` only for best-effort unload flush where supported;
- no synchronous XHR;
- global event-dispatch kill switch;
- storage/network exceptions must not break content, answer choice, reveal, navigation or YAN rendering.

Initial implementation caps for testing:

- max queued events: 50;
- max event payload: 8 KiB;
- max batch payload: 64 KiB;
- queue TTL: 24h;
- max normal retry attempts per batch: 3.

These are engineering defaults and may be tuned later based on measured reliability.

## Raw-first event ingestion

First-party events must use the same truth-preserving discipline as provider ingestion.

For an event batch:

1. validate outer schema and size;
2. accept immutable raw batch outside Git;
3. read/hash-verify immutable batch;
4. validate each event schema/allowlist;
5. dedupe by `idempotency_key`;
6. normalize accepted events into `site_events` with provenance;
7. record quality/ingestion state.

A malformed/conflicting batch never partially mutates accepted event facts unless the contract explicitly implements atomic per-event acceptance with auditable rejects. Initial launch preference: atomic batch accept/reject for simpler evidence.

## Site health/performance signals

Day 6 must also measure whether instrumentation/site execution is healthy, without collecting raw error text that could leak data.

Public-safe health snapshot may include:

- event queue depth/overflow count;
- delivery success/failure counts;
- unresolved content-ID count;
- duplicate/rejected event count;
- JS error count + coarse error type / hashed redacted signature only;
- DOMContentLoaded/load/navigation timing;
- LCP/CLS/long-task or equivalent metrics where supported without third-party dependencies;
- SiteAgent health state;
- experiment/event kill-switch state.

Health telemetry is separate from monetization provider impressions/revenue.

## Monetization placement rule

Do not change YAN provider rendering.

A DOM placement container is not a provider impression. Never report placement DOM presence as YAN impression/revenue.

`placement_id` may be attached only to site-side diagnostic/experiment context where relevant; provider-side YAN/Metrica data remains the money/delivery source of truth.

## DATA_QUALITY_HOLD conditions

Downstream autonomous optimization must be blocked when event measurement is materially unreliable, including:

- unresolved stable content IDs above accepted tolerance;
- unexpected loss of paid attribution within session;
- persistent event endpoint failure beyond freshness window;
- queue overflow/drop rate above accepted tolerance;
- impossible sequence relationships (e.g. large completed > opened anomaly);
- duplicate/rejection rate above accepted tolerance;
- experiment exposures cannot join to behavior;
- event schema incompatibility;
- site instrumentation materially breaks mobile/desktop behavior.

A telemetry failure must not make Dilivox unusable. It blocks optimizer consumption instead.

## Day 6 launch/deployment rule

Task 006 may produce a complete event layer, local event-ingestion implementation, browser artifact and deployment/rollback procedure.

Production Tilda publication remains forbidden unless the Task 006 contract explicitly reaches a separate Central Brain deployment acceptance step. No uncontrolled live dispatch is allowed.

## Acceptance gates

Task 006 is accepted only if evidence proves:

1. same event layer handles representative text and comic fixtures;
2. required behavior taxonomy has deterministic semantics;
3. content-relative progress thresholds;
4. singleton/idempotency behavior;
5. reveal and completion are distinct;
6. answer text/PII/arbitrary query data excluded;
7. next-story destination resolves stable ID;
8. paid acquisition context survives event construction;
9. experiment exposure means actual exposure;
10. browser failures/kill switch do not break Dilivox or YAN code;
11. event batch raw-first + dedupe works;
12. queue retry/TTL/caps tested;
13. unload summary is best effort/non-blocking;
14. health/performance path is privacy-minimal;
15. data quality can block optimizer consumption;
16. mobile/desktop representative tests pass;
17. no provider impression/revenue is invented from DOM events;
18. no production Tilda publication, Direct write, spend or secret exposure occurs without separate authorization.
