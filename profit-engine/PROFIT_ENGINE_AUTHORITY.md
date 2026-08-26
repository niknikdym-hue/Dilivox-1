# DILIVOX PROFIT ENGINE — AUTHORITY

Version: 0.2
Date: 2026-08-26
Branch: `profit-engine`
Repository: `niknikdym-hue/Dilivox-1`
Status: OWNER-APPROVED CORE + PROPOSED EXECUTION MODEL

## 1. PURPOSE AND AUTHORITY

This document is the canonical authority for DILIVOX PROFIT ENGINE inside this repository.

Rules:
- `APPROVED` means explicitly decided by the Owner and must not be silently changed.
- `PROPOSED` means Central Brain architecture/implementation proposal and is not an Owner decision until approved.
- `BLOCKING` means the system must not scale past that gate until the condition is satisfied.
- A later approved replacement must mark the previous decision `SUPERSEDED`; history must not be silently rewritten.

Chat is not the long-term source of truth. Approved project decisions must be synchronized here.

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

### 6.2 Revenue decomposition

A useful simplified diagnostic model is:

`YAN_RPV ≈ page_depth × monetizable_viewable_impressions_per_page × effective_revenue_per_impression`

This is diagnostic, not the accounting source of truth. Actual provider revenue remains authoritative for money.

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

### P3 — Controlled experiments

Run bounded tests on the highest-potential cells. Measure causal change in K5 and guardrails.

### P4 — Rule-based autopilot

Allow the engine to pause/reduce/hold and make bounded scale decisions using transparent rules and audit logs.

### P5 — Adaptive allocator

Only after sufficient production history, add statistical/ML optimization for allocation across profitable segments and later across monetization providers.

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

Exact statistical and spend thresholds remain to be derived from live Dilivox data rather than invented in advance.

---

## 15. WHAT PROFIT ENGINE IS NOT

It is not:
- a dashboard that only reports CTR/CPC;
- a bot that blindly lowers bids;
- an ad-click maximizer;
- a traffic-arbitrage script that ignores provider rules;
- a system tied permanently to Yandex;
- a Dilivox-only codebase.

It is an economic control system whose first mission is to discover and safely scale legitimate Dilivox traffic/monetization combinations capable of reaching the Owner's 5:1 target.

---

## 16. OPEN OWNER DECISIONS

These are intentionally NOT silently decided by Central Brain:

1. Canonical K5 measurement window: same-session, rolling period, acquisition cohort, or a defined combination.
2. Maximum absolute test-loss budget before mandatory Owner approval.
3. Exact evidence threshold for declaring `K5_TARGET_ACHIEVED` after baseline data exists.
4. Whether future-provider revenue may contribute to the same primary 5:1 KPI or whether YAN 5:1 remains an independent mandatory KPI after additional providers are connected.

Until these are approved, implementation must preserve the ability to calculate all relevant variants rather than hard-code one irreversible interpretation.

---

## 17. CHANGE LOG

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
