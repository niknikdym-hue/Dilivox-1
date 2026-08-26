# PROFIT ENGINE — OWNER DECISIONS

Status: CANONICAL / ACTIVE
Updated: 2026-08-26

## OD-001 — Economic target

Initial Dilivox optimization target is:

`1 RUB traffic acquisition spend -> 5 RUB YAN/RСЯ advertising revenue`

Equivalent target: `YAN ROAS = 5.0` / `DRR = 20%`.

This target remains active until explicitly superseded by the owner.

## OD-002 — Revenue scope

For this engine, the target revenue stream is revenue from standard YAN/RСЯ advertising blocks placed on connected sites. Other monetization streams are outside this engine's target metric unless separately added later.

## OD-003 — Legal/white-hat operation

The project is a normal lawful optimization and analytics system for high-quality sites and real users. No bots, click stimulation, motivated ad interactions, artificial impressions, or manipulation of ad systems are part of the design.

## OD-004 — Yandex role: execution instrument, not project goal

The Owner defines the economic objective. Profit Engine owns the cross-system business logic, capital-allocation rules, measurement, experimentation, and decisions required to achieve that objective.

Yandex is an important execution and data instrument used by Profit Engine where it is economically useful:

- Yandex Direct = traffic-acquisition and provider-native bidding/optimization instrument;
- Yandex Metrica = attribution, behavior and monetization-measurement instrument;
- YAN/RСЯ = first monetization provider and revenue source;
- Yandex Cloud = preferred operational infrastructure for the first production implementation.

Profit Engine does NOT attempt to replace provider auction algorithms merely for architectural independence. It should deliberately use Yandex's native algorithms when they improve the Owner's economics.

At the same time, Yandex does not set the Owner's economic target and does not have final authority over Profit Engine's cross-system allocation logic.

Canonical hierarchy:

`OWNER ECONOMIC GOAL -> PROFIT ENGINE -> YANDEX AND OTHER EXECUTION TOOLS -> MEASURED RESULT -> PROFIT ENGINE`.

The question is never «how do we replace Yandex?».

The question is:

`How do we use Yandex and every other available tool most effectively to reach and exceed the Owner's profit target?`

## OD-005 — Automation priority

Maximum practical automation is required, including automated data collection, attribution, analysis, forecasting, anomaly detection, experiment evaluation, Direct campaign control, budget redistribution, creative routine, and recommendations.

## OD-006 — Budget authority

Automatic weekly budget increase is permitted only up to +20% against the applicable current weekly budget baseline.

Any increase above +20% MUST:

1. be proposed by the engine;
2. show supporting evidence, expected impact, and risk;
3. receive explicit owner approval;
4. remain blocked until that approval is recorded.

This is a hard invariant and cannot be bypassed by any optimizer or administrator automation.

## OD-007 — Multi-site platform

The engine must support multiple owner sites from the beginning. Dilivox is the first connected site only.

New sites must be onboarded via site configuration/adapters and isolated credentials/data partitions, without forking or rewriting the optimization core.

## OD-008 — Cloud direction

Preferred production environment is Yandex Cloud for operational simplicity, locality of the surrounding ecosystem, managed database/secrets/observability, and straightforward integration. Business logic remains portable and provider-neutral where practical.

## OD-009 — Chat is not source of truth

Repository authority files are the source of truth for project decisions and state. Material decisions must be committed. Replaced decisions are marked `SUPERSEDED`, not silently deleted.

## OD-010 — Technical Yandex identity

The owner's existing second Yandex ID is designated as the preferred technical identity for Profit Engine, subject to access-compatibility checks in Direct, Metrica, and YAN.

The owner's primary Yandex ID remains the ownership/control identity.

The technical Yandex ID is used for delegated operational access and OAuth/API authorization where supported. The engine must never require or store the owner's primary Yandex password, and production OAuth/API credentials must be kept in Lockbox or an equivalent secret manager rather than GitHub.

## OD-011 — External disclosure minimization

External providers, including Yandex, receive only the information strictly required to provision, certify, operate, or troubleshoot the specific provider integration.

Do NOT disclose strategic or commercially sensitive Profit Engine information unless technically or legally required, including the internal 5:1 target, internal scoring/forecast/allocation algorithms, multi-site commercial strategy, or unnecessary architecture details.

## OD-012 — PROFIT-FIRST operating doctrine

Profit Engine is a hard machine directed at making money.

Analytics, AI, reports, dashboards, experiments and automation are tools, not product goals.

Every production capability must have a credible path to at least one of:

- increase attributable monetization revenue;
- reduce the cost of acquiring valuable traffic;
- increase monetization value per legitimate visitor;
- stop or reduce loss-making spend;
- reallocate money toward more profitable segments;
- discover new scalable profit pools;
- protect capital and earned revenue from fraud, provider sanctions, data errors or uncontrolled budget growth.

Canonical operating order:

`PROTECT CAPITAL -> MEASURE MONEY -> STOP LOSSES -> FIND PROFIT -> SCALE PROFIT -> REPEAT`

Vanity metrics are never the final optimization target.

## OD-013 — Acquisition payment/optimization model is not preselected

Profit Engine must not hard-code a permanent assumption that Yandex Direct traffic should be purchased only by clicks or only by conversions.

The acquisition strategy itself is an optimization variable.

Where Direct capabilities, data volume and campaign eligibility allow, Profit Engine must be able to compare controlled strategies including:

- click-based acquisition / CPC;
- conversion-optimized acquisition with payment for clicks;
- pay-for-conversion acquisition;
- cost-revenue-ratio / value-based variants;
- Yandex Direct `Maximum Profit` strategy;
- later, other provider-native bidding strategies.

The winner is selected by observed Profit Engine economics, primarily K5 and realized incremental profit, not by the provider's internal KPI alone.

## OD-014 — Dilivox is the reference ecosystem implementation

Dilivox is not merely a landing site receiving traffic. It is the first full site-side execution node of Profit Engine.

The first complete closed-loop ecosystem is:

`Acquisition provider -> Dilivox site instrumentation/experience -> monetization provider -> attribution/reconciliation -> Profit Engine decision -> acquisition/site action -> measured outcome`.

We develop and prove this ecosystem on Dilivox first, then connect additional owner sites through the same shared contracts and site adapters without rewriting the common core.

## OD-015 — Advertising operations are machine-operated — APPROVED

Advertising operations are machine-operated end-to-end. The Owner is not the routine operator of Yandex Direct.

After guarded write access is enabled and all safety/data gates pass, Profit Engine must itself perform recurring advertising operations through supported APIs/provider mechanisms, including where technically supported:

- create campaigns;
- create and maintain ad groups;
- create/version/maintain ads;
- prepare and populate approved headlines, descriptions, links and tracking parameters;
- upload/select/attach approved images and creative assets;
- configure targeting, geography, schedules and eligible campaign settings;
- select/configure CPC, conversion, value/DRR, Maximum Profit and other eligible native strategies using economic evidence;
- configure approved conversion goals and values;
- start, pause, resume and stop campaigns/groups/ads/strategy cells;
- create bounded campaign/creative/strategy experiments;
- suppress losing variants and segments;
- redistribute budget toward validated winners;
- scale profitable cells within Budget Governor limits;
- keep an immutable audit trail and rollback path for every write action.

Routine creative production is also to be automated as far as practical. The system should use controlled templates, the Dilivox content registry, approved source assets and machine-generated variants subject to automated quality/policy gates. The Owner is not expected to manually write routine ads or attach images.

The Owner is involved only when an action genuinely requires owner authority, including permissions/secrets, legal/payment/account-owner actions, weekly budget growth above +20%, or a true strategic decision escalated by Central Brain.

## OD-016 — Central Brain leads and executes the launch — APPROVED

Central Brain is the project brain, project lead, acceptance authority and active executor.

Central Brain must:

- maintain canonical repository authority/state;
- derive the next task from actual repository/provider state;
- perform directly all work available through its tools/capabilities;
- create one complete Codex task contract when engineering/local/deployment work is required;
- inspect Codex evidence and repository changes;
- accept/reject/rework the result against explicit gates;
- update canonical state after acceptance;
- immediately issue the next task in the launch plan without restarting discussion;
- escalate to the Owner only for actions or decisions that genuinely require Owner authority.

Codex is an engineering executor, not the project brain and not an independent product decision maker.

## OD-017 — Full Dilivox workstream is launch-critical — APPROVED

The complete Dilivox site-side Profit Engine workstream defined in `DILIVOX_SITE_INTEGRATION.md` is mandatory launch scope, including attribution, stable content IDs, first-party events, monetization placement registry, experiment SDK, recirculation/return-value optimization, proxy conversions, performance/quality measurement, kill switches and closed-loop site actions.

Profit Engine launch is not complete if only provider connectors or a dashboard exist.

## OD-018 — Local workspace separation — APPROVED

The existing Dilivox site workspace and the Profit Engine workspace are separate and must remain separate.

Existing site workspace:

`~/Documents/New project/Dilivox`

Canonical Profit Engine workspace:

`~/Documents/New project/Profit Engine/Dilivox-1`

The existing Dilivox folder must not be deleted, reset, overwritten, moved or repurposed as the Profit Engine clone. Codex may inspect it read-only when required to understand the current site implementation. All Profit Engine implementation work that requires a local Git working copy uses the canonical Profit Engine workspace unless a later Owner decision explicitly supersedes this rule.
