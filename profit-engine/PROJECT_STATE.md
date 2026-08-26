# PROFIT ENGINE — PROJECT STATE

Status: IMPLEMENTATION STARTED / DAY 1 — LOCAL BOOTSTRAP + M0
Updated: 2026-08-26
Canonical branch: `profit-engine`

## Current objective

Launch a guarded-production, machine-operated, multi-site Profit Engine whose first closed loop is:

`Yandex Direct -> Dilivox -> user behavior -> YAN revenue -> attribution/reconciliation -> Profit Engine -> guarded Direct + Dilivox actions -> measured outcome`.

First production site: Dilivox (`site_id=dilivox`).

Primary launch target:

`1 RUB Yandex Direct spend -> 5 RUB YAN/RСЯ advertising revenue attributable to the acquired Dilivox audience`.

This is the optimization target. It is not a claimed current result.

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

## Canonical implementation package now present

- `README.md`
- `PROJECT_HANDOFF.md`
- `OWNER_DECISIONS.md`
- `PROFIT_ENGINE_AUTHORITY.md`
- `GOVERNANCE_AND_EXECUTION.md`
- `HARD_12_DAY_LAUNCH_PLAN.md`
- `ARCHITECTURE.md`
- `IMPLEMENTATION_PLAN.md`
- `DILIVOX_SITE_INTEGRATION.md`
- `MACHINE_ADVERTISING_OPERATIONS.md`
- `ACQUISITION_STRATEGY_LAB.md`
- `WORLD_BENCHMARK_AND_DESIGN.md`
- `WORLD_BEST_PRACTICES_ADOPTION_2026.md`
- `YANDEX_CLOUD_ARCHITECTURE.md`
- `SECURITY_AND_ACCESS.md`
- `ACCESS_SETUP_CHECKLIST.md`
- `OAUTH_API_SETUP.md`
- `SITE_ONBOARDING.md`
- `sites/dilivox/SITE_STATE.md`
- `tasks/TASK-001-LOCAL-BOOTSTRAP-M0.md`

## Verified/known state before Task 001

From repository evidence and Owner updates:
- dedicated technical Yandex identity exists and is verified;
- Direct managing-account `Reading` access was confirmed;
- Metrica counter access was granted;
- YAN Partner Assistant access for Dilivox/statistics UI was granted;
- OAuth application `Profit Engine` exists with `direct:api` and `metrika:read` scopes;
- Direct sandbox creation is unavailable in the current UI;
- Owner reported on 2026-08-26 that Direct programmatic access is open and the account UI shows 32,000 API points for legacy v4/Live 4;
- this indicates provider programmatic permission, but production readiness still requires an actual authenticated API read against the current intended Direct API path;
- Direct write access remains intentionally disabled until guarded-autopilot gates pass;
- local Profit Engine working folder on the Owner Mac has not yet been certified by Codex in this workstream.

## Immediate active task

`profit-engine/tasks/TASK-001-LOCAL-BOOTSTRAP-M0.md`

Executor: Codex.
Acceptance authority: Central Brain.

Task 001 outcome:
- create/verify canonical local clone under preferred path `~/Documents/Profit Engine/Dilivox-1`;
- checkout/sync `profit-engine`;
- map the actual Dilivox implementation surface;
- classify current analytics/YAN/attribution implementation;
- safely classify provider credential availability;
- perform only safe read-only provider checks where credentials already exist;
- produce evidence for Task 002.

## Current launch day

Day 1 of `HARD_12_DAY_LAUNCH_PLAN.md` is active.

The engineering schedule continues in parallel around external-provider blockers where possible.

## Next task after Task 001 acceptance

Task 002 boundary is Day 2:
- certify Direct/Metrica/YAN read access with real API calls;
- map provider IDs to `site_id=dilivox`;
- capture current weekly Direct budget baseline;
- verify Metrica YAN monetization visibility;
- produce the exact missing-access list, if any.

Central Brain must issue Task 002 immediately after Task 001 acceptance without restarting architecture discussion.

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

Read `PROJECT_HANDOFF.md` and follow its exact read order. Verify actual `profit-engine` branch HEAD and continue the first incomplete task. Never ask the Owner to reconstruct project history from chat.
