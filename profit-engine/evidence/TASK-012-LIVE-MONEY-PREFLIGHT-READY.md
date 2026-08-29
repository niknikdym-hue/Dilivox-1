# TASK 012 — LIVE MONEY PREFLIGHT READY

Date: 2026-08-29
Status: CENTRAL BRAIN VERIFIED / READ-ONLY CODE READY / NO LIVE MUTATION

## Objective

Before Central Brain selects the first real Direct candidate, the launch path must observe money from all three production sources over the exact same date window:

1. exact Direct campaign spend;
2. Metrica YAN revenue attributed to that exact Direct campaign under last Direct click;
3. YAN Statistics revenue for exact `dilivox.ru` as the independent control total.

The result is either an observed K5 suitable for candidate evaluation or an explicit data-quality HOLD. It never authorizes a provider write.

## Implementation

Runtime:
`profit-engine/runtime/profit_engine_runtime/day12_money_preflight.py`

Implementation commit:
`bfd517ab1a654c14edc0880c55bbdc014c6d267e`

Regression tests:
`profit-engine/runtime/tests/test_day12_money_preflight.py`

Initial test commit `c3e751c09566ae5871e1d19ad7c928450b6cde63` exposed a test-harness naming collision (`run` overriding `unittest.TestCase.run`) before the money probe tests could execute. That run `33266341506` failed and is NOT acceptance evidence.

The helper collision was corrected in:
`a72f9060c6089e12f5647e70840bbdd14beae439`

Exact CI `33266404903` on `a72f9060c6089e12f5647e70840bbdd14beae439`: SUCCESS.

Secret-safe local CLI:
`profit-engine/runtime/profit_engine_runtime/day12_money_preflight_cli.py`

CLI implementation/test chain:
- `8e6bb52af38c6c02d75c5ef5f361704c4949e4ea` — loads the exact private Dilivox configuration and existing credential references, runs the read-only three-provider money preflight and prints only safe economics/evidence;
- `bc2126e61990d9b230d7677e1c5bd671632c88c3` — tests prove missing config/credentials and operator-target aliasing fail before provider calls, while token values never appear in output.

Exact CLI CI `33266505126` on `bc2126e61990d9b230d7677e1c5bd671632c88c3`: SUCCESS.

## Direct spend authority

The Day-12 money preflight does not rely on the older ingestion collector URL.

It uses the current official Reports endpoint:
`https://api.direct.yandex.com/json/v501/reports`

Direct request properties:
- exact managed advertiser `Client-Login`;
- exact one-campaign `CampaignId` filter;
- fields `Date`, `CampaignId`, `Clicks`, `Cost`;
- `returnMoneyInMicros=false`;
- `IncludeVAT=YES`;
- `IncludeDiscount=YES`;
- bounded read-only report polling: 1..5 attempts;
- any unexpected campaign ID fails closed.

The older `DirectCollector` in `collectors.py` currently contains a legacy/wrong reports host and is not Day-12 launch authority until separately reworked.

## Metrica attribution authority

Exact counter: `110349067` from private live configuration.

Dimensions:
- `ym:s:date`;
- `ym:s:last_yandex_direct_clickDirectClickOrder`.

Metrics:
- `ym:s:yanPartnerPrice`;
- `ym:s:yanRequests`;
- `ym:s:yanRenders`;
- `ym:s:yanShows`.

Only rows whose Direct campaign dimension exactly equals the candidate campaign ID are accumulated. Full accuracy is requested. Sampled or sensitive-data-restricted results produce a HOLD.

## YAN control authority

The Statistics API request is restricted to exact domain `dilivox.ru`, exact date window, RUB and Europe/Moscow.

Control fields:
- `partner_wo_nds`;
- `hits`;
- `hits_render`;
- `shows`.

Any unexpected domain fails closed.

## Output states

- `READY_FOR_CANDIDATE_EVALUATION`;
- `NO_DIRECT_SPEND`;
- `HOLD_DATA_QUALITY`.

Observed K5 is computed only when Direct spend is strictly positive:

`K5_observed = Metrica-attributed YAN revenue / exact Direct campaign spend`.

Zero spend never becomes an infinite/fake K5; the result is `NO_DIRECT_SPEND` and K5 is null.

Metrica attributed revenue is reconciled against the independent YAN site control total. Material impossible excess, ambiguous money/currency basis, sampled Metrica data or sensitive-data restrictions produce `HOLD_DATA_QUALITY`.

## CLI output contract

The local CLI outputs only:
- exact campaign/date identity;
- state and HOLD reasons;
- Direct spend;
- Metrica-attributed YAN revenue;
- YAN control revenue;
- observed K5 and attributed share;
- secret-safe Direct RequestId/Units where available;
- evidence digest;
- explicit `provider_write_allowed=false`.

No OAuth/token value is printed.

## Safety result

- provider_write_allowed: always false;
- real Direct mutation requests: 0;
- advertising spend caused by this work: 0;
- Yandex permissions changed: 0;
- no tokens stored in repository/evidence;
- no candidate is selected by this preflight itself.

## Launch interpretation

After Owner Editing is confirmed and exact live readiness passes, this preflight/CLI is the canonical Day-12 money input for candidate evaluation. A campaign with money HOLD is not eligible for SCALE/TEST. Safety STOP/HOLD remains governed by the accepted safety chain and exact live evidence.
