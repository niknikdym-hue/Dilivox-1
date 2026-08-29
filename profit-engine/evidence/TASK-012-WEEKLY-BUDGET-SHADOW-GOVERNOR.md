# TASK 012 — WEEKLY BUDGET SHADOW GOVERNOR

Date: 2026-08-29
Status: CENTRAL BRAIN VERIFIED / READ-ONLY M6 COMPATIBILITY READY / LIVE BUDGET WRITE BLOCKED

## Scope

This checkpoint connects current Direct `WeeklySpendLimit` truth to the already accepted Profit Engine ActionProposal + Budget Governor contracts without creating a provider mutation path.

It exists to replace legacy `DailyBudget` assumptions safely before any future budget automation is enabled.

## Advisory layer

Runtime:
`profit-engine/runtime/profit_engine_runtime/direct_weekly_budget_advisory.py`

Commits:
- `fa25382faebe94011c56475c83d22b727bdeb208` — advisory states from exact read-only WeeklySpendLimit inspection;
- `828bbe14544efe38236672669b1cee567b2aefe4` — advisory regressions.

CI `33266082953`: SUCCESS.

Advisory states:
- `READY_FOR_SHADOW_PLAN`;
- `PENDING_OWNER_APPROVAL`;
- `HOLD_NO_WEEKLY_SPEND_LIMIT`;
- `HOLD_AMBIGUOUS_BUDGET_SCOPE`;
- `HOLD_PACKAGE_STRATEGY_SCOPE`;
- `HOLD_INVALID_PROVIDER_SHAPE`.

Every state keeps `provider_write_allowed=false`.

## Governor binding

Runtime:
`profit-engine/runtime/profit_engine_runtime/direct_weekly_budget_governor.py`

Commits:
- `569519bafd144e9e9416849a5dcbb3849d915e89` — exact advisory / ProviderTarget / ActionProposal / Governor binding;
- `acfd0fb7920502383809795b2bada56396deac16` — Governor binding regressions.

CI `33266159339`: SUCCESS.

The bridge requires:
- exact campaign ProviderTarget;
- exact campaign ID equality with the live WeeklySpendLimit probe;
- integrity-valid ActionProposal;
- proposal current/proposed weekly budgets exactly equal the live advisory plan;
- proposal Owner-approval flag exactly equals the live advisory requirement;
- Governor `increase_percent` exactly equals the live calculation;
- Governor remains read-only (`provider_write_allowed=false`, provider requests 0, advertising spend 0).

## Owner +20% boundary

The already locked owner policy is preserved exactly:
- +20.00% may reach `SHADOW_GOVERNOR_READY` when all other gates pass;
- +20.01% must remain `PENDING_OWNER_APPROVAL`;
- a Governor claiming ready state above +20% is rejected;
- no advisory/Governor state authorizes a Direct write.

## Package/portfolio strategy safety

When `PackageBiddingStrategy` is present, individual campaign budget control remains `HOLD_PACKAGE_STRATEGY_SCOPE`. The bridge cannot override that HOLD.

## Live budget decision

There is still NO accepted `Campaigns.update` budget mutation request builder or writer.

The first engineering launch remains restricted to one reversible `campaign/ad suspend|resume` action. Strategy-aware budget writes require a later separate acceptance proving exact update shape, package ownership, Owner approval, preflight/TOCTOU, one-shot dispatch, read-back and rollback semantics.

## Provider impact

- Direct budget mutations: 0;
- provider writes: 0;
- advertising spend caused by this work: 0;
- Yandex permission changes: 0.
