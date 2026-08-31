# TASK 014 — MS5 DEDICATED MANUAL SEARCH CAMPAIGN DRY-RUN

Date: 2026-08-31
State: CODE_ACCEPTED / NON-EXECUTABLE

## Campaign concept

Exact name:
`DILIVOX | SEARCH | PROFIT ENGINE`

Provider proposal shape:

- Unified Campaign;
- Search `HIGHEST_POSITION`;
- Network `SERVING_OFF`;
- Owner-fixed initial `WeeklySpendLimit`;
- controlled keyword universe, capped to 100 terms in P0 dry-run;
- autotargeting default OFF until separately tested;
- default canonical monetization-eligible landing: `/istorii/`;
- canonical Direct tracking parameters for campaign/ad/group/criterion/keyword + UTM.

## Implementation

- `6f455b8e99eac42c33c7526ee653a4cd96215780` — dedicated campaign preview builder;
- `d1112f1e82a198f1b51d296d15e3a2c12f5c4231` — CLI;
- `571e0c1cf89290e73b13f53896ae9daef47829b8` — tests;
- CI #190 / `33437766741`: SUCCESS.

## Safety

The preview is deterministic but inert:

- `provider_requests=0`;
- `advertising_spend=0`;
- `provider_write_allowed=false`;
- `create_authorized=false`;
- every factory intent `executable=false`.

No `Campaigns.add`, ad-group, ad, keyword or moderation provider call exists in this acceptance.

## Next gate

MS6 is a separate guarded campaign-creation mutation family. It must prove exact Direct v501 request shapes, target binding, Owner-fixed budget, one-shot/no-blind-retry dispatch, read-back and audit before any real dedicated campaign may be created.
