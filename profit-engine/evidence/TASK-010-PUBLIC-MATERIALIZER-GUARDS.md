# TASK 010 Phase A — Public materializer and guards

## Repository state

- Phase status: `COMPLETE`, pending Central Brain acceptance.
- Public baseline: `e6f7609de90e030883e9b8fcf3ee9a31baab0054`.
- Phase-A implementation/final origin SHA: reported after commit/push because a commit cannot contain its own SHA.
- Branch: `profit-engine`.
- Separate Dilivox/Tilda workspace was not modified.

## Named Metrica attribution fact

`MetricaAttributionFact v1` materializes only from a validated, exact ordered list of named dimensions under explicit `last_yandex_direct_click` attribution:

- date;
- Direct campaign/order and group refs;
- named UTM source/medium/campaign/content/term;
- attributed YAN revenue as `Decimal`;
- requests/renders/shows;
- currency, money basis and timezone;
- sampling/sample-size/sample-space/accuracy/data-lag/disclosure provenance;
- immutable raw source ref and source state.

Missing, reordered, positional-only, or incompatible dimensions produce `metrica_named_attribution_dimensions_missing_or_incompatible` and `DATA_QUALITY_HOLD` semantics. Missing campaign values are held. There is no date-only, campaign-name, or generic positional inference.

## Deterministic ledger materialization

`LedgerMaterializer` consumes an immutable acquisition registration, validated Direct `Decimal` spend, named Metrica attribution fact, and YAN control total. It then:

1. registers the acquisition idempotently;
2. applies accepted first-party/Metrica/Direct attribution classification;
3. reconciles Metrica attributed revenue against YAN control using explicit scope/currency/basis/timezone;
4. uses Metrica revenue once as the K5 numerator — YAN is control only;
5. creates period K5 and cohort K5 1D/7D/30D;
6. append-versions derived measurements for late source versions while preserving earlier outputs.

Identical immutable input replays to the same materialization digest/version. A late Metrica source version creates derived version 2 without rewriting version 1. Unproven cohort linkage or reconciliation other than `MATCHED` is never optimizer-consumable.

## ActionProposal v1

The immutable public proposal supports `LEARN`, `TEST`, `SCALE`, `HOLD`, `REDUCE`, `STOP`, and `QUARANTINE`. It contains only public target/evidence/provenance refs, Decimal-compatible current/proposed/delta strings, generic guard requirements, owner-approval state, opaque private decision ref/digest, and audit metadata.

Every proposal has:

- `requires_budget_governor=true`;
- `provider_write_allowed=false`;
- deterministic proposal digest;
- no private score, formula, weight, threshold, or allocation detail.

## Budget Governor v1

Fixture results:

| Scenario | Result |
|---|---|
| +10%, all guards clean | `GOVERNOR_READY_FOR_DAY11_CONTROLLER` |
| +20.00%, all guards clean | `GOVERNOR_READY_FOR_DAY11_CONTROLLER` |
| +20.01%, no Owner approval evidence | `PENDING_OWNER_APPROVAL` |
| +20.01%, explicit synthetic Owner approval evidence and all guards clean | `GOVERNOR_READY_FOR_DAY11_CONTROLLER` |
| Missing/malformed/non-Decimal baseline | `BLOCKED_BUDGET_BASELINE` |
| Held/non-MATCHED/NOT_COMPUTABLE/immature/non-consumable SCALE or TEST | `BLOCKED_DATA_QUALITY` |
| Global kill switch | `BLOCKED_KILL_SWITCH` |
| Invalid proposal structure | `BLOCKED_PROPOSAL_CONTRACT` |
| Structurally valid STOP/HOLD/QUARANTINE | Day-11-ready even with degraded money evidence, unless kill switch is active |

The governor returns an authorization state only. It contains no Direct client and performs no budget mutation.

## Data-quality and stop-loss structural guards

Public code enforces data quality, reconciliation, money-state, maturity, optimizer-consumability, structural-contract and global-kill gates. Commercial thresholds are absent and remain private. A data-quality deterioration after private decision prevents SCALE/TEST authorization.

## Site experiment intent

`SiteExperimentIntent v1` models only `activation`, `hold`, `stop`, and `kill-switch` references. It is deterministic and always carries `executable=false`, `provider_requests=0`, and `site_requests=0`. No Tilda publication or production mutation exists.

## Global safety

- Provider requests: `0`.
- Site requests: `0`.
- Advertising spend: `0`.
- Provider write allowed: `false`.
- No OAuth credential required or accessed.
- No Direct/site/provider transport added.

## Tests and checks

- Python: `101/101 PASS` (12 new public Day-10 cases plus all prior tests).
- Node: `22/22 PASS`.
- `py_compile`, `git diff --check`, secret/private-data scan, provider/site-write scan, and proprietary-logic scan required before commit.
- Public Profit Engine CI must be GREEN on the exact Phase-A origin SHA before private pin/implementation begins.

## Files changed

- `profit-engine/runtime/profit_engine_runtime/day10_public.py`
- `profit-engine/runtime/tests/test_day10_public.py`
- `profit-engine/runtime/README.md`
- `profit-engine/evidence/TASK-010-PUBLIC-MATERIALIZER-GUARDS.md`

The unrelated untracked `profit-engine/evidence/TASK-001-M0-INVENTORY 2.md` remains untouched and excluded.

## Blockers and next boundary

- No public Phase-A engineering blocker.
- Live provider certification remains `BLOCKED_EXTERNAL_PROVIDER_CREDENTIAL`; fixtures do not authorize spend or prove production K5.
- After GREEN public CI only: pin exact Phase-A SHA in private `PUBLIC_CONTRACT_VERSION.md`, then implement sensitive ranking/allocation exclusively in the private repository.
