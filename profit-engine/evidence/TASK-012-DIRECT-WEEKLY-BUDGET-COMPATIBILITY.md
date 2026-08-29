# TASK 012 — DIRECT WEEKLY BUDGET COMPATIBILITY

Date: 2026-08-29
Status: CENTRAL BRAIN VERIFIED / READ-ONLY CAPABILITY READY / LIVE BUDGET WRITE STILL BLOCKED

## Why this rework exists

The accepted Day-11 synthetic controller modeled campaign budget changes through legacy `DailyBudget` semantics. Current Yandex Direct API documentation states that campaign daily budgets have moved to a unified weekly format and that `DailyBudget` stops working from August 22. Current strategy structures expose `WeeklySpendLimit` in integer micros.

Therefore the Day-11 DailyBudget path must never be used as a production mutation request.

## Current API authority adopted by Profit Engine

Current Campaigns.get supports the production campaign types:
- TEXT_CAMPAIGN;
- MOBILE_APP_CAMPAIGN;
- CPM_BANNER_CAMPAIGN;
- UNIFIED_CAMPAIGN.

For Text/MobileApp/Unified campaigns, type-specific reads expose `BiddingStrategy` and `PackageBiddingStrategy`. For CPM banner campaigns, `BiddingStrategy` is readable.

If `PackageBiddingStrategy` is present, the budget/strategy is not treated as campaign-owned. Profit Engine fails closed and requires separate package-strategy scope rather than attempting an individual campaign budget change.

## Implementation

Read-only strategy planner:
`profit-engine/runtime/profit_engine_runtime/direct_weekly_budget.py`

Capabilities:
- `EXACT_ONE_SLOT`;
- `NO_WEEKLY_SPEND_LIMIT`;
- `AMBIGUOUS_MULTIPLE_SLOTS`;
- `PACKAGE_STRATEGY_REQUIRES_SEPARATE_SCOPE`;
- `INVALID_PROVIDER_SHAPE`.

The planner:
- discovers observed `WeeklySpendLimit` slots only from the returned strategy structure;
- converts integer micros to exact Decimal weekly amount;
- refuses absent/malformed/ambiguous budget ownership;
- refuses package/portfolio strategy ownership at campaign scope;
- converts a proposed Decimal amount back to exact integer micros;
- preserves the hard Owner boundary: +20.00% does not require extra approval, +20.01% does;
- always returns `provider_write_allowed=false`.

Exact read-only provider probe:
`profit-engine/runtime/profit_engine_runtime/direct_weekly_budget_probe.py`

The probe:
- requires exact managed advertiser binding;
- requests exactly one campaign ID through `Campaigns.get`;
- requests `Id`, `Type`, `State`, `Status` plus supported type-specific `BiddingStrategy` / `PackageBiddingStrategy` fields;
- requires the exact requested campaign in the response;
- forwards the exact provider object to the fail-closed planner;
- performs no mutation.

## Verification

Implementation/test chain includes:
- `4847276189a7695732d29e17d10e6da61d7bdccd` — canonical digest fix for planner integrity;
- `8cbf0be3...` predecessor package-strategy hold implementation is represented by the current canonical module;
- `bf050ad02f3f18ed9e16f73e5c3c81fd8181adce` — package-strategy regression tests;
- `0270fd7b2ba68b04ddd552bbd38a7a165547e00e` — exact read-only campaign probe;
- `734f8a76f10c81f4a3e341fe1019e39feeebe268` — probe tests.

CI:
- `33265419324`: SUCCESS after planner digest correction;
- `33265550485`: SUCCESS for package-strategy HOLD;
- `33265613094`: SUCCESS for exact read-only provider probe;
- integrated later CI `33265790511`: SUCCESS with the production-writer hardening on the same branch.

## Safety decision

Budget production writes remain disabled.

No `Campaigns.update` budget request builder or mutation transport is authorized by this evidence. A future budget-write phase must separately prove the exact strategy-specific update shape, package-strategy ownership rules, fresh provider state, Governor binding, the Owner >20% approval contract, write/read-back semantics and rollback/recovery behavior.

This rework does NOT block the first engineering launch because Day 12 first-live execution is deliberately limited to one reversible `campaign/ad suspend|resume` action selected from accepted evidence.

## Provider impact

- real Direct mutation requests: 0;
- advertising spend caused by this work: 0;
- Yandex permissions changed: 0.
