# PROFIT ENGINE — PROJECT STATE

Status: IMPLEMENTATION ACTIVE / DAY 9 — ACQUISITION STRATEGY LAB
Updated: 2026-08-28
Canonical branch: `profit-engine`

## Current objective

Launch a guarded-production, machine-operated, multi-site Profit Engine whose first closed loop is:

`Yandex Direct -> Dilivox -> user behavior -> YAN revenue -> attribution/reconciliation -> Profit Engine -> guarded Direct + Dilivox actions -> measured outcome`.

First production site: `site_id=dilivox` / `dilivox.ru`.

Primary optimization target:

`1 RUB Yandex Direct spend -> 5 RUB YAN advertising revenue attributable to the acquired Dilivox audience`.

This is a target, not a claimed current result.

## Locked governance

- PROFIT-FIRST: `PROTECT CAPITAL -> MEASURE MONEY -> STOP LOSSES -> FIND PROFIT -> SCALE PROFIT -> REPEAT`.
- Yandex is an execution/data instrument, not the owner or architect of Profit Engine.
- Routine advertising operations are intended to be machine-operated; Owner is not the Direct operator.
- Acquisition mode remains an experiment variable: CPC / conversion-click / pay-for-conversion / value-CRR / Maximum Profit where eligible.
- Weekly automatic budget growth above +20% requires explicit Owner approval.
- Dilivox site-side integration is launch-critical.
- Core remains multi-site/provider-neutral.
- Central Brain leads, executes available work itself, issues Codex tasks, accepts/reworks evidence and immediately advances the plan.
- Chat is not source of truth.
- Local workspaces remain separate:
  - site/Tilda: `~/Documents/New project/Dilivox`;
  - public Profit Engine: `~/Documents/New project/Profit Engine/Dilivox-1`;
  - future private core: `~/Documents/New project/Profit Engine/profit-engine-core`.

## Tasks 001–006 — ACCEPTED

Canonical evidence exists under `profit-engine/evidence/`.

Accepted foundations include:

- local/source inventory;
- READ_ONLY Direct/Metrica/YAN diagnostics and raw-first collectors;
- immutable raw store and provider-neutral data schema;
- stable Dilivox content/placement identity;
- privacy-minimal paid attribution persistence;
- SiteAgent + first-party event layer;
- raw-first first-party ingestion/dedupe/data-quality holds;
- no provider/site writes or spend.

## Task 007 — ACCEPTED AFTER CENTRAL BRAIN HOTFIX

Codex implementation: `ffd097881cf1006a54035b7f32da8101e34dd0be`.

Central Brain found and fixed a launch-critical reconciliation/K5 gating defect. Accepted corrected code: `e5b21baa1622e77e5d1e9408f799a5843e51f2d4`.

Canonical acceptance evidence:

`profit-engine/evidence/TASK-007-CENTRAL-BRAIN-ACCEPTANCE.md`

Accepted money invariants:

- no date-only attribution fallback;
- explicit attribution grades;
- Metrica YAN revenue = attribution view;
- YAN Statistics = reconciliation/control total;
- never double-count Metrica + YAN;
- period K5 distinct from cohort K5;
- cohort 1D/7D/30D uses original acquisition spend denominator;
- unknown revenue never zero-filled;
- zero spend never yields infinity;
- non-MATCHED reconciliation cannot be optimizer-consumable;
- late-arrival recomputation is append-versioned.

## Permanent Profit Engine CI

Workflow:

`.github/workflows/profit-engine-ci.yml`

CI now validates every `profit-engine` push for Python tests, Node tests, JSON validity and diff whitespace.

## Task 008 — ACCEPTED

Final accepted Codex HEAD:

`6cdfe596a2417655d844b626bfefac8c636e868f`

Canonical evidence:

`profit-engine/evidence/TASK-008-CAMPAIGN-CREATIVE-FACTORY.md`

Final GitHub Actions run `33146201616`: GREEN.

Central Brain independently verified:

- deterministic `CampaignSpec`, `CreativeSpec`, `AssetSpec`;
- canonical content-registry landing resolution;
- tracking restricted to accepted acquisition allowlist;
- inert provider capability metadata;
- all future Direct operations represented only as `Intent(executable=false)`;
- dependency and rollback graph;
- valid preview digest `448a3120d1e1f2ea94969aff5d0c67659e9943f915b4925044cf730d8c9fef51`;
- 13 inert intents including 6 rollback intents;
- `provider_requests=0`;
- `advertising_spend=0`;
- `provider_write_allowed=false`;
- Budget Governor required by construction;
- no ranking/winner-selection/proprietary optimizer logic.

Task 008 decision: `ACCEPTED`.

## External provider credentials — parallel blocker

Live provider certification remains:

- Direct: `BLOCKED_MISSING_CREDENTIAL`;
- Metrica: `BLOCKED_MISSING_CREDENTIAL`;
- YAN Statistics: `BLOCKED_MISSING_CREDENTIAL`.

Classification: `BLOCKED_EXTERNAL_PROVIDER_CREDENTIAL`.

Safe plan:

- shared Profit Engine OAuth token for Direct + Metrica;
- separate YAN Statistics OAuth token;
- local macOS Keychain;
- private local provider mappings mode `0600`;
- production migration to Lockbox later.

Tokens/private provider IDs never enter chat or Git.

This blocker does not stop fixture/source-contract engineering.

## Private-core gate — OWNER ACTION ACTIVE

Canonical authority:

`profit-engine/PRIVATE_CORE_REPOSITORY_BOOTSTRAP.md`

Required repository:

`niknikdym-hue/profit-engine-core` — PRIVATE.

At this state update the connected GitHub integration cannot see that repository.

Tracking issue:

`#11 — Owner Gate — create private profit-engine-core repository`.

Mandatory gate:

`PRIVATE_CORE_REPOSITORY_REQUIRED_BEFORE_SENSITIVE_OPTIMIZER_IMPLEMENTATION`.

Until complete, the public repository MUST NOT contain:

- proprietary profit scoring/weights;
- learned thresholds;
- owner-specific allocation heuristics;
- strategy ranking/winner selection;
- sensitive expected-value/LTV calibration;
- confidential provider mappings or production model data.

Public Day-9 work continues without waiting for this gate.

## Immediate active task — Task 009 / Day 9

GitHub issue:

`#10 — Profit Engine Task 009 — Acquisition Strategy Lab public contracts`.

Canonical design:

`profit-engine/DAY9_ACQUISITION_STRATEGY_LAB_DESIGN.md`

Canonical task:

`profit-engine/tasks/TASK-009-ACQUISITION-STRATEGY-LAB-PUBLIC-CONTRACTS.md`

Executor: Codex.
Acceptance authority: Central Brain.

Objective:

`accepted money evidence -> StrategyCell eligibility/holds -> bounded ExperimentPreview -> versioned evidence package for future private decision core`.

Hard Day-9 public rules:

- held/unreconciled/immature/unjoinable money cannot become eligible strategy evidence;
- C-grade Metrica-only evidence cannot masquerade as proven cohort linkage;
- E/UNJOINABLE evidence held;
- proxy signals require explicit money-association state and receive no fabricated monetary weight;
- public code may validate experiments but may not rank cells or choose winners;
- rank/select/allocate/learned-score requests -> `BLOCKED_PRIVATE_CORE_REQUIRED`;
- `provider_requests=0`;
- `advertising_spend=0`;
- `provider_write_allowed=false`;
- final Profit Engine CI must be green.

## Parallel Central Brain work

Central Brain maintains a separate non-conflicting branch for the read-only ledger-materialization gap. Current finding: Task-007 `MetricaAttributionProfile` exists, but the accepted Day-4 Metrica collector still materializes generic dimension rows rather than a dedicated campaign-attribution fact. This must be closed before production materialization can honestly feed live campaign-level Strategy Lab decisions.

This gap is NOT hidden inside Task 009 and does not authorize provider writes.

## Expected Task 010 boundary

After Task 009 acceptance:

- if private core exists and is accessible: bootstrap private authority/contracts and begin sensitive ProfitAllocator/decision logic there;
- public repo: generic action-proposal contract, stop-loss/data-quality gates and Budget Governor public safety invariants;
- no provider write execution until Day-11 guarded Direct Controller gate;
- any budget growth >20% remains Owner approval only.

## Launch definition

Target engineering launch = Day 12 `GUARDED_PRODUCTION_LAUNCHED`.

Launch still requires:

- provider read ingestion/certification;
- Dilivox instrumentation;
- reconciled money ledger/K5;
- Campaign + Creative Factory;
- AcquisitionStrategyLab;
- private ProfitAllocator/decision core;
- Budget Governor;
- guarded Direct write controller;
- Dilivox experiment/kill-switch layer;
- at least one bounded, auditable real closed-loop action.

Stable proof of `K5 >= 5.0` requires reconciled live money after launch; fixtures never prove the target.

## Resume protocol

Read `PROJECT_HANDOFF.md`, follow its exact read order, verify actual `origin/profit-engine` HEAD, inspect open issues #10 and #11, and continue the first incomplete canonical task. Never reconstruct state from chat memory when repository evidence exists.
