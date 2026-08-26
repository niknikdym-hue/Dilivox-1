# PROFIT ENGINE — MACHINE ADVERTISING OPERATIONS

Status: CANONICAL / OWNER-APPROVED DIRECTION
Updated: 2026-08-26

## 1. Mission

The machine, not the Owner, performs routine advertising operations.

First acquisition provider: Yandex Direct.

Primary business target:

`K5 = attributable monetization revenue / acquisition spend >= 5.0`

Yandex Direct is an execution instrument. Profit Engine supplies the cross-system economic objective, campaign portfolio policy, site value signals, capital allocation and risk rules.

## 2. End-to-end operating loop

`Discover opportunity -> Build campaign plan -> Build creatives -> Validate -> Launch bounded test -> Observe -> Attribute revenue -> Reconcile -> Score -> Stop/Reduce/Hold/Scale -> Generate next test`

No recurring step in this loop should require the Owner to open the Direct UI when an API/provider mechanism supports automation.

## 3. Campaign Factory

Implement a provider-neutral `CampaignFactory` with Yandex Direct adapter.

Input sources:
- Dilivox content registry;
- eligible landing pages/stories;
- observed search/query opportunities;
- content categories/intent labels;
- historical K5 and revenue-per-user;
- keyword/autotargeting candidates;
- geo/device/time opportunities;
- experiment specification;
- strategy specification;
- budget/test caps.

Output: versioned `CampaignPlan` containing:
- provider;
- site_id;
- campaign type;
- campaign name/idempotency key;
- groups;
- keywords/autotargeting where applicable;
- negatives/exclusions;
- landing URLs;
- tracking parameters;
- ads/creative variants;
- image assets;
- geo/schedule/device settings where supported;
- acquisition strategy;
- goals/value settings;
- budget;
- experiment ID;
- stop-loss;
- rollback plan.

The factory must support create/update/pause/archive lifecycle rather than one-time campaign generation.

## 4. Creative Factory

Routine creative production is machine-operated.

`CreativeFactory` should generate and manage variants from:
- factual Dilivox page/story metadata;
- approved content summaries;
- approved site assets/images;
- machine-generated text variants;
- machine-generated image variants only where useful and compliant;
- reusable campaign templates.

Required controls:
- no false claims/clickbait that misrepresents landing content;
- spelling/grammar validation;
- URL/landing-content consistency;
- provider text/image constraints;
- duplicate detection;
- forbidden-claim/policy linting;
- asset provenance/version;
- automated preview/render sanity checks where possible;
- performance history by creative version.

The machine may retire losing creatives and produce challengers automatically within approved policy.

## 5. Direct API execution contract

Current Yandex Direct API supports the core machine lifecycle required by the project, including separate services/methods for campaigns, ad groups, ads, keywords/autotargeting and images, plus campaign suspend/resume operations.

Implementation must isolate provider specifics behind the Direct adapter.

Required actions:
- create/update campaigns;
- create/update/delete groups as supported;
- create/update ads;
- create keywords/autotargeting where the campaign type uses them;
- upload/select images;
- configure supported strategy/settings;
- suspend/resume campaigns;
- read status/moderation/errors;
- reconcile every provider mutation response with local desired state.

No provider write is considered successful until its response/state is recorded.

## 6. Desired-state model

Borrow the infrastructure-as-code pattern for advertising.

For every machine-managed advertising entity maintain:
- desired state;
- last observed provider state;
- drift status;
- ownership tag/label where possible;
- version;
- reason/evidence;
- rollback target.

The engine should reconcile safe drift automatically and quarantine unknown/manual drift that could affect money.

## 7. Portfolio Profit Allocator

Do not optimize each campaign in isolation.

The machine treats advertising capital as a portfolio across cells such as:

`provider x campaign x query/audience x landing x device x geo x time x strategy x creative`

Portfolio logic may allow some exploration cells below K5 while the overall controlled portfolio pursues the target, provided learning spend is explicitly capped.

Capital states:
- `DISCOVER`;
- `LEARN`;
- `TEST`;
- `SCALE`;
- `HOLD`;
- `REDUCE`;
- `STOP`;
- `QUARANTINE`;
- `PENDING_OWNER_APPROVAL`.

## 8. Strategy competition

The machine does not preselect clicks or conversions forever.

Use `ACQUISITION_STRATEGY_LAB.md` to compare eligible provider-native approaches using Owner economics.

For Yandex this includes, where supported and eligible:
- CPC/click acquisition;
- conversion optimization with click payment;
- pay for conversion;
- value/DRR strategies;
- Maximum Profit;
- later provider strategies.

Provider-native auction algorithms should be exploited when useful; Profit Engine judges them by reconciled K5 and contribution.

## 9. Proxy/value feedback

Direct needs signals it can learn from. Profit Engine should identify Dilivox behaviors that predict monetization value and expose only validated goals/value signals through supported interfaces.

Possible candidates:
- deep story completion;
- next-story continuation;
- high-value session;
- high-value content path;
- return behavior where a suitable conversion representation exists.

A proxy is retired or revalued if it stops predicting later revenue.

## 10. Rule Engine / automated routines

Implement a deterministic Rule Engine before adding opaque ML control.

Examples:
- if data stale -> `QUARANTINE`, no scale;
- if reconciliation error above tolerance -> `DATA_QUALITY_HOLD`;
- if significant downside crosses stop-loss -> pause test;
- if segment is consistently negative -> reduce/stop;
- if creative underperforms credible challenger -> retire/replace;
- if query is irrelevant/low-value -> exclude where supported;
- if K5/confidence/scale capacity pass -> permit bounded increase;
- if requested weekly growth >20% -> `PENDING_OWNER_APPROVAL`.

Rules run on schedules appropriate to data freshness; they must not thrash campaigns with excessive changes.

## 11. Change pacing / learning protection

Automated advertising systems need learning stability.

The engine must:
- limit unnecessary simultaneous changes;
- track strategy learning/change windows;
- avoid interpreting immediate post-change noise as truth;
- use bounded step sizes;
- record conversion/revenue delay;
- compare stable cohorts/windows;
- maintain exploration budget separately from proven scale budget.

## 12. Experiment system

Every material strategy/creative/landing change should be an experiment when practical.

Required:
- control/holdout or comparable test design;
- traffic/spend allocation;
- minimum evidence window;
- primary money metric;
- guardrail metrics;
- auto-pause/stop-loss;
- experiment version;
- decision record.

The system may automatically apply a winner only when predeclared acceptance gates pass.

## 13. Machine launch workflow

For a new Dilivox opportunity:

1. Profit Engine detects candidate intent/content cell.
2. Campaign Factory produces the campaign/group/targeting structure.
3. Creative Factory produces eligible text/image variants.
4. Policy/quality validator rejects invalid variants.
5. Budget Governor assigns bounded learning/test exposure.
6. Direct adapter creates entities in controlled state.
7. Machine launches the bounded test.
8. Data layer measures Direct cost + Dilivox behavior + YAN revenue.
9. Reconciliation validates money.
10. ProfitAllocator decides next capital/action state.
11. Machine pauses, modifies, scales or replaces variants.
12. Cycle repeats.

## 14. Owner interaction contract

The Owner should NOT be asked to:
- create campaigns;
- create groups;
- write routine ad copy;
- upload routine images;
- add routine keywords;
- monitor daily spend;
- pause bad ads;
- choose every bid strategy;
- perform recurring optimization.

Owner is asked only for:
- access/secret/legal/payment actions that cannot be automated;
- budget growth >20% weekly;
- true strategic/business decisions.

## 15. Safety and rollback

Required:
- dry-run plan mode;
- per-provider write switch;
- site/campaign scope allowlist;
- maximum daily/test loss;
- maximum change count per cycle;
- idempotency keys;
- uncertain-response quarantine;
- emergency global pause;
- restore last-known-good configuration;
- immutable audit log.

## 16. Multi-provider future

The Campaign Factory, Creative Factory, ProfitAllocator and Rule Engine are provider-neutral.

Yandex Direct is adapter #1.

Future acquisition providers are added as adapters and compete for capital by expected/realized Owner economics, subject to each provider's policies and capabilities.
