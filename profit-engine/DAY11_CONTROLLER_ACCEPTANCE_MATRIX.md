# PROFIT ENGINE — DAY 11 CONTROLLER ACCEPTANCE MATRIX

Status: CANONICAL
Updated: 2026-08-28

Task 011 is accepted only if a Governor-ready ActionProposal becomes a fully audited, non-executing controller plan that cannot bypass money, Owner approval, kill switches, freshness, concurrency, rollback or write-authority safety.

Direct Editing remains disabled during Task 011.

## A. Proposal/Governor binding

PASS only if:
- proposal digest validates;
- Governor state is exactly `GOVERNOR_READY_FOR_DAY11_CONTROLLER`;
- proposal/governor refer to same proposal digest;
- `requires_budget_governor=true`;
- proposal `provider_write_allowed=false`;
- held/pending/blocked states never become Day12-ready.

Negative tests: forged digest, mismatched governor, pending Owner approval, DQ hold, kill-switch block, missing governor ref.

## B. Owner approval >20%

Tests:
- +20.00%, clean governor -> may continue without extra approval;
- +20.01%, no approval -> blocked;
- different proposal -> blocked;
- lower amount/cap -> blocked;
- expired/superseded -> blocked;
- exact valid approval -> may continue.

## C. Exact provider identity/preflight

Target must resolve to exact registered provider entity ID.

Forbidden: name, text, date, URL guess, fuzzy matching.

Fresh preflight binds provider state/status/budget/subtype and digest.

Changed/stale state -> `BLOCKED_STALE_PROVIDER_STATE`.

## D. Method allowlist

Launch allowlist:
- campaign suspend/resume;
- ad suspend/resume;
- bounded campaign budget update.

Reject create/add/delete/archive/moderate/strategy migration/unapproved service-method/multi-object mutation.

## E. Budget conversion truth

`ProviderBudgetPlan` must explicitly prove weekly-envelope -> provider daily-budget conversion.

Test valid 7-day and explicit reduced active-day schedules; unknown basis/wrong amount/currency mismatch/non-Decimal/inexact conversion -> blocked.

No implicit weekly/7 assumption.

## F. Mutation cadence

`MAX_AUTONOMOUS_BUDGET_MUTATIONS_PER_CAMPAIGN_PER_DAY = 1`.

First clean plan may continue; one prior autonomous mutation or ambiguous audit -> blocked.

## G. Kill switches

Test global/site/provider/advertiser/target/experiment scopes.

Any applicable active switch -> blocked and overrides recommendation, Governor and Owner approval.

## H. Execution lock

Per-target lock required. Same target locked -> blocked. Different target independent. Expired lock recovery only through audited lease-expiry path.

## I. One-object request

Exactly one object for a future provider mutation. Zero invalid; >1 blocked. One plan cannot fan out.

## J. Retry / uncertain result

Fake-transport tests:
- success -> read-back required;
- timeout -> no immediate retry;
- read-back desired -> recovered applied;
- unchanged state -> future explicit bounded retry state only;
- unexpected state -> uncertain/review;
- attempts bounded and audited.

## K. Provider response semantics

Distinguish HTTP/transport, top-level provider error, per-object error/warning/success, `RequestId`, `Units`.

HTTP 200 alone never equals success.

## L. Read-back

No future COMPLETED without read-back of exact expected provider state. Budget read-back validates exact provider amount and normalized weekly mapping.

## M. Rollback

Rollback derives from preflight. Exact prior budget may be restored only if safe; suspend/resume inverse only when prior state proves it. Unknown prior state -> no automatic rollback. Rollback remains separately guarded/audited.

## N. Audit chain

Hash-linked append-only evidence must validate ordering/tamper detection.

Minimum Day-11 chain:
`PLAN_CREATED -> PREFLIGHT_CAPTURED -> AUTHORIZATION_READY`.

Synthetic execution may extend through lock/dispatch/response/readback.

## O. Secret/log safety

No OAuth/token/provider private mappings in plan/audit/exceptions/public fixtures. RequestId/Units allowed. Redaction tests inject token-like strings.

## P. Write-authority safety

During Task 011:
- Direct access remains READ_ONLY;
- real mutation count = 0;
- spend = 0;
- production writer flag = false;
- default runtime cannot reach a real Direct writer.

## Q. Regression

Require:
- Task 010R tests green;
- all public Python tests green;
- all Node tests green;
- secret scan green;
- provider-write reachability scan green;
- `git diff --check` green;
- final Profit Engine CI green.

## Central Brain decision

PASS => `TASK_011_ACCEPTED_CONTROLLER_READY_FOR_EDITING_ACCESS_UPGRADE`.

FAIL => `TASK_011_REWORK`; Editing remains disabled.
