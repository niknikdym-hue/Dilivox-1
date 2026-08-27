# PROFIT ENGINE — PROJECT STATE

Status: IMPLEMENTATION ACTIVE / DAY 5 — DILIVOX IDENTITY + ATTRIBUTION
Updated: 2026-08-27
Canonical branch: `profit-engine`

## Current objective

Launch a guarded-production, machine-operated, multi-site Profit Engine whose first closed loop is:

`Yandex Direct -> Dilivox -> user behavior -> YAN revenue -> attribution/reconciliation -> Profit Engine -> guarded Direct + Dilivox actions -> measured outcome`.

First production site: `site_id=dilivox` / `dilivox.ru`.

Primary launch target:

`1 RUB Yandex Direct spend -> 5 RUB YAN/RСЯ advertising revenue attributable to the acquired Dilivox audience`.

This is an optimization target, not a claimed current result.

## Locked Owner/governance rules

- PROFIT-FIRST: `PROTECT CAPITAL -> MEASURE MONEY -> STOP LOSSES -> FIND PROFIT -> SCALE PROFIT -> REPEAT`.
- Yandex is an execution/data tool used to achieve Owner economics.
- Routine advertising operations are machine-operated; Owner is not the Direct operator.
- Acquisition mode is an optimization variable: CPC / conversion / pay-for-conversion / value-DRR / Maximum Profit where eligible.
- Weekly automatic budget growth above +20% is forbidden without explicit Owner approval.
- Full Dilivox site-side integration is launch-critical.
- Dilivox is site #1; common core remains multi-site/provider-neutral.
- Central Brain leads, performs available work, issues Codex tasks, accepts/reworks evidence and immediately advances the plan.
- Chat is not source of truth.
- Workspaces remain separated: `~/Documents/New project/Dilivox` is the site/Tilda workspace; `~/Documents/New project/Profit Engine/Dilivox-1` is the Profit Engine workspace.

## Tasks 001–003 — ACCEPTED

Canonical evidence:

- `profit-engine/evidence/TASK-001-M0-INVENTORY.md`
- `profit-engine/evidence/TASK-002-READ-FOUNDATION.md`
- `profit-engine/evidence/TASK-003-DATA-FOUNDATION.md`

Accepted foundations include:

- local workspace and Dilivox implementation inventory;
- provider-neutral READ_ONLY Direct/Metrica/YAN diagnostic clients;
- secret-safe config/redaction boundary;
- PostgreSQL schema foundation;
- immutable raw snapshot contract/store;
- provider-neutral storage/secret/health/audit interfaces;
- `DATA_QUALITY_HOLD` primitives;
- explicit public/private core boundary.

Mandatory private-core gate remains:

`PRIVATE_CORE_REPOSITORY_REQUIRED_BEFORE_SENSITIVE_OPTIMIZER_IMPLEMENTATION`.

## Task 004 — ACCEPTED

Accepted implementation HEAD:

`8e7bb96450e6d878b513f47649929c27a868ea4b`

Canonical evidence:

`profit-engine/evidence/TASK-004-READ-ONLY-INGESTION.md`

Central Brain independently inspected the implementation and accepted:

- ingestion lifecycle `started/complete/failed/held`;
- deterministic request/run/fact identities and replay-safe normalization;
- enforced RAW-FIRST sequence: provider/fixture read -> immutable raw put -> raw read/hash verification -> normalization;
- raw conflict -> held with no normalized output from conflicting payload;
- Direct campaign metadata + daily Reports collector with Decimal spend and explicit VAT/discount basis;
- Metrica traffic + YAN monetization collector with sampling/accuracy provenance;
- YAN Statistics tree-driven collector with revenue-field semantic validation and money/currency/timezone provenance;
- ambiguous/unknown money semantics -> `DATA_QUALITY_HOLD`, never guessed/zero revenue;
- provider-neutral normalized campaign/traffic/monetization facts;
- CLI for Direct/Metrica/YAN/all with deterministic fixture mode;
- fixture result: 3 raw snapshots -> 1 campaign snapshot + 2 traffic facts + 2 monetization facts;
- 38/38 tests reported PASS and previous tests preserved;
- secret scan/provider-write scan/diff checks PASS;
- no Direct/site/provider write, spend, Cloud apply or Tilda publication.

Task 004 acceptance decision: `ACCEPTED`.

## External provider credential blocker — parallel only

Live provider certification/collection remains:

- Direct: `BLOCKED_MISSING_CREDENTIAL`;
- Metrica: `BLOCKED_MISSING_CREDENTIAL`;
- YAN Statistics: `BLOCKED_MISSING_CREDENTIAL`.

Classification:

`BLOCKED_EXTERNAL_PROVIDER_CREDENTIAL`.

Required later Owner/provider actions remain secret-safe:

1. securely authorize/store shared Direct+Metrica OAuth token;
2. securely obtain/store separate YAN Statistics OAuth token;
3. populate private local provider mappings with mode `0600`;
4. rerun provider doctor/live bounded READ_ONLY collectors.

Never send tokens/private provider IDs in chat or Git.

This external blocker does not stop Day-5 engineering.

## Public/private core boundary

Current repository is public.

Public-safe here:

- generic provider/site adapters;
- schemas/contracts;
- data-quality/safety invariants;
- browser SiteAgent contracts;
- identity/attribution plumbing;
- content/placement registries that contain no confidential provider/account mappings;
- redaction/audit/health/storage utilities.

Still forbidden here before private core exists:

- proprietary profit scoring formulas/weights;
- learned thresholds;
- owner-specific capital allocation heuristics;
- commercially sensitive creative ranking/generation logic;
- private provider/account mappings;
- production datasets/raw exports.

## Immediate active task — Task 005 / Day 5

Canonical contract:

`profit-engine/tasks/TASK-005-DILIVOX-IDENTITY-ATTRIBUTION-SITE-AGENT.md`

Executor: Codex.
Acceptance authority: Central Brain.

Task 005 objective:

`paid acquisition -> immutable Dilivox content_id -> persistent first-party attribution -> SiteAgent context -> provider-neutral placement identity -> Day-6 event context`.

Required scope:

- persistent stable Dilivox content/page/story registry;
- immutable opaque `content_id` independent of later title/URL/slug changes;
- reusable browser-side `SiteAgent` contract + `DilivoxSiteAgent` adapter;
- privacy-minimal allowlisted UTM/yclid/Direct attribution capture;
- attribution persistence across internal navigation;
- pseudonymous session/acquisition references with no fingerprinting;
- provider-neutral current YAN placement registry mapped from actual `data-dv-ad-block` source;
- experiment/variant identity hooks and kill-switch context only, no proprietary optimizer;
- event-envelope/context contract for Day 6;
- self-contained Tilda/T123 integration artifact prepared but NOT published;
- tests/coverage/evidence.

Production/Tilda publication remains forbidden in Task 005.

## Current launch day

Day 5 of `HARD_12_DAY_LAUNCH_PLAN.md` is active.

The separate current Dilivox/Tilda workspace may be inspected for source truth and local integration validation, but production publication requires a later controlled deployment gate.

## Expected Task 006 boundary

After Task 005 acceptance, Day 6 should implement:

- canonical first-party event taxonomy;
- browser event capture/dedupe;
- local/portable first-party event ingestion;
- story progress/choice/reveal/completion/next-story/return signals;
- experiment exposure context;
- mobile/desktop validation;
- JS/performance/failure signals;
- first-party event kill switch/fail-safe behavior;
- controlled production deployment preparation;
- no autonomous money scaling until first-party and provider data reconcile.

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
