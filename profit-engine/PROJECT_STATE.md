# PROFIT ENGINE — PROJECT STATE

Status: IMPLEMENTATION ACTIVE / DAY 3 — DATA FOUNDATION
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

Canonical evidence is now on origin:

`profit-engine/evidence/TASK-001-M0-INVENTORY.md`

Accepted findings:
- local Profit Engine clone exists and is cleanly separated from the site workspace;
- current Dilivox implementation surface, Metrica hooks and YAN placements were inventoried;
- no production/site/provider writes occurred;
- current gaps include UTM/yclid persistence, stable immutable content IDs and Profit Engine first-party ingestion;
- provider live API checks were blocked by missing secure tokens.

## Task 002 — ENGINEERING ACCEPTED / LIVE CERTIFICATION BLOCKED EXTERNALLY

Evidence-bearing HEAD reviewed by Central Brain:

`a5de1b32a8460fb18428625e01b09509686d158a`

Canonical evidence:

`profit-engine/evidence/TASK-002-READ-FOUNDATION.md`

Accepted engineering deliverables:
- Task 001 evidence safely rebased/pushed without force push;
- root `.gitignore` and secret hygiene in place;
- provider-neutral READ_ONLY runtime foundation;
- Direct/Metrica/YAN diagnostic read clients;
- public-example/private-local configuration boundary;
- redacted logging and bounded retries;
- fixture/unit test suite reported 11 PASS;
- no provider write methods, spend, Tilda publication or production mutation.

Central Brain independently checked the request shapes against current official Yandex documentation: Direct Clients/Campaigns read pattern, Metrica `ym:s:yanPartnerPrice`, and YAN Statistics API structure are consistent with current provider contracts.

### D2 live certification blocker

Current status:
- Direct: `BLOCKED_MISSING_CREDENTIAL`;
- Metrica: `BLOCKED_MISSING_CREDENTIAL`;
- YAN Statistics: `BLOCKED_MISSING_CREDENTIAL`.

Required Owner/provider actions in parallel:
1. securely authorize/store the Profit Engine OAuth token for Direct + Metrica (`direct:api` + `metrika:read`);
2. securely obtain/store the separate YAN Statistics API OAuth token;
3. create the private local Dilivox provider mapping config with mode `0600`;
4. rerun provider doctor.

Tokens/private provider IDs must never be sent through chat or committed to GitHub.

This blocker is classified `BLOCKED_EXTERNAL_PROVIDER_CREDENTIAL` and does NOT stop parallel engineering.

## Public/private core risk

`niknikdym-hue/Dilivox-1` is public.

Generic interfaces, schemas, site contracts, safety controls and non-secret examples may remain here.

Before proprietary optimizer/scoring/allocation logic expands, the private-core repository boundary must be resolved. Until then, sensitive scoring weights, owner-specific allocation heuristics, confidential provider mappings, production datasets and commercial optimizer implementation must not be added to the public repository.

Current migration gate:

`PRIVATE_CORE_REPOSITORY_REQUIRED_BEFORE_SENSITIVE_OPTIMIZER_IMPLEMENTATION`.

## Immediate active task — Task 003 / Day 3

GitHub issue: `#4 — Profit Engine Task 003 — Data foundation + private-core boundary`

Canonical contract:

`profit-engine/tasks/TASK-003-DATA-FOUNDATION-PRIVATE-CORE-BOUNDARY.md`

Executor: Codex.
Acceptance authority: Central Brain.

Task 003 scope:
- explicit private-core boundary;
- versioned PostgreSQL schema foundation;
- immutable raw snapshot contract and local development raw store;
- provider-neutral relational/raw/secret/health/audit interfaces;
- data-quality primitives and `DATA_QUALITY_HOLD`;
- minimal portable collector/deployment structure;
- rerun provider doctor only if secure credentials become available;
- tests, secret scan and committed evidence.

No production Dilivox changes, Direct writes, campaign/budget mutations, spend, real raw provider data in Git, or paid Cloud resource creation are authorized in Task 003.

## Current launch day

Day 3 of `HARD_12_DAY_LAUNCH_PLAN.md` is active.

Provider credential certification continues in parallel.

## Expected Task 004 boundary

Day 4 target after Task 003 acceptance:
- Direct read collector;
- Metrica read collector;
- YAN statistics collector;
- idempotent ingestion-run orchestration;
- raw snapshot persistence;
- normalized provider-neutral facts;
- freshness/retry/error handling;
- source fidelity checks;
- no Direct writes.

If provider tokens are still unavailable, collector implementations and fixture/source-contract validation continue while live provider execution remains externally blocked.

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
