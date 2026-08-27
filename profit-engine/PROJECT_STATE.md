# PROFIT ENGINE — PROJECT STATE

Status: IMPLEMENTATION ACTIVE / DAY 7 — MONEY LEDGER + ATTRIBUTION + RECONCILIATION
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
- Full Dilivox site-side integration is launch-critical.
- Core remains multi-site/provider-neutral.
- Central Brain leads, executes available work itself, issues Codex tasks, accepts/reworks evidence and immediately advances the plan.
- Chat is not source of truth.
- Local workspaces remain separated:
  - site/Tilda: `~/Documents/New project/Dilivox`;
  - Profit Engine: `~/Documents/New project/Profit Engine/Dilivox-1`.

## Tasks 001–005 — ACCEPTED

Canonical evidence exists under `profit-engine/evidence/`.

Accepted foundation includes:

- local/source inventory;
- READ_ONLY Direct/Metrica/YAN diagnostics and collectors;
- immutable raw storage and provider-neutral PostgreSQL schema foundation;
- raw-first provider ingestion and deterministic normalization;
- stable Dilivox content identities and placement registry;
- strict paid-attribution allowlist and first-party acquisition/session context;
- generic SiteAgent + `DilivoxSiteAgent`;
- no provider/site write or spend.

## Task 006 — ACCEPTED

Accepted implementation HEAD:

`ff5b0251daeb90e373aa890e2ca198282a533102`

Canonical evidence:

`profit-engine/evidence/TASK-006-FIRST-PARTY-EVENTS.md`

Central Brain independently inspected and accepted:

- all 16 canonical first-party event types;
- strict event schema/property privacy allowlist;
- shared text/comic browser event controller;
- content-relative progress 25/50/75;
- trusted choice event and strict `version_selected != story_completed` semantics;
- completion only after reveal open + genuine reveal/final visibility;
- bounded async queue: 50 events, 8 KiB/event, 64 KiB/batch, 24h TTL, max 3 retries;
- dispatch kill switch/fail-open behavior;
- raw-first event batch ingestion with immutable raw put + SHA verification before normalization;
- authoritative dedupe/idempotency/conflict handling;
- health/performance signals without raw URL/stack/PII;
- nine material `DATA_QUALITY_HOLD` classes with `optimizer_consumable=false`;
- reported Node 22/22 PASS and Python 44/44 PASS;
- no real event endpoint, no production dispatch, no Tilda publication, no YAN mutation.

Task 006 decision: `ACCEPTED`.

## External provider credentials — parallel blocker only

Live provider certification remains:

- Direct: `BLOCKED_MISSING_CREDENTIAL`;
- Metrica: `BLOCKED_MISSING_CREDENTIAL`;
- YAN Statistics: `BLOCKED_MISSING_CREDENTIAL`.

Classification:

`BLOCKED_EXTERNAL_PROVIDER_CREDENTIAL`.

Safe plan remains:

- one existing Profit Engine OAuth token under technical Yandex identity for `direct:api` + `metrika:read`;
- separate YAN Statistics OAuth token;
- macOS Keychain for local development;
- private provider mappings in local mode-`0600` config;
- production migration to Lockbox later.

Tokens/private provider IDs never enter chat or Git.

This blocker does not stop Day 7 fixture/source-contract engineering.

## Public/private core gate

Current `Dilivox-1` repository is public.

Public-safe:

- generic provider/site adapters;
- schemas/contracts;
- identity/attribution/event plumbing;
- ledger/reconciliation/data-quality measurement logic;
- generic safety/controller interfaces.

Forbidden before private core exists:

- proprietary profit scoring formulas/weights;
- learned optimizer thresholds;
- owner-specific capital allocation heuristics;
- commercially sensitive creative ranking/generation logic;
- confidential provider mappings;
- production model data/raw exports.

Mandatory gate:

`PRIVATE_CORE_REPOSITORY_REQUIRED_BEFORE_SENSITIVE_OPTIMIZER_IMPLEMENTATION`.

Central Brain continues preparing this boundary in parallel before Days 9–10.

## Canonical Day 7 design

`profit-engine/DAY7_MONEY_LEDGER_DESIGN.md`

Critical money rules:

1. no date-proximity attribution;
2. every join has explicit `attribution_grade`;
3. Metrica YAN revenue is the attribution view;
4. YAN Partner Statistics is a control/reconciliation total;
5. Metrica + YAN revenue are never double-counted;
6. `period_K5` and cohort `K5_1D/7D/30D` are different measurements;
7. cohort K5 is `NOT_COMPUTABLE_ATTRIBUTION_HOLD` if later revenue cannot be proven to belong to the original acquisition cohort;
8. unknown revenue is never converted to zero;
9. zero spend never yields infinite K5;
10. material uncertainty -> `DATA_QUALITY_HOLD`.

Current official Yandex contracts confirm Metrica attribution-aware Direct campaign/group/UTM dimensions and YAN monetization metrics, while Direct supports dynamic campaign/ad/group/click identifiers in landing URLs. Task 007 therefore cross-checks independent attribution paths rather than trusting one source blindly.

## Immediate active task — Task 007 / Day 7

Canonical contract:

`profit-engine/tasks/TASK-007-MONEY-LEDGER-RECONCILIATION.md`

Executor: Codex.
Acceptance authority: Central Brain.

Task 007 scope:

- versioned acquisition/money/reconciliation/K5 schema migration;
- strict privacy-safe acquisition registration contract;
- Direct spend ledger input;
- Metrica Direct-attributed YAN report contract;
- explicit attribution grades and cross-check engine;
- Metrica-vs-YAN control-total reconciliation;
- period K5 and distinct cohort K5 1D/7D/30D;
- source states `ESTIMATED/FINAL/RECONCILED/NOT_COMPUTABLE`;
- late-arrival/versioned recomputation;
- revenue/user and revenue/visit with compatible denominator scopes only;
- comprehensive `DATA_QUALITY_HOLD` matrix;
- fixture/source-contract execution while provider credentials remain externally blocked;
- no optimizer or provider/site write.

## Current launch day

Day 7 of `HARD_12_DAY_LAUNCH_PLAN.md` is active.

## Expected Task 008 boundary after Task 007 acceptance

Day 8 target remains Campaign Factory + Creative Factory foundation in non-spending dry-run mode:

- provider-neutral campaign specification;
- Yandex Direct entity lifecycle adapter contracts;
- campaign/group/ad/keyword-or-autotargeting construction where supported;
- tracking-parameter generation aligned with the accepted attribution ledger;
- creative asset registry/versioning;
- automated public-safe validation/policy hooks;
- complete preview/dry-run plan before any provider write;
- no money spend and no Direct Editing enablement.

Central Brain is preparing Day-8 public-safe contracts in parallel while Codex executes Task 007.

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

Stable proof of `K5 >= 5.0` requires reconciled live money after launch. Fixture calculations never prove the target.

Expected post-launch observation/optimization phase remains approximately 14–30 days depending on traffic/revenue delay.

## Resume protocol

Read `PROJECT_HANDOFF.md`, follow its exact read order, verify actual `origin/profit-engine` HEAD, and continue the first incomplete canonical task. Never reconstruct state from chat memory when repository evidence exists.
