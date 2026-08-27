# PROFIT ENGINE — LEDGER MATERIALIZATION PREWORK

Status: CENTRAL BRAIN PARALLEL PREWORK / NOT YET CANONICAL
Updated: 2026-08-27
Branch: `central-brain/day8-ledger-materializer`

## Purpose

Prepare the read-only bridge from accepted raw/provider/event facts into the accepted Task-007 acquisition/reconciliation/K5 interfaces without blocking Day-8 Campaign Factory work.

No optimizer logic, provider writes or production data are part of this stream.

## Important gap discovered

Task 007 correctly introduced `MetricaAttributionProfile` and money-ledger attribution grades, but the current Day-4 `MetricaCollector` materializes generic traffic/YAN monetization rows and does not yet emit a dedicated normalized campaign-attribution fact matching the Task-007 profile.

Therefore a production ledger materializer MUST NOT infer campaign attribution from:

- report date;
- tuple position without validated dimension identity;
- campaign name text;
- generic `dimensions.values` with unknown schema.

Until attribution-aware Metrica ingestion exists, fixture-only materialization may be tested, but production cohort/K5 joins must remain held.

## Required safe extension

Add a READ_ONLY attribution-aware Metrica collection/materialization path that:

1. declares an explicit attribution model;
2. requests validated Direct campaign/group/UTM/date dimensions compatible with `MetricaAttributionProfile`;
3. requests YAN revenue/delivery metrics;
4. preserves returned dimension names and values, not only positional values;
5. preserves currency/sampling/accuracy/data-lag/disclosure provenance;
6. produces a provider-neutral attribution fact with explicit fields such as:
   - `site_id`;
   - `occurred_on`;
   - `attribution_model`;
   - `direct_campaign_ref` when returned;
   - `direct_group_ref` when returned;
   - UTM fields when returned;
   - attributed YAN revenue Decimal;
   - delivery metrics;
   - raw snapshot/source ref;
   - source state;
   - data-quality holds;
7. fails closed on incompatible/missing dimensions or unknown money semantics.

No provider write is involved.

## Materializer contract

After normalized attribution facts exist, a generic read-only materializer should:

`immutable normalized facts -> validate source states -> register acquisition -> classify attribution -> aggregate compatible Direct spend -> select Metrica-attributed numerator -> reconcile against YAN control -> derive versioned period/cohort measurements -> persist/emit ledger records`.

Rules:

- no raw history mutation;
- no date-only attribution;
- no Metrica+YAN double-count;
- only Decimal money;
- non-MATCHED reconciliation cannot be optimizer-consumable;
- cohort measurement requires proven acquisition linkage;
- late-arrival recomputation is append-versioned;
- private UTM mappings are injectable and remain outside public Git;
- held upstream facts propagate hold downstream.

## Scheduler/maturity contract

A later scheduler can select windows for recomputation, but commercial thresholds remain outside this public-safe layer.

Generic rules:

- D0/1D/7D/30D windows use explicit site/provider timezone;
- open windows remain held/estimated;
- late-arrival grace is explicit/versioned;
- reconciliation runs are idempotent by scope/window/source-version;
- later provider corrections create new derived version;
- no old derived version or raw snapshot is overwritten.

## Acceptance tests for eventual integration

1. attribution-aware Metrica response preserves named Direct dimensions;
2. missing Direct attribution dimension -> hold, not inferred campaign;
3. Metrica attribution fact joins first-party campaign -> grade A when Direct fact agrees;
4. Metrica-only attribution -> grade C and cannot prove cohort linkage;
5. YAN control is used only for reconciliation;
6. non-MATCHED reconciliation blocks K5 consumption;
7. same immutable inputs -> deterministic materialization/idempotency;
8. late source version -> new derived measurement version;
9. period/cohort measurement remains distinct;
10. all existing Profit Engine CI tests stay green.

## Scheduling

This bridge can be integrated after Task 008 or in parallel before Task 009, because it is public-safe and READ_ONLY. It must be complete before any optimizer is allowed to consume real production money measurements.
