# TASK 011R — GUARDED DIRECT CONTROLLER EXECUTION-BINDING REWORK

Status: READY FOR EXECUTION
Owner: Central Brain
Executor: Codex
Acceptance: Central Brain
Scope: bounded rework of Task 011 only

## Baseline

Public repository: `niknikdym-hue/Dilivox-1`
Branch: `profit-engine`
Required ancestor: `d8d3a9887d4a3e38d90ac0cfb7567092aaf3997a`

Do not redesign Task 010/010R, private ProfitAllocator, Campaign Factory, Strategy Lab, or Budget Governor.

Preserve all accepted Task-011 components unless needed for the exact fixes below.

## Why rework is required

Central Brain found four launch-critical write-safety bypasses in the otherwise strong Day-11 implementation.

### Defect 1 — execution lock can be bypassed

`build_controller_plan(..., locks=None)` can still return `READY_FOR_DAY12_EXECUTION`.

`simulate_with_fake()` appends `EXECUTION_LOCK_ACQUIRED` but does not actually acquire the lock from `ExecutionLockRegistry`.

Required invariant:

`NO LOCK REGISTRY / LOCK ACQUIRE FAILURE -> NO DISPATCH`.

The execution path must atomically acquire the exact target lock before synthetic dispatch and audit the actual acquisition. It must release through an audited path after terminal synthetic outcome.

### Defect 2 — TOCTOU gate is not on the dispatch path

`pre_dispatch_snapshot_matches()` exists, but `simulate_with_fake()` can dispatch without invoking it.

Required invariant:

`FRESH READ-ONLY SNAPSHOT MUST MATCH THE PLAN-BOUND PREFLIGHT IMMEDIATELY BEFORE DISPATCH`.

Synthetic dispatch must require a fresh pre-dispatch snapshot and call the canonical comparison. Stale/mismatched/held fresh state must block with zero dispatches.

Runtime kill switches must also be rechecked immediately before dispatch; an activation after plan creation must still stop the write.

### Defect 3 — mutation cadence evidence is stale/forgeable

Current `MutationCadenceEvidence` has no integrity digest and its `day` is not validated against the current execution day.

Required:

immutable `MutationCadenceEvidence v1` with deterministic digest, exact campaign ref, explicit day, timezone/basis reference, prior autonomous mutation count, audit/source refs, and integrity validation.

At authorization time:
- evidence digest must validate;
- campaign ref must match exact target;
- cadence day must equal the current execution day under the explicit cadence timezone/basis;
- prior mutations must equal 0;
- missing/ambiguous audit/source evidence blocks;
- stale yesterday/tomorrow evidence blocks.

Launch rule remains:

`MAX_AUTONOMOUS_BUDGET_MUTATIONS_PER_CAMPAIGN_PER_DAY = 1`.

### Defect 4 — request payload is not bound to the authorized target/budget plan

Current controller checks only that there is exactly one request object and that it is secret-safe.

A budget proposal/budget plan can therefore be READY while the request object contains a different target or amount.

This is forbidden.

Implement a canonical normalized mutation-object contract and fail closed unless the one request object is exactly consistent with the plan.

For `campaign.update_budget` it must bind at minimum:
- exact `provider_entity_id` from registered target;
- exact provider daily-budget value/micros from `ProviderBudgetPlan`;
- no additional unapproved mutation fields.

For `campaign.suspend/resume` and `ad.suspend/resume` it must bind:
- exact `provider_entity_id`;
- only the state/lifecycle operation implied by the allowlisted method;
- no extra mutation fields.

Wrong target, wrong budget, extra mutation field, or missing required field -> `CONTROLLER_PLAN_INVALID` or a dedicated fail-closed state; never Day12-ready.

## Additional hardening required by the canonical design

### Owner approval authority must be trusted, not merely self-declared

For >20% proposals, `OwnerApprovalEvidence v1` already binds proposal/target/action/amount/expiry. Complete the canonical timestamp/version/authority checks:
- version exactly supported;
- approval id non-empty;
- `approved_at <= now < expires_at`;
- not superseded;
- authority ref non-empty;
- authority ref must resolve in a trusted Owner-approval authority registry/set supplied to the controller;
- exact proposal/site/target/action/amount/currency binding remains mandatory.

A caller must not be able to create an arbitrary `OwnerApprovalEvidence` with an arbitrary authority string and thereby authorize >20%.

No secrets or signatures are required in public fixtures. Model trust through an explicit exact authority registry/reference boundary.

### Read-back expectation must be plan-bound

Synthetic completion must not depend on an arbitrary caller-provided `expected_state` that can disagree with the mutation plan.

Derive or validate the expected normalized read-back state from the immutable ControllerPlan/request object/method. If caller-provided expected state is retained for test plumbing, it must equal the plan-derived expectation or execution is blocked before dispatch.

Budget read-back expectation must correspond exactly to the authorized budget request. Suspend/resume read-back expectation must correspond exactly to the lifecycle method.

## Required negative tests

Add regression tests proving all of these:

1. `locks=None` cannot reach dispatch-ready synthetic execution.
2. lock already held -> zero dispatch.
3. lock acquisition occurs for real in fake execution and is audited.
4. lock is released through an audited terminal path.
5. fresh pre-dispatch snapshot identical -> may continue.
6. fresh snapshot changed state -> zero dispatch.
7. fresh snapshot changed budget -> zero dispatch.
8. fresh snapshot stale/held -> zero dispatch.
9. kill switch activated after plan creation -> zero dispatch.
10. cadence evidence valid today -> may continue.
11. cadence evidence yesterday -> blocked.
12. cadence evidence tomorrow -> blocked.
13. forged cadence digest -> blocked.
14. cadence campaign mismatch -> blocked.
15. prior mutation count 1 -> blocked.
16. missing cadence source/audit evidence -> blocked.
17. budget request exact target + exact micros -> may continue.
18. budget request wrong provider entity id -> blocked.
19. budget request wrong daily budget/micros -> blocked.
20. budget request extra mutation field -> blocked.
21. suspend/resume wrong target -> blocked.
22. suspend/resume extra mutation field -> blocked.
23. >20% approval arbitrary/untrusted authority -> blocked.
24. >20% approval approved_at in future -> blocked.
25. >20% approval exact trusted authority + exact binding -> may continue.
26. read-back expected state not equal to plan-derived expectation -> blocked/no false COMPLETED.
27. timeout still causes max one dispatch and read-back-before-any-retry.
28. all previous Task-011 tests remain green after adapting fixtures to the stronger contracts.
29. all Task-010R regressions remain green.

## Global Day-11 safety remains unchanged

During Task 011R:

`REAL_PROVIDER_REQUESTS = 0`

`ADVERTISING_SPEND = 0`

`PRODUCTION_WRITER_ENABLED = false`

Direct access remains Reading.

No real Yandex mutation, no OAuth write credential, no Tilda/site mutation, no paid Cloud apply, no force push.

Private core remains proposal-only and must not gain provider authority.

## Evidence

Create:

`profit-engine/evidence/TASK-011R-EXECUTION-BINDINGS.md`

Evidence must explicitly prove:
- lock is on the actual dispatch path;
- TOCTOU comparison is on the actual dispatch path;
- runtime kill-switch recheck is on the actual dispatch path;
- cadence evidence is current-day + integrity-bound;
- mutation request is exact-target/exact-budget bound;
- Owner authority is trusted through an exact registry/boundary;
- read-back expectation is plan-derived;
- zero real provider requests/spend and writer hard-disabled.

## Verification

Run:
- full Python suite;
- full Node suite;
- Task-010R regression;
- Task-011 regression;
- `py_compile`;
- JSON validation;
- `git diff --check`;
- secret scan;
- provider-write reachability scan;
- final Profit Engine CI GREEN on exact final SHA.

Commit and normal fast-forward push to `profit-engine`.

## Final report

Return:
- STATUS
- BASELINE_HEAD
- FINAL_HEAD
- ORIGIN_PROFIT_ENGINE
- LOCK_DISPATCH_BINDING
- TOCTOU_DISPATCH_BINDING
- RUNTIME_KILL_SWITCH_RECHECK
- CADENCE_INTEGRITY_DAY_BINDING
- REQUEST_TARGET_BUDGET_BINDING
- OWNER_AUTHORITY_TRUST
- PLAN_DERIVED_READBACK
- RETRY_SAFETY
- REAL_PROVIDER_REQUESTS
- ADVERTISING_SPEND
- PRODUCTION_WRITER_ENABLED
- TESTS
- FINAL_CI
- FILES_CHANGED
- BLOCKERS

Do not self-accept. Central Brain performs acceptance.
