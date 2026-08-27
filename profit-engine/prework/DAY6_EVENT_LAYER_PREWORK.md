# PROFIT ENGINE — DAY 6 EVENT LAYER PREWORK

Status: CENTRAL BRAIN PREWORK / NOT YET CANONICAL
Prepared: 2026-08-27
Branch: `central-brain/day6-event-prework`
Target integration: after Task 005 acceptance

## Purpose

Prepare the exact Day 6 first-party event semantics and safety gates without modifying `origin/profit-engine` while Codex executes Task 005.

This prework is based on current Dilivox T123 structure already visible in repository sources. It must be reconciled against Task 005 final SiteAgent/content registry before becoming canonical.

## Existing source contract confirmed

Text stories and comics share a compatible machine-readable structure:

- page root: `[data-dv-page="story"]`;
- current source identity hook: `data-dv-story-slug`;
- story body: `[data-dv-story-text]`;
- answer choices: `[data-dv-choice]`;
- answer correctness metadata: `data-dv-correct`;
- reveal block: `[data-dv-reveal]`;
- navigation hooks: `data-dv-goal`, including `next-story`, `prev-story`, `back-to-stories` where present;
- monetization containers: `[data-dv-ad-block]`;
- existing YAN rendering must remain untouched.

Therefore Day 6 should use one generic browser event layer through `SiteAgent`, not separate text/comic event implementations.

## Event schema v1

Every emitted event must be constructed from the SiteAgent context and use a strict allowlist.

Common fields:

- `schema_version`;
- `event_id` — random opaque ID;
- `idempotency_key` — deterministic logical event identity;
- `event_type`;
- `occurred_at` UTC timestamp;
- `site_id`;
- `content_id`;
- `page_type` / `content_type`;
- `session_id` or pseudonymous session reference;
- `acquisition_id` / cohort reference where active;
- `experiment_id` / `variant_id` where actually exposed;
- `placement_id` only when relevant;
- `source_content_id` / `destination_content_id` for navigation events;
- deployment/event-layer version.

Never include full arbitrary query strings, free text, email, phone, name, fingerprint material, raw ad-provider credentials/IDs outside the approved public placement identity contract, or unnecessary personal data.

## Exact event semantics

### `page_view_site`

Emit once per document/page-load identity after SiteAgent resolves a valid page/content context.

Do not duplicate on internal DOM mutations.

### `story_open`

Emit once when:

- page root resolves as `story`;
- stable `content_id` is known;
- story content root exists.

Do not treat simple tab visibility restoration as a new open.

### `story_progress_25`, `story_progress_50`, `story_progress_75`

Progress is measured against the actual story-content experience, not generic page-scroll percentage.

For text stories: use `[data-dv-story-text]` content geometry.

For comics: use the story/comic reader container / ordered comic frames resolved by SiteAgent.

Preferred implementation: generated internal progress sentinels or equivalent geometry calculation with `IntersectionObserver`; each threshold emits at most once per content/session.

Ads/header/footer must not distort progress thresholds.

### `version_section_seen`

Emit once when the choice block becomes genuinely viewable, recommended threshold >=50% intersection where practical.

Merely existing in DOM is not an exposure.

### `version_selected`

Emit on the first trusted user activation of `[data-dv-choice]` for the story attempt.

Allowed properties:

- opaque/numeric choice index;
- `is_correct` boolean if already encoded in authoritative DOM state;
- attempt ordinal only if multiple attempts are ever product-authorized.

Do not send answer text.

### `reveal_opened`

Emit once when `[data-dv-reveal]` actually transitions from hidden/non-visible to revealed state following the user flow.

Use DOM state observation / SiteAgent hook. Do not infer it merely from clicking a choice if reveal did not become available.

### `story_completed`

Do NOT equate completion with a choice click.

Completion requires:

1. reveal is open; and
2. the reveal/final section becomes genuinely viewed (recommended >=50% intersection of a completion sentinel/reveal heading/block).

This distinguishes “clicked answer then left” from completed content consumption.

### `next_story_seen`

Emit once when an eligible next-story recommendation/control becomes genuinely viewable.

For current markup, `.dv-next-story` / `data-dv-goal="next-story"` is a direct hook where present.

If Task 005 later introduces a generic recommendation hook, use the SiteAgent abstraction rather than hard-coding class names.

### `next_story_clicked`

Emit on trusted navigation activation to the next recommended story.

Include `source_content_id` and resolved `destination_content_id`.

### `catalog_opened`

Emit on trusted navigation to catalog from approved existing hooks such as `back-to-stories`, `home-to-stories`, or equivalent SiteAgent-resolved action.

### `return_visit`

Do not calculate “return” from fingerprinting.

Use the optional first-party anonymous return ID/session state from Task 005 only.

A return visit means a new session after a previous completed/expired session identity. Server-side/reporting logic later buckets return value into 1d/7d/30d windows.

Default session boundary: 30 minutes inactivity unless canonical policy later supersedes it.

### `session_end_summary`

Best-effort diagnostic event, not a hard financial source of truth.

Trigger on `pagehide` and/or `visibilitychange -> hidden` only when a meaningful session summary exists. Use bounded payload and best-effort delivery (`sendBeacon` or `fetch(..., keepalive:true)` where supported).

Never block navigation.

### `experiment_exposure`

Emit only when the assigned variant is actually rendered/experienced and eligibility passed.

Assignment alone is not exposure.

At most once per `session × content × experiment × variant` unless experiment contract explicitly defines otherwise.

### `experiment_conversion`

Emit only from an approved proxy-conversion rule. No arbitrary UI action becomes a conversion merely because it is easy to measure.

The underlying source event must remain available for audit.

## Idempotency and deduplication

Every event gets:

- random `event_id` for transport identity;
- deterministic `idempotency_key` for logical dedupe.

Logical singleton keys should include at least:

`schema_version + site_id + session_id + content_id + event_type + instance_key`.

Examples of `instance_key`:

- page-load ID for `page_view_site`;
- progress threshold for progress events;
- choice ID for selection;
- destination content ID for next-story click;
- experiment/variant pair for exposure.

The future event ingestion service must reject duplicate idempotency keys without double-counting.

## Browser delivery policy for Day 6

Delivery must never break the site.

Required properties:

- first-party endpoint only;
- small bounded queue;
- batch where useful;
- short timeout;
- bounded retries with jitter;
- offline/network failures stored only in bounded local queue if privacy policy permits;
- queue TTL; stale events are dropped rather than retried forever;
- `sendBeacon` / keepalive path for unload summaries;
- no synchronous XHR;
- no third-party JS dependency;
- global event-dispatch kill switch;
- SiteAgent/event failure is fail-open for normal Dilivox content and YAN rendering.

Suggested initial caps to validate in Task 006 rather than silently hard-code as business policy:

- max queued events: 50;
- max event payload: 8 KiB;
- max batch payload: 64 KiB;
- queue TTL: 24h;
- maximum normal retry attempts per batch: 3.

## Data-quality signals

The event layer must expose delivery/quality health separately from user events.

Minimum conditions that can contribute to `DATA_QUALITY_HOLD` for downstream money decisions:

- SiteAgent cannot resolve content ID for a meaningful share of story traffic;
- duplicate rate above accepted threshold;
- event queue persistent overflow;
- large sequence gaps;
- event endpoint unavailable beyond freshness window;
- progress/reveal events impossible to reconcile with page/story opens;
- attribution context unexpectedly disappears inside paid sessions;
- experiment exposures cannot join to events;
- event schema version mismatch.

A browser telemetry defect must not disable core site content; instead it blocks autonomous optimizer consumption when measurement reliability is insufficient.

## Monetization placement joins

Day 6 must not modify YAN provider rendering code.

The event context may carry registry `placement_id` only where the event is specifically associated with a placement/placement experiment.

Do not claim a provider impression/revenue event from DOM presence. Provider-side YAN/Metrica statistics remain the monetization money source of truth.

If site-side placement visibility diagnostics are later added, name them explicitly as container/viewability diagnostics, not provider impressions.

## Current source-derived acceptance observations

1. Text story 48 already exposes many placement wrappers across the reading path (`story-start`, multiple inline placements, before-choice, after-reveal, sidebar), so placement registry coverage can be audited against real markup.
2. Current navigation includes an explicit next-story hook on text stories.
3. Choice and reveal markup is structurally shared between text story and comic source.
4. Existing YAN code has its own eager/lazy/desktop/reveal rendering logic. Event instrumentation must observe around it, never replace it.

## Day 6 acceptance gates — draft

Task 006 should not be accepted unless tests prove:

1. one event layer handles both representative text and comic fixtures;
2. all required taxonomy events have deterministic semantics;
3. progress thresholds are content-relative, not page-relative;
4. singleton events dedupe correctly;
5. choice text/PII/arbitrary URL params never enter payloads;
6. reveal and completion are distinct events;
7. next-story click resolves destination stable ID;
8. acquisition context survives event construction;
9. event dispatch failures never break content, choice/reveal, navigation, or YAN code;
10. global event kill switch works;
11. experiment exposure means actual exposure;
12. unload/session-summary path is best effort and non-blocking;
13. no event is misrepresented as provider revenue/impression;
14. event schema validation fails closed for telemetry but site fails open;
15. event endpoint fixture demonstrates server-side idempotency;
16. data-quality health can place downstream data into `DATA_QUALITY_HOLD`;
17. mobile/desktop representative tests pass;
18. no production publication occurs until a separate deployment gate.

## Reconciliation required after Task 005

Before converting this prework to a canonical Task 006 contract, Central Brain must compare it against:

- actual Task 005 content registry IDs;
- final `DilivoxSiteAgent` API;
- attribution persistence implementation;
- placement registry structure;
- Tilda integration artifact;
- Task 005 browser tests/evidence.

Any conflicts are resolved in favor of the accepted Task 005 implementation plus canonical owner decisions.
