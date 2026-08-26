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

## OD-004 — Independence

Profit Engine is an independent owner-controlled system. Yandex services are external infrastructure/data/control providers. Yandex does not define the engine's architecture, optimization policy, ownership, or business logic.

## OD-005 — Automation priority

Maximum practical automation is required, including automated data collection, attribution, analysis, forecasting, anomaly detection, experiment evaluation, Direct campaign control, budget redistribution, and recommendations.

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

Do NOT disclose strategic or commercially sensitive Profit Engine information unless technically or legally required, including:

- the internal `1 RUB -> 5 RUB` economic target;
- YAN ROAS/LTV targets or optimization economics;
- internal scoring, forecasting, allocation, scaling, or recommendation algorithms;
- multi-site commercial strategy;
- owner-specific budget governance details beyond what is necessary for the requested provider operation;
- internal data architecture or provider-neutral design details that are not required for certification.

For Direct API certification, disclose only the minimal truthful information needed to explain Direct API use: requested functions, protocol/language, authentication, basic interaction flow, current development stage, and credential handling.

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

No Direct strategy receives permanent authority merely because it is branded as automated or profit-maximizing.

## OD-014 — Dilivox is the reference ecosystem implementation

Dilivox is not merely a landing site receiving traffic. It is the first full site-side execution node of Profit Engine.

The first complete closed-loop ecosystem is:

`Acquisition provider -> Dilivox site instrumentation/experience -> monetization provider -> attribution/reconciliation -> Profit Engine decision -> acquisition/site action -> measured outcome`.

We develop and prove this ecosystem on Dilivox first, then connect additional owner sites through the same shared contracts and site adapters without rewriting the common core.

Dilivox-specific code and content rules must remain separated from reusable Profit Engine interfaces.
