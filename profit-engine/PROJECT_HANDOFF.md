# PROFIT ENGINE — CANONICAL PROJECT HANDOFF

Status: ACTIVE / READ FIRST AFTER CONTEXT LOSS
Updated: 2026-08-26
Branch: `profit-engine`
Repository: `niknikdym-hue/Dilivox-1`

## 1. What this project is

DILIVOX PROFIT ENGINE is an owner-controlled, profit-first, multi-site economic control system.

First site: `site_id=dilivox` / `dilivox.ru`.
First acquisition provider: Yandex Direct.
First monetization provider: YAN/RСЯ advertising blocks on Dilivox.

Primary launch economic target:

`1 RUB Yandex Direct spend -> 5 RUB YAN revenue attributable to the acquired Dilivox audience`.

This is the optimization target, not a fabricated current result.

## 2. Operating doctrine

`PROTECT CAPITAL -> MEASURE MONEY -> STOP LOSSES -> FIND PROFIT -> SCALE PROFIT -> REPEAT`

The project is a hard machine for making money. Analytics, AI, dashboards and experiments are tools.

## 3. Yandex role

Yandex is an execution/data instrument, not the project owner or goal setter.

- Direct = acquisition and native bidding tool;
- Metrica = attribution/behavior/monetization measurement;
- YAN = monetization provider #1;
- Yandex Cloud = preferred initial infrastructure.

Profit Engine defines the Owner-level cross-system economics and uses provider-native algorithms when they help the target.

## 4. Machine advertising rule

Routine advertising operations are machine-operated.

After guarded writes are enabled, Profit Engine must be capable of creating and maintaining campaigns, groups, ads, keywords/autotargeting where applicable, images/assets, settings, strategies, budgets and experiments through supported APIs.

Owner is not the routine Direct operator.

## 5. Dilivox is part of the machine

Dilivox is the first SiteAgent/reference implementation, not merely a landing destination.

Launch-critical site work includes:
- stable content IDs;
- acquisition attribution persistence;
- first-party event taxonomy;
- monetization placement registry;
- proxy/value signals;
- experiment SDK;
- recirculation/next-story optimization;
- return-value measurement;
- performance/UX safeguards;
- kill switches/fallbacks.

Read `DILIVOX_SITE_INTEGRATION.md` for full scope.

## 6. Budget authority

Automatic weekly budget increase up to +20% may occur only when all guards pass.

Any weekly increase above +20% is blocked as `PENDING_OWNER_APPROVAL` until explicit Owner approval.

This cannot be bypassed.

## 7. Governance

Central Brain is project brain + lead + active executor + Codex task author + acceptance authority.

Codex is engineering executor.

Owner is involved only for true Owner actions/approvals.

Central Brain loop:

`verify state -> execute directly -> issue Codex task -> inspect evidence -> accept/rework -> update state -> issue next task`.

No routine waiting for a new Owner prompt.

## 8. Hard schedule

Canonical launch schedule: `HARD_12_DAY_LAUNCH_PLAN.md`.

Target: guarded-production closed loop by Day 12, excluding unavoidable external-provider waiting time.

Stable proof of K5>=5.0 requires subsequent live evidence; never fabricate it to meet a date.

## 9. Read order

On a new chat/session, read in this order:

1. `profit-engine/README.md`
2. `profit-engine/PROJECT_HANDOFF.md`
3. `profit-engine/OWNER_DECISIONS.md`
4. `profit-engine/PROJECT_STATE.md`
5. `profit-engine/HARD_12_DAY_LAUNCH_PLAN.md`
6. `profit-engine/GOVERNANCE_AND_EXECUTION.md`
7. `profit-engine/PROFIT_ENGINE_AUTHORITY.md`
8. `profit-engine/ARCHITECTURE.md`
9. `profit-engine/DILIVOX_SITE_INTEGRATION.md`
10. `profit-engine/MACHINE_ADVERTISING_OPERATIONS.md`
11. `profit-engine/ACQUISITION_STRATEGY_LAB.md`
12. `profit-engine/WORLD_BEST_PRACTICES_ADOPTION_2026.md`
13. `profit-engine/SECURITY_AND_ACCESS.md`
14. `profit-engine/ACCESS_SETUP_CHECKLIST.md`
15. `profit-engine/sites/dilivox/SITE_STATE.md`
16. active task contract under `profit-engine/tasks/`.

Then verify actual branch HEAD and continue the first incomplete gate.

## 10. Known access state at handoff

Repository evidence before this handoff states:
- technical Yandex identity exists and is verified;
- Direct managing-account read access is confirmed;
- Metrica counter access has been granted but monetization visibility still needs technical verification;
- YAN Partner Assistant access to Dilivox/statistics UI is granted;
- OAuth application Profit Engine has `direct:api` and `metrika:read` scopes configured;
- user reported on 2026-08-26 that Direct programmatic access is open; repository state must be technically verified with an actual authenticated API read before marking API-read gate complete;
- write-capable Direct access remains intentionally disabled until guarded-autopilot gate.

Never put tokens/secrets in GitHub or chat.

## 11. Immediate execution

The immediate task is local bootstrap + M0 verification.

Canonical Codex contract:
`profit-engine/tasks/TASK-001-LOCAL-BOOTSTRAP-M0.md`.

After Codex returns evidence, Central Brain must accept/rework it and immediately issue Task 002 from the Day 2/Data-readiness scope.

## 12. Definition of successful first launch

The project is launched when it can execute a bounded, auditable, guarded loop:

`Direct machine action -> real Dilivox traffic -> Dilivox behavior -> YAN revenue -> reconciliation -> K5 decision -> next machine action`.

A dashboard alone is not launch.
A connector alone is not launch.
An optimizer that cannot act is not launch.
A Direct automation without Dilivox money attribution is not launch.
