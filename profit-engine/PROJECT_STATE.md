# PROFIT ENGINE — PROJECT STATE

Status: IMPLEMENTATION STARTED / DAY 2 — READ-ONLY PROVIDER + DATA FOUNDATION
Updated: 2026-08-27
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
- Local workspaces are separated: existing site workspace `~/Documents/New project/Dilivox` remains independent; canonical Profit Engine workspace is `~/Documents/New project/Profit Engine/Dilivox-1`.

## Day 1 / Task 001 acceptance

Central Brain decision: `ACCEPTED_SUBSTANTIVELY / REPOSITORY_SYNC_REQUIRED`.

Codex reported:
- local workspace exists at `/Users/elenadymova/Documents/New project/Profit Engine/Dilivox-1`;
- branch `profit-engine`;
- accepted local evidence commit `dd0f3025335ed174077e9e84b568baa58e21120a`;
- old origin baseline at execution time `51eb6be7d7fe6cc06d795d33ae2a64c0c965010c`;
- clean worktree;
- existing Dilivox site workspace inspected read-only and not modified;
- Metrica hooks/goals, YAN placement surfaces and current tracking gaps inventoried;
- UTM/`yclid` persistence, stable immutable content IDs and Profit Engine first-party ingestion are not yet implemented;
- no safe Direct/Metrica OAuth token or YAN Statistics API token was available;
- no provider writes/spend occurred;
- no secrets were exposed.

Task 001 evidence commit remains to be synchronized to current origin because Central Brain advanced `origin/profit-engine` after the Codex local baseline. Task 002 Step 0 owns this fast-forward-safe synchronization. Issue #2 remains open only until that sync is confirmed.

## Central Brain direct implementation after Task 001

Central Brain added a root `.gitignore` to reduce secret/local-state risk before further implementation.

Current safety rule:
- no secret values or private provider mappings in Git;
- public repo may contain generic contracts/examples only;
- competitively sensitive production/scoring implementation must not be expanded in the public repo without resolving the private-core boundary described in `SECURITY_AND_ACCESS.md`.

## Current provider/access state

Known from authority + Task 001 report:
- dedicated technical Yandex identity exists and is verified;
- Direct managing-account `Reading` access is confirmed in UI;
- Metrica counter access was granted in UI;
- YAN Partner Assistant access for Dilivox/statistics UI was granted;
- OAuth application `Profit Engine` exists with `direct:api` and `metrika:read` scopes;
- Owner reported programmatic access open in Direct UI and legacy API points visible;
- actual Direct API v5 readiness is NOT yet certified because no OAuth token was safely available to Codex;
- Metrica API read is NOT yet certified for the same reason;
- YAN Partner Statistics API read is NOT yet certified because the statistics-specific token was unavailable;
- Direct write access remains intentionally disabled until guarded-autopilot gates pass.

## Immediate active task — Task 002 / Day 2

Canonical contract:

`profit-engine/tasks/TASK-002-READ-FOUNDATION-PROVIDER-CERTIFICATION.md`

Executor: Codex.
Acceptance authority: Central Brain.

Task 002 objectives:
1. safely rebase/cherry-pick and push accepted Task 001 evidence onto current `origin/profit-engine` without force push;
2. verify root `.gitignore`/secret hygiene;
3. create minimal provider-neutral READ_ONLY runtime foundation;
4. create public example/private local configuration boundary;
5. implement Direct/Metrica/YAN diagnostic read clients with redacted logging and fixture tests;
6. perform live READ_ONLY provider checks for every securely available credential;
7. isolate absent credentials as exact Owner/provider actions without blocking engineering work;
8. commit/push Task 002 evidence.

No production Dilivox changes, campaign writes, budget changes or spend are authorized in Task 002.

## Current launch day

Day 2 of `HARD_12_DAY_LAUNCH_PLAN.md` is active.

External token/UI dependencies are treated as `BLOCKED_EXTERNAL_PROVIDER_CREDENTIAL` while parallel engineering foundation continues.

## Expected Task 003 boundary after Task 002 acceptance

Primary Day 3 scope remains minimal Cloud/data foundation:
- decide/confirm private-core repository boundary before competitively sensitive production code expands;
- establish minimal runtime deployment structure;
- secret-manager contract / Lockbox integration when Cloud access is available;
- PostgreSQL/data schema foundation;
- immutable raw snapshot contract;
- logging/health checks;
- no Direct writes.

If provider read tokens remain the sole blocker, provider certification continues in parallel and does not justify idling the engineering schedule.

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
