# PROFIT ENGINE — WORLD BENCHMARK AND DESIGN BASIS

Status: RESEARCH / PROPOSED DESIGN BASIS
Updated: 2026-08-26

## Purpose

This file records world technology patterns that are relevant to DILIVOX PROFIT ENGINE so the project does not depend on chat memory and does not reinvent solved parts of the problem.

This is NOT a decision to buy or copy any vendor. External products are references. Profit Engine remains owner-controlled and provider-neutral.

Primary Owner target remains:

`1 RUB Yandex Direct spend -> 5 RUB YAN revenue on Dilivox`

Primary operating doctrine:

`PROTECT CAPITAL -> MEASURE MONEY -> STOP LOSSES -> FIND PROFIT -> SCALE PROFIT -> REPEAT`

---

## 1. World pattern: value-based acquisition, not click maximization

### Google Ads Smart Bidding / Target ROAS

Google's value-based bidding separates two concepts:

- conversion-volume optimization (Target CPA / Max conversions);
- conversion-value optimization (Target ROAS / Max conversion value).

The important design lesson is that two conversions should not automatically be treated as equal. The bidding layer should receive business value, not only event counts.

Official references:

- https://support.google.com/google-ads/answer/15099424
- https://support.google.com/google-ads/answer/7684216
- https://support.google.com/google-ads/answer/13064207

### Profit Engine adoption

Profit Engine must maintain its own value model for each acquisition outcome.

For Dilivox, a conversion goal is useful only if it predicts or represents monetization value. A cheap conversion with poor YAN revenue can be worse than an expensive conversion with high long-term YAN revenue.

Therefore:

`event count != business value`

The optimization hierarchy is:

`reconciled revenue / profit -> predicted LTV -> high-quality proxy goals -> clicks`.

Clicks remain useful for exploration and sparse-data campaigns, not as the permanent north-star objective.

---

## 2. World pattern: native auction-time optimizer + external business brain

Google Smart Bidding and Yandex Direct automated strategies use auction-time signals that are not fully available to an external controller.

Yandex Direct currently exposes native strategies including:

- average CPC / click optimization;
- average CPA;
- pay for conversion;
- cost-revenue-ratio variants;
- `MAX_PROFIT` / «Максимум прибыли».

Official references:

- https://yandex.ru/dev/direct/doc/ru/annex/strategies
- https://yandex.ru/dev/direct/doc/ru/objects/campaign-strategies
- https://yandex.ru/support/direct/ru/strategies/maximum-profit

### Profit Engine adoption

Do not attempt to replace the provider's millisecond auction optimizer with slower external bid micromanagement when the provider has superior auction-time information.

Profit Engine should operate one level above it:

1. estimate true business value / K5 economics;
2. define conversion values and goals;
3. choose which provider-native bidding strategy is eligible;
4. choose campaign/segment membership;
5. set caps, target economics and budgets;
6. compare strategies experimentally;
7. stop or reallocate money when realized economics fail;
8. manage Dilivox-side monetization and user value in parallel.

This creates a two-level control system:

`Provider auction optimizer -> wins individual auctions`

`Profit Engine -> decides what is worth buying and how much capital deserves to be exposed`.

---

## 3. World pattern: paid-audience profitability as an end-to-end publisher stack

Kueez publicly describes an end-to-end publisher/performance stack combining:

- media buying;
- campaign-level revenue attribution;
- AI optimization;
- page optimization;
- revenue-per-session optimization;
- compliance controls.

References:

- https://weare.kueez.com/performance-marketing
- https://deck.kueez.com/compliant-audience-acquisition/

Kueez is a commercial vendor and its performance claims are not treated as independent evidence. The relevant point for Profit Engine is architectural: the traffic buyer and the monetized page cannot be optimized independently.

### Profit Engine adoption

Our closed loop must combine:

`traffic economics + landing/content selection + session economics + ad yield + return behavior`.

This is the closest public world pattern to the business loop we are building, but Profit Engine remains our own system and uses Yandex first.

---

## 4. World pattern: revenue per session/user, not only CPM

Publisher optimization literature repeatedly decomposes revenue into traffic volume, page/session depth and yield.

Outbrain's publisher framework explicitly uses revenue drivers such as:

- RPM;
- page views per visit;
- visitors;
- revenue per user;
- return visits;
- LTV.

References:

- https://www.outbrain.com/blog/publisher-series-revenue-optimization-part-1-data-insights-reporting/
- https://www.outbrain.com/blog/publisher-series-revenue-optimization-part-4-traffic-sources/
- https://www.outbrain.com/blog/publisher-series-revenue-optimization-part-5-ltv-revenue-planning/

### Profit Engine adoption

For Dilivox the key site-side monetary metric is not ad CTR and not isolated CPM.

Use:

- `RevenuePerVisit`;
- `RevenuePerAcquiredUser`;
- `RevenuePerSession`;
- `RevenuePerStoryOpen`;
- `CohortRevenue_1D/7D/30D`;
- return probability;
- next-story probability;
- story completion;
- monetizable visible impressions per session.

A page with lower CPM but much higher continuation/return can be more valuable than a page with higher immediate CPM.

---

## 5. World pattern: engagement -> loyalty -> more monetizable attention

OpenWeb's publisher model explicitly connects participation/engagement to loyalty, return frequency, high-attention inventory and incremental revenue.

References:

- https://www.openweb.com/publishers/
- https://www.openweb.com/publishers/monetization/

### Profit Engine adoption

Dilivox already has a useful product mechanic: readers consume a story, notice clues, choose a version and reveal an ending. This gives the site stronger first-party engagement signals than a passive article page.

Profit Engine should exploit that product structure to increase real user value:

`story open -> progress -> version decision -> reveal -> completion -> next story -> return`.

The goal is not to trap the user on pages. It is to make the next content choice genuinely attractive, because real continued consumption creates additional monetizable opportunities and improves long-term economics.

---

## 6. World pattern: optimize each ad impression / inventory opportunity by expected value

Google Ad Manager uses dynamic allocation and expected-value logic to choose among demand sources. It also provides experiments for testing revenue changes.

References:

- https://support.google.com/admanager/answer/2566686
- https://support.google.com/admanager/answer/152039
- https://support.google.com/admanager/answer/6286726

### Profit Engine adoption

When multiple monetization providers are connected later, Profit Engine should not use a static provider priority.

Future provider selection should consider expected net yield per eligible impression/session while preserving UX and provider policies.

First launch remains YAN-only, but the common schema must preserve:

- provider;
- placement;
- request;
- fill/show;
- viewability;
- revenue;
- latency;
- adjustment/finality state.

---

## 7. World pattern: dynamic floors / multi-demand competition

Prebid provides an open framework for header bidding and dynamic price-floor rules across bidder demand.

References:

- https://docs.prebid.org/
- https://docs.prebid.org/dev-docs/modules/floors.html
- https://docs.prebid.org/prebid-server/features/pbs-floors.html

### Profit Engine adoption

This is a LATER-PHASE reference only.

Do not introduce Prebid or multi-provider auction complexity before the YAN-only economics and site measurement are trustworthy.

Once multiple providers are connected, a `YieldRouter` can compare demand and later support provider-native or open-auction mechanisms where legally/technically appropriate.

---

## 8. World pattern: revenue experiments before rollout

Google Ad Manager revenue experiments and modern optimization systems test changes on a bounded share of traffic before broad rollout.

Profit Engine must use the same principle for both acquisition and site-side changes.

Experiment examples:

- CPC vs pay-per-conversion;
- pay-per-click conversion optimization vs pay-per-conversion;
- Direct Maximum Profit vs Profit Engine-selected CPA/CRR strategy;
- landing story A vs B;
- next-story recommendation algorithm A vs B;
- YAN placement/layout A vs B where provider rules allow;
- mobile layout A vs B.

The winner metric is not click-through rate. It is realized K5 / incremental profit subject to user-quality and compliance guardrails.

---

## 9. World pattern: compliant paid audience, not MFA arbitrage

Jounce Media defines MFA risk around paid-traffic dependence, aggressive monetization and superficial KPIs/user-hostile ad experience.

References:

- https://jouncemedia.com/resources/mfa-evaluation-criteria
- https://jouncemedia.com/resources/terminology

A July 2026 publisher framework discussed by Jounce/Kueez emphasizes three paid-audience safeguards:

1. paid acquisition should build an audience, not replace the organic audience;
2. promoted content should align with the site's normal content;
3. paid users should receive the same normal ad experience as organic users.

Reference:

- https://deck.kueez.com/compliant-audience-acquisition/

### Profit Engine adoption

Profit Engine must not achieve K5 through an MFA pattern.

Permanent rules:

- paid users see real Dilivox content;
- no separate ad-stuffed paid-traffic page variant;
- no click stimulation;
- no excessive/hidden/accidental ad interactions;
- no forced page reload loops;
- no aggressive auto-refresh solely to manufacture inventory;
- ad experience is source-neutral;
- organic/direct audience growth is itself a valuable long-term profit signal.

This is both a provider-safety requirement and an economic requirement: a user who returns without a second acquisition cost can have extremely high cohort K5.

---

## 10. Best-of-world architecture selected for Profit Engine — PROPOSED

Profit Engine combines five proven patterns instead of copying one product:

### Layer A — VALUE-BASED ACQUISITION

World reference: Google Target ROAS/value bidding + Yandex Direct CPA/CRR/Maximum Profit.

Our implementation:

`AcquisitionStrategyLab`

It chooses and compares buying strategies against our K5.

### Layer B — AUDIENCE ECONOMICS / LTV

World reference: publisher RPU/LTV and paid-audience optimization.

Our implementation:

`AudienceValueModel`

It estimates monetization value for a user/session/cohort and feeds this back into acquisition decisions.

### Layer C — SITE VALUE OPTIMIZATION

World reference: Kueez page optimization + publisher recirculation/engagement systems.

Our implementation:

`DilivoxSiteAgent + RecirculationOptimizer + ExperimentSDK`.

### Layer D — AD YIELD

World reference: Google Ad Manager dynamic allocation + later Prebid multi-demand mechanisms.

Our implementation:

`MonetizationProvider adapters + YieldRouter`.

YAN is provider #1. Other networks are added later.

### Layer E — CAPITAL ALLOCATION

World reference: portfolio bidding, but owner-controlled.

Our implementation:

`ProfitAllocator + BudgetGovernor`.

Optimizer can propose/execute bounded allocation changes, but the Owner's +20% weekly budget rule remains absolute.

---

## 11. What is unique in our system

External systems normally optimize only their own side:

- ad platform optimizes purchase;
- ad network optimizes its inventory;
- publisher tool optimizes page yield;
- recommendation system optimizes engagement.

Profit Engine must optimize the OWNER'S total loop:

`Acquisition cost -> reader behavior -> provider revenue -> cohort LTV -> profit -> capital reallocation`.

This cross-system owner-level objective is the central product advantage.

---

## 12. Anti-patterns explicitly rejected

Do NOT build:

1. a CPC dashboard mislabeled as Profit Engine;
2. an ad-CTR optimizer;
3. a pageview factory;
4. an MFA/ad-density engine;
5. a black-box AI that can move money without guards;
6. a YAN-only data model that cannot add providers;
7. a Dilivox-only core that cannot add sites;
8. a system that confuses provider forecast revenue with reconciled owner revenue;
9. a system that picks one Direct strategy forever without testing alternatives;
10. an optimizer that scales lucky small samples.

---

## 13. Design conclusion

The best architecture is not to reproduce one world vendor.

Build a closed owner-level economic operating system using:

`value bidding + acquisition strategy competition + cohort LTV + site recirculation + yield optimization + controlled experimentation + capital governance`.

For launch this becomes:

`Yandex Direct -> Dilivox -> Metrica/YAN -> Profit Engine -> Direct + Dilivox`.

After proof on Dilivox:

`multiple acquisition providers -> multiple owner sites -> multiple monetization providers -> one shared Profit Engine core`.
