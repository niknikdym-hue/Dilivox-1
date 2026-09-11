# DILIVOX ADAPTIVE FUNNEL — PROFIT-GATED IMPLEMENTATION PLAN

Status: OWNER-APPROVED STRATEGIC DIRECTION + IMPLEMENTATION PLAN
Date: 2026-09-11
Repository: `niknikdym-hue/Dilivox-1`
Branch: `profit-engine`
Authority: `profit-engine/PROFIT_ENGINE_AUTHORITY.md`

If this document conflicts with `PROFIT_ENGINE_AUTHORITY.md`, the authority document wins.

## 1. PURPOSE

Build a low-cost adaptive reading funnel for Dilivox only when it has a credible and measurable path to profit.

The product goal is not an "AI site". The product goal is a profitable content system that:
- acquires legitimate readers;
- routes each reader to useful next content;
- increases recirculation, completion and return visits;
- increases attributable monetization revenue per legitimate visitor;
- keeps infrastructure and AI costs materially below the incremental revenue they create;
- stops features, content waves and experiments that do not meet the Owner's profit gates.

Canonical flow:

`paid/organic visitor -> story -> measured behavior -> next-best allowed route -> more legitimate reading/return -> monetization -> Profit Engine -> evidence -> keep/reallocate/stop`

AI is optional. Profit is mandatory.

## 2. OWNER PROFIT GATES

### 2.1 Existing acquisition target

The existing canonical target remains:

`K5 = attributable_monetization_revenue / paid_traffic_cost >= 5.0`

Equivalent operating inequality:

`Direct_CPV <= YAN_RPV / 5`

If paid acquisition costs 1 RUB per legitimate visitor, attributable monetization revenue must target at least 5 RUB per acquired visitor.

### 2.2 Feature Profit Gate

For any optional paid feature, AI layer, third-party service, adaptive module or material infrastructure expansion:

`feature_net_profit = incremental_attributable_revenue - full_feature_cost`

`FEATURE_ROI = feature_net_profit / full_feature_cost`

Scale is allowed only when:

`FEATURE_ROI >= 3.0`

Equivalent requirement:

`incremental_attributable_revenue >= 4 x full_feature_cost`

Example: a feature costing 100 RUB must create at least 400 RUB of incremental attributable revenue, leaving at least 300 RUB incremental profit.

Full feature cost includes all material incremental costs attributable to the feature:
- AI/API usage;
- cloud compute/storage/egress;
- third-party services;
- incremental content-production expense;
- incremental paid operations;
- material build/maintenance cost when it should reasonably be amortized into the test.

Mandatory compliance, security, fraud-prevention, accounting-integrity and capital-protection controls are not optional growth features and are not disabled merely for failing a direct revenue test.

### 2.3 Content-wave profit gate

A content-production wave is an investment, not a vanity target.

For a wave of `W` new stories at incremental cost `S` RUB per story:

`wave_cost = W x S`

The default scale requirement is:

`incremental_attributable_revenue_over_payback_window >= 4 x wave_cost`

Because the real per-story production cost and payback window are not yet canonically measured, they must be tracked explicitly rather than invented.

Illustrative break-even requirements:

| Cost/story | 50-story wave cost | Required incremental revenue | 100-story wave cost | Required incremental revenue |
|---:|---:|---:|---:|---:|
| 200 RUB | 10,000 | 40,000 | 20,000 | 80,000 |
| 500 RUB | 25,000 | 100,000 | 50,000 | 200,000 |
| 1,000 RUB | 50,000 | 200,000 | 100,000 | 400,000 |
| 2,000 RUB | 100,000 | 400,000 | 200,000 | 800,000 |

These are planning examples only. Actual production costs must replace them.

## 3. CURRENT CONTENT BASELINE

The current active Dilivox catalog contains 50 catalog-discoverable monetizable story/comic units.

Current distribution is shallow and intentionally broad:
- detectives: 8 units, including 2 comics;
- fantasy: 6;
- humor: 6;
- portal fantasy / `popadantsy`: 6;
- thrillers: 6;
- horror: 6;
- action: 6;
- adventure: 6.

This is sufficient for instrumentation and early routing tests, but not a commercial-scale adaptive catalog. A reader who strongly prefers one cluster currently exhausts the relevant inventory too quickly.

The source of truth for item identity remains:
`profit-engine/sites/dilivox/content-registry.json`.

## 4. WHY CATALOG DEPTH MATTERS

Adaptive routing creates value only when the system has enough good alternatives to route a reader without repetition or topic mismatch.

Planning model for a high-value reader:
- 3 stories per session;
- 2 sessions per month;
- 6-month useful freshness horizon.

That reader can consume about:

`3 x 2 x 6 = 36 stories`

inside a preferred cluster over six months.

A commercially useful cluster therefore needs roughly 50-70 relevant stories to provide:
- non-repeating continuation;
- several alternative next-step candidates;
- series/cycle continuation;
- room for A/B routing;
- freshness for return visitors.

Five meaningful reader-interest clusters at 50-70 stories each imply 250-350 stories, before secondary/discovery inventory. This is the economic basis for a 300-400 story commercial threshold rather than a 50-100 story catalog.

## 5. CATALOG SCALE GATES

Catalog count is not itself a success metric. It is a stage gate.

### Stage C0 — 50 units: measurement laboratory

Purpose:
- close production instrumentation;
- establish actual YAN ARPU/RPM and Direct CPV;
- measure completion, next-story click, recirculation and return;
- establish cluster-level economics;
- do not deploy expensive real-time AI.

No claim of commercial-scale Adaptive Funnel is allowed at this stage.

### Stage C1 — 150 units: genre-economics gate

Grow from 50 to 150 in small waves, not one blind batch.

Planning allocation for the first 100 new stories before Dilivox-specific winner data exists:
- +35 fantasy / portal fantasy / romantic fantasy;
- +30 detective / thriller;
- +20 romance hybrids: romantic fantasy, romantic mystery, romantic thriller;
- +10 science fiction / adventure;
- +5 horror / humor / experimental formats.

This market-informed prior is temporary. Dilivox cohort economics must override it.

At 150, evaluate:
- ARPU by cluster;
- K5 by acquisition -> cluster path;
- completion rate;
- next-story CTR;
- stories/session;
- 7/30-day return rate where attribution is valid;
- incremental revenue from series vs standalone content.

If the catalog does not show improving reader value and monetization, do not automatically proceed to 300.

### Stage C2 — 300 units: rule-based Adaptive Funnel gate

From 150 to 300:
- at least 60% of new production goes to the top three Dilivox clusters by attributable economic evidence;
- about 25% goes to the next-best two clusters;
- no more than about 15% remains exploration inventory unless evidence supports more.

Target structure:
- winning clusters should normally contain at least 50 stories each;
- secondary clusters should normally contain at least 20-30;
- a material share of content should belong to explicit series/cycles.

At this point full rule-based visitor routing is economically justifiable if C1 evidence is positive.

### Stage C3 — 400 units: commercial adaptive-catalog target

Initial planning mix for a 400-unit catalog:

| Reader cluster | Target units | Planning share |
|---|---:|---:|
| Fantasy + portal fantasy + romantic fantasy | 120 | 30% |
| Detective + thriller | 100 | 25% |
| Romance + romantic mystery/thriller | 80 | 20% |
| Science fiction + adventure | 50 | 12.5% |
| Horror/mysticism | 30 | 7.5% |
| Humor + comics + experimental | 20 | 5% |

This is not an immutable editorial quota. Rebalance every 50-story wave using actual Dilivox economics.

Target series structure at this stage:
- approximately 60% or more of new catalog inventory should participate in series/cycles where editorially appropriate;
- typical series size: roughly 6-10 stories;
- standalone stories remain important for acquisition and discovery.

### Stage C4 — 400-600 units: profitable scale range

400-600 is the intended first commercial-scale inventory range.

Growth beyond 400 is conditional on:
- reconciled monetization data;
- positive cluster economics;
- useful recirculation/return behavior;
- content-wave ROI evidence;
- no policy or traffic-quality warning.

### Stage C5 — 800+ units: prohibited by default until proven

Do not mass-produce 800+ stories merely because a large library looks impressive.

Crossing 800 requires sustained evidence that the 400-600 catalog is profitable and additional inventory still increases attributable visitor value rather than creating dead inventory.

## 6. GENRE STRATEGY

External market data is a prior, not the final optimizer.

Relevant 2025-2026 market signals:
- fantasy led Litres 2025 revenue with a 19% share;
- detectives were second with 9%;
- science fiction was third with 8.5%;
- in January-June 2026 Litres and Yandex Books both reported fantasy, romance, science fiction and detectives among major digital-reading trends;
- light fiction, including romance and detectives, is particularly important for mass entertainment reading.

Therefore the production hypothesis is to deepen three primary commercial families first:
1. fantasy / portal fantasy / romantic fantasy;
2. detective / thriller;
3. romance hybrids.

Action/adventure, science fiction, horror, humor and comics remain useful secondary/exploration clusters and can become primary if Dilivox evidence proves them stronger.

No genre receives permanent priority merely because the general market likes it. Dilivox must rank genres by attributable value per legitimate visitor and acquisition economics.

## 7. ACQUISITION / MONETIZATION MATH

### 7.1 ARPU required by paid traffic cost

For canonical K5=5:

`required_YAN_ARPU = 5 x Direct_CPV`

| Direct cost per legitimate visitor | Required attributable YAN ARPU |
|---:|---:|
| 0.20 RUB | 1.00 RUB |
| 0.50 RUB | 2.50 RUB |
| 1.00 RUB | 5.00 RUB |
| 1.50 RUB | 7.50 RUB |

If the real ARPU does not support the acquisition price, more content alone does not repair the business.

### 7.2 Diagnostic story-equivalent model

For planning only, if a fully consumed story produces `q` monetization requests and YAN RPM is `R` RUB per 1000 requests:

`estimated_revenue_per_story = q x R / 1000`

For K5=5:

`required_story_equivalents = 5000 x Direct_CPV / (q x R)`

Using `q=4` only as an illustrative diagnostic assumption:

| Direct CPV | RPM 50 | RPM 100 | RPM 150 | RPM 200 | RPM 300 |
|---:|---:|---:|---:|---:|---:|
| 0.20 | 5.00 | 2.50 | 1.67 | 1.25 | 0.83 |
| 0.50 | 12.50 | 6.25 | 4.17 | 3.12 | 2.08 |
| 1.00 | 25.00 | 12.50 | 8.33 | 6.25 | 4.17 |
| 1.50 | 37.50 | 18.75 | 12.50 | 9.38 | 6.25 |

This table is deliberately a stress test. It shows why low RPM plus expensive traffic cannot be solved by adding hundreds of stories: a reader will not consume an unlimited number of stories per acquisition.

Provider revenue/ARPU remains the accounting truth; this formula is only a diagnostic model.

## 8. ADAPTIVE FUNNEL ARCHITECTURE

### 8.1 Cheap path first

The default visitor path must not require an LLM call.

`event -> visitor/session state -> allowed candidate set -> rule/statistical ranker -> next content -> measurement`

Initial allowed actions:
- `CONTINUE_SERIES`;
- `SHOW_SIMILAR_STORY`;
- `SHOW_DIFFERENT_CLUSTER`;
- `SHOW_SHORTER_STORY`;
- `SHOW_HIGH_COMPLETION_STORY`;
- `SHOW_HIGH_RETURN_PATH`;
- `RESTORE_PREVIOUS_SESSION`.

The funnel must never optimize for ad clicks. It optimizes legitimate content consumption and attributable visitor value.

### 8.2 Required first-party events

At minimum:
- story impression/view;
- 25/50/75% progress where technically reliable;
- story completion;
- recommendation impression;
- recommendation click;
- route assignment and route version;
- next-story open;
- return visit;
- series continuation;
- experiment/control identity;
- monetization/revenue join identity where policy and data contracts permit.

### 8.3 Series-first routing

Series/cycles are a preferred low-cost retention mechanism because they create explicit reader intent without real-time model inference.

The engine should compare:
- series-first continuation;
- same-cluster recommendation;
- cross-cluster discovery;
- static current-site recommendation/control.

## 9. AI DOCTRINE

### 9.1 AI is optional and provider-neutral

Architecture must expose an `AIProvider` boundary rather than hard-code Yandex AI.

First candidate adapter may be Yandex AI Studio because of local infrastructure and low-cost models, but a future OpenAI or other adapter must remain possible.

### 9.2 Allowed low-cost AI uses

Before real-time AI is justified, AI may be used offline/batch for:
- semantic tagging of stories;
- embeddings and similarity map generation;
- content-cluster QA;
- experiment analysis;
- hypothesis generation;
- anomaly explanation for the Owner.

### 9.3 Real-time AI is not default

No real-time LLM call for every pageview or click by default.

Illustrative current Yandex AI Studio cost for one compact decision with about 300 input and 30 output tokens:

| Model | Approx. cost/decision | Cost per 1,000 decisions | Incremental revenue required by 4x gate |
|---|---:|---:|---:|
| Alice AI LLM Flash | 0.036 RUB | 36 RUB | 144 RUB |
| YandexGPT Lite | 0.066 RUB | 66 RUB | 264 RUB |
| YandexGPT Pro 5.1 | 0.264 RUB | 264 RUB | 1,056 RUB |

These figures use the 2026-09-11 published token prices and must be refreshed before any production budget decision.

Real-time AI may enter a bounded experiment only when:
- the rule-based funnel is already measured;
- there is a specific unresolved decision where AI might add value;
- traffic is split into control/treatment;
- full AI cost is logged;
- incremental revenue is attributable;
- the feature can be disabled instantly.

### 9.4 AI experiment rollout

Recommended first rollout:
- 0% AI in baseline production;
- 5-10% eligible traffic in first AI treatment;
- no scale until `FEATURE_ROI >= 3.0` with sufficient evidence;
- if the lower-confidence economic result is materially negative, stop immediately.

## 10. INFRASTRUCTURE COST DOCTRINE

Use serverless/on-demand infrastructure before dedicated compute.

As of 2026-09-11 Yandex Cloud publishes free monthly serverless tiers including the first 1,000,000 Cloud Functions/Serverless Container invocations, with additional compute free-tier allowances.

Therefore the adaptive routing service itself should be engineered to remain cheap. Dedicated always-on AI/GPU capacity is prohibited unless measured traffic and ROI justify it.

## 11. EXPERIMENT EVIDENCE

Routing decisions must be causal where practical.

For a typical next-story CTR around 20%, detecting a move to roughly 23% at 80% power and 5% two-sided alpha requires about 2,943 eligible sessions per arm under a simple two-proportion approximation. A move from 20% to 24% requires about 1,683 per arm.

Operational default:
- do not scale a routing variant from tiny samples;
- target at least about 3,000 eligible sessions per arm for moderate engagement lifts, unless a stronger statistical method/effect justifies otherwise;
- revenue/ARPU remains the final business outcome and should use reconciled windows/confidence, not engagement significance alone;
- severe downside can stop earlier.

## 12. FEATURE-COST SENSITIVITY

The Feature Profit Gate can be restated as the minimum ARPU lift required from the treatment:

`required_delta_ARPU = 4 x monthly_feature_cost / eligible_monthly_visitors`

| Monthly feature cost | 10k visitors | 50k visitors | 100k visitors | 500k visitors |
|---:|---:|---:|---:|---:|
| 500 RUB | +0.20 | +0.04 | +0.02 | +0.004 |
| 2,000 RUB | +0.80 | +0.16 | +0.08 | +0.016 |
| 5,000 RUB | +2.00 | +0.40 | +0.20 | +0.040 |
| 10,000 RUB | +4.00 | +0.80 | +0.40 | +0.080 |
| 20,000 RUB | +8.00 | +1.60 | +0.80 | +0.160 |

This is why low fixed/serverless cost is strategically important at small traffic volumes.

## 13. IMPLEMENTATION WORKSTREAMS

### W0 — Close measurement before sophistication

Required before serious adaptive work:
- production event instrumentation verified;
- Metrica/YAN monetization link verified;
- reconciled ARPU/RPM/Direct CPV available;
- route/experiment identity joinable;
- no unresolved privacy/compliance blocker;
- written YAN clarification before paid Direct -> YAN scale remains required by project authority.

### W1 — Build the 50-story baseline map

For all current content:
- canonical genre/cluster tags;
- series/standalone identity;
- length/format tags;
- baseline completion;
- next-story CTR;
- ARPU/revenue by content/cluster where available;
- acquisition-source compatibility;
- current recommendation path map.

### W2 — Implement rule-based Adaptive Funnel MVP

Build:
- visitor/session state;
- candidate generator;
- deterministic ranker;
- route versioning;
- fallback to static site;
- experiment assignment;
- kill switch;
- complete audit events.

No LLM dependency.

### W3 — Grow 50 -> 150 in measured waves

Produce new stories in waves of 25-50, not one 100-story blind batch.

After each wave:
- validate quality/originality;
- publish/instrument;
- measure cluster performance;
- reallocate the next wave.

### W4 — 150-story economic review

Gate decision:
- `STOP/REWORK` if ARPU/recirculation does not improve or new inventory remains unused;
- `CONTINUE` if at least several clusters show repeatable incremental reader value and the next production wave has a credible ROI path.

### W5 — Grow 150 -> 300 around winners

Use the 60/25/15 winner-secondary-exploration allocation rule.
Build series/cycles intentionally.

### W6 — Full rule-based funnel at 300

Enable:
- series-first routing;
- cluster routing;
- session-depth adaptive rules;
- return-session restoration;
- profitability-aware candidate ranking using public-safe economic signals;
- A/B and holdout controls.

### W7 — Grow 300 -> 400 and run commercial-scale test

Reach sufficient catalog depth only where C2 economics support it.
At 400, evaluate whether the adaptive catalog improves the full paid/monetization loop enough to justify 400-600 scale.

### W8 — Optional AI experiment

Only after W6/W7 evidence:
- start offline embeddings/semantic ranker if useful;
- then optionally test one compact real-time AI decision on 5-10% traffic;
- apply Feature Profit Gate;
- stop if it does not create at least 4x incremental attributable revenue versus its full cost.

### W9 — 400 -> 600 conditional scale

Add content only to economically productive clusters/series.
No automatic move to 800+.

## 14. DASHBOARD / OWNER PANEL REQUIREMENTS

Owner must be able to see, in RUB and not only percentages:
- paid traffic cost;
- attributable YAN revenue;
- K5;
- YAN ARPU/RPM;
- stories per session;
- next-story CTR;
- return rate;
- revenue by genre/cluster/series;
- content-wave cost and payback;
- each adaptive feature's cost;
- each adaptive feature's incremental revenue;
- `FEATURE_ROI`;
- status: `TEST / KEEP / SCALE / HOLD / KILL`;
- AI cost and AI incremental revenue separately.

## 15. KILL RULES

Immediately hold/kill optional adaptive work when:
- attribution is not trustworthy;
- revenue data is unreconciled;
- feature causes policy/traffic-quality risk;
- site quality degrades materially;
- treatment reduces attributable revenue beyond defined safety tolerance;
- cost grows without matching incremental revenue;
- a content wave produces dead inventory without increasing useful recirculation/return;
- real-time AI cannot prove a 4x incremental revenue-to-cost ratio after sufficient evidence.

## 16. WHAT SUCCESS LOOKS LIKE

The first successful Adaptive Funnel release is not the fanciest one.

It is the cheapest system that can prove:
1. readers consume more relevant Dilivox content voluntarily;
2. they return more often;
3. attributable monetization value per visitor increases;
4. the increase survives control/treatment comparison and reconciliation;
5. the extra profit materially exceeds the cost of creating the increase;
6. the system remains compliant and reversible.

The project then scales content and intelligence only where money evidence supports it.

## 17. EXTERNAL EVIDENCE SNAPSHOT — 2026-09-11

Planning references to refresh periodically:
- Yandex Advertising Network participation rules, published 2026-08-28: artificial impressions/clicks are prohibited and paid-traffic monetization must remain compliant.
- Yandex Metrica YAN reports: ARPU is average revenue per visitor; RPM is revenue per 1000 ad requests; monetization can be analyzed by traffic source/page/device.
- Kommersant, 2026-02-20 citing Litres 2025: fantasy 19% of Litres revenue, detectives 9%, science fiction 8.5%.
- Vedomosti, 2026-07-03: Litres/Yandex Books report fantasy, romance, science fiction and detectives among major digital-reading trends in H1 2026.
- Yandex AI Studio pricing snapshot 2026-09-11: Alice AI LLM Flash 0.1 RUB/1k input and 0.2 RUB/1k output tokens; YandexGPT Lite 0.2/0.2; YandexGPT Pro 5.1 0.8/0.8.
- Yandex Cloud Functions / Serverless Containers pricing snapshot 2026-09-09: first 1,000,000 invocations per month are free, with published compute free tiers.

This external evidence informs hypotheses. Dilivox production money evidence always overrides generic market assumptions.