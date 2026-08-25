# PROFIT ENGINE — CANONICAL PROJECT ENTRY

Status: ACTIVE / AUTHORITY ENTRY
Updated: 2026-08-25
Repository: niknikdym-hue/Dilivox-1
Initial site: https://dilivox.ru

## Purpose

`profit-engine/` is the canonical project direction for an independent multi-site advertising yield and traffic-profit platform.

Dilivox is the first connected site, but the engine MUST be multi-site from day one. Future sites are added as isolated site configurations/adapters while sharing the same analytics, attribution, optimization, safety, and budget-control core.

## North-star objective

For each connected site, maximize legal revenue from standard RСЯ/YAN advertising inventory by combining:

- high-quality real audience acquisition;
- strong content/product engagement;
- accurate attribution of acquisition cost to YAN revenue;
- large-scale experimentation and analytics;
- automatic campaign optimization;
- automatic content recirculation optimization;
- strict owner-controlled budget governance.

Initial Dilivox target:

`1 RUB acquisition spend -> 5 RUB YAN revenue` (`YAN ROAS = 5.0`, `DRR = 20%`).

This is a target to optimize toward, not a fabricated current result. The system must measure actual economics honestly and scale only statistically supported winners.

## Independence principle

The Profit Engine is our own system. Yandex services are external providers/connectors only:

- Yandex Direct = traffic acquisition channel and campaign control API;
- Yandex Metrica = behavioral/attribution/monetization analytics source;
- YAN/RСЯ = advertising inventory and revenue/statistics source;
- Yandex Cloud = recommended hosting/data/secret/observability platform.

Core decision logic, site scoring, LTV attribution, experiment policy, budget governor, anomaly detection, and optimization algorithms belong to Profit Engine and must remain provider-neutral where practical.

## Hard owner budget rule

Automatic weekly budget increase is allowed up to +20% versus the applicable current weekly budget baseline.

Any weekly budget increase above +20% MUST remain `PENDING_OWNER_APPROVAL` and cannot be applied until the owner explicitly approves it.

No optimization score, forecast, ROAS, or emergency mode may bypass this rule.

## Canonical files

Read in this order when resuming the project after any chat/context loss:

1. `profit-engine/PROJECT_STATE.md`
2. `profit-engine/OWNER_DECISIONS.md`
3. `profit-engine/IMPLEMENTATION_PLAN.md`
4. `profit-engine/ARCHITECTURE.md`
5. `profit-engine/YANDEX_CLOUD_ARCHITECTURE.md`
6. `profit-engine/SECURITY_AND_ACCESS.md`
7. `profit-engine/SITE_ONBOARDING.md`
8. site-specific file, beginning with `profit-engine/sites/dilivox/SITE_STATE.md`

## Source-of-truth rule

Chat is not the project source of truth. Decisions that materially change target economics, budget authority, architecture, providers, attribution, or rollout must be written into these repository files. Superseded decisions must be marked as such rather than silently overwritten.

## Secret handling

NEVER commit OAuth tokens, passwords, API secrets, account identifiers that are not intended to be public, or production credentials to this repository. Production secrets belong in Yandex Lockbox (or an equivalent secret manager). Repository files contain secret names and access contracts only.
