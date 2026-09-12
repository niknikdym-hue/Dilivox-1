# DILIVOX OWNER CONTROL — WHOLE-PROJECT PANEL REQUIREMENTS

Status: IMPLEMENTATION CONTRACT / SINGLE-PANEL EXTENSION
Date: 2026-09-12
Repository: `niknikdym-hue/Dilivox-1`
Branch: `profit-engine`
Existing implementation to extend: `profit-engine/runtime/profit_engine_runtime/control_panel.py`
Authority: `profit-engine/PROFIT_ENGINE_AUTHORITY.md`
Execution project: `profit-engine/ADAPTIVE_FUNNEL_EXECUTION_PROJECT.md`

## 1. PURPOSE

Extend the existing local `Profit Engine.app` into the Owner's single control surface for the whole DILIVOX Profit Engine program.

Do not create a second owner application or a second project/task database.

The panel must answer at a glance:
1. Are we making money and what is current K5?
2. What exact milestone are we trying to reach next?
3. What is code-ready versus live-site/provider verified versus economically proven?
4. What is blocking the next milestone?
5. What is Adaptive Funnel doing and can it be killed safely?
6. Which content clusters/series are earning or wasting money?
7. What actually requires Owner action now?
8. What development work is Codex doing/has completed, without confusing agent activity with product progress?

## 2. SINGLE-PANEL INVARIANT

The existing `control_panel.py` / `Profit Engine.app` remains the shell.

New whole-project views must be added to that shell or to modules imported by it.

Forbidden:
- second localhost owner app for Adaptive Funnel;
- second task database that can diverge from GitHub/canonical docs;
- browser-stored optimistic project truth;
- panel availability becoming a dependency of dilivox.ru;
- panel rendering causing provider writes.

## 3. SOURCE-OF-TRUTH MODEL

### Project semantics
Read from canonical repository documents and task specs:
- `PROFIT_ENGINE_AUTHORITY.md`;
- `PROJECT_STATE.md`;
- `P0_SYSTEM_COMPLETION_BOARD.md`;
- `ADAPTIVE_FUNNEL_EXECUTION_PROJECT.md`;
- `tasks/TASK-*.md` and machine-readable projection derived from them.

### Repository facts
Read from GitHub where available:
- branch/head SHA;
- PR state;
- exact commit;
- CI/check results;
- accepted evidence references.

### Runtime/provider facts
Read only from admitted evidence/snapshots:
- Direct;
- Metrica;
- YAN;
- first-party event endpoint;
- site live verification;
- reconciled money evidence.

A source conflict must render `STALE/CONFLICT` or an equivalent explicit hold. The panel must not silently choose the optimistic source.

## 4. TOP-LEVEL PROJECT RAIL

Persistent stages:

### A — Measurement & Compliance
Includes:
- production instrumentation;
- money reconciliation;
- Privacy v2 / first-party endpoint;
- YAN compliance clarification;
- data-quality truth.

### B — Profit Engine Live Control
Includes:
- guarded Direct controller;
- manual Search Profit Control;
- owner-advice loop;
- capital/budget guardrails;
- provider-safe live actions.

### C — Adaptive Funnel MVP
Includes AF-0..AF-4:
- measurement;
- 50-story baseline;
- routing core;
- bounded experiment;
- economic decision.

### D — Content Scale
Includes:
- 50 -> 150;
- 150 economic gate;
- 150 -> 300;
- series/cluster production and content-wave ROI.

### E — Commercial Scale / Expansion
Includes:
- 300 -> 400-600;
- additional monetization providers where justified;
- optional profit-gated AI experiments;
- later 800+ only after proof.

Each stage shows:
- status;
- finite completed/required task count where objectively defined;
- blocker count;
- Owner Gate count;
- next milestone;
- whether economic proof exists where required.

Do not fabricate percentages when denominator is not objective.

## 5. REQUIRED VIEWS

### 5.1 Profit
Keep and extend the current money-first screen.

Headline metrics:
- Direct spend;
- attributable YAN revenue;
- K5;
- YAN ARPU/RPV;
- stories/session;
- next-story continuation rate.

Below:
- primary recommended action;
- campaign/traffic economics;
- compact reader funnel;
- up to three high-priority alerts.

### 5.2 Critical Path
Only tasks that can move/block the next real milestone.

Must preserve dependency order.

### 5.3 Adaptive Funnel
Show:
- AF-0..AF-4 states;
- current policy version;
- control/treatment experiment id;
- kill-switch state;
- static fallback state;
- eligible sessions/sample;
- continuation/stories/session/return deltas;
- incremental revenue;
- incremental feature cost;
- FEATURE_ROI;
- current decision `TEST/KEEP/HOLD/KILL/SCALE_ALLOWED`.

### 5.4 Content
Show:
- active catalog count;
- target gate: 50 / 150 / 300 / 400-600;
- units by cluster/genre;
- units in series vs standalone;
- top clusters by reconciled ARPU/K5 where valid;
- dead/low-utilization inventory;
- current content wave cost;
- attributable incremental revenue;
- content-wave ROI/payback status;
- next-wave allocation recommendation.

### 5.5 Providers & Compliance
Show:
- Direct health;
- Metrica health;
- YAN health;
- site instrumentation state;
- first-party endpoint/privacy state;
- reconciliation state;
- traffic-quality/compliance holds;
- no secrets.

### 5.6 Owner Gates
Only actions that really require Owner authorization, including where applicable:
- Tilda/public publication;
- privacy publication;
- exact live provider mutation;
- >20% weekly budget increase;
- production spend outside approved bound;
- future AI experiment spend beyond approved bound;
- weakening of privacy/compliance/capital safeguards.

Routine development questions are not Owner Gates.

### 5.7 History
Accepted milestones, evidence and formerly critical items remain queryable.

Completed work must not disappear and make the project look unfinished from zero.

## 6. TASK CARD CONTRACT

Every project task card should expose, where applicable:
- `task_id`;
- title;
- plain-Russian business/user outcome;
- stage;
- workstream;
- status;
- target state;
- dependencies;
- blocker type/detail;
- branch/PR/head SHA;
- CI/check evidence;
- live-site/provider evidence state;
- economic evidence state;
- executor (`Central Brain`, `Codex`, `Owner`, `External`);
- owner gate yes/no;
- current action;
- next action;
- last evidence timestamp;
- evidence refs.

## 7. STATUS SEMANTICS

At minimum preserve these distinct states:
- `NOT_STARTED`;
- `DESIGNED`;
- `CODE_READY`;
- `LIVE_PROVIDER_VERIFIED`;
- `LIVE_SITE_VERIFIED`;
- `ECONOMICALLY_PROVEN`;
- `BLOCKED_EXTERNAL`;
- `BLOCKED_DATA`;
- `OWNER_GATE`;
- `DONE`.

Rules:
- CI green != live site verified;
- live site verified != economic proof;
- economic proof requires reconciled compatible money evidence;
- cached/stale data may never upgrade a status.

## 8. DEVELOPMENT ACTIVITY

Codex development activity may be shown separately:
- current bounded task;
- repository/branch/SHA boundary;
- run/check state;
- expected acceptance evidence;
- last review result;
- owner gate if encountered.

Codex activity is not product progress by itself. It becomes progress only after accepted evidence advances a project task.

Codex remains development-only and never appears as a production routing actor.

## 9. CONTROLS

First whole-project panel release remains operationally conservative.

Allowed initial controls:
- refresh status/data;
- select/view a bounded development task;
- open the exact GitHub workflow/PR/evidence page;
- toggle a local/project-level Adaptive Funnel kill-switch only if the underlying accepted runtime contract supports it safely;
- display Owner Gate instructions.

Do not add direct provider mutation buttons merely because the panel exists. Existing provider-write governance remains separate and guarded.

If future Start/Pause/Resume/Stop development controls are added like Eksamio, they must dispatch only the bounded development workflow and must not grant merge/deploy/provider-write authority.

## 10. SAFETY / ISOLATION

- localhost/private by default;
- no browser credentials/provider secrets;
- no raw OAuth material;
- no public dependency on panel availability;
- no Direct/YAN/Metrica mutation from render/refresh paths;
- unknown snapshot fields dropped or explicitly ignored;
- stale/conflicted source visible;
- money reconciliation hold blocks optimistic scale messaging.

## 11. ACCEPTANCE CRITERIA — OWNER CONTROL V2

Accepted only when:
1. existing money view still works;
2. stages A-E are always visible;
3. Critical Path shows dependency-ordered current blockers/tasks;
4. Adaptive Funnel shows AF-0..AF-4 and kill/fallback state;
5. Content shows catalog gate and wave economics;
6. Owner Gates contains only actual Owner actions;
7. GitHub/project evidence can distinguish code/live/economic states;
8. stale/conflict renders visibly;
9. no second task database exists;
10. panel outage cannot affect public reading;
11. no provider secret is needed in browser;
12. no provider write is possible from ordinary panel refresh/render;
13. Codex remains development-only;
14. tests verify stage/task completeness and status non-upgrade rules.

## 12. IMPLEMENTATION ORDER

1. define machine-readable whole-project board projection;
2. extend current snapshot model with project/adaptive/content facts;
3. add read-only stage rail + views to existing panel;
4. add GitHub/evidence adapter where appropriate;
5. add conflict/staleness detection;
6. add AF experiment/economics view;
7. add content-wave economics view;
8. add separate development activity block;
9. test completeness/status semantics;
10. only then consider optional bounded development workflow controls.
