# TASK 009 — Acquisition Strategy Lab public-safe contracts

## Status and repository

- Engineering status: `COMPLETE`; Central Brain retains acceptance authority.
- Baseline: `c7ada0e98829ab7790bc834bcaefd9e9671acef8`.
- Final implementation/origin SHA: reported after commit/push because a commit cannot contain its own SHA.
- Branch/workspace: `profit-engine` at `/Users/elenadymova/Documents/New project/Profit Engine/Dilivox-1`.
- Separate Dilivox/Tilda workspace was not modified.

## StrategyCell v1

The immutable `StrategyCellRequest` → `StrategyCell` contract carries site/cell identity, accepted Campaign Factory preview/spec digest refs, campaign/strategy kind, stable landing content ID, public dimensions, measurement/evidence refs, attribution/reconciliation/money/source states, cohort-link proof, maturity/late-arrival state, optional proxy contract, explicit eligibility/holds, and canonical SHA-256 digest.

Identical inputs produce an identical cell digest. A material cell-key change changes the digest. The lab never recomputes K5 or upgrades evidence quality.

## Eligibility and hold matrix

| Input evidence | Result |
|---|---|
| A-grade, MATCHED, mature, proven, consumable cohort K5 | `CELL_ELIGIBLE_FOR_EXPERIMENT_PREVIEW` |
| B-grade, MATCHED, mature, proven, consumable cohort K5 | `CELL_ELIGIBLE_FOR_EXPERIMENT_PREVIEW` |
| D-grade with explicit injected private-map evidence and all money gates | `CELL_ELIGIBLE_FOR_EXPERIMENT_PREVIEW` |
| C-grade period evidence | diagnostic only; `CELL_HELD_ATTRIBUTION` for autonomous experiment evidence |
| C-grade cohort claim | `metrica_only_cohort_forbidden` and `cohort_link_not_proven` |
| E-grade or UNJOINABLE | `CELL_HELD_ATTRIBUTION` |
| PENDING/DRIFT/BASIS_BLOCKED/SOURCE_MISSING reconciliation | held; `reconciliation_not_matched` |
| NOT_COMPUTABLE or `optimizer_consumable=false` | `CELL_BLOCKED_MONEY_EVIDENCE` |
| IMMATURE or LATE_ARRIVAL_OPEN | `CELL_HELD_MATURITY` |
| Missing numerator/denominator/evidence provenance | `CELL_HELD_DATA_QUALITY` |
| Source state other than FINAL/RECONCILED | `CELL_HELD_DATA_QUALITY` |
| Unsupported measurement or strategy/campaign capability | blocked money/provider capability |

No held state is converted into eligible evidence by Strategy Lab.

## Strategy capability

The lab reuses the accepted Day-8 `direct-v5-v501-preview-1` capability metadata. Fixtures validate `cpc`, `conversion_click`, `pay_for_conversion`, `value_crr`, and eligible unified-performance `maximum_profit`. Unsupported kinds/combinations return `CELL_BLOCKED_PROVIDER_CAPABILITY`. No strategy is preferred or compared.

## Proxy contract

All canonical proxy states are implemented:

- `PROXY_UNPROVEN`;
- `PROXY_EVIDENCE_PENDING`;
- `PROXY_MONEY_ASSOCIATION_SUPPORTED`;
- `PROXY_REJECTED`.

Unproven, pending, or rejected proxies cannot unlock a conversion/value strategy. Supported association may be referenced but carries no fabricated monetary value or learned weight.

## ExperimentPreview v1

The deterministic preview requires one explicit control, one or more distinct treatments, a declared holdout, hypothesis, common primary measurement, positive observation window, maturity requirement, late-arrival grace, generic evidence prerequisites, Campaign Factory preview refs, inert budget proposal refs, and guardrails.

Synthetic valid preview:

- control: A-grade eligible, digest `36dc583ed1f818949e513e56710c4053ae59716b6281e9bfd3cb0ce19c4e7c82`;
- treatment: B-grade eligible, digest `e70c1ed15420a17d461e47b9cd19b6e756d7703da5d2348b42610216f3ae2728`;
- state: `EXPERIMENT_PREVIEW_VALID`;
- digest: `bc221b2744ae32fe2a31d80dda21d911e20fcc91ab51045e332a6ba63a4be109`.

A held treatment, missing holdout, incompatible measurement, missing references, or invalid observation contract produces `EXPERIMENT_PREVIEW_INVALID`. The preview never launches anything.

## Public evidence package

`PublicStrategyEvidencePackage` v1 contains cell digests, measurement refs, explicit eligibility/money/reconciliation/attribution/source states, experiment digest, capability version, and zero/false safety state. Synthetic package digest: `0f63ce7a74418a83c6e4f15ea07746b4a3a0151cf2fba28767e35a9a1656a13a`.

It contains no secret, provider ID, private mapping, production payload, score, or commercial outcome.

## Private decision boundary proof

The only public boundary for commercially sensitive decisions returns `BLOCKED_PRIVATE_CORE_REQUIRED`. Fixture tests prove this for `rank`, `select`, `winner`, `allocate`, `learned-score`, and `scale-candidate`, as well as unknown requests.

There is no callable ranking, comparison, allocation, scaling, launch, or execution implementation; no sorting/max-K5/weighted-sum path exists. Input/list order is never interpreted as preference.

## Hard safety state

- `provider_requests=0`.
- `advertising_spend=0`.
- `provider_write_allowed=false`.
- No Direct write, budget change, campaign/ad/group/keyword/image mutation, Tilda publication, production-site mutation, or credential use occurred.

## Tests and checks

- Python: `89/89 PASS`, including 17 Strategy Lab tests and all prior tests.
- Node: `22/22 PASS`.
- CLI fixture and private-boundary scenarios: PASS.
- `py_compile`, `git diff --check`, secret/private-data scan, provider-write reachability scan, and public proprietary-logic scan are required before commit.
- Final GitHub Actions `Profit Engine CI` is required on final origin HEAD and will be recorded in the final report.

## Files changed

- `profit-engine/runtime/profit_engine_runtime/strategy_lab.py`
- `profit-engine/runtime/profit_engine_runtime/strategy_lab_cli.py`
- `profit-engine/runtime/tests/test_strategy_lab.py`
- `profit-engine/runtime/README.md`
- `profit-engine/evidence/TASK-009-ACQUISITION-STRATEGY-LAB.md`

The unrelated untracked `profit-engine/evidence/TASK-001-M0-INVENTORY 2.md` remains untouched and excluded.

## Blockers

- No Task-009 public-safe engineering blocker.
- `PRIVATE_CORE_REPOSITORY_REQUIRED_BEFORE_SENSITIVE_OPTIMIZER_IMPLEMENTATION` remains active for proprietary Task-010 logic.
- Live provider certification remains `BLOCKED_EXTERNAL_PROVIDER_CREDENTIAL`, independent of fixture/source-contract completion.

## Recommended Task 010 boundary

If the private repository is accessible, bootstrap its authority/version boundary and keep commercially sensitive decision logic there. In the public repository, add only generic action-proposal, data-quality/stop-loss, and Budget Governor safety contracts. No provider write execution before the guarded Day-11 controller gate; weekly growth above 20% remains Owner-approval-only.
