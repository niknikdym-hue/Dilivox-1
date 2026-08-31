# TASK 014 — MANUAL SEARCH PROFIT CONTROLLER

Status: P0 / BUILD FIRST AFTER MONEY TRUTH
Current executor: Central Brain
Campaign concept: `DILIVOX | SEARCH | PROFIT ENGINE`

## Objective

Build a dedicated Yandex Search acquisition loop where Profit Engine controls keyword/autotargeting bids under Owner economics.

Primary objective:

`K5 = attributable YAN revenue / Direct spend`

Provider CTR/CPC/CPA are diagnostics, not the optimization target.

## Provider shape

Dedicated Unified Campaign proposal:

- Search strategy: `HIGHEST_POSITION`;
- network: `SERVING_OFF`;
- explicit Owner-fixed `WeeklySpendLimit` for first live learning;
- exact keyword/autotargeting inventory;
- `KeywordBids.get` for current bid + auction/traffic-volume evidence;
- later `KeywordBids.set` with `SearchBid` only after separate write acceptance.

No live campaign create or bid write is authorized by this task specification alone.

## Phase 1 — read model

Implement exact read-only joins for:

- campaign;
- ad group;
- keyword/autotargeting;
- current SearchBid;
- keyword bid auction/traffic-volume data;
- search query;
- clicks/cost/actual CPC;
- landing/content identity;
- device/time window;
- Metrica behavior;
- YAN revenue evidence;
- weekly spend limit and capital guardroom.

Ambiguous identity => HOLD.

## Phase 2 — attribution grain

Determine the finest defensible economic grain.

Never fabricate keyword-level K5 from campaign-level YAN revenue.

Allowed outputs include:

- exact keyword/query revenue evidence when truly supported;
- cohort/query-cluster/landing attribution with explicit uncertainty;
- campaign-level fallback marked too coarse for bid automation.

## Phase 3 — shadow controller

Deterministic first version. Each decision cell emits exactly one:

- `LEARN`;
- `HOLD`;
- `RAISE_BID`;
- `LOWER_BID`;
- `PAUSE_TERM`;
- `QUARANTINE`;
- `PENDING_OWNER_APPROVAL` where capital authority is implicated.

Required guards:

- minimum evidence/sample thresholds;
- max bid ceiling;
- max per-cycle percentage/absolute bid move;
- spend stop-loss;
- K5 downside threshold;
- stale-data hold;
- attribution-quality hold;
- provider-state hold;
- kill switch;
- exact proposal digest.

## Phase 4 — control-panel integration

Show:

- current bid;
- actual spend/CPC;
- revenue evidence;
- K5/confidence;
- controller recommendation;
- why the recommendation was made;
- allowed next bid range;
- writer state `SHADOW/LOCKED/LIVE`.

## Phase 5 — dedicated campaign factory

Generate a dry-run proposal for `DILIVOX | SEARCH | PROFIT ENGINE` with:

- exact landing set;
- controlled keyword/query universe;
- negative keywords;
- tracking/attribution parameters;
- search-only strategy;
- Owner-fixed initial weekly budget;
- no broad unbounded expansion.

## Phase 6 — guarded create acceptance

Campaign creation is a new mutation family and needs separate acceptance:

- `Campaigns.add`;
- ad groups;
- ads;
- keywords/autotargeting;
- exact moderation state/read-back;
- one-shot/no-blind-retry/audit.

Task-012 suspend/resume authority does not authorize this.

## Phase 7 — guarded bid writer

Accept `KeywordBids.set` only after shadow evidence.

First live bid change:

- exact one keyword/autotargeting target;
- fresh current bid read;
- exact shadow proposal;
- max-step gate;
- Owner-fixed weekly budget remains unchanged;
- one network attempt;
- no blind retry;
- immediate exact read-back;
- immutable audit.

## Phase 8 — supervised learning

Run bounded campaign with human visibility in local panel.

Bid decisions may progress:

`SHADOW -> OWNER_VISIBLE_SUPERVISED -> BOUNDED_AUTOMATIC`

only after accepted live evidence.

## Budget authority

Bid automation and capital automation are separate.

For the initial manual-search campaign:

- weekly budget is Owner-fixed;
- no bid adjustment may raise `WeeklySpendLimit`;
- future automatic weekly budget increase <= +20.00% still requires all Governor gates;
- >= +20.01% requires exact Owner approval.

## Benchmark

After manual search reaches a stable evidence baseline, compare it fairly against native CPC/CPA/DRR/Maximum Profit using reconciled Owner economics.

## Acceptance

Task 014 is not complete until a live search-only campaign can run under a bounded, explainable bid loop with exact read-back, K5 evidence and independent capital governance.
