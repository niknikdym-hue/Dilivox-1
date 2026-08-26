# PROFIT ENGINE — ACQUISITION STRATEGY LAB

Status: CANONICAL DESIGN / EXPERIMENT POLICY
Updated: 2026-08-26

## Mission

Profit Engine must determine how to buy traffic based on Owner economics, not habit.

Primary launch objective:

`K5 = attributable YAN revenue / Yandex Direct spend >= 5.0`

Yandex Direct is an execution instrument. Profit Engine uses its native strategies when they help reach the Owner's target and replaces/reconfigures a strategy when realized economics show a better option.

## Strategy families

Where campaign type, data volume and Yandex Direct eligibility allow, compare controlled variants of:

1. `CPC` — click-oriented acquisition / payment for clicks.
2. `CPA_CLICK` — optimization toward a conversion while payment remains click-based.
3. `CPA_CONVERSION` — payment for conversion.
4. `VALUE/DRR` — value-based or cost-revenue-ratio strategies where supported.
5. `MAX_PROFIT` — Yandex Direct «Максимум прибыли».

No mode is permanently preferred.

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

CTR, CPC, CPA and conversion rate are diagnostic variables only.

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

## Test design

Strategy comparison must use isolated experiments where practical.

Each test records:

- experiment ID;
- campaign scope;
- eligible traffic;
- strategy family;
- provider parameters;
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

For new/low-data segments, Profit Engine may use click-oriented exploration because value/conversion models may not yet have enough evidence.

Cold-start traffic receives a bounded learning budget.

It must graduate from `LEARN` only after sufficient evidence.

## Pay-for-conversion rule

Pay-for-conversion is not automatically safer or more profitable.

Before it can scale:

- the goal must represent a valuable user action;
- the goal-to-revenue relationship must be validated;
- realized K5 must beat or justify the alternative strategy;
- conversion eligibility and provider restrictions must be satisfied.

## Maximum Profit rule

Yandex Direct `Maximum Profit` is a first-class candidate because it can use provider-side auction signals unavailable to Profit Engine.

Profit Engine should deliberately exploit this capability when useful.

However, Profit Engine remains the cross-system judge because it sees:

- acquisition cost;
- Dilivox behavior;
- YAN monetization;
- cohort return value;
- owner budget policy;
- alternative campaign/site experiments.

`Maximum Profit` may win and become the active strategy if reconciled evidence shows that it best serves the Owner target.

## Portfolio allocator

Profit Engine ultimately allocates budget across strategy/segment cells, for example:

`campaign x audience/query x landing x device x strategy`.

Capital flow:

- `LEARN` — small bounded exploration;
- `TEST` — controlled evidence collection;
- `SCALE` — receives more budget when K5/confidence pass;
- `HOLD` — no growth;
- `REDUCE` — budget reduced;
- `STOP` — spend stopped;
- `QUARANTINE` — data/compliance anomaly;
- `PENDING_OWNER_APPROVAL` — growth would violate Owner authority threshold.

## Budget rule

No acquisition strategy can bypass the Budget Governor.

Automatic weekly budget increase up to +20% is possible only when all other guards pass.

Any increase above +20% requires explicit Owner approval.

## Implementation phases

### A0 — Observe

Read current Direct strategies, spend and outcomes. No writes.

### A1 — Baseline

Calculate K5 by existing campaign/strategy/segment.

### A2 — Proxy-value validation

Identify behavioral events that truly predict YAN revenue.

### A3 — Controlled CPC/CPA tests

Run bounded experiments comparing click and conversion-oriented approaches.

### A4 — Native profit/value tests

Evaluate value/DRR/Maximum Profit strategies where eligible.

### A5 — Strategy allocator

Automatically select/allocate among proven strategy cells under Budget Governor.

## Success definition

The lab succeeds when Profit Engine can answer with reconciled evidence:

`For this traffic/content segment, which Yandex Direct buying strategy turns the next ruble of spend into the most owner revenue/profit, and how much capital should it receive?`
