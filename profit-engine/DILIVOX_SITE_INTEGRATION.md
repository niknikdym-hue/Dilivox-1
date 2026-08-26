# PROFIT ENGINE — DILIVOX SITE INTEGRATION

Status: CANONICAL DESIGN / FIRST REFERENCE IMPLEMENTATION
Updated: 2026-08-26
Site ID: `dilivox`
Domain: `dilivox.ru`

## 1. Purpose

Dilivox is the first full site-side execution node of Profit Engine.

It is not merely a destination for paid traffic. It must participate in the closed money loop:

`Yandex Direct -> Dilivox -> user behavior -> YAN blocks -> revenue -> attribution -> Profit Engine -> Direct + Dilivox actions -> measured result`.

The implementation must be reusable: site-specific details live in the Dilivox adapter/config, while the common Profit Engine core remains generic.

Primary target for the first ecosystem:

`1 RUB Yandex Direct spend -> 5 RUB YAN revenue attributable to the acquired Dilivox audience`.

The site-side objective is therefore to maximize legitimate monetization value per acquired user while preserving content quality, user trust, provider compliance and long-term return behavior.

---

## 2. Site-side profit equation

For a paid acquisition cohort:

`K5 = cohort_monetization_revenue / acquisition_spend`.

A useful site-side decomposition is:

`cohort_monetization_revenue ≈ users × sessions_per_user × pages_or_story_steps_per_session × monetizable_viewable_opportunities × effective_yield`.

This decomposition is diagnostic only; reconciled provider revenue remains the money source of truth.

Dilivox can improve K5 by increasing legitimate user value in several ways:

1. make the landing content match the acquisition intent;
2. increase completion of the story/product experience;
3. make the next content choice attractive;
4. increase return visits without paying for the same user again;
5. improve ad viewability/yield without degrading the experience;
6. send Profit Engine high-quality first-party signals so Direct can buy better users.

---

## 3. Mandatory Site Agent

Implement a reusable `SiteAgent` contract in the shared system and a first adapter:

`DilivoxSiteAgent`.

The site agent must expose or emit at least:

- stable `site_id`;
- stable page/content/story IDs;
- page type / content type;
- experiment and variant IDs;
- acquisition attribution identifiers;
- first-party behavior events;
- recommendation candidates;
- monetization placement identifiers where technically available;
- deployment/version metadata;
- health status.

The shared core must never contain branches such as `if site == dilivox` for business logic that can be represented through this contract.

---

## 4. Stable content identity

Every monetizable/content item used in experiments or attribution must have a stable machine-readable identity independent of title text and URL changes where practical.

Minimum fields:

- `site_id`;
- `content_id` / `story_id`;
- canonical URL;
- content type;
- category/genre;
- publish/version timestamp;
- active/inactive state;
- experiment eligibility;
- monetization eligibility.

Profit Engine must be able to answer:

- which story/page received the paid user;
- which story/page produced monetization value;
- which next content was shown/clicked;
- which content cluster produces the highest cohort value.

---

## 5. Acquisition attribution on Dilivox

Dilivox must preserve acquisition identity across the landing/session flow.

Required support:

- Yandex Direct tracking identifiers and dynamic parameters where available;
- UTM parameters;
- campaign/ad/group/criterion/search-query identity where legally and technically available;
- landing content ID;
- acquisition timestamp;
- device/context dimensions supplied by analytics rather than unnecessarily duplicated first-party.

Do not collect unnecessary personal data.

Attribution data must survive internal navigation so later story/content events can still be associated with the original acquisition cohort according to the approved attribution window.

---

## 6. First-party event taxonomy v1

Required initial events:

- `page_view_site`;
- `story_open`;
- `story_progress_25`;
- `story_progress_50`;
- `story_progress_75`;
- `version_section_seen`;
- `version_selected`;
- `reveal_opened`;
- `story_completed`;
- `next_story_seen`;
- `next_story_clicked`;
- `catalog_opened`;
- `return_visit`;
- `session_end_summary` where technically appropriate;
- `experiment_exposure`;
- `experiment_conversion` for approved proxy goals.

Event payload must include, where relevant:

- `site_id`;
- `content_id`;
- source content ID;
- destination content ID;
- experiment ID / variant ID;
- pseudonymous session/user identifier where permitted;
- acquisition cohort key/reference;
- event schema version.

Do not send sensitive or unnecessary personal information.

---

## 7. Monetization instrumentation

YAN is monetization provider #1.

Dilivox must maintain a provider-neutral placement registry even while only YAN is active.

Minimum placement metadata:

- `provider_id`;
- `placement_id`;
- `site_id`;
- page/content type eligibility;
- location class (header/body/after-story/etc.);
- device eligibility;
- experiment variant if applicable;
- active dates/version.

The site must allow Profit Engine to join page/content behavior with provider-side monetization statistics without altering provider ad code in prohibited ways.

Future providers must be connectable through the same placement abstraction.

---

## 8. Ad-experience invariants

Dilivox must never become an MFA/ad-density product merely to increase short-term ad revenue.

Hard site rules:

- paid users receive real Dilivox content, not a special ad-stuffed paid-traffic version;
- no encouragement to click ads;
- no accidental-click design;
- no hidden ads;
- no forced reload loops to manufacture inventory;
- no prohibited auto-refresh;
- no modification of provider creative/code beyond supported configuration;
- no experiment may create more advertising than useful content;
- no layout experiment may sacrifice site usability solely to boost ad interactions.

Optimization target is revenue from legitimate attention and repeat use.

---

## 9. Landing optimization

Profit Engine should be able to choose among eligible landing pages/stories based on expected cohort value, not only topical relevance or CTR.

Candidate scoring inputs:

- query/ad intent match;
- historical K5 by landing;
- YAN revenue per visit/user;
- completion rate;
- next-story rate;
- return rate;
- mobile/desktop performance;
- page speed/technical health;
- sample/confidence;
- provider/compliance state.

Landing experiments must preserve message-to-content truthfulness.

---

## 10. Recirculation engine

Dilivox has a structural advantage over passive article sites: interactive stories naturally create a completion point followed by a next-content decision.

Implement a reusable `RecirculationOptimizer` with a Dilivox candidate provider.

Objective:

`maximize expected future cohort monetization value`, not merely next-click probability.

Candidate score can include:

- probability of click;
- probability of completion;
- expected downstream YAN revenue;
- return probability;
- novelty/category diversity;
- current user's observed content path;
- content freshness;
- confidence/sample size.

The optimizer must preserve a holdout/control group so we can distinguish causal improvement from selection bias.

---

## 11. Return-value engine

A user acquired once and returning later can generate additional monetization revenue with no second acquisition cost.

Therefore return behavior is a first-class profit lever.

Measure at minimum:

- 1-day return;
- 7-day return;
- 30-day return where attribution is valid;
- sessions per acquired user;
- revenue per acquired user by cohort window;
- incremental revenue from return sessions.

Do not use dark patterns or spam to force return.

Future allowed retention surfaces can include first-party subscription/notification mechanisms only after separate product/privacy decisions.

---

## 12. Performance and Core Web quality

Site performance is an economic variable because slow/unstable pages can destroy both engagement and viewable monetization opportunities.

Track by page/device/variant:

- load and render health;
- Core Web Vitals or equivalent performance measures;
- JS errors;
- ad-load latency where observable;
- content interaction latency;
- failed event delivery.

Any monetization experiment that increases revenue but causes severe performance degradation must be flagged for review rather than automatically scaled.

---

## 13. Experiment SDK

Dilivox must have a site-owned experiment layer independent of any one ad provider.

Minimum requirements:

- deterministic assignment;
- stable experiment/variant IDs;
- holdout support;
- start/end dates;
- exposure logging;
- eligibility rules;
- kill switch;
- version history;
- server/client compatibility as implementation requires;
- no experiment without a declared primary money metric and guardrails.

Experiment types:

- landing selection;
- content sequencing;
- recommendation algorithm;
- UI/layout;
- approved YAN placement/layout variants;
- device-specific presentation;
- acquisition strategy pairing.

Primary outcome:

`incremental reconciled K5 / incremental profit`.

Secondary diagnostics can include engagement, completion, viewability and performance.

---

## 14. Proxy conversions for Direct

Profit Engine may define high-quality behavioral goals in Metrica/Direct if they predict later YAN revenue and help native bidding learn faster.

Candidate proxy goals include combinations such as:

- story completion;
- next-story click;
- deep session;
- repeat visit;
- high-value content path.

Important rule:

A proxy conversion is not valuable because it is easy to optimize. It is valuable only if historical/experimental evidence shows that it predicts higher realized cohort monetization.

Profit Engine must periodically re-estimate the monetary value of each proxy goal.

---

## 15. Site-side value signal

Longer-term proposed interface:

`expected_user_value` or `expected_cohort_value` computed by Profit Engine from observed Dilivox behavior and reconciled monetization.

This signal can be used to:

- rank landing pages;
- rank recommendations;
- define/weight provider conversion values where supported;
- compare Direct strategies;
- allocate test budget.

Never send strategic internal value details to an external provider unless required by the chosen bidding/value interface.

---

## 16. Site kill switches

Required independent controls:

- disable Profit Engine experiments globally;
- disable one experiment;
- disable one monetization placement variant;
- disable automated landing routing;
- disable recommendation optimizer;
- fall back to stable site defaults;
- disable first-party event dispatch if it causes site defects without removing core analytics unexpectedly.

Profit Engine must fail safe: a control-plane outage must not make Dilivox unusable.

---

## 17. Data-quality acceptance

Before Dilivox can drive money decisions, verify:

- content IDs stable;
- attribution parameters preserved;
- events fire once as specified;
- mobile/desktop delivery works;
- experiment exposures join correctly;
- Metrica and first-party counts are explainably consistent;
- YAN monetization data is available;
- provider revenue can be reconciled;
- Direct spend joins to acquisition cohorts;
- no material leakage between organic and paid cohorts;
- no experiment changes traffic-source attribution unexpectedly.

Failure -> `DATA_QUALITY_HOLD` and no autonomous scaling.

---

## 18. Dilivox reference implementation phases

### D0 — Inventory

Map current pages/stories, Metrica counter, YAN placements, Direct campaigns, events and current technical stack.

### D1 — Identity + attribution

Add stable content IDs, acquisition preservation and event schema.

### D2 — Money map

Join Direct spend -> Dilivox cohort -> Metrica/YAN revenue.

### D3 — Baseline

Measure K5, revenue/visit/user, completion, recirculation, return and placement yield.

### D4 — Site Experiment SDK

Enable controlled tests with holdouts and kill switches.

### D5 — Recirculation optimization

Optimize next-content sequence for expected cohort value.

### D6 — Monetization optimization

Test supported YAN placements/layouts and later provider routing while protecting UX/compliance.

### D7 — Closed-loop execution

Profit Engine changes both acquisition allocation and approved Dilivox-side variables, then measures realized economics.

---

## 19. Scaling contract to other sites

When the Dilivox implementation is proven, a new site should only need:

- `site_id`;
- site adapter;
- content/page identity mapping;
- event mapping;
- acquisition connector scope;
- monetization provider mapping;
- target economics;
- allowed site actions;
- budget limits;
- experiment surfaces.

The common Profit Engine core, Budget Governor, ledger, experiment evaluator, value model and provider interfaces must remain unchanged.

---

## 20. Definition of success

Dilivox site integration is successful when Profit Engine can answer and act on this chain with evidence:

`What did we pay? -> who/what did we acquire? -> what did the user consume? -> what revenue did that cohort generate? -> what site/acquisition choice caused the difference? -> where should the next ruble go?`

That is the first complete Profit Engine ecosystem.
