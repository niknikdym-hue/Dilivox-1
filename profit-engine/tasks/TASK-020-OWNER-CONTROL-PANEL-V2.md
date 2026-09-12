# TASK 020 — DILIVOX OWNER CONTROL PANEL V2

Status: READY FOR BOUNDED DEVELOPMENT / OWNER DUAL-WINDOW UPDATE APPLIES
Executor: Codex development-only under Central Brain acceptance
Depends on:
- existing `profit_engine_runtime/control_panel.py`;
- `DILIVOX_OWNER_CONTROL_PANEL_REQUIREMENTS.md`;
- `ADAPTIVE_FUNNEL_EXECUTION_PROJECT.md`.
May begin before AF-0 live acceptance: YES, read-only/offline project projection only

## Objective

Extend the existing local `Profit Engine.app` into one application with one localhost backend and two separate top-level windows: `/profit` for the money-first `Пульт прибыли`, and `/project` for `DILIVOX — Управление проектом`.

Do not create a second app, backend or task database. GitHub remains durable truth/execution backend, while normal Owner work happens inside Project Control.

## Existing surface to preserve

Current panel already provides:
- period selection;
- K5;
- Direct spend;
- YAN revenue;
- primary owner advice;
- campaign economics;
- three profit levers;
- Manual Search Profit Control status;
- technical diagnostics;
- localhost/private/no provider-write rendering.

These must not regress.

## Required implementation slices

### Slice 1 — machine-readable whole-project board

Create a deterministic projection with stages:
- A Measurement & Compliance;
- B Profit Engine Live Control;
- C Adaptive Funnel MVP;
- D Content Scale;
- E Commercial Scale / Expansion.

The board must derive from canonical task/state documents and have tests for unique task IDs, stage membership, dependencies and status vocabulary.

No second mutable task database.

### Slice 2 — project status model

Extend the panel snapshot with bounded project facts:
- current stage/milestone;
- critical blockers;
- Owner Gates;
- task status/target states;
- branch/PR/SHA/check refs where admitted;
- AF-0..AF-4 status;
- content gate/count;
- source freshness/conflict state.

### Slice 3 — dual-window UI views

Preserve the existing Profit screen as a separate money-only window. Add to the Project window:
1. Critical Path;
2. Whole Project;
3. Adaptive Funnel;
4. Content;
5. Providers & Compliance;
6. Owner Gates;
7. Development;
8. History.

Responsive/mobile behavior must remain usable.

### Slice 4 — status truth semantics

Visually distinguish:
- `DESIGNED`;
- `CODE_READY`;
- `LIVE_PROVIDER_VERIFIED`;
- `LIVE_SITE_VERIFIED`;
- `ECONOMICALLY_PROVEN`;
- `BLOCKED_EXTERNAL`;
- `BLOCKED_DATA`;
- `OWNER_GATE`;
- `DONE`.

CI green may never automatically become live/economic proof.

### Slice 5 — Adaptive Funnel economics

Consume Task 019 aggregate snapshot when available and show:
- control/treatment metrics;
- incremental revenue;
- feature cost;
- FEATURE_ROI;
- evidence state;
- TEST/KEEP/HOLD/KILL/SCALE_ALLOWED;
- policy/experiment version;
- kill/fallback state.

Before Task 019 data exists, render honest `NO_DATA / NOT_YET_PROVEN`, not zeros that look economic.

### Slice 6 — Content scale view

Show:
- catalog count/gate;
- cluster/series distribution;
- current wave;
- dead/low-utilization inventory when evidence exists;
- wave cost/revenue/ROI state when evidence exists;
- next-wave recommendation.

### Slice 7 — development activity and controls

Required in-panel development state:
- bounded task;
- branch/PR/SHA;
- CI/check result;
- expected acceptance evidence.

Codex activity must be visually separate from product completion. Add exact bounded controls for refresh/start/start-package/pause/resume/stop via the accepted Task 021 control plane.

## Controls

Required:
- start selected exact canonical task;
- start canonical next Critical Path task without inventing priority;
- sequential bounded package of 1-5 compatible tasks;
- pause after current bounded step;
- resume only from exact checkpoint;
- stop exact active run/package;
- refresh GitHub/runtime/project truth;
- quality-first route preview with upward-only Owner override.

The browser never receives GitHub/OpenAI credentials and cannot choose arbitrary repository/workflow/branch/shell commands.

Still not allowed merely because Project Control exists:
- Direct provider mutations from ordinary panel buttons;
- budget changes;
- Tilda publication;
- automatic merge/deploy authority;
- production AI execution.

Owner Gate decisions are exact-scope durable evidence and never grant generic production authority.

## Source conflict behavior

If canonical project docs, GitHub facts and live evidence disagree:
- show `STALE/CONFLICT`;
- identify conflicting sources;
- do not upgrade status;
- do not recommend scaling based on conflicted evidence.

Cached data is non-authoritative.

## Safety invariants

- localhost/private by default;
- no secrets in HTML/JSON/browser storage;
- panel failure cannot affect dilivox.ru;
- refresh/render performs no provider mutation;
- no second task database;
- no duplicate Owner app;
- no raw visitor event/PII needed for aggregate panel;
- no production Codex role.

## Acceptance criteria

1. Existing Profit screen regression tests remain green.
2. Stages A-E are visible and complete against the board projection.
3. Critical Path is dependency-aware.
4. AF-0..AF-4 states appear without inventing completion.
5. Content gate is visible.
6. Owner Gates contains only real gated actions.
7. Code/live/economic truth states cannot collapse into one generic Done.
8. `STALE/CONFLICT` is tested.
9. Panel can run with provider network unavailable using honest stale/no-data states.
10. Panel outage has zero effect on public site/runtime.
11. No provider write endpoint is introduced by this task.
12. Codex remains development-only.
13. UI works on desktop and narrow/mobile layout.
14. tests/CI pass;
15. one app/one backend opens distinct Profit and Project windows without duplicate backend processes;
16. full bounded controls pass mock adapter/security/idempotency/package tests;
17. free G0 end-to-end control smoke passes with zero OpenAI calls and unchanged `DEV_AI_COST`;
18. exact-head CI is green and one Draft PR awaits Central Brain acceptance.

Terminal state:
`DILIVOX_OWNER_CONTROL_FULL_CODE_READY`.

Live/operational acceptance is separate from code readiness and requires real project/provider evidence feeds.
