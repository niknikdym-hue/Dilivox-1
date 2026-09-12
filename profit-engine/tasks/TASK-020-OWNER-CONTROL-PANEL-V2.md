# TASK 020 — DILIVOX OWNER CONTROL PANEL V2

Status: READY FOR BOUNDED DEVELOPMENT
Executor: Codex development-only under Central Brain acceptance
Depends on:
- existing `profit_engine_runtime/control_panel.py`;
- `DILIVOX_OWNER_CONTROL_PANEL_REQUIREMENTS.md`;
- `ADAPTIVE_FUNNEL_EXECUTION_PROJECT.md`.
May begin before AF-0 live acceptance: YES, read-only/offline project projection only

## Objective

Extend the existing local `Profit Engine.app` into the single whole-project Owner Control surface, borrowing Eksamio's useful project-control UI principles while preserving DILIVOX's money-first operation and existing panel.

Do not create a second app.

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

### Slice 3 — UI views

Add to the existing panel shell:
1. Profit;
2. Critical Path;
3. Adaptive Funnel;
4. Content;
5. Providers & Compliance;
6. Owner Gates;
7. History.

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

### Slice 7 — development activity

Optional read-only block for Codex development state:
- bounded task;
- branch/PR/SHA;
- CI/check result;
- expected acceptance evidence.

Codex activity must be visually separate from product completion.

## Controls

First V2 remains conservative.

Allowed:
- refresh data/status;
- filter/search tasks;
- open exact GitHub task/PR/workflow/evidence;
- show Owner Gate instructions;
- safe local Adaptive Funnel kill/fallback control only if backed by an accepted runtime contract.

Not allowed merely because V2 exists:
- Direct provider mutations from ordinary panel buttons;
- budget changes;
- Tilda publication;
- merge/deploy authority;
- production AI execution.

Future Start/Pause/Resume/Stop development controls may be added only as a separate accepted slice and may dispatch bounded development workflows only.

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
14. Tests/CI pass.

Terminal state:
`DILIVOX_OWNER_CONTROL_V2_CODE_READY`.

Live/operational acceptance is separate from code readiness and requires real project/provider evidence feeds.
