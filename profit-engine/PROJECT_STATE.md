# PROFIT ENGINE — PROJECT STATE

Status: IMPLEMENTATION ACTIVE / DAY 6 — FIRST-PARTY EVENTS + SITE SAFETY
Updated: 2026-08-27
Canonical branch: `profit-engine`

## Current objective

Launch a guarded-production, machine-operated, multi-site Profit Engine whose first closed loop is:

`Yandex Direct -> Dilivox -> user behavior -> YAN revenue -> attribution/reconciliation -> Profit Engine -> guarded Direct + Dilivox actions -> measured outcome`.

First production site: `site_id=dilivox` / `dilivox.ru`.

Primary launch target:

`1 RUB Yandex Direct spend -> 5 RUB YAN/RСЯ advertising revenue attributable to the acquired Dilivox audience`.

This is an optimization target, not a claimed current result.

## Locked governance

- PROFIT-FIRST: `PROTECT CAPITAL -> MEASURE MONEY -> STOP LOSSES -> FIND PROFIT -> SCALE PROFIT -> REPEAT`.
- Yandex is an execution/data instrument used to achieve Owner economics.
- Routine advertising operations are machine-operated; Owner is not the Direct operator.
- Acquisition mode is an optimization variable: CPC / conversion / pay-for-conversion / value-DRR / Maximum Profit where eligible.
- Weekly automatic budget growth above +20% requires explicit Owner approval.
- Dilivox site-side integration is launch-critical.
- Core remains multi-site/provider-neutral.
- Central Brain leads, performs available work itself, issues Codex tasks, accepts/reworks evidence and immediately advances the plan.
- Chat is not source of truth.
- Local workspaces remain separated:
  - site/Tilda: `~/Documents/New project/Dilivox`;
  - Profit Engine: `~/Documents/New project/Profit Engine/Dilivox-1`.

## Tasks 001–004 — ACCEPTED

Canonical evidence:

- `profit-engine/evidence/TASK-001-M0-INVENTORY.md`
- `profit-engine/evidence/TASK-002-READ-FOUNDATION.md`
- `profit-engine/evidence/TASK-003-DATA-FOUNDATION.md`
- `profit-engine/evidence/TASK-004-READ-ONLY-INGESTION.md`

Accepted foundation includes:

- local/source inventory;
- read-only Direct/Metrica/YAN diagnostics;
- secret-safe configuration/redaction;
- PostgreSQL schema foundation;
- immutable raw snapshot store;
- provider-neutral storage/health/audit/data-quality contracts;
- `DATA_QUALITY_HOLD`;
- raw-first Direct/Metrica/YAN ingestion;
- deterministic/idempotent normalization;
- 38-test suite reported green by Task 004;
- no provider/site writes or spend.

## Task 005 — ACCEPTED

Accepted implementation HEAD:

`ec3590f9a4daee08fcbdac957269fd77d78c9a15`

Canonical evidence:

`profit-engine/evidence/TASK-005-DILIVOX-IDENTITY-ATTRIBUTION.md`

Central Brain independently inspected and accepted:

- 61 immutable opaque content identities;
- 56/56 source story/comic coverage;
- 50/50 discoverable active content coverage;
- immutable ID preservation independent of URL/title/slug changes;
- 12/12 current YAN `data-dv-ad-block` placement mappings;
- generic SiteAgent + `DilivoxSiteAgent` adapter;
- strict acquisition allowlist (`yclid`, approved UTM/Direct identifiers only);
- paid acquisition persistence across internal navigation;
- deterministic paid->paid supersession;
- 30-day hard attribution/return TTL cap;
- privacy-gated durable return identity;
- no fingerprinting and no Metrica ClientID identity;
- experiment/variant identity + kill switches without optimizer logic;
- event-context schema for Day 6;
- self-contained unpublished Tilda integration artifact;
- 11/11 Node simulations and previous 38/38 Python tests reported green;
- no `fetch` event dispatch or `Ya.Context` mutation in the Task 005 SiteAgent artifact;
- no Tilda publication, Direct write, spend or secret exposure.

Task 005 decision: `ACCEPTED`.

## External provider credentials — parallel blocker only

Live provider certification remains:

- Direct: `BLOCKED_MISSING_CREDENTIAL`;
- Metrica: `BLOCKED_MISSING_CREDENTIAL`;
- YAN Statistics: `BLOCKED_MISSING_CREDENTIAL`.

Classification:

`BLOCKED_EXTERNAL_PROVIDER_CREDENTIAL`.

Current safe plan:

- one existing Profit Engine Yandex OAuth token for technical identity with `direct:api` + `metrika:read` scopes;
- separate YAN Statistics OAuth token;
- local macOS Keychain storage during development;
- private provider mappings in `~/.config/profit-engine/sites/dilivox.json` mode `0600`;
- later migrate production secrets to Lockbox.

Token values/private provider IDs never enter chat or Git.

This blocker does not stop Day 6 engineering.

## Public/private core gate

Current `Dilivox-1` repository is public.

Public-safe:

- generic provider/site adapters;
- schemas/contracts;
- identity/attribution/event plumbing;
- data-quality/safety invariants;
- generic controller interfaces;
- public-safe registries/fixtures.

Forbidden here before private core exists:

- proprietary profit scoring formulas/weights;
- learned optimizer thresholds;
- owner-specific capital allocation heuristics;
- commercially sensitive creative ranking/generation logic;
- confidential provider mappings;
- production model data/raw exports.

Mandatory gate:

`PRIVATE_CORE_REPOSITORY_REQUIRED_BEFORE_SENSITIVE_OPTIMIZER_IMPLEMENTATION`.

Central Brain has prepared a parallel private-core repository design so this does not become a Day 9/10 surprise blocker; actual private repository creation remains a later explicit implementation step.

## Canonical Day 6 design

`profit-engine/DAY6_EVENT_LAYER_DESIGN.md`

Key rule:

`version_selected != story_completed`.

Completion requires reveal to be open AND genuinely viewed; a choice click alone is not a completed reader.

Canonical event path:

`Dilivox DOM -> SiteAgent -> canonical event -> bounded browser queue -> first-party event batch -> immutable raw -> dedupe/validation -> site_events -> data-quality state`.

## Immediate active task — Task 006 / Day 6

Canonical contract:

`profit-engine/tasks/TASK-006-FIRST-PARTY-EVENTS-SITE-SAFETY.md`

Executor: Codex.
Acceptance authority: Central Brain.

Task 006 scope:

- canonical behavior event taxonomy;
- content-relative story progress 25/50/75;
- choice/reveal/completion semantics;
- next-story/catalog/return/experiment events;
- strict event envelope/privacy allowlist;
- deterministic idempotency/dedupe;
- bounded async browser queue with retry/TTL/kill switch;
- raw-first first-party event batch ingestion;
- normalization into `site_events`;
- JS/performance/event-delivery health signals;
- `DATA_QUALITY_HOLD` for unreliable telemetry;
- representative text/comic/mobile/desktop tests;
- Task 006 successor Tilda artifact prepared but NOT published;
- no provider impression/revenue invention from DOM events.

## Current launch day

Day 6 of `HARD_12_DAY_LAUNCH_PLAN.md` is active.

## Expected Task 007 boundary after Task 006 acceptance

Day 7 is the money ledger/reconciliation milestone:

- join Direct spend to acquired Dilivox cohorts;
- join first-party events/content identity to Metrica/YAN monetization;
- reconcile Metrica YAN revenue vs Partner Statistics;
- calculate observed `K5_1D`, `K5_7D`, `K5_30D` where source data exists;
- calculate revenue/visit and revenue/acquired-user;
- preserve estimated/final/reconciled states;
- enforce `DATA_QUALITY_HOLD` on unresolved money or attribution discrepancies;
- expose evidence-ready money map, not a vanity dashboard.

Live monetary reconciliation remains fixture-contract capable until OAuth provider reads are unblocked.

## Launch definition

Target engineering launch = Day 12 `GUARDED_PRODUCTION_LAUNCHED`.

Launch requires:

- provider read ingestion;
- Dilivox instrumentation;
- reconciled money ledger/K5;
- Campaign Factory + Creative Factory foundation;
- AcquisitionStrategyLab;
- ProfitAllocator/Rule Engine;
- Budget Governor;
- guarded Direct write controller;
- Dilivox experiment/kill-switch layer;
- at least one bounded, auditable real closed-loop action.

## Economic proof after launch

Stable proof of `K5 >= 5.0` requires reconciled live money after launch. Expected observation/optimization phase remains approximately 14–30 days depending on traffic/revenue delay.

## Resume protocol

Read `PROJECT_HANDOFF.md`, follow its exact read order, verify actual `origin/profit-engine` HEAD, and continue the first incomplete canonical task. Never reconstruct state from chat memory when repository evidence exists.
