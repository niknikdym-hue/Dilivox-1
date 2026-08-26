# PROFIT ENGINE — CANONICAL PROJECT ENTRY

Status: ACTIVE / IMPLEMENTATION
Updated: 2026-08-26
Repository: `niknikdym-hue/Dilivox-1`
Canonical branch: `profit-engine`
Initial site: `https://dilivox.ru`

## Purpose

`profit-engine/` is the canonical source of truth for an owner-controlled, profit-first, multi-site advertising economics system.

Dilivox is the first full reference implementation, not the architectural boundary.

## North-star objective

Initial Dilivox target:

`1 RUB Yandex Direct spend -> 5 RUB YAN/RСЯ advertising revenue attributable to the acquired Dilivox audience`.

Equivalent target: `K5 >= 5.0` / `YAN ROAS = 5.0` / `DRR = 20%` for the launch revenue loop.

This is a target to optimize toward, not a fabricated current result.

## Profit-first doctrine

`PROTECT CAPITAL -> MEASURE MONEY -> STOP LOSSES -> FIND PROFIT -> SCALE PROFIT -> REPEAT`

The system is not a dashboard. Routine advertising operations are intended to be machine-operated.

## First closed-loop ecosystem

`Yandex Direct -> Dilivox -> Metrica/YAN -> Profit Engine -> guarded Direct + Dilivox action -> measured money`.

Yandex is a powerful execution/data instrument used to achieve the Owner's objective:
- Direct = acquisition/campaign/bidding instrument;
- Metrica = attribution/behavior/monetization measurement;
- YAN/RСЯ = monetization provider #1;
- Yandex Cloud = preferred initial infrastructure.

The shared Profit Engine economic logic remains owner-controlled and extensible to future sites/providers.

## Hard Owner budget rule

Automatic weekly budget increase is allowed up to +20% only when all guards pass.

Any weekly budget increase above +20% MUST remain `PENDING_OWNER_APPROVAL` until the Owner explicitly approves it.

No optimizer, provider strategy or admin automation may bypass this rule.

## Governance

Central Brain:
- leads the project;
- executes all work available through its tools;
- writes exact Codex engineering contracts;
- independently accepts/rejects Codex evidence;
- updates canonical state;
- immediately advances to the next task.

Codex:
- engineering/local/deployment executor;
- does not change Owner authority or project strategy.

Owner:
- strategic/authority layer only;
- is not the routine Direct operator.

See `GOVERNANCE_AND_EXECUTION.md`.

## Hard schedule

Guarded-production engineering target: 12 calendar days under `HARD_12_DAY_LAUNCH_PLAN.md`, excluding unavoidable external-provider waiting time.

Stable proof of K5>=5.0 follows from real reconciled money, typically requiring additional live observation/optimization; it is never fabricated to meet a date.

## Canonical read order after any chat/context loss

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
13. `profit-engine/WORLD_BENCHMARK_AND_DESIGN.md`
14. `profit-engine/YANDEX_CLOUD_ARCHITECTURE.md`
15. `profit-engine/SECURITY_AND_ACCESS.md`
16. `profit-engine/ACCESS_SETUP_CHECKLIST.md`
17. `profit-engine/OAUTH_API_SETUP.md`
18. `profit-engine/SITE_ONBOARDING.md`
19. `profit-engine/sites/dilivox/SITE_STATE.md`
20. active task contract under `profit-engine/tasks/`.

Then verify actual `profit-engine` branch HEAD and continue the first incomplete task from `PROJECT_STATE.md`. Do not re-plan from chat memory.

## Current active task

`profit-engine/tasks/TASK-001-LOCAL-BOOTSTRAP-M0.md`

This task creates/verifies the Owner's local Mac clone under the preferred path:

`~/Documents/Profit Engine/Dilivox-1`

and performs the first implementation/M0 inventory in read-only mode.

## Secret handling

NEVER commit OAuth tokens, passwords, API secrets, account identifiers not intended to be public, or production credentials.

Production secrets belong in Yandex Lockbox or an equivalent secure secret manager. Repository files contain secret names/contracts only.
