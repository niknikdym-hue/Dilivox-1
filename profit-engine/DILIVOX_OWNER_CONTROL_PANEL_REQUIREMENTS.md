# DILIVOX OWNER CONTROL — DUAL-WINDOW PROJECT MANAGEMENT REQUIREMENTS

Status: OWNER-UPDATED IMPLEMENTATION CONTRACT / ONE APP + ONE BACKEND + TWO WINDOWS
Date: 2026-09-12
Repository: `niknikdym-hue/Dilivox-1`
Branch: `profit-engine`
Existing implementation to extend: `profit-engine/runtime/profit_engine_runtime/control_panel.py`
Authority: `profit-engine/PROFIT_ENGINE_AUTHORITY.md`
Execution project: `profit-engine/ADAPTIVE_FUNNEL_EXECUTION_PROJECT.md`
Development FinOps: `profit-engine/DEVELOPMENT_FINOPS_POLICY.md`

## 1. PURPOSE

Extend the existing local `Profit Engine.app` into the Owner's single application for the whole DILIVOX Profit Engine program.

Owner decision of 2026-09-12 supersedes the earlier combined/read-mostly UI assumption in this companion: the one application and one localhost backend expose two separate top-level working windows:

- `/profit` — `Пульт прибыли`, exclusively money-first commercial control;
- `/project` — `DILIVOX — Управление проектом`, whole-project development control.

GitHub remains durable source of truth and execution backend, but normal Owner operation must not require the GitHub web UI.

Do not create a second owner application or a second project/task database.

The panel must answer at a glance:
1. Are we making money and what is current K5?
2. What exact milestone are we trying to reach next?
3. What is code-ready versus live-site/provider verified versus economically proven?
4. What is blocking the next milestone?
5. What is Adaptive Funnel doing and can it be killed safely?
6. Which content clusters/series are earning or wasting money?
7. What actually requires Owner action now?
8. What development work is GitHub/Codex doing/has completed, why that route was selected, and how much paid development budget remains?

## 2. ONE-APPLICATION / DUAL-WINDOW INVARIANT

The existing `control_panel.py` / `Profit Engine.app` remains the money-first shell and application identity. `owner_control_v2.py` extends its one local backend and opens the two distinct routes/windows. Both consume the same canonical projection and runtime truth.

The Profit window contains no development task list or GitHub controls. The Project window contains the whole-project cockpit and bounded development controls.

Forbidden:
- second localhost backend or owner app for Adaptive Funnel;
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
- `DEVELOPMENT_FINOPS_POLICY.md`;
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

## 5. REQUIRED WINDOWS AND PROJECT VIEWS

### 5.1 Profit window
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

No project-development task clutter or GitHub controls are permitted in this window.

### 5.2 Project: Critical Path
Only tasks that can move/block the next real milestone.

Must preserve dependency order.

### 5.3 Project: Whole Project

Show every canonical task and accepted historical task. Task detail must be understandable without opening GitHub.

### 5.4 Project: Adaptive Funnel
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

### 5.5 Project: Content
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

### 5.6 Project: Providers & Compliance
Show:
- Direct health;
- Metrica health;
- YAN health;
- site instrumentation state;
- first-party endpoint/privacy state;
- reconciliation state;
- traffic-quality/compliance holds;
- no secrets.

### 5.7 Project: Owner Gates
Only actions that really require Owner authorization, including where applicable:
- Tilda/public publication;
- privacy publication;
- exact live provider mutation;
- >20% weekly budget increase;
- production spend outside approved bound;
- future AI experiment spend beyond approved bound;
- Development AI envelope exhausted or proposed extension;
- Astra use without an already approved Astra envelope;
- weakening of privacy/compliance/capital safeguards.

Routine development questions and normal Codex work inside the approved development envelope are not Owner Gates.

Owner decisions are exact-scope, SHA-bound, append-only local evidence plus a server-side GitHub workflow evidence dispatch. `APPROVE` never becomes generic provider/write authority.

### 5.8 Project: Development

Show current task/package, base SHA, branch, run/checks, route/model, current and latest completed action, checkpoint/pause state, result, Draft PR state, scope result and cost evidence. Raw GitHub links may appear only under expandable diagnostics/evidence.

### 5.9 Project: History
Accepted milestones, evidence and formerly critical items remain queryable.

Completed work must not disappear and make the project look unfinished from zero.

### 5.10 Project: Development FinOps
Show development execution economics separately from production economics.

Headline fields:
- current development task;
- `execution_route` (`G0|G1|G2|G3|G4`);
- model (`none|Luna|Terra|Sol|Astra`);
- `routing_reason`;
- `why_not_cheaper` where applicable;
- quality floor;
- task/package hard cap;
- actual `DEV_AI_COST`;
- phase development envelope;
- remaining envelope;
- 80% warning state;
- Astra enabled/disabled.

Summary counters:
- GitHub-native tasks and OpenAI cost `$0`;
- Luna task count/cost;
- Terra task count/cost;
- Sol task count/cost;
- Astra task count/cost.

Rules:
- free route is not displayed as preferable when it cannot meet the task quality floor;
- normal paid development inside the approved envelope must not be shown as a blocker merely because it costs money;
- development AI cost must never be mixed with `PRODUCTION_AI_COST`, visitor economics or K5;
- a stronger route is acceptable when its task record shows why a cheaper route would reduce quality, increase risk or create predictable rework.

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
- executor (`Central Brain`, `GitHub-native`, `Codex`, `Owner`, `External`);
- execution route/model;
- routing reason / why-not-cheaper;
- quality floor;
- development hard cap / actual cost where applicable;
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

GitHub-native/Codex development activity may be shown separately:
- current bounded task;
- repository/branch/SHA boundary;
- execution/model route;
- quality/routing rationale;
- run/check state;
- expected acceptance evidence;
- spend/cap;
- last review result;
- owner gate if encountered.

Development activity is not product progress by itself. It becomes progress only after accepted evidence advances a project task.

Codex remains development-only and never appears as a production routing actor.

## 9. FULL BOUNDED DEVELOPMENT CONTROLS

The Project window must provide `refresh`, `start`, `start_package`, `pause`, `resume` and `stop` through explicit localhost endpoints.

Rules:
- browser -> localhost backend -> authenticated fixed-scope GitHub adapter -> allowlisted workflow dispatch;
- Start binds exact canonical task, dependencies, authority SHA, route/model, allowed paths, checks and hard cap;
- package contains 1-5 compatible tasks and advances sequentially only after the prior technical PASS;
- Pause takes effect after the current bounded step and prevents the next package task;
- Resume requires an exact proven checkpoint and unchanged authority base;
- Stop targets the exact active run/package; no automatic retry;
- Owner may override G1 upward to G2/G3 and G2 upward to G3, never below quality floor;
- G4/Astra is separately explicit and never automatic;
- no automatic merge, deploy, Tilda publication, provider mutation or commercial action.

Production actions remain governed by their accepted exact controllers and separate Owner approvals; generic project buttons grant no production authority.

State-changing local requests require exact `127.0.0.1` Origin, per-launch anti-CSRF token, JSON-only bodies, command allowlists, idempotency/request IDs and burst protection. Credentials remain server-side.

## 10. SAFETY / ISOLATION

- localhost/private by default;
- no browser credentials/provider secrets;
- no raw OAuth material;
- no public dependency on panel availability;
- no Direct/YAN/Metrica mutation from render/refresh paths;
- unknown snapshot fields dropped or explicitly ignored;
- stale/conflicted source visible;
- money reconciliation hold blocks optimistic scale messaging.

## 11. ACCEPTANCE CRITERIA — OWNER CONTROL FULL

Accepted only when:
1. one `Profit Engine.app` starts/reuses one backend and opens separate `/profit` and `/project` windows;
2. existing money view still works and contains no development clutter;
3. stages A-E are always visible in Project Control;
4. Critical Path shows dependency-ordered current blockers/tasks;
5. Adaptive Funnel shows AF-0..AF-4 and kill/fallback state;
6. Content shows catalog gate and wave economics;
7. Owner Gates contains only actual Owner actions;
8. GitHub/project evidence can distinguish code/live/economic states;
9. stale/conflict renders visibly;
10. no second task database exists;
11. panel outage cannot affect public reading;
12. no provider secret is needed in browser;
13. no provider write is possible from ordinary panel refresh/render;
14. Codex remains development-only;
15. tests verify stage/task completeness and status non-upgrade rules;
16. Development FinOps view shows route/model/quality rationale/reserved cap/actual DEV_AI_COST/envelope balance;
17. Start/Pause/Resume/Stop/Refresh and bounded sequential packages are exercised against a mock GitHub adapter;
18. a free route cannot be selected by policy when the task contract requires a higher quality/capability route;
19. normal Codex spend inside the approved envelope does not create a false Owner Gate;
20. security tests reject foreign/missing Origin, missing CSRF, arbitrary repository/workflow/command and duplicate Start;
21. the first real end-to-end smoke is G0/free and leaves `DEV_AI_COST` unchanged;
22. no automatic merge/deploy/provider write is introduced.

## 12. IMPLEMENTATION ORDER

1. define machine-readable whole-project board projection;
2. extend current snapshot model with project/adaptive/content/development-FinOps facts;
3. add dual-window routes while preserving the existing Profit screen;
4. add the server-side fixed-scope GitHub control/evidence adapter;
5. add conflict/staleness detection;
6. add AF experiment/economics view;
7. add content-wave economics view;
8. add separate development activity/FinOps block;
9. test completeness/status semantics/quality-routing semantics;
10. add and test bounded development workflow controls;
11. run the free G0 Project Control smoke before any paid smoke.
