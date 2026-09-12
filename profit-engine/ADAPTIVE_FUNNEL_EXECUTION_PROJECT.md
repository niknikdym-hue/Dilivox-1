# DILIVOX ADAPTIVE FUNNEL — EXECUTION PROJECT

Status: EXECUTION-READY / CENTRAL BRAIN DELIVERY PLAN
Date: 2026-09-12
Repository: `niknikdym-hue/Dilivox-1`
Branch: `profit-engine`
Authority: `profit-engine/PROFIT_ENGINE_AUTHORITY.md` v0.4
Strategic plan: `profit-engine/ADAPTIVE_FUNNEL_IMPLEMENTATION_PLAN.md`
Pattern constraint: `profit-engine/EKSAMIO_PATTERN_ADOPTION_FOR_ADAPTIVE_FUNNEL.md`
Owner panel contract: `profit-engine/DILIVOX_OWNER_CONTROL_PANEL_REQUIREMENTS.md`
Development tooling: `profit-engine/CODEX_DEVELOPMENT_ONLY_POLICY.md`

If this document conflicts with `PROFIT_ENGINE_AUTHORITY.md`, authority wins.

---

## 1. DELIVERY OUTCOME

Deliver a production-safe, low-cost Adaptive Funnel that starts on the current ~50-story catalog, proves or disproves incremental economics, and can later scale content only through explicit economic gates.

Canonical first loop:

`DILIVOX page`
`-> allowlisted behavior event`
`-> VisitorStateLite`
`-> candidate generator`
`-> NextContentDecision`
`-> transparent rule policy`
`-> recommendation UI`
`-> outcome event`
`-> Metrica / YAN / Direct accounting join`
`-> Profit Engine`
`-> TEST / KEEP / HOLD / KILL / SCALE`

Failure path:

`adaptive unavailable / stale state / invalid config / unsafe money evidence -> STATIC_EDITORIAL_FALLBACK`

No production AI is required for this loop.

---

## 2. NON-NEGOTIABLE BUSINESS GATES

### Acquisition target

`K5 = attributable_monetization_revenue / paid_traffic_cost`

Target:

`K5 >= 5.0`

### Optional-feature gate

`feature_net_profit = incremental_attributable_revenue - full_feature_cost`

`FEATURE_ROI = feature_net_profit / full_feature_cost`

Scale only when:

`FEATURE_ROI >= 3.0`

Equivalent:

`incremental_attributable_revenue >= 4 x full_feature_cost`

Engagement lift without economic lift is not a scale signal.

### Catalog gates

`50 -> 150 -> 300 -> 400-600`

No automatic transition to the next catalog stage. Content is produced in measured waves of 25-50 units and reviewed economically.

---

## 3. FACTUAL STARTING POINT

This is not a greenfield build.

Already available in the project:
- provider-side Direct, Metrica and YAN read paths;
- YAN -> Metrica monetization path reaching `READ_MODEL_READY` in the recorded P0 state;
- canonical Metrica goals and provider read-back evidence;
- money-preflight tooling;
- content registry for DILIVOX;
- site event contracts and validation work from Tasks 005/006;
- Task 013 for production site instrumentation and goals;
- Task 015 for durable first-party event endpoint;
- local `Profit Engine.app` / `control_panel.py` on `127.0.0.1:8765`;
- owner-advice/money view in the existing panel;
- guarded provider-write architecture and Owner governance.

Still unresolved at the recorded production state:
- live Tilda instrumentation verification;
- first-party network event dispatch until Privacy v2 + Task 015 acceptance;
- economically proven K5;
- Adaptive Funnel routing and economic experiment evidence.

Hard constraints:
- `DILIVOX_SYSTEM_V1` remains the sole authoritative reading UX/event controller;
- Profit Engine must not install a duplicate DOM progress/navigation controller;
- browser signals never become authoritative money truth;
- Codex/OpenAI API is development tooling only, not production routing/commercial logic.

---

## 4. UNAMBIGUOUS EXECUTION PACKAGES

Earlier approved documents use `W1/W2` at different levels of granularity. They are not rewritten. This project defines execution package IDs that Codex and the Owner Panel must use:

| Package | Prior-plan mapping | Purpose | Terminal state |
|---|---|---|---|
| `AF-0` | strategic W0 + pattern W0 | production measurement truth | `ADAPTIVE_AF0_MEASUREMENT_READY` |
| `AF-1` | strategic W1 | current 50-story content/baseline map | `ADAPTIVE_AF1_BASELINE_READY` |
| `AF-2` | strategic W2 part 1 + pattern W1 | formal routing core | `ADAPTIVE_AF2_ROUTING_CORE_READY` |
| `AF-3` | strategic W2 part 2 + pattern W2 | bounded rule-based experiment | `ADAPTIVE_AF3_EXPERIMENT_EVIDENCE_READY` |
| `AF-4` | W2 close / W3 gate | economic evaluation / scale decision | `ADAPTIVE_AF4_SCALE_DECISION_READY` |

Owner Panel V2 is a cross-cutting execution task. Its read-only project projection may be developed before AF-4; its economic widgets consume AF-4 truth when available.

After AF-4, content growth follows the approved W3-W9 strategy.

---

## 5. AF-0 — MEASUREMENT TRUTH

Existing task ownership:
- `TASK-013-PRODUCTION-SITE-INSTRUMENTATION-AND-GOALS.md`;
- `TASK-015-FIRST-PARTY-EVENT-ENDPOINT.md`.

Required result:
- production behavior instrumentation is live-verified;
- event names/parameters are allowlisted;
- key events are not duplicated/inflated;
- stable content/session/experiment identities exist;
- Direct spend and YAN revenue remain provider-sourced;
- behavior can be joined to content/cluster/traffic source where valid;
- endpoint outage cannot break reading;
- stale/unreconciled money blocks profit-aware conclusions.

AF-0 live gate may remain pending while AF-1, AF-2 and read-only Owner Panel project work are developed/tested offline.

---

## 6. AF-1 — CURRENT 50-STORY BASELINE

Implementation task:

`TASK-016-ADAPTIVE-BASELINE-CONTENT-MAP.md`

Deliverables:
- adaptive metadata for every current content ID;
- genre/cluster family;
- series/standalone identity and explicit series-next relation;
- format/length bucket;
- static/editorial recommendation graph;
- baseline metric materialization contract;
- missing/dead metadata report;
- no AI dependency.

Acceptance:
- every adaptive candidate references a canonical content-registry ID;
- no invented/nonexistent story IDs;
- series-next is explicit, not guessed at runtime;
- baseline can be aggregated by story/cluster/series/source;
- static recommendation path remains available independently of Adaptive Funnel.

---

## 7. AF-2 — FORMAL ROUTING CORE

Implementation task:

`TASK-017-NEXT-CONTENT-DECISION-CORE.md`

Deliverables:
- `VisitorStateLite` contract and reducer;
- candidate generator;
- `NextContentDecision` schema;
- bounded action/reason-code vocabularies;
- deterministic rule policy v0.1;
- static editorial control route;
- global kill switch;
- fail-safe `STATIC_EDITORIAL_FALLBACK`;
- deterministic tests.

Initial policy order:
1. exclude invalid/current/recently seen content;
2. prefer explicit next item in a series;
3. otherwise prefer compatible same-cluster candidates with safe baseline evidence;
4. preserve bounded exploration;
5. if evidence/state/candidates are unsafe, fall back to static editorial routing.

No real-time LLM is permitted.

Acceptance:
- every recommendation is traceable to `decision_id`, reason codes and policy version;
- deterministic input produces deterministic decision;
- empty/invalid/stale inputs cannot break the page;
- profit-aware signal use is disabled when money evidence is stale/unreconciled;
- control/static behavior remains intact.

---

## 8. AF-3 — BOUNDED RULE-BASED EXPERIMENT

Implementation task:

`TASK-018-RULE-BASED-ADAPTIVE-EXPERIMENT.md`

Deliverables:
- stable control/treatment assignment;
- treatment = AF-2 policy;
- control = current/static editorial behavior;
- non-invasive recommendation UI adapter around existing `DILIVOX_SYSTEM_V1`;
- decision/outcome events: `SHOWN`, `CLICKED`, `OPENED`, `COMPLETED`, `ABANDONED`;
- experiment/policy version identity;
- live kill switch and automatic static fallback;
- no AI calls;
- no provider writes from routing request path.

Experiment rules:
- do not scale from tiny samples;
- severe downside may stop early;
- engagement is diagnostic only;
- revenue/ARPU outcome uses reconciled compatible windows;
- paid traffic budget rules remain independent and unchanged.

Acceptance:
- control/treatment assignment is reproducible;
- outcome events join back to the exact decision;
- site works normally with adaptive service disabled;
- production smoke proves zero duplicate DOM controller behavior;
- experiment can be killed without Tilda rebuild where technically feasible.

---

## 9. AF-4 — ECONOMIC EVALUATION + SCALE DECISION

Implementation task:

`TASK-019-ADAPTIVE-PROFIT-EVALUATION.md`

Deliverables:
- treatment vs control comparison for continuation, stories/session, return and ARPU/RPV;
- incremental attributable revenue calculation;
- full incremental feature-cost ledger;
- `FEATURE_ROI`;
- evidence state/confidence/sample status;
- decision output: `TEST`, `KEEP`, `HOLD`, `KILL`, `SCALE_ALLOWED`;
- bounded aggregate snapshot for Owner Panel V2.

Scale rules:
- `FEATURE_ROI >= 3.0` required for scale;
- unresolved reconciliation => `HOLD`;
- positive engagement but inadequate economics => continue bounded test or `KILL`, never automatic scale;
- severe economic downside => `KILL`;
- AI remains OFF.

AF-4 is the gate into content-growth W3.

---

## 10. CONTENT SCALE AFTER AF-4

### 50 -> 150

Only after AF-4 provides a credible routing/baseline foundation.

Produce in 25-50 story waves. Initial prior remains concentrated in:
1. fantasy / portal fantasy / romantic fantasy;
2. detective / thriller;
3. romance hybrids.

After each wave:
- quality/originality check;
- registry/instrumentation acceptance;
- consumption/utilization check;
- cluster ARPU/K5/recirculation review;
- next-wave reallocation.

At 150: explicit `STOP/REWORK/CONTINUE` gate.

### 150 -> 300

Use measured winner allocation (roughly 60/25/15 winner-secondary-exploration unless evidence supports change).

At 300: enable fuller rule-based adaptive routing only if economics remain positive.

### 300 -> 400-600

Commercial-scale test and conditional growth only. No automatic 800+ catalog.

---

## 11. OWNER PANEL V2

Implementation task:

`TASK-020-OWNER-CONTROL-PANEL-V2.md`

The existing `Profit Engine.app` is the single Owner Control surface and must be extended rather than replaced.

Required top-level project rail:
- `A — Measurement & Compliance`;
- `B — Profit Engine Live Control`;
- `C — Adaptive Funnel MVP`;
- `D — Content Scale 50 -> 150 -> 300`;
- `E — Commercial Scale 400-600 / Optional AI & Providers`.

Required views:
1. `Profit` — K5, spend, revenue, ARPU/RPV, actionable money advice;
2. `Critical Path` — only tasks that move/block the next real milestone;
3. `Adaptive Funnel` — AF-0..AF-4 state, experiments, policy/kill-switch state;
4. `Content` — catalog count, cluster/series mix, wave economics, dead inventory;
5. `Providers & Compliance` — Direct/Metrica/YAN health and policy gates;
6. `Owner Gates` — only actions requiring explicit Owner approval;
7. `History` — accepted milestones/evidence; completed work must not disappear.

Owner Panel must keep status semantics separate:
- `DESIGNED`;
- `CODE_READY`;
- `LIVE_PROVIDER_VERIFIED`;
- `LIVE_SITE_VERIFIED`;
- `ECONOMICALLY_PROVEN`;
- `BLOCKED_EXTERNAL`;
- `BLOCKED_DATA`;
- `OWNER_GATE`;
- `DONE`.

A successful CI run must never render as `ECONOMICALLY_PROVEN`.

The panel remains localhost/private by default and must be able to fail without affecting dilivox.ru.

---

## 12. DEVELOPMENT EXECUTION MODEL

Central Brain responsibilities:
- architecture and sequencing;
- bounded task definitions;
- acceptance criteria;
- review of evidence;
- project-state synchronization;
- preventing scope drift/duplicate systems.

Codex/OpenAI API responsibilities:
- implement bounded development tasks;
- write/update tests;
- produce PR/commit evidence;
- no production visitor routing role;
- no autonomous commercial/provider decisions.

Astra is not required to start execution. If an independent architecture review is later used, it is a bounded review gate, not a permanent runtime/development dependency.

---

## 13. OWNER GATES

Owner approval remains required for actions already governed by project authority, including:
- material production publication/Tilda changes where Owner action is required;
- first-party analytics privacy publication;
- live Direct/provider mutations requiring explicit authorization;
- budget increase beyond approved autonomy;
- future paid AI experiment budget beyond an approved bound;
- changes that weaken compliance/privacy/capital safeguards.

Routine code development, deterministic tests and read-only project/panel work must not be escalated into unnecessary Owner Gates.

---

## 14. START ORDER

Development may begin immediately in this order:

1. finish/verify AF-0 obligations using Tasks 013 and 015;
2. implement Task 016 baseline content map;
3. implement Task 017 routing core entirely offline/deterministically;
4. implement Task 020 slices 1-4 in parallel: whole-project board, status model, views, truth semantics;
5. only after AF-0 live acceptance, perform Task 018 bounded production experiment;
6. Task 019 economic evaluation determines `TEST/KEEP/HOLD/KILL/SCALE_ALLOWED`;
7. feed Task 019 truth into Task 020 Adaptive/Content/Profit views;
8. only then authorize the first 50 -> 150 measured content wave.

Parallel-safe work before Tilda/endpoint live gates:
- Task 016;
- Task 017;
- Task 020 read-only project/task projection and offline UI tests.

Not parallel-safe before AF-0 live acceptance:
- production treatment traffic;
- profit-aware routing using unreconciled money;
- content-scale claim based on Adaptive Funnel economics;
- production AI routing.

---

## 15. DEFINITION OF EXECUTION-READY

This project is execution-ready when:
- authority + strategic plan + Eksamio adoption constraint are linked;
- AF-0..AF-4 packages are unambiguous;
- Tasks 016-020 provide bounded implementation contracts;
- dependencies and Owner Gates are explicit;
- acceptance states distinguish code/live/economic truth;
- existing Owner Panel extension target is specified;
- no task requires production AI;
- no task duplicates Task 013/015 or creates a second reader/control system.
