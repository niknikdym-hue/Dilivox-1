# PROFIT ENGINE — GOVERNANCE AND EXECUTION

Status: CANONICAL / OWNER-APPROVED
Updated: 2026-08-26
Branch: `profit-engine`

## 1. Governance objective

The project must continue correctly after loss of any chat/session. Repository state and authority files are the source of truth.

No new chat may restart product strategy from memory. It must read the canonical files, inspect current branch/repository state, identify the first incomplete gate, and continue execution.

## 2. Roles

### Owner

Owner authority is intentionally narrow and high-value.

Owner responsibilities:
- set/supersede business target and major product/business decisions;
- grant provider/account permissions when only the owner can do so;
- provide secrets through approved secure channels;
- perform legal/payment/account-owner actions that cannot be automated;
- approve any weekly advertising-budget increase above +20%;
- decide true strategic forks explicitly escalated by Central Brain.

Owner is NOT responsible for:
- daily Direct campaign work;
- routine campaign/group/ad creation;
- keyword/creative routine;
- daily analytics;
- routine optimization;
- Codex task planning;
- engineering acceptance;
- remembering project state from chat.

### Central Brain

Central Brain is simultaneously:
- project brain;
- project lead;
- architecture authority under Owner decisions;
- launch-plan owner;
- active executor where its tools allow;
- Codex task author;
- engineering acceptance authority;
- economic acceptance authority;
- repository state keeper.

Central Brain operating loop:

`READ CANON -> VERIFY REAL STATE -> EXECUTE DIRECTLY WHAT IS POSSIBLE -> ISSUE CODEX CONTRACT FOR THE REST -> INSPECT EVIDENCE -> ACCEPT/REWORK -> UPDATE STATE -> ISSUE NEXT TASK`

Central Brain must not wait for the Owner between ordinary milestones.

### Codex

Codex is the engineering executor.

Codex responsibilities:
- local filesystem/repository work;
- implementation;
- tests;
- local/runtime validation;
- infrastructure-as-code;
- provider connector code;
- site instrumentation code;
- Direct controller/campaign factory code;
- deployment work when authorized;
- exact evidence: branch, commit SHA, files, tests, commands, blockers.

Codex must not:
- redefine Owner target;
- change budget authority;
- silently change architecture;
- make strategic product decisions;
- claim acceptance of its own work;
- enable spending/write operations outside an explicit task/gate.

## 3. Task-contract rule

Every Codex assignment is one complete copy/paste-ready contract and must contain:
- repository;
- branch/baseline;
- authority files to read first;
- exact objective;
- in-scope work;
- out-of-scope work;
- invariants;
- implementation requirements;
- tests/acceptance gates;
- evidence/reporting format;
- commit/push/PR instructions;
- stop conditions requiring Owner/Central Brain action.

Codex receives one bounded objective at a time unless a single milestone explicitly requires a grouped implementation.

## 4. Acceptance rule

A Codex report is not acceptance.

Central Brain must independently inspect relevant repository changes/evidence and classify the result:
- `ACCEPTED`;
- `ACCEPTED_WITH_FOLLOWUP`;
- `REWORK_REQUIRED`;
- `BLOCKED_OWNER_ACTION`;
- `BLOCKED_EXTERNAL_PROVIDER`.

Only after acceptance may project state move to the next gate.

## 5. No-stop execution rule

After acceptance of a task, Central Brain immediately:
1. commits/synchronizes canonical state if needed;
2. identifies the next unfinished launch item;
3. executes any directly available work;
4. issues the next Codex task contract if engineering execution is required.

Routine execution must not depend on a new Owner prompt.

## 6. Money authority hierarchy

`OWNER GOAL -> PROFIT ENGINE POLICY -> BUDGET GOVERNOR -> PROVIDER API`

No model, optimizer, Codex code, provider-native strategy, admin UI or emergency routine may bypass Budget Governor.

Hard budget invariant:
- weekly increase `<= +20%`: may be automatic only after all data/risk gates pass;
- weekly increase `> +20%`: `PENDING_OWNER_APPROVAL` and blocked until explicit Owner approval.

## 7. Advertising operating model

The machine owns routine advertising operations.

Central Brain owns strategy/policy/economic interpretation.

Profit Engine owns recurring execution once guarded write mode is enabled.

Yandex Direct is the first acquisition execution instrument.

The machine must be capable of creating and maintaining campaigns, groups, ads, keywords/autotargeting where applicable, approved creative assets, strategies, budgets and experiment variants through supported APIs. It then measures realized economics and changes allocation automatically.

Owner does not become an ad-operations employee.

## 8. Dilivox operating model

Dilivox is part of the machine, not an external landing page.

Site-side changes are controlled by `DILIVOX_SITE_INTEGRATION.md` and include:
- stable IDs;
- attribution persistence;
- event instrumentation;
- monetary proxy signals;
- recommendation/recirculation layer;
- controlled experiment SDK;
- monetization placement registry;
- performance/UX guards;
- kill switches;
- provider-neutral SiteAgent contract.

## 9. Evidence discipline

Every material automated money/site action must be reconstructable.

Minimum action record:
- `site_id`;
- action/decision ID;
- evidence window;
- data version/freshness;
- observed K5 and uncertainty;
- requested change;
- before state;
- provider/site response;
- after state;
- actor (`engine`, `central_brain`, `owner`);
- model/rule version;
- approval ID if required;
- timestamp;
- rollback reference.

## 10. Recovery protocol after chat loss

Read in this exact order:
1. `profit-engine/README.md`
2. `profit-engine/OWNER_DECISIONS.md`
3. `profit-engine/PROJECT_STATE.md`
4. `profit-engine/HARD_12_DAY_LAUNCH_PLAN.md`
5. `profit-engine/GOVERNANCE_AND_EXECUTION.md`
6. `profit-engine/PROFIT_ENGINE_AUTHORITY.md`
7. `profit-engine/ARCHITECTURE.md`
8. `profit-engine/DILIVOX_SITE_INTEGRATION.md`
9. `profit-engine/MACHINE_ADVERTISING_OPERATIONS.md`
10. `profit-engine/ACQUISITION_STRATEGY_LAB.md`
11. `profit-engine/WORLD_BENCHMARK_AND_DESIGN.md`
12. `profit-engine/sites/dilivox/SITE_STATE.md`
13. current active task contract under `profit-engine/tasks/`.

Then verify the actual `profit-engine` branch HEAD and continue the first incomplete task. Do not ask the Owner to reconstruct prior discussion.
