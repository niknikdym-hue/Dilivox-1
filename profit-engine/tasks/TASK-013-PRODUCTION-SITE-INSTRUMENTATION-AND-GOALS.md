# TASK 013 — DILIVOX PRODUCTION SITE INSTRUMENTATION + METRICA GOALS

Status: P0 / IMPLEMENTATION ACTIVE
Owner approval: inherited from `OWNER_APPROVAL_DILIVOX_SITE_WORKSTREAM.md`
Current executor: Central Brain

## Objective

Close the gap between accepted site-side code and the real `dilivox.ru` production site.

A Task-005/006 artifact in Git is not production instrumentation. Task 013 is complete only after live Tilda publication and provider evidence.

## Scope

1. canonical five-goal Metrica registry;
2. live goal audit and missing-only guarded creation;
3. production-safe `reachGoal` bridge using existing Dilivox hooks;
4. production publication of accepted SiteAgent/event layer;
5. controlled Tilda publication of the goal bridge;
6. live validation in Metrica;
7. no YAN ad-layout mutation in this task;
8. first-party event dispatch remains disabled until Task 015 endpoint is accepted.

## Canonical goals

Counter `110349067`:

- `pe_story_progress_75`;
- `pe_version_selected`;
- `pe_story_completed`;
- `pe_next_story_clicked`;
- `pe_return_visit`.

They are proxy goals, not K5 itself. `native_bidding_eligible=false` until revenue validation.

## Required artifacts

- `sites/dilivox/metrica-goals.json`;
- `runtime/profit_engine_runtime/metrica_goals_cli.py`;
- `sites/dilivox/tilda/dilivox-event-layer-task006.js`;
- `sites/dilivox/tilda/dilivox-metrica-goals-v1.js`;
- exact production publication package/instructions;
- live validation evidence.

## Metrica write safety

Goal apply may only:

- create a missing exact canonical goal;
- never update/delete an existing goal;
- stop if a canonical identifier is duplicated or wrong-type;
- make no blind retry;
- read back after apply and require PASS.

## Site publication safety

Before publication:

- CI green;
- JS tests green;
- no `Ya.Context` mutation in new goal bridge;
- no change to existing YAN block IDs/layout;
- event dispatch remains disabled;
- kill switches documented.

After publication validate:

- story navigation remains functional;
- version choice/reveal remains functional;
- YAN blocks still render normally;
- `ProfitEngineEvents` exists;
- `ProfitEngineMetricaGoals` exists;
- each canonical event reaches Metrica on a bounded real interaction test;
- no duplicate storm;
- no console/network errors caused by Profit Engine.

## Rollback

- set `window.PROFIT_ENGINE_METRICA_GOALS_KILL=true` for goal bridge emergency stop;
- retain Task-006 event-layer kill/dispatch-disabled behavior;
- remove the two injected production scripts and republish if needed.

## Acceptance

`TASK_013_PRODUCTION_SITE_INSTRUMENTATION_ACCEPTED` only after live production evidence. Code-ready is not enough.
