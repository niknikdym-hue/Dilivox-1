# PROFIT ENGINE — PROJECT STATE

Status: P0 SYSTEM COMPLETION / SITE PUBLICATION + MONEY REVIEW / ADAPTIVE EXECUTION READY
Updated: 2026-09-12
Canonical public branch: `profit-engine`
Private core branch: `main`
Operational authority: `profit-engine/P0_SYSTEM_COMPLETION_BOARD.md`
Adaptive authority: `profit-engine/PROFIT_ENGINE_AUTHORITY.md` v0.4
Adaptive execution project: `profit-engine/ADAPTIVE_FUNNEL_EXECUTION_PROJECT.md`
Owner Panel contract: `profit-engine/DILIVOX_OWNER_CONTROL_PANEL_REQUIREMENTS.md`
Development FinOps: `profit-engine/DEVELOPMENT_FINOPS_POLICY.md`
Tracking issue: `#19 — Profit Engine Task 012 — Live guarded production launch`

## Objective

Build and operate the complete Dilivox profit loop:

`Yandex Direct -> Dilivox -> attributable reader behavior -> YAN/RSYA revenue -> Metrica/YAN reconciliation -> K5 -> proposal/Governor -> guarded Direct/site actions -> measured money outcome`.

Extend that loop with a low-cost, profit-gated Adaptive Funnel:

`behavior evidence -> VisitorStateLite -> candidate set -> NextContentDecision -> transparent rule policy -> measured outcome -> Profit Engine -> KEEP/HOLD/KILL/SCALE`.

First site: `site_id=dilivox` / `dilivox.ru`.
Target: `1 RUB Direct spend -> 5 RUB attributable YAN/RSYA revenue`.
K5=5 is a target, not yet an economically proven result.

## Central Brain rule

GitHub is source of truth. Distinguish `DESIGNED`, `CODE_READY`, `LIVE_PROVIDER_VERIFIED`, `LIVE_SITE_VERIFIED`, and `ECONOMICALLY_PROVEN`.

Codex/OpenAI API is development tooling only under `CODEX_DEVELOPMENT_ONLY_POLICY.md`. It may implement bounded tasks but does not participate in production visitor routing or commercial decision-making.

Development routing is `QUALITY-FIRST / COST-AWARE` under `DEVELOPMENT_FINOPS_POLICY.md`: use the least expensive route that is fully sufficient for the required quality and risk level. There is no requirement to try a free route first. If the task genuinely requires Codex, Codex is used directly; if complexity/risk justifies Sol, Sol may be selected directly inside the approved development envelope.

Initial shared OpenAI development envelope for AF-0/AF-1/AF-2 + executor + read-only Owner Panel slices:

`INITIAL_OPENAI_DEV_ENVELOPE_USD = 10.00`.

Astra is not required to begin the current execution plan and is OFF by default. A future independent architecture/review pass may be used only as a bounded review when justified; without a separately approved Astra envelope, Astra use is an Owner Gate.

## Locked governance

- private core is proposal-only;
- exact provider identity only;
- no secrets in Git/chat/logs;
- no blind mutation retry;
- first Direct write = exactly one campaign object;
- first method restricted to `campaign.suspend` or `campaign.resume`;
- `campaign.update_budget` not live-enabled for first launch;
- weekly budget increase > +20.00% requires explicit Owner approval;
- manual bid control never silently changes weekly capital;
- no motivated/artificial/incentivized traffic or ad clicks;
- optional paid features require `FEATURE_ROI >= 3.0` before scale;
- Adaptive Funnel default production path is rule-based and must work without an LLM;
- Codex is development-only;
- development cost optimization may not reduce quality or knowingly create repair-heavy work;
- normal bounded Luna/Terra/Sol work inside the approved development envelope is not itself an Owner Gate;
- hard development envelope exhaustion is an Owner Gate before additional paid work.

## Live provider state — latest recorded evidence

The latest recorded production/provider evidence in this state remains the 2026-09-01 P0 evidence until a newer live refresh is accepted. Do not infer current live success merely from newer documentation commits.

Direct Managing Account/operator `reklamadymova` had Editing access. Fresh exact provider reads passed for Direct, Metrica and YAN at the recorded evidence point.

Exact Dilivox campaigns:

- `712203524` — `Dilivox` — last recorded live `SUSPENDED` / `ACCEPTED`;
- `712791195` — `dilivox.ru` — last recorded live `ACTIVE` / `ACCEPTED`.

Other campaigns are excluded from first Dilivox smoke.

## YAN -> Metrica monetization — RECORDED LIVE TECHNICAL PASS

Owner enabled YAN reports for Metrica counter `110349067` on 2026-08-31.

The 2026-09-01 canonical bootstrap subsequently reached `READ_MODEL_READY`. By runtime definition that state is only reachable after the monetization probe `yan_total_by_date` returns PASS. The old `partner is not enabled for 110349067` propagation blocker was therefore closed in the recorded evidence.

## Canonical Metrica goals — RECORDED LIVE PASS

Separate OAuth app: `Profit Engine — Metrica Admin`.
Scopes: `metrika:read` + `metrika:write`.
The working Direct OAuth application was not modified.

Recorded live missing-only apply + read-back result:

- provider goals: 27;
- missing canonical goals: 0;
- invalid canonical IDs: 0;
- duplicate canonical IDs: 0;
- HTTP 200;
- audit `PASS`;
- apply `APPLIED_AND_VERIFIED`;
- terminal marker `METRICA_WRITE_SCOPE_VERIFIED`.

Canonical goals:

- `pe_story_progress_75`;
- `pe_version_selected`;
- `pe_story_completed`;
- `pe_next_story_clicked`;
- `pe_return_visit`.

All remain `native_bidding_eligible=false` until revenue validation.

Evidence:
`evidence/TASK-013-METRICA-GOALS-AND-READ-MODEL-PASS-2026-09-01.md`.

## Money preflight — RECORDED LIVE RAN / REVIEW REQUIRED

The recorded bootstrap reached `READ_MODEL_READY`, which also means both exact Dilivox campaign money preflights completed without runtime `ERROR` at that evidence point.

This does **not** prove K5>=5 and does not grant Direct write authority. Exact money outcomes require Central Brain review before any reversible smoke action.

## Production site instrumentation — CURRENT RECORDED P0 BLOCKER

Provider-side goals and monetization were ready in the last accepted state, but browser instrumentation was not yet published/verified on production Tilda.

`DILIVOX_SYSTEM_V1` remains the sole authoritative UX/event source for reading progress, story choice/reveal and next-story navigation. The Profit Engine package is only an idempotent Metrica normalizer: it initializes no counter, installs no second progress/navigation controller, maps the existing legacy 75%/next-story signals, and adds only missing canonical choice/completion/return mappings.

Recorded bootstrap:

- `site_instrumentation_live=false`;
- `site_probe_exit_code=2`;
- prepared package: `~/.config/profit-engine/tilda/dilivox-profit-engine-head-v1.html`.

The Owner publication step remains: keep the existing counter and `DILIVOX_SYSTEM_V1` once, paste/replace the one minimal Profit Engine bridge once immediately after it, publish all pages, then rerun live-site verification. Do not publish `dilivox-event-layer-task006.js` as a second DOM controller.

First-party event dispatch remains disabled until Privacy v2 + Task 015 endpoint acceptance.

## Local control panel

Existing implementation:
`profit-engine/runtime/profit_engine_runtime/control_panel.py`.

Installed local app was recorded at `~/Applications/Profit Engine.app`.

Current design properties:
- Russian UI;
- localhost only `127.0.0.1:8765`;
- money-first K5/spend/revenue view;
- owner advice;
- provider-write endpoints absent from ordinary panel operation;
- writer state recorded as `LOCKED` in the prior snapshot model.

Owner-approved direction on 2026-09-12: extend this existing app into the single whole-project Owner Control V2. Do not create a second Adaptive Funnel owner app or second task database.

Panel implementation contract:
`profit-engine/DILIVOX_OWNER_CONTROL_PANEL_REQUIREMENTS.md`.

Implementation task:
`profit-engine/tasks/TASK-020-OWNER-CONTROL-PANEL-V2.md`.

Owner Control V2 must also expose Development FinOps separately from production economics: selected execution/model route, routing reason, why-not-cheaper, quality floor, hard cap, actual `DEV_AI_COST`, shared envelope, remaining balance, 80% warning and Astra enabled/disabled state.

## Production Direct writer

Accepted in code in the prior P0 state; no live Direct mutation is asserted here as having been sent.

First smoke requires fresh exact money review, one ActionProposal/Governor/ControllerPlan, explicit Owner authorization for the exact action, <=5 minute arm, exact target lock, fresh state/TOCTOU/kill-switch checks, exactly one mutation network attempt, immediate read-back and immutable audit.

## Manual Search Profit Control

Dedicated concept: `DILIVOX | SEARCH | PROFIT ENGINE`.

Previously accepted in recorded state:
- MS1 exact read model;
- MS2 attribution-grain boundary;
- MS3 shadow controller;
- MS5 dedicated campaign dry-run.

Recorded next build slice: MS4 panel integration.
MS6 guarded campaign create is not authorized.
MS7 guarded `KeywordBids.set` is not implemented/authorized.

## Adaptive Funnel execution lane — OWNER-APPROVED / EXECUTION READY

Authority/policy:
- `PROFIT_ENGINE_AUTHORITY.md` v0.4;
- `ADAPTIVE_FUNNEL_IMPLEMENTATION_PLAN.md`;
- `EKSAMIO_PATTERN_ADOPTION_FOR_ADAPTIVE_FUNNEL.md`;
- `ADAPTIVE_FUNNEL_EXECUTION_PROJECT.md`;
- `DEVELOPMENT_FINOPS_POLICY.md`.

Execution packages:
- `AF-0` measurement truth — Tasks 013 + 015;
- `AF-1` 50-story baseline — Task 016;
- `AF-2` formal routing core — Task 017;
- `AF-3` bounded rule-based production experiment — Task 018;
- `AF-4` economic evaluation/Feature ROI — Task 019;
- cross-cutting whole-project Owner Panel V2 — Task 020;
- bounded quality-first Codex development executor — Task 021.

New task specs:
- `tasks/TASK-016-ADAPTIVE-BASELINE-CONTENT-MAP.md`;
- `tasks/TASK-017-NEXT-CONTENT-DECISION-CORE.md`;
- `tasks/TASK-018-RULE-BASED-ADAPTIVE-EXPERIMENT.md`;
- `tasks/TASK-019-ADAPTIVE-PROFIT-EVALUATION.md`;
- `tasks/TASK-020-OWNER-CONTROL-PANEL-V2.md`;
- `tasks/TASK-021-CODEX-DEVELOPMENT-EXECUTOR.md`.

Tasks 016, 017, 020 read-only/project slices and 021 may be developed before live AF-0 acceptance.

Task 018 production experiment is blocked until the relevant AF-0 live instrumentation/privacy/endpoint gates pass.
Task 019 requires real Task 018 evidence and reconciled money.

## Development execution routing — CURRENT OWNER DECISION

Canonical priority:

`QUALITY & CORRECTNESS -> DELIVERY SPEED -> COST EFFICIENCY -> MODEL MINIMIZATION`.

Routes:
- `G0`: GitHub-native/deterministic when fully sufficient, OpenAI `$0`;
- `G1`: Luna for small bounded reasoning/code work;
- `G2`: Terra as default paid developer for normal engineering;
- `G3`: Sol for genuinely complex/high-consequence engineering;
- `G4`: Astra exceptional/explicit only.

There is no mandatory `G0 -> G1 -> G2 -> G3` ladder. A task may start directly on the minimum sufficient route.

Examples for current lane:
- Task 016: mostly G0, with bounded model assistance only where metadata cannot be derived deterministically;
- Task 017: G2/Terra by default;
- Task 015 endpoint/idempotency/security slices: G2 or G3 according to exact risk;
- Direct/money/reconciliation safety logic: G3/Sol review where materially justified;
- Astra: only separately justified architecture/critical review.

## Content scale direction

Catalog scale is gated, not automatic:

`50 -> 150 -> 300 -> 400-600`.

Current ~50 stories are a measurement laboratory.

The first 50 -> 150 production wave is not authorized merely by this state file. It follows AF-4 evidence and must be produced in measured 25-50 story waves under the Feature/content profit rules.

Initial market-informed priority remains evidence-reallocatable:
1. fantasy / portal fantasy / romantic fantasy;
2. detective / thriller;
3. romance hybrids.

Dilivox-specific economics override generic market popularity.

## Current execution order

### Lane A — close live Profit Engine truth
1. Task 013: publish/live-verify the minimal Tilda instrumentation bridge;
2. refresh/review exact money preflight outcomes;
3. prepare any reversible Direct smoke only under existing exact Owner authorization rules;
4. continue MS4 panel/shadow integration where it does not conflict with the new Owner Panel contract;
5. Privacy v2 + Task 015 first-party endpoint acceptance.

### Lane B — parallel Adaptive development that is safe before live gates
1. Task 021 bounded quality-first development executor;
2. Task 016 baseline content map;
3. Task 017 NextContentDecision core;
4. Task 020 Owner Panel V2 slices 1-4: whole-project board, status model, views, truth semantics, Development FinOps view.

### Lane C — only after AF-0 live acceptance
1. Task 018 bounded rule-based production experiment;
2. Task 019 economic evaluation / Feature ROI;
3. feed accepted Task 019 truth into Owner Panel;
4. decide `KEEP/HOLD/KILL/SCALE`;
5. only then consider the first measured 50 -> 150 content wave.

## Completion definition

First-site Profit Engine ecosystem is complete only when paid acquisition, production behavior instrumentation, YAN monetization, reconciled K5, guarded Direct/site actions, Owner Control, and manual-search control are live-evidenced inside Owner governance.

Adaptive Funnel is economically accepted only when the rule-based treatment has attributable evidence, full incremental feature cost is known, reconciliation is clean, and the Feature Profit Gate is satisfied for scale.

Owner Control V2 is the single local/private view of project truth; its availability must never be a dependency of the public site.
