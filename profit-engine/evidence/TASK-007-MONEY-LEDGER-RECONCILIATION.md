# TASK 007 — Money ledger + reconciliation + K5 foundation

## Status

- Implementation status: `COMPLETE`
- Acceptance status: pending Central Brain review; this evidence does not self-accept the task.
- Baseline and pre-push `origin/profit-engine`: `05c90d1d197e9ebc223b14a36669500ffb7e9b0a`
- Final commit and final origin SHA: recorded in the commit/push result and final report because a commit cannot contain its own SHA.
- Workspace: `/Users/elenadymova/Documents/New project/Profit Engine/Dilivox-1`
- Canonical branch: `profit-engine`

## Schema foundation

Migration `data/migrations/0002_money_ledger_reconciliation.sql` adds site-scoped, versioned PostgreSQL contracts for:

- `acquisitions`;
- `acquisition_attribution_evidence`;
- `reconciliation_runs`;
- `money_ledger_facts`;
- `k5_measurements`.

All monetary values and ratios use PostgreSQL `numeric` and Python `Decimal`; no floating-point money is used. Records carry idempotency/version fields, source provenance, timestamps, explicit attribution grade, money/reconciliation state, data-quality reasons, and `optimizer_consumable` state.

## Acquisition ledger and privacy boundary

`sites/dilivox/acquisition-registration.schema.json` is a strict schema with `additionalProperties: false`. The runtime accepts only the canonical acquisition envelope and the existing first-party attribution allowlist (`yclid`, Direct identity fields, and bounded UTM fields). Arbitrary query parameters and PII fields are rejected.

Registration is content-hashed. Replaying the same acquisition ID and identical content is idempotent; replaying that ID with different content produces `conflicting_acquisition_registration` and preserves the original record.

## Attribution grades

The fixture suite proves these explicit grades without any date-only fallback:

| Evidence | Grade | Cohort link |
|---|---|---|
| First-party campaign + Metrica campaign + Direct fact agree | `A_STRONG_DIRECT_CROSSCHECK` | proven |
| First-party campaign agrees with Direct facts | `B_DIRECT_ID` | proven |
| Metrica campaign agrees with Direct facts, no first-party identity | `C_METRICA_DIRECT` | not proven |
| UTM resolves through an injected private mapper and Direct facts | `D_UTM_PRIVATE_MAP` | proven |
| Direct-like source only | `E_SOURCE_ONLY` | not proven |
| Contradictory or absent evidence | `UNJOINABLE` | held |

Contradictory first-party and Metrica campaign identities are held. The implementation has no date-coincidence attribution path. Private UTM mappings are injected at runtime and are not stored in this repository.

## Metrica attribution view

The public provider-neutral profile declares `last_yandex_direct_click` and validates the returned Direct order/group, UTM campaign, and date dimensions together with YAN partner price/request/render/show metrics and currency metadata. Missing dimensions or unknown money semantics produce holds.

Metrica YAN revenue is the attribution numerator. YAN Partner Statistics is a reconciliation/control total only. `select_revenue(..., combine=True)` rejects addition with `attempted_metrica_yan_double_count`.

## Reconciliation proof

Reconciliation compares compatible scope, currency, VAT/money basis, and timezone before comparing amounts. States are `PENDING`, `MATCHED`, `DRIFT`, `BASIS_BLOCKED`, and `SOURCE_MISSING`; the result also carries tolerance version and source references.

Synthetic fixture outcomes:

- Metrica `10.000 RUB` vs YAN control `10.005 RUB`, tolerance `0.01 RUB` -> `MATCHED`;
- Metrica `10 RUB` vs YAN control `11 RUB` -> `DRIFT`, held;
- RUB vs USD or incompatible/unknown basis -> `BASIS_BLOCKED`, held;
- missing side -> `SOURCE_MISSING`, held.

## Synthetic fixture money map

These values are tests only and are not evidence of production performance:

| Measurement | Spend denominator | Metrica-attributed revenue | YAN control total | Result |
|---|---:|---:|---:|---:|
| `period_K5` | 2.50 RUB | 12.50 RUB | reconciliation only | 5.0 |
| `K5_1D` | 4.00 RUB original cohort spend | 4.00 RUB | reconciliation only | 1.0 |
| `K5_7D` | 4.00 RUB original cohort spend | 12.00 RUB | reconciliation only | 3.0 |
| `K5_30D` | 4.00 RUB original cohort spend | 20.00 RUB | reconciliation only | 5.0 |

`period_K5` and cohort `K5_1D/K5_7D/K5_30D` have distinct measurement kinds. Every cohort window retains the original acquisition-spend denominator. A Metrica-only grade C record cannot become a cohort measurement and receives `NOT_COMPUTABLE_ATTRIBUTION_HOLD`. Zero spend is undefined rather than infinity; missing revenue is undefined rather than zero.

The synthetic `5.0` values above do **not** prove real `K5 >= 5`.

## Late arrival and recomputation

Derived measurements are append-versioned. A fixture creates version 1 from revenue 8/spend 2 and version 2 from late revenue 10/spend 2; version 1 remains unchanged at 4.0. The late-arrival grace is explicit (default two days), and immature 7D/30D windows carry `late_arrival_window_open` and cannot be final/optimizer-consumable.

## Data-quality hold matrix

| Condition | Result |
|---|---|
| Missing Direct spend | `missing_direct_spend` |
| Missing YAN/Metrica-attributed revenue | `missing_yan_revenue` |
| Zero or unknown denominator | `zero_denominator` / `zero_or_unknown_denominator` |
| Unjoinable acquisition | `unjoinable_acquisition` |
| Contradictory first-party/Metrica campaign | `contradictory_campaign_identity` |
| Scope/currency/VAT/timezone mismatch | `BASIS_BLOCKED` / `scope_currency_basis_mismatch` |
| Stale/incomplete or held upstream | `held_upstream_source` or Direct input validation hold |
| Reconciliation drift | `reconciliation_drift` |
| Immature late-arrival window | `late_arrival_window_open` |
| Conflicting registration | `conflicting_acquisition_registration` |
| Metrica + YAN addition | `attempted_metrica_yan_double_count` |
| Cohort K5 without proven acquisition linkage | `NOT_COMPUTABLE_ATTRIBUTION_HOLD` |

Every material hold sets or implies `optimizer_consumable=false`.

## Live provider status

`BLOCKED_EXTERNAL_PROVIDER_CREDENTIAL`. No live provider collection was attempted and no production payload was written. The fixture/source-contract implementation continued independently of this external blocker.

## Tests and checks

- Python: `58/58 PASS` — `PYTHONPATH=profit-engine/runtime python3 -m unittest discover -s profit-engine/runtime/tests -v`
- Node: `22/22 PASS` — `node --test profit-engine/sites/dilivox/tests/*.test.cjs`
- Acquisition JSON schema parse: required before commit.
- `git diff --check`: required before commit.
- Staged secret/private-data signature scan: required before commit.
- Staged provider-write scan: required before commit.
- Staged proprietary optimizer/scoring/allocation scan: required before commit.

## Files changed

- `profit-engine/data/migrations/0002_money_ledger_reconciliation.sql`
- `profit-engine/sites/dilivox/acquisition-registration.schema.json`
- `profit-engine/runtime/profit_engine_runtime/money_ledger.py`
- `profit-engine/runtime/tests/test_money_ledger.py`
- `profit-engine/evidence/TASK-007-MONEY-LEDGER-RECONCILIATION.md`

The unrelated untracked `profit-engine/evidence/TASK-001-M0-INVENTORY 2.md` is intentionally untouched and excluded from the Task 007 commit.

## Blockers

- Live Direct/Metrica/YAN certification remains `BLOCKED_EXTERNAL_PROVIDER_CREDENTIAL`.
- Consequently there is no live reconciliation or production K5 claim.

## Recommended Task 008 boundary

Add a read-only, private-configured materialization path from immutable provider/event facts into these generic ledger interfaces, with late-arrival scheduling, reconciliation observability, and cohort maturity gates. Keep private mappings and production data outside Git; do not introduce optimizer/scoring/allocation logic or any provider write capability.
