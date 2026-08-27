# PROFIT ENGINE — PROJECT STATE

Status: IMPLEMENTATION ACTIVE / DAY 8 — CAMPAIGN FACTORY + CREATIVE FACTORY DRY-RUN
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

## Tasks 001–006 — ACCEPTED

Canonical evidence exists under `profit-engine/evidence/`.

Accepted foundation includes:

- local/source inventory;
- READ_ONLY Direct/Metrica/YAN diagnostics and collectors;
- immutable raw storage and provider-neutral PostgreSQL schema foundation;
- raw-first provider ingestion and deterministic normalization;
- stable Dilivox content identities and placement registry;
- strict paid-attribution allowlist and first-party acquisition/session context;
- generic SiteAgent + `DilivoxSiteAgent`;
- canonical first-party event layer with raw-first ingestion, dedupe and site-safe fail-open behavior;
- no provider/site write or spend.

## Task 007 — ACCEPTED AFTER CENTRAL BRAIN HOTFIX

Codex implementation:

`ffd097881cf1006a54035b7f32da8101e34dd0be`

Central Brain found one launch-critical defect before acceptance: non-MATCHED reconciliation states were not uniformly propagated into K5 holds, so mature/proven cohort K5 could become optimizer-consumable despite bad reconciliation.

Central Brain corrected it directly:

- `f6579eac2030084fb7d27fac0b89a99d36371b2f` — common reconciliation gate for period/cohort K5 and optimizer consumption;
- `e5b21baa1622e77e5d1e9408f799a5843e51f2d4` — regression coverage for all non-MATCHED reconciliation states and diagnostic-only unit revenue behavior.

Accepted Task-007 code state:

`e5b21baa1622e77e5d1e9408f799a5843e51f2d4`

Canonical acceptance evidence:

`profit-engine/evidence/TASK-007-CENTRAL-BRAIN-ACCEPTANCE.md`

Accepted money rules now include:

- explicit attribution grades;
- no date-only attribution fallback;
- Metrica YAN revenue as attribution view;
- YAN Statistics as reconciliation/control total only;
- no Metrica+YAN double-count;
- distinct period K5 vs cohort K5;
- original cohort-spend denominator for 1D/7D/30D;
- late-arrival append-versioning;
- unknown revenue never zero-filled;
- zero spend never produces infinity;
- `PENDING/DRIFT/BASIS_BLOCKED/SOURCE_MISSING` reconciliation cannot be optimizer-consumable.

No real `K5 >= 5.0` is claimed from fixtures.

## Permanent Profit Engine CI

Central Brain added:

`.github/workflows/profit-engine-ci.yml`

Verification descendant:

`7bf092c63c4d04f71eb5d48192395845a110f206`

GitHub Actions run #2 is GREEN:

- Python `60/60 PASS`;
- Node `22/22 PASS`;
- JSON validation PASS;
- diff whitespace check PASS.

All future Codex tasks must finish with green `Profit Engine CI` on the final origin HEAD.

## External provider credentials — parallel blocker only

Live provider certification remains:

- Direct: `BLOCKED_MISSING_CREDENTIAL`;
- Metrica: `BLOCKED_MISSING_CREDENTIAL`;
- YAN Statistics: `BLOCKED_MISSING_CREDENTIAL`.

Classification:

`BLOCKED_EXTERNAL_PROVIDER_CREDENTIAL`.

Safe plan remains:

- one Profit Engine OAuth token under technical Yandex identity for `direct:api` + `metrika:read`;
- separate YAN Statistics OAuth token;
- macOS Keychain for local development;
- private provider mappings in local mode-`0600` config;
- production migration to Lockbox later.

Tokens/private provider IDs never enter chat or Git.

This blocker does not stop Day 8 dry-run engineering.

## Public/private core gate

Current `Dilivox-1` repository is public.

Public-safe on Day 8:

- deterministic campaign/creative specs;
- provider capability metadata;
- tracking validation;
- asset identity/versioning;
- inert provider intents;
- dry-run dependency/rollback planning;
- safety/validation code.

Forbidden before private core exists:

- proprietary profit scoring formulas/weights;
- learned optimizer thresholds;
- owner-specific capital allocation heuristics;
- commercially sensitive creative ranking/winner-selection;
- confidential provider mappings;
- production model data/raw exports.

Mandatory gate before sensitive Day-9/10 implementation:

`PRIVATE_CORE_REPOSITORY_REQUIRED_BEFORE_SENSITIVE_OPTIMIZER_IMPLEMENTATION`.

Central Brain has already prepared the repository-boundary design. Actual private-repository creation is an Owner/GitHub action because the current connector cannot create a new repository. This does not block Task 008, but must be resolved before private optimizer logic begins.

## Canonical Day 8 design

- `profit-engine/DAY8_CAMPAIGN_FACTORY_DESIGN.md`
- `profit-engine/DAY8_ACCEPTANCE_MATRIX.md`

Current provider contracts were rechecked against current Yandex Direct API v5/v501 documentation before issuing Task 008. Campaigns, AdGroups, Ads, Keywords/autotargeting and AdImages remain separate lifecycle services; unified performance campaigns/groups use v501-compatible contracts. Day 8 models these only as inert future intents.

## Immediate active task — Task 008 / Day 8

Canonical contract:

`profit-engine/tasks/TASK-008-CAMPAIGN-CREATIVE-FACTORY-DRY-RUN.md`

Executor: Codex.
Acceptance authority: Central Brain.

Task 008 objective:

`CampaignSpec -> validation -> Creative/Asset specs -> inert Direct entity intents -> dependency graph -> tracking plan -> rollback graph -> immutable preview digest`.

Hard Task-008 invariants:

- `provider_write_allowed=false`;
- `requires_budget_governor=true` for any budget intent;
- `provider_requests=0`;
- `advertising_spend=0`;
- no executable Direct write path;
- no image upload;
- no moderation submission;
- no budget mutation;
- no proprietary commercial winner-selection in the public repo;
- final `Profit Engine CI` must be green.

Allowed result states include `PREVIEW_VALID`, explicit invalid/block states, and deliberately no `EXECUTED` state.

## Current launch day

Day 8 of `HARD_12_DAY_LAUNCH_PLAN.md` is active.

## Parallel Central Brain work

Central Brain continues two non-conflicting streams while Codex executes Task 008:

1. private-core boundary / Day-9 readiness;
2. read-only ledger materialization bridge from immutable provider/event facts into accepted generic money-ledger interfaces, without optimizer logic or provider writes.

These streams are kept separate from Codex's branch writes until compatibility is verified.

## Expected Task 009 boundary

Day 9 target:

- AcquisitionStrategyLab contract;
- strategy-cell model for CPC / conversion-click / pay-for-conversion / value/CRR / Maximum Profit where eligible;
- proxy-value inputs only where proven by money evidence;
- bounded experiment definitions;
- comparison using K5/expected contribution rather than vanity provider KPIs;
- private-core gate enforced before sensitive strategy selection/weights;
- no Direct write execution yet.

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
