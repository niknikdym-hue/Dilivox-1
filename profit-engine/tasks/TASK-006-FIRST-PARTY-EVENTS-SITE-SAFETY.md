# CODEX TASK 006 — FIRST-PARTY EVENTS + SITE SAFETY

Status: READY FOR EXECUTION
Owner: Central Brain
Executor: Codex
Repository: `niknikdym-hue/Dilivox-1`
Canonical branch: `profit-engine`
Launch day: Day 6
Accepted Task 005 implementation HEAD: `ec3590f9a4daee08fcbdac957269fd77d78c9a15`

## ROLE

You are the engineering executor. Central Brain owns product/economic authority and acceptance.

## WORKSPACE

Canonical Profit Engine workspace:

`~/Documents/New project/Profit Engine/Dilivox-1`

Separate Dilivox site workspace:

`~/Documents/New project/Dilivox`

The site workspace may be inspected READ_ONLY for source truth/local unpublished validation. No Tilda publication or production mutation is authorized.

## SYNC FIRST

Before work:

1. `git fetch origin`;
2. fast-forward safely to current `origin/profit-engine`;
3. verify accepted Task 005 commit is an ancestor;
4. read the current Central Brain additions after Task 005;
5. no force push and no discarding unrelated local files.

## READ FIRST — MANDATORY

Read at minimum:

1. `profit-engine/PROJECT_HANDOFF.md`
2. `profit-engine/OWNER_DECISIONS.md`
3. `profit-engine/PROJECT_STATE.md`
4. `profit-engine/HARD_12_DAY_LAUNCH_PLAN.md`
5. `profit-engine/DILIVOX_SITE_INTEGRATION.md`
6. `profit-engine/DAY6_EVENT_LAYER_DESIGN.md`
7. `profit-engine/sites/dilivox/SITE_AGENT_CONTRACT.md`
8. `profit-engine/sites/dilivox/event-context.schema.json`
9. `profit-engine/sites/dilivox/content-registry.json`
10. `profit-engine/sites/dilivox/placement-registry.json`
11. `profit-engine/sites/dilivox/tilda/dilivox-site-agent-task005.js`
12. Task 005 evidence.

## OBJECTIVE

Implement a reliable, privacy-minimal, fail-safe first-party event layer and local/portable raw-first event ingestion foundation:

`Dilivox DOM -> SiteAgent -> canonical event -> bounded queue -> event batch -> immutable raw -> dedupe/validate -> site_events -> data-quality state`.

No production dispatch/publication in this task unless explicitly stated by Central Brain after acceptance.

## A. BEHAVIOR EVENT TAXONOMY

Implement exact canonical events from `DAY6_EVENT_LAYER_DESIGN.md`:

- `page_view_site`;
- `story_open`;
- `story_progress_25`;
- `story_progress_50`;
- `story_progress_75`;
- `version_section_seen`;
- `version_selected`;
- `reveal_opened`;
- `story_completed`;
- `next_story_seen`;
- `next_story_clicked`;
- `catalog_opened`;
- `return_visit` only behind Task 005 privacy gate;
- `session_end_summary` best-effort;
- `experiment_exposure`;
- `experiment_conversion` only through explicit approved mapping fixture/contract, not arbitrary auto-promotion of clicks.

## B. EVENT SEMANTICS — HARD RULES

### Page/story

- page view once per page-load identity;
- story open once only when stable content identity resolves and story body exists.

### Progress

- use actual `[data-dv-story-text]` geometry;
- ads/header/footer cannot alter progress;
- 25/50/75 each once per session/content;
- work for representative text + comic fixture/source.

### Choice/reveal/completion

- `version_section_seen` = genuine visibility, not DOM presence;
- `version_selected` = first trusted activation of `[data-dv-choice]`;
- allowed property: choice index/ref + `is_correct` boolean, NEVER answer text;
- `reveal_opened` = actual hidden->revealed state;
- `story_completed` only after reveal is open AND user actually views final/reveal completion region;
- choice click alone is never completion.

### Navigation

- next-story seen = genuinely visible eligible control;
- next-story clicked resolves source + destination stable IDs;
- catalog opened uses approved existing navigation hooks.

### Experiment

- exposure only when variant actually rendered/experienced;
- assignment alone is not exposure;
- kill switch suppresses exposure/conversion context.

## C. EVENT ENVELOPE + PRIVACY

Create a versioned event schema/validator consistent with Task 005 event context.

Required common fields are defined in canonical Day 6 design.

Hard exclusions:

- no arbitrary query params;
- no full query string;
- no free/answer text;
- no email/phone/name/forms;
- no fingerprinting;
- no Metrica ClientID as identity;
- no raw JS stacks/full URLs that can leak data;
- no tokens/provider credentials/private mappings.

The event builder should reject/discard non-allowlisted properties rather than forwarding unknown objects.

## D. IDEMPOTENCY

Implement:

- random opaque `event_id`;
- deterministic logical `idempotency_key`;
- documented `instance_key` strategy per singleton event;
- duplicate logical event suppression client-side where practical;
- server/ingestor dedupe as authoritative.

Retries must never double-count.

## E. BROWSER QUEUE / TRANSPORT ABSTRACTION

Implement a bounded first-party event queue with an injectable transport.

Test defaults:

- queue max: 50 events;
- event max: 8 KiB;
- batch max: 64 KiB;
- local queue TTL: 24 hours;
- normal retry max: 3 with bounded jitter/backoff.

Requirements:

- async/non-blocking;
- no synchronous XHR;
- no third-party dependency;
- navigation never blocked;
- `sendBeacon` or `fetch keepalive` only as best-effort unload flush where supported;
- global event-dispatch kill switch;
- network/storage failure cannot break content, choices, reveal, nav, existing YAN rendering;
- queue overflow/drop is counted as health signal;
- production endpoint URL must be placeholder/local config, not a real deployed endpoint committed here.

Task 006 must NOT send real production events to a new external endpoint.

## F. RAW-FIRST EVENT INGESTION

Implement provider-neutral/local event ingestion using existing raw/data contracts.

Preferred provider/source identity:

- provider/source family representing first-party site events without confusing them with YAN/Direct provider data;
- immutable raw batch outside Git;
- hash verification before normalized event writes.

Required path:

1. batch schema/size validation;
2. immutable raw batch put;
3. raw read/hash verification;
4. event schema/allowlist validation;
5. dedupe;
6. normalize into `site_events` compatible records;
7. quality outcome.

Initial acceptance preference: atomic batch acceptance/rejection for malformed/conflicting batches. If per-event partial acceptance is implemented instead, rejects must be explicit/auditable and tests must prove no silent partial corruption.

Add an in-memory/local fixture adapter; do not claim real PostgreSQL production certification unless actually connected.

## G. HEALTH / PERFORMANCE

Implement privacy-minimal public-safe health metrics for tests/fixtures:

- unresolved content identity count;
- event created/sent/acked/rejected/dropped counts;
- queue depth/overflow;
- duplicate count;
- delivery failures;
- SiteAgent health;
- coarse JS error count/type or hashed redacted signature only;
- navigation/load timing;
- LCP/CLS/long-task or equivalent where browser supports standard APIs;
- event/experiment kill-switch state.

Do not capture raw error stack, arbitrary URL query or page text.

## H. DATA QUALITY

Implement/extend quality assessment so downstream optimizer consumption becomes false when materially unreliable.

Fixture-test at least:

- unresolved content identity;
- event endpoint stale/unavailable beyond freshness policy;
- queue overflow/drop;
- impossible event sequence anomaly;
- duplicate/reject anomaly;
- lost acquisition context inside paid session;
- experiment exposure join failure;
- schema incompatibility;
- instrumentation exception/failure.

Use `DATA_QUALITY_HOLD` as the downstream block state. Telemetry failure must not break Dilivox UX.

## I. YAN/MONETIZATION SAFETY

Do not modify current YAN rendering logic.

Do not emit or normalize a DOM placement event as a YAN provider impression/revenue.

A placement container may appear only as site-side diagnostic/experiment context. Provider-side YAN/Metrica data remains money/delivery truth.

## J. TILDA ARTIFACT

Produce a Task 006 successor integration artifact based on the accepted Task 005 SiteAgent artifact.

Requirements:

- self-contained;
- dependency-free;
- non-blocking;
- safe-noop fallback;
- event-dispatch kill switch;
- compatible with current text/comic markup;
- no existing content/YAN code mutation;
- NO production endpoint enabled by default;
- update installation/rollback docs;
- DO NOT publish to Tilda.

## K. TESTS — REQUIRED

Keep all previous tests green.

Add browser/Node and Python/local ingestion coverage for:

1. text + comic representative fixtures;
2. page/story singleton events;
3. 25/50/75 content-relative progress;
4. choice section exposure;
5. choice event has no answer text;
6. reveal != completion;
7. completion requires reveal view;
8. next-story stable destination ID;
9. catalog navigation event;
10. attribution context retained;
11. privacy-gated return behavior;
12. experiment actual exposure + kill switch;
13. deterministic idempotency;
14. retry without double counting;
15. queue caps/TTL/overflow;
16. transport/storage exception fail-open for site;
17. raw-first batch order;
18. malformed/conflicting batch behavior;
19. dedupe into `site_events`;
20. health/performance privacy minimization;
21. DATA_QUALITY_HOLD propagation;
22. no YAN rendering mutation;
23. no real production network dispatch;
24. mobile/desktop representative behavior;
25. `git diff --check`;
26. secret/private-ID/production-data scan;
27. no proprietary optimizer/scoring logic;
28. no Tilda publication.

## EXTERNAL PROVIDER STATUS

Direct/Metrica/YAN OAuth credential certification remains a parallel blocker and does not block Task 006 engineering.

If secure credentials become available during Task 006, provider doctor may be rerun READ_ONLY, but this task must not add provider writes.

## DO NOT

- do not publish Tilda;
- do not change production Dilivox;
- do not change YAN rendering/provider code;
- do not create/modify/pause Direct campaigns/groups/ads;
- do not change budgets or spend money;
- do not create paid Cloud resources;
- do not commit secrets/private mappings/raw production data;
- do not implement proprietary optimizer/ranking/allocation logic in public repo;
- do not force push;
- do not merge to `main`.

## EVIDENCE

Create:

`profit-engine/evidence/TASK-006-FIRST-PARTY-EVENTS.md`

Evidence must report:

- baseline/final/origin SHAs;
- exact event types implemented;
- event schema/version;
- DOM/SiteAgent source hooks used;
- progress/reveal/completion semantics;
- queue caps/retry/TTL;
- idempotency/dedupe design;
- raw-first event ingestion proof;
- normalized fixture counts;
- health/performance signals;
- data-quality/hold cases;
- text/comic/mobile/desktop coverage;
- artifact/install path;
- network dispatch status;
- tests/checks;
- files changed;
- blockers;
- recommended Task 007 boundary.

## FINAL REPORT

Return compact report fields:

- `STATUS:`
- `BASELINE_HEAD:`
- `FINAL_HEAD:`
- `ORIGIN_PROFIT_ENGINE:`
- `WORKTREE:`
- `EVENT_TAXONOMY:`
- `EVENT_SCHEMA:`
- `BROWSER_INSTRUMENTATION:`
- `QUEUE_TRANSPORT:`
- `RAW_FIRST_EVENT_INGESTION:`
- `NORMALIZED_SITE_EVENTS:`
- `HEALTH_PERFORMANCE:`
- `DATA_QUALITY:`
- `TILDA_ARTIFACT:`
- `LIVE_DISPATCH_STATUS:`
- `SECRET_SAFETY:`
- `FILES_CHANGED:`
- `COMMIT_SHA:`
- `TESTS/CHECKS:`
- `BLOCKERS:`
- `RECOMMENDED_TASK_007:`

Do not self-accept. Central Brain reviews origin/evidence and advances immediately.
