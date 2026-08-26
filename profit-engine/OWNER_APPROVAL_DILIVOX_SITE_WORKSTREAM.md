# OWNER APPROVAL — DILIVOX SITE WORKSTREAM

Status: OWNER-APPROVED / MANDATORY FOR LAUNCH
Date: 2026-08-26
Site: `dilivox`
Branch: `profit-engine`

## Decision

The full Dilivox site-side workstream defined in `profit-engine/DILIVOX_SITE_INTEGRATION.md` is approved by the Owner and is mandatory for Profit Engine launch.

Dilivox is not merely a traffic destination. It is the first complete site-side execution node of the Profit Engine ecosystem.

The launch loop is:

`Yandex Direct -> Dilivox -> user behavior -> YAN/RСЯ ad blocks -> revenue -> attribution/reconciliation -> Profit Engine -> decision -> Direct and/or Dilivox action -> measured money result`.

## Approved mandatory work on Dilivox

1. Full paid-traffic attribution and preservation through the session.
2. Stable machine-readable IDs for stories, pages, content and experiments.
3. First-party behavioral event instrumentation.
4. Money-linked proxy conversions for Yandex Direct only when evidence shows they predict monetization value.
5. Landing-page/story routing optimization by expected cohort economics.
6. Value-based next-story / recirculation optimization.
7. Return-visit and cohort-LTV measurement.
8. Provider-neutral monetization placement registry, with YAN/RСЯ as provider #1.
9. Controlled compliant ad-placement/layout experiments.
10. Site-owned A/B / experiment infrastructure with holdouts, money KPIs and kill switches.
11. Separate mobile/desktop economics and optimization where justified.
12. Performance, reliability and Core Web quality as economic guardrails.
13. Reusable `SiteAgent` contract and first implementation `DilivoxSiteAgent`.
14. Independent site-side kill switches and safe fallback behavior.
15. Full data-quality validation before any money-moving automation.
16. Closed-loop execution where Profit Engine can change approved acquisition and site-side variables and measure the realized monetary outcome.

## Money-first acceptance rule

No Dilivox site change is considered successful merely because it improves CTR, page views, session duration, completion, ad impressions or another intermediate metric.

A production winner must show a credible causal path to improved money economics, primarily:

- higher attributable YAN/RСЯ revenue;
- higher revenue per acquired visitor/user;
- higher K5;
- lower acquisition cost for equally or more valuable traffic;
- lower loss / better capital protection;
- or improved long-term cohort value without violating provider rules or damaging the product.

## Launch gate

Profit Engine is not considered launched as a complete first-site ecosystem until the Dilivox site-side workstream is integrated into the same measured control loop as Yandex Direct, Metrica and YAN/RСЯ.

The canonical detailed implementation specification remains:

`profit-engine/DILIVOX_SITE_INTEGRATION.md`

This approval converts that specification from design-only material into an Owner-approved mandatory launch workstream.
