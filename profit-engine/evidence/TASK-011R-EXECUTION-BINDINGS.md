# TASK 011R — Execution-binding safety rework

## Status and scope

- Bounded rework implementation: `COMPLETE`, pending Central Brain acceptance.
- Canonical baseline: `032fd4c7e344366b80e73615c80113161c49ff54`.
- Task-011 ancestor preserved: `d8d3a9887d4a3e38d90ac0cfb7567092aaf3997a`.
- Final SHA and exact final CI run are reported after push.
- Task 010/010R, Budget Governor, Campaign Factory, Strategy Lab, private core,
  rollback, audit hashing, redaction, and one-object rule were not redesigned.

## Lock-to-dispatch binding

`locks=None` is blocked both at plan authorization and synthetic execution. The
in-memory registry uses a guarded atomic check-and-set for the exact lock key:

`site:provider:advertiser:entity_type:provider_entity_id`.

The fake execution path calls the real `acquire()` before any preflight read or
dispatch. Acquisition failure produces zero dispatches. Only a successful
acquisition emits `EXECUTION_LOCK_ACQUIRED`. Every terminal path, including
TOCTOU/kill-switch blocks and uncertain outcomes, releases in `finally` and emits
`EXECUTION_LOCK_RELEASED` through the hash-linked audit.

## TOCTOU and runtime kill-switch binding

After lock acquisition, fake transport performs a fresh read-only preflight.
The actual execution path calls canonical `pre_dispatch_snapshot_matches()` and
checks exact target/provider entity, state, status, current budget, currency,
strategy subtype, freshness, integrity, and DQ holds. Changed state/budget,
stale or held snapshots produce zero dispatches.

Applicable global/site/provider/advertiser/target/experiment-action kill switches
are rechecked again after fresh preflight and immediately before dispatch. A
switch activated after plan creation produces zero dispatches.

## Cadence evidence

Immutable `MutationCadenceEvidence v1` binds campaign reference, exact day,
timezone offset and day-basis reference, prior autonomous mutation count,
audit/source refs, and deterministic digest. Authorization verifies integrity,
supported version, exact target campaign, execution-day equality in the explicit
timezone basis, zero prior mutations, and non-empty provenance. Yesterday,
tomorrow, forged digest, campaign mismatch, missing provenance, and prior count 1
all fail closed.

`MAX_AUTONOMOUS_BUDGET_MUTATIONS_PER_CAMPAIGN_PER_DAY = 1` remains unchanged.

## Exact normalized request binding

`campaign.update_budget` permits exactly one object with exactly:

- registered `provider_entity_id`;
- authorized Decimal `daily_budget`;
- exact `provider_integer_micros` from `ProviderBudgetPlan`.

Wrong target, amount, micros, missing field, non-exact type, or extra mutation
field yields `CONTROLLER_PLAN_INVALID`. Lifecycle methods permit only exact
provider entity plus method-derived desired state; wrong state/target or extra
field is blocked. The immutable `ControllerPlan` now validates its own digest on
the execution path.

## Trusted Owner authority

Above +20%, `OwnerApprovalEvidence v1` must resolve its non-empty authority ref
through an explicit `TrustedOwnerAuthorityRegistry`. The controller verifies
version, approval ID, `approved_at <= now < expires_at`, supersession, exact
proposal/site/target/action/amount/currency, approval digest, and authority
membership. Arbitrary/untrusted authority and future-dated approval are blocked;
exact trusted approval may continue through remaining gates. Fixtures contain
only synthetic references and no signatures or secrets.

## Plan-derived read-back and retry

Expected normalized read-back is derived from immutable plan method and exact
normalized request. Budget expectation is the authorized daily amount/micros;
suspend/resume expectation is method-derived state. Any retained caller test
expectation must equal the derived value before lock/preflight/dispatch, otherwise
execution blocks with zero dispatches and cannot falsely complete.

Retry behavior remains: maximum one dispatch; timeout always read-backs first;
desired already present is recovered-applied; unchanged preflight state requires
an explicit future retry plan; unexpected state stops uncertain/review. There is
no blind or automatic retry.

## Global safety and verification

- `REAL_PROVIDER_REQUESTS=0`
- `ADVERTISING_SPEND=0`
- `PRODUCTION_WRITER_ENABLED=false`
- Direct access remained Reading; no write credential requested
- no Yandex/Tilda/site/Cloud mutation
- Task-011/011R controller tests: `23/23 PASS`
- full Python suite: `130/130 PASS`
- Task-010R regression: `18/18 PASS`
- Node suite: `22/22 PASS`
- py_compile: `PASS`
- JSON validation: `11/11 PASS`
- `git diff --check`: `PASS`
- secret/private-data scan: `PASS`
- provider-write reachability scan: `PASS`; no network/provider writer imports,
  writer flag false, real request/spend counters zero
- final exact-origin Profit Engine CI: reported after push

## Files changed

- `profit-engine/runtime/profit_engine_runtime/direct_controller.py`
- `profit-engine/runtime/tests/test_direct_controller.py`
- `profit-engine/runtime/README.md`
- `profit-engine/evidence/TASK-011R-EXECUTION-BINDINGS.md`
