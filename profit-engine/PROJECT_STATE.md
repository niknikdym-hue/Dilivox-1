# PROFIT ENGINE — PROJECT STATE

Status: IMPLEMENTATION ACTIVE / DAY 4 — READ-ONLY INGESTION
Updated: 2026-08-27
Canonical branch: `profit-engine`

## Current objective

Launch a guarded-production, machine-operated, multi-site Profit Engine whose first closed loop is:

`Yandex Direct -> Dilivox -> user behavior -> YAN revenue -> attribution/reconciliation -> Profit Engine -> guarded Direct + Dilivox actions -> measured outcome`.

First production site: `site_id=dilivox` / `dilivox.ru`.

Primary launch target:

`1 RUB Yandex Direct spend -> 5 RUB YAN/RСЯ advertising revenue attributable to the acquired Dilivox audience`.

This is the optimization target, not a claimed current result.

## Locked Owner decisions

- PROFIT-FIRST machine: `PROTECT CAPITAL -> MEASURE MONEY -> STOP LOSSES -> FIND PROFIT -> SCALE PROFIT -> REPEAT`.
- Yandex is an execution/data tool used to achieve the Owner objective.
- YAN/RСЯ is monetization provider #1; architecture must accept additional providers later.
- Dilivox is site #1; core is multi-site from day one.
- Routine advertising operations are machine-operated; Owner is not the Direct operator.
- Acquisition mode is an experiment variable: CPC / conversion / pay-for-conversion / value-DRR / Maximum Profit where eligible.
- Weekly automatic budget growth above +20% is forbidden without explicit Owner approval.
- Full Dilivox site-side integration is launch-critical.
- Central Brain leads, executes available work, issues Codex tasks, accepts results and immediately advances the plan.
- Chat is not source of truth.
- Local workspaces are separated: `~/Documents/New project/Dilivox` remains the site workspace; `~/Documents/New project/Profit Engine/Dilivox-1` is the Profit Engine workspace.

## Task 001 — ACCEPTED

Canonical evidence:

`profit-engine/evidence/TASK-001-M0-INVENTORY.md`

Accepted:
- local Profit Engine clone exists and is separated from the site workspace;
- Dilivox implementation surface, Metrica hooks and YAN placements inventoried;
- no production/provider writes occurred;
- gaps identified: UTM/yclid persistence, stable immutable content IDs, Profit Engine first-party ingestion;
- provider live reads blocked by missing secure tokens.

## Task 002 — ENGINEERING ACCEPTED / LIVE CERTIFICATION BLOCKED EXTERNALLY

Accepted implementation HEAD:

`a5de1b32a8460fb18428625e01b09509686d158a`

Canonical evidence:

`profit-engine/evidence/TASK-002-READ-FOUNDATION.md`

Accepted:
- provider-neutral READ_ONLY runtime;
- Direct/Metrica/YAN diagnostic clients;
- redacted logging and bounded retry;
- public example/private local config boundary;
- Task 001 evidence safely synchronized;
- 11 tests reported PASS;
- no provider writes/spend/site mutation.

Live state remains:
- Direct: `BLOCKED_MISSING_CREDENTIAL`;
- Metrica: `BLOCKED_MISSING_CREDENTIAL`;
- YAN Statistics: `BLOCKED_MISSING_CREDENTIAL`.

This is `BLOCKED_EXTERNAL_PROVIDER_CREDENTIAL` and continues in parallel.

## Task 003 — ACCEPTED

Accepted implementation HEAD:

`3d521ff2d44532035025f31d6de8ea0428dc94fe`

Canonical evidence:

`profit-engine/evidence/TASK-003-DATA-FOUNDATION.md`

Central Brain independently inspected the implementation and accepted:
- explicit public/private core boundary;
- gate `PRIVATE_CORE_REPOSITORY_REQUIRED_BEFORE_SENSITIVE_OPTIMIZER_IMPLEMENTATION`;
- versioned PostgreSQL migration `0001_data_foundation.sql` with 14 provider-neutral site-scoped tables;
- Decimal-compatible monetary schema using `numeric(20,6)`;
- immutable raw snapshot envelope/store;
- atomic create-only raw writes;
- idempotent same-content replay and conflict rejection;
- SHA-256 validation at write/read;
- provider-neutral relational/raw/secret/health/audit interfaces;
- `DATA_QUALITY_HOLD` primitives preventing held/not-ready data from optimizer use;
- portable deployment boundaries without paid Cloud apply;
- 21/21 tests reported PASS;
- secret scan and `git diff --check` PASS;
- no production/site/provider write or spend.

## Public/private core boundary

The current repository is public.

Public-safe here:
- provider adapters/collectors;
- generic schemas/interfaces;
- data quality/safety invariants;
- site adapter contracts;
- redaction, audit, health and generic storage utilities.

Forbidden here before a private-core repository exists:
- proprietary profit scoring formulas/weights;
- learned optimizer thresholds;
- owner-specific capital allocation heuristics;
- commercially sensitive creative ranking/generation logic;
- confidential provider mappings;
- secrets/production datasets/raw exports.

Mandatory gate:

`PRIVATE_CORE_REPOSITORY_REQUIRED_BEFORE_SENSITIVE_OPTIMIZER_IMPLEMENTATION`.

Task 004 remains public-safe because it is strictly READ_ONLY ingestion and normalization without commercial optimization policy.

## Immediate active task — Task 004 / Day 4

Canonical contract:

`profit-engine/tasks/TASK-004-READ-ONLY-INGESTION.md`

Executor: Codex.
Acceptance authority: Central Brain.

Task 004 objective:

`provider read -> immutable raw snapshot -> ingestion metadata -> normalization -> provider-neutral facts -> data-quality state`

Required scope:
- ingestion-run orchestrator with started/complete/failed/held lifecycle;
- Direct campaign metadata + Reports spend/performance collector;
- Metrica traffic/YAN monetization collector;
- YAN Statistics tree-driven collector;
- raw-first invariant;
- deterministic normalization;
- idempotent replay/conflict protection;
- normalized `campaign_snapshots`, `traffic_facts`, `monetization_facts` where source semantics are known;
- freshness/completeness/money-basis quality checks;
- `DATA_QUALITY_HOLD` propagation;
- fixture/local execution while live credentials are absent;
- live READ_ONLY collection only after provider doctor PASS;
- tests, secret scan and evidence push.

No Direct writes, budget changes, spend, production Dilivox/Tilda changes, paid Cloud resources, or proprietary optimizer logic are authorized.

## Current launch day

Day 4 of `HARD_12_DAY_LAUNCH_PLAN.md` is active.

Provider credential certification continues in parallel and does not justify engineering idle time.

## Expected Task 005 boundary after Task 004 acceptance

Day 5 target:
- stable Dilivox content/story/page IDs;
- `DilivoxSiteAgent` first implementation;
- Direct/UTM/yclid attribution persistence across internal navigation;
- provider-neutral monetization placement registry foundation;
- experiment identity hooks;
- integration design compatible with existing Tilda/T123 implementation;
- no uncontrolled production deployment.

Central Brain will derive the exact Task 005 contract from Task 004 evidence and current Dilivox source state.

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

Expected live evidence/optimization phase: approximately 14–30 days depending on traffic volume and revenue/conversion delay.

Only reconciled live money may prove `K5 >= 5.0`.

## Resume protocol

Read `PROJECT_HANDOFF.md`, follow its exact read order, verify actual `origin/profit-engine` HEAD, and continue the first incomplete task. Never reconstruct state from chat memory when repository evidence exists.
