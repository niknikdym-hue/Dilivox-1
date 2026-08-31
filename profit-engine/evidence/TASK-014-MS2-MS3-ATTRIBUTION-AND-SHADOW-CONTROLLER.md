# TASK 014 — MS2/MS3 ATTRIBUTION GRAIN + SHADOW BID CONTROLLER

Date: 2026-08-31
State: CODE_ACCEPTED / SHADOW ONLY

## Implementation

- `abe1f5f82c743765363f3fbc0fc514e4146f28c0` — revenue-attribution grain and criterion economics;
- `314986f8ad89e93c10c56e0ea1010f4889abeb78` — bounded deterministic shadow bid controller;
- `c439f7933482b3c9d0c59ba45836d98b368f6772` — regressions;
- CI #193 / `33438030762`: SUCCESS.

## Attribution boundary

Accepted revenue grains:

- `EXACT_CRITERION`;
- `QUERY_CLUSTER` with explicit criterion membership.

Non-automatable grains:

- `LANDING_COHORT`;
- `CAMPAIGN_ONLY`;
- no revenue evidence.

Campaign/landing revenue must never be assigned proportionally to individual criteria merely to manufacture keyword K5.

Exact/cluster evidence must:

- cover the same date window as Direct spend;
- be reconciled;
- carry attribution share >= 0.80 and <= 1.00;
- have non-negative revenue.

Zero spend produces no K5.

## Shadow decisions

Deterministic initial policy emits exactly one:

- `LEARN`;
- `HOLD`;
- `RAISE_BID`;
- `LOWER_BID`;
- `PAUSE_TERM`;
- `QUARANTINE`.

Initial policy defaults:

- target K5 = 5;
- strong K5 = 6;
- weak K5 = 3;
- minimum bid-decision sample = 8 clicks and 20 RUB spend;
- pause evidence = >=20 clicks and >=100 RUB spend with persistently weak K5;
- raise step = max +10% per shadow cycle;
- lower step = max -15% per shadow cycle;
- default bid ceiling = 50 RUB;
- default bid floor = 0.30 RUB.

These are shadow-policy defaults, not permanent production tuning. Any future live writer acceptance may tighten them.

## Safety

Every proposal is:

- `executable=false`;
- `provider_write_allowed=false`;
- digest-bound;
- unable to change `WeeklySpendLimit`;
- unable to call `KeywordBids.set`.

Coarse, unreconciled, low-attribution-share, invalid-identity, or missing-bid data fails to `QUARANTINE/LEARN/HOLD` rather than generating a live bid recommendation.

## Current next manual-search gate

MS4 integrates accepted read/economic/shadow state into the local control panel.

MS5 dedicated campaign dry-run is already implemented in parallel and separately CI-accepted; actual campaign creation remains an MS6 mutation family requiring separate guarded acceptance.
