# TASK 010R — Cohort materialization truth gate

## Status

- Rework implementation: `COMPLETE`, pending Central Brain acceptance.
- Baseline: `78c6d6b121f72ad60dabd3a0aa5cda79f7e84e92`.
- Final public SHA/CI: reported after commit and push.

## Corrected semantic boundary

`MetricaAttributionFact` is campaign/day period evidence. It may feed `period_K5` when its existing attribution, money, provenance and reconciliation gates pass. It is never automatically used as a cohort numerator.

Without explicit cohort linkage proof, `K5_1D`, `K5_7D`, and `K5_30D` now have:

- `value=None`;
- `numerator=None`;
- `state=NOT_COMPUTABLE`;
- `NOT_COMPUTABLE_ATTRIBUTION_HOLD`;
- `optimizer_consumable=false`.

No campaign-name, date-only, positional dimension, missing-day, zero-fill, ClientID, PII, or arbitrary mapping inference exists.

## CohortRevenueEvidence v1

The immutable public contract binds:

- site/cohort identity;
- exact 1D, 7D, or 30D window and boundaries;
- attributed cohort revenue as `Decimal`;
- currency, money basis and timezone;
- source finality and reconciliation state;
- immutable source and explicit linkage evidence refs/basis;
- maturity and late-arrival state;
- holds and deterministic digest.

Materialization verifies evidence digest integrity, rejects conflicting duplicate windows, and context-checks site, cohort ref, dates, currency, basis, and timezone.

## Computation proof

Synthetic fixtures use original acquisition spend `10 RUB`:

| Explicit evidence | Cohort numerator | Result |
|---|---:|---:|
| D0 / 1D | 4 RUB | `K5_1D=0.4` |
| D0..D0+6 / 7D | 12 RUB | `K5_7D=1.2` |
| D0..D0+29 / 30D | 20 RUB | `K5_30D=2.0` |

Providing only 1D evidence computes only `K5_1D`; 7D/30D remain held. Every window uses its own proven numerator and the same original acquisition-spend denominator.

Wrong cohort ref, incompatible currency/basis/timezone, non-MATCHED reconciliation, non-final source, immature/late-arrival-open state, missing proof, digest mismatch, or duplicate evidence fails closed.

## Replay and late arrival

Identical inputs replay deterministically. Adding valid late cohort evidence changes the bound source/materialization digest and appends derived version 2 while version 1 remains unchanged and held. Raw/source history is never rewritten.

## Preserved Task-010 behavior

- Named Metrica attribution fact and period K5 path remain intact.
- ActionProposal v1, Budget Governor, structural guards and site intents are unchanged.
- No private allocator ranking/scoring policy changed in the public repository.

## Verification and safety

- Python: `107/107 PASS`.
- Node: `22/22 PASS`.
- Provider requests: `0`.
- Advertising spend: `0`.
- Provider write allowed: `false`.
- No Direct/site/provider mutation, Tilda publication, secret, private provider ID or production export.
- `git diff --check`, secret scan, provider-write scan and proprietary-logic scan required before commit.

Fixtures are synthetic. They do not prove live cohort K5 or production `K5 >= 5`.

## Files changed

- `profit-engine/runtime/profit_engine_runtime/day10_public.py`
- `profit-engine/runtime/tests/test_day10_public.py`
- `profit-engine/evidence/TASK-010-COHORT-MATERIALIZATION-REWORK.md`

After GREEN public CI, the exact rework SHA must be pinned in private `PUBLIC_CONTRACT_VERSION.md` and allocator constant without changing private commercial policy.
