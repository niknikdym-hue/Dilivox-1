# PROFIT ENGINE — WORLD BEST PRACTICES ADOPTION 2026

Status: RESEARCH BASIS / ADOPTED DESIGN DIRECTIONS
Updated: 2026-08-26

Purpose: record the strongest current world patterns relevant to the exact Profit Engine task so implementation does not depend on chat memory.

Primary project target remains:

`1 RUB Yandex Direct spend -> 5 RUB monetization revenue on Dilivox`.

This file does not authorize purchasing a third-party product. It records design ideas to reproduce in our own owner-controlled platform using Yandex first.

---

## BP-01 — Value-based bidding beats conversion-count thinking

World pattern:
Google Ads value-based bidding/Target ROAS explicitly optimizes conversion value rather than treating all conversions as equal.

Adopt:
- Profit Engine assigns monetary value to observed outcomes/proxies;
- Direct conversion goals are useful only when correlated with later monetization revenue;
- click/conversion counts are diagnostics, not the objective;
- K5 and contribution are the final judge.

Implementation:
`AudienceValueModel + AcquisitionStrategyLab`.

Reference:
https://support.google.com/google-ads/answer/15099424

---

## BP-02 — Portfolio capital allocation, not campaign-by-campaign tunnel vision

World pattern:
Search Ads 360 portfolio/budget bid strategies optimize bids/budgets across groups of campaigns toward a shared business target; individual campaigns need not all have identical ROI if the portfolio target is achieved.

Adopt:
- manage the Owner's capital as a portfolio;
- allocate across campaign/segment/strategy cells;
- allow bounded exploration below target;
- scale proven cells;
- evaluate portfolio K5 plus cell-level economics;
- avoid abrupt large changes that destabilize learning.

Implementation:
`ProfitAllocator + BudgetGovernor`.

References:
https://support.google.com/sa360/answer/14270628
https://support.google.com/sa360/answer/13384420

---

## BP-03 — Separate provider auction-time intelligence from Owner business intelligence

World pattern:
Modern ad platforms optimize individual auctions using private auction-time signals. External portfolio systems define business goals, conversion sources, target economics and budget allocation.

Adopt:
- do not waste engineering trying to outbid Yandex millisecond-by-millisecond without equivalent signals;
- use Direct native bidding algorithms as tools;
- Profit Engine decides what is worth buying, what goal/value to provide, which strategy to use and how much capital to allocate;
- realized owner economics decide whether a native strategy stays active.

Implementation:
`AcquisitionStrategyLab` above the Yandex Direct adapter.

---

## BP-04 — Feed/template-driven Campaign Factory removes ad-ops labor

World pattern:
Optmyzr Campaign Automator and similar systems build and maintain campaigns from a structured feed/template, dynamically creating campaigns, groups, ads, keywords, budgets, targets and assets and updating them when the source changes.

Adopt:
- Dilivox content registry acts as a structured feed;
- reusable templates produce campaigns/groups/ads;
- eligibility filters decide which content is worth advertising;
- campaign desired state is versioned;
- machine updates/pause/removes entities when source/economics change;
- use the same factory contract for future sites/providers.

Implementation:
`CampaignFactory`.

References:
https://help.optmyzr.com/en/articles/3121014-campaign-automator-user-guide
https://help.optmyzr.com/en/articles/10337621-campaign-automator-global-templates

---

## BP-05 — AI can build complete campaign drafts, but money gates must be deterministic

World pattern:
Current commercial tooling can generate campaign structure, ad groups, keywords, copy and assets from a website URL using AI.

Adopt:
- use machine generation for candidate structure/copy/assets;
- machine validation, provider rules and economic experiment gates decide what can launch;
- AI output has no independent spending authority;
- versions are auditable and challengers can be generated automatically.

Implementation:
`CreativeFactory + CampaignFactory + Validator`.

Reference:
https://help.optmyzr.com/en/articles/11693577-campaign-creation-user-guide

---

## BP-06 — Scheduled Rule Engine kills routine PPC work

World pattern:
Rule-engine products automate repetitive PPC optimizations on schedules and can alter bids/entities based on custom CPA/ROAS/business rules.

Adopt:
- deterministic rules first;
- automated stop-loss, exclusion, pause, reduction, scale eligibility, anomaly quarantine;
- schedule according to data freshness and provider learning windows;
- no human daily campaign maintenance.

Implementation:
`RuleEngine`.

Reference:
https://help.optmyzr.com/en/articles/3076017-what-is-the-rule-engine

---

## BP-07 — Revenue experiments need traffic allocation + auto-pause

World pattern:
Google Ad Manager revenue experiments use a real traffic percentage, control/variation comparisons, minimum evidence periods and auto-pause conditions that limit revenue downside.

Adopt on both sides:
- acquisition experiments have test spend/traffic allocation;
- site/ad-placement experiments have traffic allocation;
- explicit control;
- revenue/K5 primary metric;
- stop-loss/auto-pause;
- do not call a winner on tiny samples;
- use significant downside detection to stop losses early.

Implementation:
`ExperimentEngine` shared by acquisition and Dilivox site workstreams.

References:
https://support.google.com/admanager/answer/9799933
https://support.google.com/admanager/answer/9827314

---

## BP-08 — Yield optimization must be an independent layer

World pattern:
Google Ad Manager and Prebid-style ecosystems treat ad demand/yield as a separate optimization layer: expected value, floors, demand competition, experiments.

Adopt:
- YAN adapter is provider #1;
- placement-level economics are normalized;
- future providers connect through `MonetizationProvider`;
- future `YieldRouter` chooses among providers/eligible mechanisms based on expected net yield, UX, latency and policy;
- no need to rebuild acquisition logic when provider #2 is added.

Implementation:
`MonetizationProvider + YieldRouter`.

Initial phase remains YAN-only until measurement is trusted.

---

## BP-09 — Desired-state reconciliation is better than fragile imperative scripts

World lesson borrowed from infrastructure automation and mature ad-ops systems:
a machine-managed account needs a declared desired state and drift detection rather than a sequence of one-off API calls.

Adopt:
For every machine-owned campaign/group/ad/asset:
- desired state;
- observed provider state;
- version;
- drift;
- last successful write;
- rollback target;
- ownership scope.

Unknown/manual drift affecting money -> quarantine/review rather than silently overwrite.

Implementation:
`AdvertisingDesiredStateReconciler`.

---

## BP-10 — Exploration and exploitation must use separate capital

World pattern:
Portfolio optimizers and bandit systems preserve exploration while concentrating most capital into proven winners.

Adopt:
- `LEARNING_BUDGET` for discovering new query/landing/strategy/creative cells;
- `SCALE_BUDGET` for validated winners;
- separate caps and evidence requirements;
- never starve discovery completely;
- never let experiments consume uncontrolled capital.

Implementation:
`ProfitAllocator` capital buckets.

---

## BP-11 — Creative is a continuous optimization surface

World pattern:
Modern campaign automation continuously creates, tests and refreshes ads/assets rather than treating creative as a one-time setup task.

Adopt:
- creative variant lineage;
- automatic challenger generation;
- landing-message truthfulness;
- test by realized K5, not CTR alone;
- retire fatigue/losers;
- preserve approved source-asset registry;
- learn which content/visual/message combinations attract high-value readers.

Implementation:
`CreativeFactory + CreativePerformanceModel`.

---

## BP-12 — Site engagement and monetization must be optimized jointly

World publisher practice:
Revenue depends on user value/session depth/return behavior as well as per-impression yield.

Adopt:
- optimize `RevenuePerVisit`, `RevenuePerAcquiredUser`, cohort revenue and return value;
- use Dilivox's interactive story mechanics as an advantage;
- next-story recommendation optimizes expected future monetary value, not raw click probability;
- performance/UX degradation blocks short-term monetization wins.

Implementation:
`DilivoxSiteAgent + RecirculationOptimizer + AudienceValueModel`.

---

## BP-13 — Machine-operated Direct is technically feasible with current API

Current Yandex Direct API exposes programmatic services/methods required for major routine operations, including:
- campaigns create/update/suspend/resume;
- ad groups create/update/delete/get;
- ads create/update;
- keywords/autotargeting create where applicable;
- ad image upload/get/delete.

Therefore the project requirement that the Owner not manually build routine campaigns is technically aligned with the provider API, subject to campaign-type-specific constraints, moderation and permissions.

References:
https://yandex.ru/dev/direct/doc/ru/campaigns/campaigns
https://yandex.ru/dev/direct/doc/ru/campaigns/add
https://yandex.ru/dev/direct/doc/ru/adgroups/adgroups
https://yandex.ru/dev/direct/doc/ru/ads/add
https://yandex.ru/dev/direct/doc/ru/keywords/add
https://yandex.ru/dev/direct/doc/ru/adimages/adimages

---

## Adopted combined architecture

The best combined system for our exact goal is:

`Content/Opportunity Registry`
→ `CampaignFactory`
→ `CreativeFactory`
→ `Policy/Quality Validator`
→ `AcquisitionStrategyLab`
→ `BudgetGovernor`
→ `YandexDirectAdapter`
→ `DilivoxSiteAgent`
→ `MonetizationProvider(YAN)`
→ `MoneyLedger/Reconciler`
→ `AudienceValueModel`
→ `ProfitAllocator + RuleEngine`
→ back to acquisition and site actions.

Later:
- additional acquisition providers plug into the acquisition adapter layer;
- additional owner sites plug into SiteAgent;
- additional ad networks plug into MonetizationProvider/YieldRouter.

The shared economic brain remains unchanged.
