# TASK 014 — MS1 MANUAL SEARCH READ MODEL

Date: 2026-08-31
State: CODE_ACCEPTED / LIVE DEDICATED CAMPAIGN NOT YET CREATED

## Owner priority

Manual search control is a P0 development line for Dilivox because it exposes the bid as an explicit Profit Engine-controlled economic lever while K5 remains the owner objective.

## Implementation

Runtime:
`profit-engine/runtime/profit_engine_runtime/manual_search_read_model.py`

CLI:
`profit-engine/runtime/profit_engine_runtime/manual_search_read_model_cli.py`

Tests:
`profit-engine/runtime/tests/test_manual_search_read_model.py`

Implementation chain:

- `d8a910ac428fb9354eb42b32654a8d6e8c4b1cc9` — exact read model;
- `ba5a2fef9bd274c3028171982f30887175c570f7` — CLI;
- `fd4158a05af0d31ee24a754985c4ecd5d467676d` — regressions;
- CI #179 / `33437117719`: SUCCESS.

## Exact provider assumptions

The model requires before keyword/bid reads:

- campaign type `UNIFIED_CAMPAIGN`;
- Search `BiddingStrategyType=HIGHEST_POSITION`;
- Network `BiddingStrategyType=SERVING_OFF`;
- exact `HighestPosition.WeeklySpendLimit`.

Any mismatch holds before deeper reads.

It then performs only read operations:

1. exact `Campaigns.get`;
2. bounded `Keywords.get` up to 10,000 objects;
3. bounded `KeywordBids.get` up to 10,000 objects with Search `Bid`, `AutotargetingSearchBidIsAuto`, and `AuctionBids`;
4. bounded `CRITERIA_PERFORMANCE_REPORT` for exact campaign/date window with CriterionId, impressions, clicks, cost and AvgCpc.

Provider monetary bid values are converted from Direct micro-units explicitly.

## Economic precision boundary

MS1 does **not** assign revenue or K5 to individual keywords.

Every read cell currently emits:

- actual search bid;
- auction bid/price levels;
- current state/status/serving status;
- impressions;
- clicks;
- cost;
- average CPC;
- `revenue_rub=null`;
- `k5=null`;
- `economic_grain_state=REVENUE_ATTRIBUTION_NOT_JOINED_YET`.

This is intentional fail-closed behavior. Task 014 MS2 must determine the finest defensible revenue-attribution grain before any bid recommendation can claim K5 evidence.

## Write boundary

- `provider_write_allowed=false`;
- `provider_write_requests=0`;
- no `KeywordBids.set` implementation is present in MS1;
- no campaign creation is authorized;
- no weekly budget mutation is authorized.

## Next phase

`MS2_ATTRIBUTION_GRAIN` — join the search-demand read model to defensible Metrica/YAN/cohort revenue evidence without fabricated keyword precision.
