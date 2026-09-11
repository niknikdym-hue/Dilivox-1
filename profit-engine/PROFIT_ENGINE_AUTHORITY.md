# DILIVOX PROFIT ENGINE — AUTHORITY

Version: 0.3
Date: 2026-09-11
Branch: `profit-engine`
Repository: `niknikdym-hue/Dilivox-1`
Status: OWNER-APPROVED CORE + OWNER-APPROVED ADAPTIVE FUNNEL PROFIT GATES + PROPOSED EXECUTION MODEL

## 1. PURPOSE AND AUTHORITY

This document is the canonical authority for DILIVOX PROFIT ENGINE inside this repository.

Rules:
- `APPROVED` means explicitly decided by the Owner and must not be silently changed.
- `PROPOSED` means Central Brain architecture/implementation proposal and is not an Owner decision until approved.
- `BLOCKING` means the system must not scale past that gate until the condition is satisfied.
- A later approved replacement must mark the previous decision `SUPERSEDED`; history must not be silently rewritten.

Chat is not the long-term source of truth. Approved project decisions must be synchronized here.

Canonical companion for the adaptive-site workstream:

`profit-engine/ADAPTIVE_FUNNEL_IMPLEMENTATION_PLAN.md`

That companion contains the detailed calculations, catalog-growth model, genre hypotheses, AI cost examples and staged implementation plan. If it conflicts with this authority document, this authority document wins.

---

## 2. OWNER-APPROVED PROJECT CORE

### A-001 — Primary economic KPI — APPROVED

The system is built around one primary economic target for the first launch:

> For every 1 RUB spent in Yandex Direct, Dilivox must target 5 RUB of revenue from Yandex Advertising Network (YAN / РСЯ) ad blocks placed on Dilivox.

Canonical ratio:

`YAN_REVENUE_FROM_DIRECT / YANDEX_DIRECT_SPEND >= 5.0`

Equivalent target: 5:1 / 500% revenue-to-ad-spend ratio for this monetization loop.

This is revenue from YAN ad blocks versus Yandex Direct spend. It is not net profit after all business expenses.

### A-002 — First site — APPROVED

Dilivox is the first launched site and is identified by:

`site_id = dilivox`

Dilivox is the first operating object of Profit Engine, not the architectural boundary of the system.

### A-003 — First monetization provider — APPROVED

Yandex Advertising Network (YAN / РСЯ) is the first provider of advertising blocks for Dilivox.

YAN must be implemented as the first adapter, not hard-coded as the permanent and only monetization provider.

### A-004 — Provider-neutral monetization architecture — APPROVED

Profit Engine must be ready to add other advertising-block providers / ad networks without rewriting the common economic and analytical core.

The engine must be able to calculate economics:
- per provider;
- per site;
- per placement / ad block;
- per page / content cluster;
- per traffic segment;
- across all providers combined.

### A-005 — Independent system — APPROVED

Yandex is an external infrastructure/provider, not the owner, architect, or governing system of Profit Engine.

Yandex Direct, Yandex Metrica, YAN and their APIs are external inputs/control surfaces. Economic logic, decision rules, history, safeguards and optimization belong to Profit Engine.

### A-006 — Multi-site architecture — APPROVED

The common core must support gradual connection of additional Owner sites using isolated site configurations/adapters, permissions and data without rewriting the common analytical and budget engine.

### A-007 — Budget autonomy limit — APPROVED

Automatic increase of weekly advertising budget is allowed up to +20% without Owner confirmation.

Any increase above +20% requires explicit Owner approval before application.

### A-008 — PROFIT-FIRST OPERATING DOCTRINE — APPROVED

DILIVOX PROFIT ENGINE is a hard profit-first machine whose purpose is to make money.

Every production function must have a direct economic role. It must do at least one of the following:
- increase attributable monetization revenue;
- reduce the cost of acquiring valuable traffic;
- increase monetization value per legitimate visitor;
- reallocate spend toward higher-profit segments;
- stop or reduce loss-making spend;
- discover and validate new profitable traffic/monetization combinations;
- protect earned money from fraud, invalid traffic, provider sanctions, data errors or uncontrolled budget growth.

Analytics, AI, dashboards, reports, experimentation and automation are instruments, not goals.

No feature is justified merely because it is technologically interesting, visually impressive, or analytically sophisticated. If a feature has no credible path to increasing profit or protecting profit, it is secondary to Profit Engine launch.

The default decision hierarchy is:

`PROTECT CAPITAL → MEASURE MONEY → STOP LOSSES → FIND PROFIT → SCALE PROFIT → REPEAT`

The system must prefer measurable economic outcomes over vanity metrics. CTR, CPC, traffic volume, pageviews, session duration and similar indicators are diagnostic variables only; they are not the final optimization objective.

### A-009 — FEATURE PROFIT GATE — APPROVED

Optional paid features, AI layers, third-party services, adaptive modules and material infrastructure additions must not scale merely because they improve an engagement metric.

For an optional feature:

`feature_net_profit = incremental_attributable_revenue - full_feature_cost`

`FEATURE_ROI = feature_net_profit / full_feature_cost`

Scale is allowed only when:

`FEATURE_ROI >= 3.0`

Equivalent requirement:

`incremental_attributable_revenue >= 4 × full_feature_cost`

Therefore 100 RUB of feature cost must create at least 400 RUB of incremental attributable revenue, leaving at least 300 RUB of incremental profit.

Full feature cost must include all material incremental costs attributable to the feature, including AI/API usage, cloud/infrastructure, third-party services, incremental production/operations expense and material build/maintenance cost where appropriate.

Mandatory compliance, security, fraud-prevention, accounting-integrity and capital-protection controls are not optional growth features and must not be disabled merely because they do not directly generate revenue.

### A-010 — ADAPTIVE FUNNEL DIRECTION — APPROVED

Dilivox should evolve into an adaptive content funnel connected to the existing Profit Engine. This is not a separate new product and must not replace the existing economic/governance core.

Canonical direction:

`visitor -> measured behavior/state -> allowed next-content candidates -> cheap rule/statistical ranker -> next useful story -> measured outcome -> Profit Engine`

The Adaptive Funnel exists to increase legitimate reader value, recirculation, return probability and attributable monetization value per visitor.

It must never optimize for ad clicks, accidental ad interaction or artificial impressions.

The default path must remain cheap and deterministic enough to work without an LLM call.

### A-011 — CONTENT SCALE GATES — APPROVED

Catalog size is a stage gate, not a vanity metric.

Current baseline: approximately 50 active catalog-discoverable monetizable story/comic units.

Owner-approved scale doctrine:
- `50` units = measurement laboratory, not commercial-scale Adaptive Funnel;
- `150` units = first genre/cluster economics gate;
- `300` units = threshold for a full rule-based Adaptive Funnel if earlier evidence is positive;
- `400-600` units = intended first commercial-scale catalog range;
- `800+` units = blocked by default until the 400-600 catalog proves that additional inventory still increases attributable value and profit.

Content must be added in measured waves, normally 25-50 stories at a time, with economic review between waves.

Do not keep producing equal six-story genre batches. Deepen winners.

From the 150 -> 300 stage, the default allocation principle is:
- at least about 60% of new production to the top three Dilivox clusters by attributable economic evidence;
- about 25% to the next two strongest clusters;
- no more than about 15% to exploration unless evidence supports more.

Series/cycles are a preferred low-cost retention mechanism and should become a material share of the catalog where editorially appropriate.

### A-012 — GENRE PORTFOLIO DIRECTION — APPROVED, EVIDENCE-REALLOCATABLE

External digital-reading market evidence may be used only as the initial prior. Dilivox production money evidence must override generic market popularity.

Initial priority families:
1. fantasy / portal fantasy (`popadantsy`) / romantic fantasy;
2. detective / thriller;
3. romance hybrids: romantic fantasy, romantic mystery, romantic thriller.

Secondary/exploration families:
- science fiction / adventure;
- horror / mysticism;
- humor / comics / experimental formats;
- action where Dilivox-specific economics support it.

Initial planning mix at a 400-unit catalog:
- 30% fantasy + portal fantasy + romantic fantasy;
- 25% detective + thriller;
- 20% romance hybrids;
- 12.5% science fiction + adventure;
- 7.5% horror/mysticism;
- 5% humor + comics + experimental.

This is not an immutable editorial quota. Reallocate after each measured content wave using Dilivox-specific ARPU, K5, completion, recirculation, return and content-wave ROI.

### A-013 — AI COST DOCTRINE — APPROVED

AI is optional. Profit is mandatory.

Rules:
- architecture must expose a provider-neutral `AIProvider` boundary rather than hard-code one AI vendor;
- Yandex AI Studio may be the first practical provider, but the system must remain replaceable/comparable with other providers;
- offline/batch AI for tagging, embeddings, similarity maps, experiment analysis and hypothesis generation is preferred before real-time AI;
- no default LLM call on every pageview/click;
- no dedicated always-on AI/GPU capacity unless measured traffic and economics justify it;
- the first real-time AI experiment, if later justified, should normally be limited to about 5-10% of eligible traffic with a control group;
- real-time AI may scale only after it independently satisfies A-009 (`FEATURE_ROI >= 3.0`) on attributable economic evidence.

---

## 3. KPI CONTRACT

### 3.1 Canonical target

`K5 = attributable_monetization_revenue / paid_traffic_cost`

For the first launch:

`K5_YAN_DIRECT = YAN_revenue_attributable_to_Direct / Direct_spend`

Target:

`K5_YAN_DIRECT >= 5.0`

### 3.2 Operational unit economics — PROPOSED

For a traffic segment over the same measurement window:

`Direct_CPV = Direct_spend / Direct_visits`

`YAN_RPV = YAN_revenue / Direct_visits`

Then:

`K5 = YAN_RPV / Direct_CPV`

Therefore the 5x condition can be expressed as:

`Direct_CPV <= YAN_RPV / 5`

This must become the core operating inequality of the optimizer.

### 3.3 Why the engine must work on segments — PROPOSED

The 5:1 ratio is not expected to be identical for every individual click. Advertising auction price and ad monetization are stochastic. The optimizer must make the portfolio and selected scalable segments satisfy the target over a defined measurement window.

Segment dimensions should include, when data allows:
- Direct campaign;
- ad group;
- ad / creative;
- keyword / targeting criterion;
- search query;
- Direct platform / platform type;
- landing page;
- content cluster;
- geography;
- device;
- browser;
- hour / day;
- YAN placement / block;
- monetization provider;
- experiment variant.

### 3.4 Measurement-window decision — PROPOSED / NOT OWNER-LOCKED

Use two parallel views:

1. `FAST_K5` — short-window revenue and spend for operational stop-loss and rapid diagnostics.
2. `COHORT_K5` — acquisition-cohort revenue over a longer window, including subsequent monetized return visits when attribution is technically valid.

The exact canonical window (for example same-session, 7-day, 30-day, or another window) remains to be owner-approved after baseline data is inspected.

### 3.5 Full-cost optional-feature economics — APPROVED

For a feature with monthly/full-window cost `F` and `V` eligible visitors, the minimum incremental ARPU required by A-009 is:

`required_delta_ARPU = 4 × F / V`

For a content wave of `W` stories with actual incremental production cost `S` per story:

`wave_cost = W × S`

Default scale requirement:

`incremental_attributable_revenue_over_payback_window >= 4 × wave_cost`

The exact content-wave payback window remains an open owner decision until baseline Dilivox revenue and production-cost data are available.

---

## 4. COMPLIANCE GATE — BLOCKING BEFORE SCALE

Current YAN participation guidance warns against artificially attracting additional visitors to pages containing Yandex ads and specifically warns that paid-per-click / paid-impression visitor-acquisition services can result in invalid impressions/clicks and disconnection from YAN.

Therefore Profit Engine must not assume that a Direct-to-YAN monetization loop is automatically permitted at scale merely because both products are Yandex products.

### C-001 — Required action — BLOCKING

Before scaling paid Direct traffic whose economics are explicitly monetized through YAN blocks, obtain written clarification from YAN support for the concrete Dilivox model:
- real users;
- transparent Yandex Direct campaigns;
- original Dilivox content;
- no incentivized traffic;
- no artificial impressions/clicks;
- no requests to click ads;
- compliant ad placement;
- optimization on revenue economics, not on forcing YAN ad clicks.

If YAN confirms restrictions that make the target loop unavailable, the provider-neutral architecture remains mandatory and another compliant monetization provider can be added without replacing the Profit Engine core.

### C-002 — Permanent safety constraints — APPROVED BY PROJECT PRINCIPLE / IMPLEMENTATION REQUIRED

The system must never optimize by:
- creating artificial visits, impressions or clicks;
- motivating users to click advertising;
- placing blocks to cause accidental clicks;
- altering YAN ad code or ad contents in prohibited ways;
- placing more advertising than content;
- sacrificing site quality solely to increase ad interactions.

Optimization target is sustainable monetization of legitimate user attention.

---

## 5. DATA TRUTH ARCHITECTURE — PROPOSED

### 5.1 Yandex Direct adapter

Primary source for:
- spend;
- clicks;
- CPC;
- campaign ID;
- ad group ID;
- ad ID;
- keyword / criterion;
- search query where available;
- platform / placement dimensions;
- dates and other report dimensions.

Use current Yandex Direct API v5 Reports for production statistics. Legacy v4/Live 4 capabilities may be used only where an actually required method still exists there and the architecture explicitly isolates it.

### 5.2 Yandex Metrica adapter

Primary behavioral/attribution bridge between acquisition and monetization.

Important available concepts include:
- Direct campaign/ad/criterion/search-query dimensions;
- Direct attribution models including last Yandex Direct click;
- visits, users, bounce, page depth, session duration;
- YAN monetization metrics such as YAN partner revenue and YAN revenue per visit;
- YAN monetization breakdowns by traffic source, page, geography and device.

Metrica is the preferred analytical bridge for answering:

`Which paid traffic produced how much monetization value on Dilivox?`

### 5.3 YAN Partner Statistics adapter

Use the YAN Partner Statistics API as the monetization-provider accounting source for detailed YAN statistics and revenue reconciliation.

Required dimensions/metrics should be discovered from the statistics tree and normalized into the common provider-neutral revenue model.

### 5.4 Reconciliation rule

Profit Engine must not trust a single source blindly.

Daily/periodic reconciliation should compare:
- Direct spend from Direct reports;
- Direct-attributed visits from Metrica;
- YAN monetization in Metrica;
- provider-side YAN statistics/revenue.

Discrepancies, delayed adjustments and invalid-traffic corrections must be surfaced and must be able to pause scaling.

---

## 6. ECONOMIC ENGINE — PROPOSED

### 6.1 Core facts calculated for every eligible segment

At minimum:
- spend;
- visits;
- cost per visit;
- YAN revenue;
- YAN revenue per visit;
- K5 ratio;
- page depth;
- session duration;
- bounce rate;
- ad requests;
- served impressions;
- viewable impressions / available viewability proxy;
- fill rate where available;
- CPM/CPMV where available;
- sample size;
- data freshness;
- confidence / uncertainty state.

For Adaptive Funnel/content-scale decisions, also calculate when data allows:
- story completion;
- recommendation impressions/clicks;
- next-story CTR;
- stories per session;
- series continuation;
- return rate;
- ARPU/RPV by content cluster/series;
- content-wave cost/payback;
- adaptive-feature cost;
- adaptive-feature incremental revenue;
- `FEATURE_ROI`.

### 6.2 Revenue decomposition

A useful simplified diagnostic model is:

`YAN_RPV ≈ page_depth × monetizable_viewable_impressions_per_page × effective_revenue_per_impression`

This is diagnostic, not the accounting source of truth. Actual provider revenue remains authoritative for money.

A second planning-only diagnostic for a fully consumed story is:

`estimated_revenue_per_story ≈ ad_requests_per_story × RPM / 1000`

This must never become a reason to increase ad load beyond compliant/user-safe levels. Provider revenue/ARPU remains authoritative.

### 6.3 Two fundamental ways to reach 5x

1. Reduce `Direct_CPV` without destroying traffic quality.
2. Increase `YAN_RPV` without violating policy or degrading user experience.

Profit Engine must optimize both sides together.

---

## 7. ACQUISITION OPTIMIZER — PROPOSED

The system should discover traffic where monetization value is structurally high relative to acquisition price.

Primary levers:
- campaign / ad group separation;
- search-query and keyword economics;
- negative keyword / low-value traffic exclusion;
- geography;
- device;
- time/day;
- Direct platform / site type;
- creative-message match;
- landing-page match;
- bid / budget allocation within allowed API controls.

The ranking metric is not CTR and not cheap CPC by itself.

Primary acquisition score must be based on expected `K5` and expected incremental revenue after cost.

---

## 8. SITE VALUE AND MONETIZATION OPTIMIZER — PROPOSED

Profit Engine must increase legitimate value generated by each acquired visit.

Primary levers:
- exact landing-page relevance to the acquisition intent;
- page speed and stability;
- content quality;
- internal navigation to useful next pages;
- session depth;
- return probability;
- ad block viewability;
- compliant format/placement experiments;
- device-specific layouts;
- page/content-cluster monetization yield;
- provider selection once additional providers exist.

The system must never equate higher ad CTR with higher quality. Accidental or manipulated ad interaction is a negative safety signal.

### 8.1 Adaptive Funnel implementation boundary — OWNER-APPROVED DIRECTION

The first production Adaptive Funnel should be transparent and rule-based.

Initial allowed next-content actions may include:
- `CONTINUE_SERIES`;
- `SHOW_SIMILAR_STORY`;
- `SHOW_DIFFERENT_CLUSTER`;
- `SHOW_SHORTER_STORY`;
- `SHOW_HIGH_COMPLETION_STORY`;
- `SHOW_HIGH_RETURN_PATH`;
- `RESTORE_PREVIOUS_SESSION`.

Required behavior:
- route versioning;
- control/treatment identity;
- static-site fallback;
- kill switch;
- complete audit events;
- no dependence on AI for basic site operation.

Series/cycles should be tested against same-cluster and cross-cluster recommendations as a cheap retention mechanism.

---

## 9. EXPERIMENT ENGINE — PROPOSED

Every material optimization should be treated as an experiment with explicit before/after or control/treatment evidence.

Experiment cells can combine:

`traffic segment × landing/content variant × monetization layout/provider`

Rules:
- change as few causal variables as practical per experiment;
- record experiment version and dates;
- preserve source IDs;
- measure revenue and spend on compatible windows;
- use minimum evidence thresholds before scaling;
- do not scale tiny lucky samples;
- automatically detect severe downside and pause the test.

A later phase may use contextual bandits/Bayesian allocation, but the first production optimizer should be transparent and rule-based.

For Adaptive Funnel routing, engagement significance is not enough. Reconciled incremental ARPU/revenue and A-009 remain the final scale gate.

---

## 10. DECISION ENGINE — PROPOSED

For every segment the engine should assign one of these actions:

- `BLOCKED_COMPLIANCE`
- `NO_DATA`
- `LEARN`
- `PAUSE`
- `REDUCE`
- `HOLD`
- `SCALE_ALLOWED`
- `OWNER_APPROVAL_REQUIRED`

Decision inputs:
- expected K5;
- conservative K5 / confidence floor;
- spend exposure;
- data freshness;
- sample sufficiency;
- traffic-quality guardrails;
- YAN policy/invalid-traffic signals;
- current weekly budget and +20% autonomy limit.

Adaptive/content decisions must also consider:
- `FEATURE_ROI`;
- content-wave cost/payback;
- cluster-level ARPU/revenue;
- recirculation and return value;
- inventory utilization/dead inventory;
- AI cost where applicable.

No autonomous scale decision may rely solely on a point estimate from a small sample.

---

## 11. PROVIDER-NEUTRAL MONETIZATION CONTRACT — PROPOSED

Common abstraction:

`MonetizationProvider`

Each provider adapter should normalize at least:
- `provider_id`;
- `site_id`;
- `placement_id`;
- `page/content_id` where available;
- `date/time bucket`;
- requests;
- served impressions;
- measurable/viewable impressions where available;
- revenue;
- currency;
- provider-specific CPM/fill metrics;
- adjustment/finality status.

First adapter:

`provider_id = yandex_yan`

Future providers must be connectable without changing Direct acquisition logic or the economic ledger.

---

## 12. MULTI-SITE CONTRACT — PROPOSED

Common entities must carry `site_id` from the beginning.

Minimum isolation:
- credentials/reference identifiers;
- acquisition accounts;
- analytics counters;
- monetization providers;
- budget rules;
- revenue data;
- experiments;
- decisions;
- audit log.

First production configuration:

`site_id = dilivox`

---

## 13. IMPLEMENTATION SEQUENCE — PROPOSED

### P0 — Compliance certainty

Obtain written YAN clarification for the intended Direct → Dilivox → YAN paid-traffic monetization model. No aggressive scaling before this gate passes.

### P1 — Data truth

Connect read-only data flows first:
- Direct Reports API;
- Metrica Reporting/Logs API as needed;
- YAN Partner Statistics API.

Produce reconciled daily economic ledger.

### P2 — Baseline economic map

Calculate actual K5 and its components for current Dilivox traffic by:
- campaign;
- query/criterion;
- landing page;
- content cluster;
- geo;
- device;
- time;
- YAN placement where possible.

This stage answers whether 5x is currently reachable in any existing segment and identifies the bottleneck: acquisition price, revenue per visit, or both.

For the current 50-unit catalog, also establish baseline story/cluster completion, recirculation, next-story CTR, return behavior and monetization value.

### P3 — Controlled experiments

Run bounded tests on the highest-potential cells. Measure causal change in K5 and guardrails.

Adaptive Funnel starts with static/control vs cheap rule-based routes. Do not begin with a real-time AI dependency.

### P4 — Rule-based autopilot

Allow the engine to pause/reduce/hold and make bounded scale decisions using transparent rules and audit logs.

At the site layer, deploy rule-based next-content routing only after instrumentation and economic evidence are trustworthy.

### P5 — Adaptive allocator

Only after sufficient production history, add statistical/ML optimization for allocation across profitable segments and later across monetization providers.

### P6 — Profit-gated content scale

Use the A-011 gates:

`50 -> 150 -> 300 -> 400-600`

with 25-50 story production waves and an economic review between waves.

Do not cross 800+ by default.

### P7 — Optional AI layer

Only after the rule-based funnel and catalog economics are measured, run a bounded AI treatment if there is a specific decision where AI may add value.

AI must remain optional, reversible, provider-neutral and subject to A-009 independently of the rest of the system.

---

## 14. PRODUCTION GATES — PROPOSED

Profit Engine must not claim that 5x has been achieved merely because one small sample exceeded 5.0.

A production gate should require:
- reconciled spend and revenue;
- no unresolved material data mismatch;
- adequate sample/exposure;
- target K5 sustained on the chosen measurement window;
- no traffic-quality or policy warning;
- no dependence on prohibited/adversarial behavior;
- repeatability across a meaningful share of spend.

For optional adaptive features/content waves, scale additionally requires:
- attributable incremental revenue versus a credible control/counterfactual;
- full incremental cost accounting;
- A-009 `FEATURE_ROI >= 3.0` or the content-wave equivalent;
- no material site-quality degradation;
- evidence that additional inventory is being consumed rather than becoming dead stock.

Exact statistical, spend and content-payback thresholds remain to be derived/refined from live Dilivox data rather than silently invented.

---

## 15. WHAT PROFIT ENGINE IS NOT

It is not:
- a dashboard that only reports CTR/CPC;
- a bot that blindly lowers bids;
- an ad-click maximizer;
- a traffic-arbitrage script that ignores provider rules;
- a system tied permanently to Yandex;
- a Dilivox-only codebase;
- an AI showcase that burns money for personalization;
- a content factory that produces hundreds of unused stories without measured demand.

It is an economic control system whose first mission is to discover and safely scale legitimate Dilivox traffic/monetization combinations capable of reaching the Owner's 5:1 target and to reject optional complexity that cannot prove profit.

---

## 16. OPEN OWNER DECISIONS

These are intentionally NOT silently decided by Central Brain:

1. Canonical K5 measurement window: same-session, rolling period, acquisition cohort, or a defined combination.
2. Maximum absolute test-loss budget before mandatory Owner approval.
3. Exact evidence threshold for declaring `K5_TARGET_ACHIEVED` after baseline data exists.
4. Whether future-provider revenue may contribute to the same primary 5:1 KPI or whether YAN 5:1 remains an independent mandatory KPI after additional providers are connected.
5. Canonical payback window for a content-production wave after actual production cost and baseline revenue are measured.
6. Maximum absolute AI experiment budget before a new explicit Owner approval is required.

Until these are approved, implementation must preserve the ability to calculate all relevant variants rather than hard-code one irreversible interpretation.

---

## 17. CHANGE LOG

### 0.3 — 2026-09-11
- Owner approved the Feature Profit Gate: optional features must create at least 4× incremental attributable revenue versus full feature cost, equivalent to `FEATURE_ROI >= 3.0`.
- Owner approved Adaptive Funnel as an extension of the existing Profit Engine, not a separate product.
- Locked content scale gates: 50 measurement lab; 150 genre-economics gate; 300 rule-based Adaptive Funnel gate; 400-600 first commercial-scale range; 800+ blocked until proven.
- Locked measured content waves of 25-50 stories and winner-deepening rather than equal genre batches.
- Added initial evidence-reallocatable genre direction: fantasy/portal/romantic fantasy; detective/thriller; romance hybrids as primary hypotheses.
- Added provider-neutral AI doctrine: cheap/offline first, no default per-page LLM, bounded 5-10% real-time AI treatment only after rule-based evidence, and independent Feature Profit Gate.
- Added canonical companion `ADAPTIVE_FUNNEL_IMPLEMENTATION_PLAN.md` containing detailed calculations and implementation workstreams.

### 0.2 — 2026-08-26
- Owner approved the PROFIT-FIRST operating doctrine.
- Added A-008: every production function must increase profit, reduce acquisition cost, stop losses, discover scalable profit, or protect capital.
- Added mandatory decision hierarchy: `PROTECT CAPITAL → MEASURE MONEY → STOP LOSSES → FIND PROFIT → SCALE PROFIT → REPEAT`.

### 0.1 — 2026-08-26
- Created canonical Profit Engine authority document.
- Recorded Owner-approved 5:1 Direct-to-YAN economic target.
- Recorded Dilivox as first site.
- Recorded YAN as first monetization provider and provider-neutral expansion requirement.
- Recorded multi-site architecture and +20% weekly budget autonomy limit.
- Added proposed data/economic/decision/experiment architecture.
- Added blocking compliance clarification gate before scale.