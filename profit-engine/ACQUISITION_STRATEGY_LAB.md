# PROFIT ENGINE — ACQUISITION STRATEGY LAB

Status: CANONICAL DESIGN / P0 MANUAL SEARCH PRIORITY
Updated: 2026-08-31

## Mission

Profit Engine must determine how to buy traffic based on Owner economics, not habit.

Primary launch objective:

`K5 = attributable YAN revenue / Yandex Direct spend >= 5.0`

Yandex Direct is an execution instrument. Profit Engine uses native provider strategies where they help, but the Owner has now promoted a separate search-only manual-bid strategy to first-priority development because it gives Profit Engine direct control over the main economic lever: the bid paid for each search demand segment.

## P0 owner decision — manual search profit control

The first-priority acquisition-control variant is now:

`DILIVOX | SEARCH | PROFIT ENGINE`

Target shape:

- separate Dilivox campaign, not a retrofit of another product campaign;
- Yandex Search only;
- Unified Campaign search strategy `HIGHEST_POSITION` / «Максимум кликов с ручными ставками»;
- network strategy `SERVING_OFF`;
- explicit `WeeklySpendLimit`;
- explicit keyword/autotargeting bid state through Direct `KeywordBids`;
- Profit Engine, not Yandex native optimization, is the cross-system bid judge;
- primary control objective is reconciled K5, not CTR, traffic volume, CPC, CPA or provider conversion count.

This priority does not authorize an immediate live campaign create or bid write. Task-012 production safety remains authoritative. New campaign creation, strategy configuration and `KeywordBids.set` require their own exact guarded write acceptance before provider execution.

## Why this is P0

Manual search control is closest to the Owner economic target because Profit Engine can observe:

`query/keyword -> bid -> actual CPC/spend -> visitor behavior -> attributable YAN revenue -> reconciled K5`

and then decide the next bid from Owner economics rather than from a proxy goal alone.

The intended long-term control loop is:

`READ -> ATTRIBUTE -> RECONCILE -> SCORE -> PROPOSE BID -> GUARD -> APPLY ONE BOUNDED CHANGE -> READ BACK -> MEASURE`

No bid change is justified by CTR/CPC alone.

## Strategy families

Controlled variants remain eligible for later comparison, but development priority is now ordered:

1. `MANUAL_SEARCH_PROFIT_CONTROL` — search-only manual bids controlled by Profit Engine. **P0 / build first.**
2. `CPC_NATIVE` — provider click-oriented acquisition.
3. `CPA_CLICK` — optimization toward a conversion while payment remains click-based.
4. `CPA_CONVERSION` — payment for conversion.
5. `VALUE/DRR` — value-based or cost-revenue-ratio strategies where supported.
6. `MAX_PROFIT` — Yandex Direct «Максимум прибыли».

No mode is permanently declared the economic winner. The P0 designation is a development priority, not a claim that manual search will beat all provider-native strategies.

## Manual-search control dimensions

The first controller should reason at the smallest useful evidence unit supported by data volume:

`campaign -> ad group -> keyword/autotargeting -> query cluster -> landing -> device -> time window`

The controller may aggregate upward when sample size is insufficient. It must not fabricate keyword-level K5 from campaign-level revenue.

Required read-side inputs:

- exact campaign/ad-group/keyword identity;
- current `SearchBid`;
- Direct auction/traffic-volume data from `KeywordBids.get`;
- clicks, cost and actual CPC from Direct Reports;
- Metrica campaign/search attribution and landing/session behavior;
- YAN revenue and reconciled control totals;
- current weekly budget ownership and remaining guardroom;
- current campaign state and moderation eligibility.

## Bid decision model

The initial controller is deterministic and bounded. Machine learning is not required for first launch.

Each decision cell must produce one of:

- `LEARN` — insufficient evidence; bounded exploratory bid only;
- `HOLD` — keep bid unchanged;
- `RAISE_BID` — increase within accepted per-step and budget limits;
- `LOWER_BID` — decrease within accepted limits;
- `PAUSE_TERM` — stop spend on a persistently bad term after sufficient evidence;
- `QUARANTINE` — attribution/data/compliance anomaly;
- `PENDING_OWNER_APPROVAL` — proposed capital increase crosses Owner authority.

Initial bid changes must be capped per decision cycle. The exact cap will be accepted before `KeywordBids.set` is enabled; until then the bid controller remains shadow/read-only.

## Economic selection rule

The winner is selected by realized Owner economics, not provider vanity metrics.

Primary ranking:

1. reconciled K5;
2. incremental YAN revenue;
3. incremental contribution after acquisition spend;
4. stability across multiple windows;
5. scale capacity;
6. sample sufficiency / uncertainty;
7. user quality and retention;
8. data quality;
9. provider/compliance safety.

CTR, CPC, CPA, conversion rate and auction traffic volume are diagnostic variables only.

## Conversion-goal policy

A conversion goal is useful only if it predicts or represents monetization value.

Candidate Dilivox proxy goals can include:

- story completion;
- next-story click;
- deep-session threshold;
- high-value content path;
- return visit;
- composite high-value-reader event.

Every proxy goal must be periodically validated against later reconciled YAN revenue.

Required evidence chain:

`goal occurrence -> cohort -> later YAN revenue -> estimated monetary value`.

If a goal becomes easy for Direct to optimize but no longer predicts higher revenue, its value must be reduced or the goal removed from acquisition control.

Manual search does not remove this layer; it demotes proxy goals from primary objective to explanatory/predictive features behind K5.

## Test design

Strategy comparison must use isolated experiments where practical.

Each test records:

- experiment ID;
- campaign scope;
- eligible traffic;
- strategy family;
- provider parameters;
- keyword/query universe;
- bid-policy version;
- conversion goal/value configuration;
- start/end;
- spend cap;
- landing/content configuration;
- K5 windows;
- holdout/control where possible;
- stop-loss rules;
- final reconciliation state.

Do not compare strategies when landing pages, targeting and monetization layouts changed simultaneously unless the experiment explicitly tests the whole bundle.

## Cold-start rule

For new/low-data segments, Profit Engine may use bounded manual search exploration because value/conversion models may not yet have enough evidence.

Cold-start traffic receives a small learning budget and a conservative bid ceiling.

It must graduate from `LEARN` only after sufficient evidence.

## Maximum Profit rule

Yandex Direct `Maximum Profit` remains a first-class comparison candidate because it can use provider-side auction signals unavailable to Profit Engine.

Profit Engine should deliberately compare against it after the manual-search baseline is mature enough to be fair.

However, Profit Engine remains the cross-system judge because it sees acquisition cost, Dilivox behavior, YAN monetization, cohort return value, Owner budget policy and alternative experiments.

## Portfolio allocator

Profit Engine ultimately allocates capital across strategy/segment cells, for example:

`campaign x query/keyword x landing x device x strategy`.

Capital flow:

- `LEARN` — small bounded exploration;
- `TEST` — controlled evidence collection;
- `SCALE` — receives more budget when K5/confidence pass;
- `HOLD` — no growth;
- `REDUCE` — bid/budget reduced;
- `STOP` — spend stopped;
- `QUARANTINE` — data/compliance anomaly;
- `PENDING_OWNER_APPROVAL` — growth would violate Owner authority threshold.

## Budget rule

No acquisition strategy can bypass the Budget Governor.

Automatic weekly budget increase up to +20% is possible only when all other guards pass. Any increase above +20% requires explicit Owner approval.

For the first manual-search implementation, weekly budget changes stay separate from bid automation. Bid control may be developed/activated first while the campaign `WeeklySpendLimit` remains Owner-fixed. This prevents bid learning from silently becoming capital expansion.

## Local operator panel — required part of P0

The macOS Profit Engine control panel is part of this P0 line, not optional polish.

Minimum operator view:

- launch/provider status;
- Metrica ↔ YAN monetization-link status;
- Direct campaign state;
- weekly budget and spend;
- YAN revenue;
- observed K5 and confidence/data-quality state;
- keyword/query cells with current bid, spend, revenue attribution and recommended action;
- shadow controller recommendation vs applied state;
- stop-loss/kill-switch status;
- immutable last-action/read-back status.

The panel may expose `Refresh`, `Run read-only check`, `Preview proposal` and guarded action flows. It must not contain an unguarded direct provider-write button.

## P0 implementation sequence

### M0 — Close monetization data gate

Confirm that the newly enabled Dilivox YAN ↔ Metrica link is readable and restore exact money preflight.

### M1 — Manual-search read model

Implement exact read-only campaign strategy inspection plus `KeywordBids.get`, keyword/autotargeting inventory and Direct Reports join. No writes.

### M2 — K5 attribution grain

Determine the finest defensible revenue-attribution grain. If keyword-level YAN revenue is not directly supportable, use query/cohort/landing models with explicit uncertainty and never fabricate precision.

### M3 — Shadow bid controller

Produce deterministic `HOLD/RAISE/LOWER/PAUSE/LEARN/QUARANTINE` recommendations with hard bid caps, sample thresholds, stop-losses and Budget Governor context. No `KeywordBids.set` yet.

### M4 — Local operator panel

Install a localhost-only macOS panel that surfaces the live read model, K5, controller recommendations, gates and exact campaign state. Secrets remain in Keychain/private local config.

### M5 — Campaign factory for dedicated experiment

Generate and validate an exact proposed search-only campaign `DILIVOX | SEARCH | PROFIT ENGINE`: `HIGHEST_POSITION`, network `SERVING_OFF`, explicit `WeeklySpendLimit`, controlled keyword universe, negative keywords, landing binding and tracking parameters. Dry-run first.

### M6 — Guarded campaign creation

Separately accept the Direct `Campaigns.add`/ad-group/ad/keyword create path. One-shot, exact target, no blind retry, read-back/audit. This is not inherited from Task-012 suspend/resume authorization.

### M7 — Guarded bid writer

Accept `KeywordBids.set` for exact one/few bounded keyword targets with preflight, proposal/Governor binding, max step, exact read-back, no blind retry and kill switch.

### M8 — Human-supervised live learning

Run the new campaign with Owner-fixed weekly budget. Profit Engine recommends/applies only accepted bounded bid moves. Evaluate completed-window K5 and stop-losses.

### M9 — Bid automation

Only after sufficient accepted live evidence, allow scheduled automatic bid decisions under the same hard gates. Budget growth remains independently governed.

### M10 — Strategy benchmark

Compare manual-search controller against native CPC/CPA/DRR/Maximum Profit alternatives using reconciled economics.

## Success definition

The P0 manual-search line succeeds when Profit Engine can answer and act safely on:

`For this exact search demand cell, what is the highest defensible next bid that preserves the best expected Owner economics under K5, evidence confidence and budget/safety limits?`

The broader lab succeeds when it can then compare that result fairly against provider-native strategies and allocate the next ruble to the best proven option.
