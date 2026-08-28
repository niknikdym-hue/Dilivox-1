# TASK 011 — Guarded Direct Controller dry-run / write-safety gate

## Status

- Implementation: `COMPLETE`, pending Central Brain acceptance.
- Baseline: `b5d07a125dff3491543f9922c658dfc7fa8e5eb8`.
- Final public SHA and exact CI run: reported after commit, push, and GREEN CI.
- Direct access remained `READ_ONLY` throughout Task 011.

## Controller and binding proof

The public state model contains exactly the canonical Day-11 plan/blocked states
and `READY_FOR_DAY12_EXECUTION`; it deliberately contains no `EXECUTED` state.
Immutable `GovernorEvidence` binds the exact valid `ActionProposal` digest to the
exact `GovernorDecision`. A plan fails closed unless the proposal digest,
governor evidence digest, target reference, and
`GOVERNOR_READY_FOR_DAY11_CONTROLLER` state all match. There is no ungoverned
constructor or alternate authorization path.

`OwnerApprovalEvidence v1` binds proposal/site/exact provider target/action,
exact weekly amount, currency, authority, timestamps, expiry, supersession, and
its own digest. Tests prove +20.00% can reach readiness without extra approval;
+20.01% without approval is blocked; wrong proposal/target, lower amount,
expired, or superseded approval is blocked; exact valid +20.01% approval may
pass the remaining gates.

## Provider identity, preflight, and methods

Only an exact registered provider entity ID resolves; names, text, URLs, dates,
and fuzzy inference have no code path. `ProviderPreflightSnapshot v1` binds exact
site/provider/advertiser/entity identity, normalized state/status, provider
budget, currency, strategy subtype, timestamps, provenance, RequestId/Units, DQ
holds, and deterministic digest.

Expired, held, mismatched, or tampered snapshots fail closed. The explicit
pre-dispatch TOCTOU comparator requires a fresh snapshot with the same exact
mutation-relevant normalized state.

The method allowlist is limited to campaign suspend/resume, ad suspend/resume,
and one bounded campaign budget update. Add/create/delete/archive/moderation,
strategy migration, arbitrary methods, zero-object and multi-object requests are
rejected. `MAX_MUTATION_OBJECTS_PER_PROVIDER_REQUEST = 1`.

## Budget, cadence, kill switches, and lock

`ProviderBudgetPlan v1` binds Decimal weekly and provider daily amounts, explicit
active-day/time-targeting evidence, mapping version, RUB currency, exact integer
micros, exact rounding rule, preflight/proposal/governor refs, and Owner approval
ref when required. Seven-day and explicit reduced-day schedules are tested.
Empty/unknown basis, wrong totals, currency mismatch, non-Decimal or inexact
micros are blocked. No implicit weekly/7 conversion exists.

`MAX_AUTONOMOUS_BUDGET_MUTATIONS_PER_CAMPAIGN_PER_DAY = 1`; readiness requires
audit evidence proving zero prior autonomous changes for that campaign/day.
Missing, ambiguous, or one-prior-mutation evidence is blocked.

Applicable active global, site, provider, advertiser, target, and
experiment/action kill switches override every other gate. The execution lock
uses `site:provider:advertiser:entity_type:provider_entity_id`; same-target
contention blocks while different targets remain independent. Lease expiry is
explicitly time-based.

## Retry, read-back, rollback, and audit

The only transport is `InMemoryDirectTransport`. Synthetic tests distinguish
transport timeout, HTTP status, provider top-level errors, per-object
success/error/warning, RequestId, and Units. HTTP 200 alone is never success.

Every synthetic dispatch count is exactly one. A timeout causes read-back before
any retry decision: desired state present gives `RECOVERED_APPLIED`; unchanged
preflight state gives `EXPLICIT_RETRY_PLAN_REQUIRED`, with no retry; unexpected
state gives `EXECUTION_UNCERTAIN_REVIEW`, with no retry.

Even clear synthetic success needs exact read-back before synthetic completion.
Rollback is inert and derived only from immutable preflight: exact prior budget
or a state inverse proven by prior state. Unknown prior state produces no
automatic rollback.

Audit records are append-only, deterministic, sequence-checked, and hash-linked
from `GENESIS`. The minimum plan chain is
`PLAN_CREATED -> PREFLIGHT_CAPTURED -> AUTHORIZATION_READY`; synthetic paths add
lock/dispatch/response/read-back/completion or uncertainty. Tamper/reordering
invalidates the chain. RequestId/Units are retained; token-like values and
sensitive keyed fields are redacted before hashing/logging.

## Safety invariants

- `real_provider_requests=0`
- `advertising_spend=0`
- `production_writer_enabled=false`
- no real provider writer class or network dependency exists in the controller
- no Direct Editing/write credential was requested
- no production Direct, Dilivox, Tilda, YAN, Cloud, campaign, or budget mutation
- private `profit-engine-core` was not changed

## Verification

- New Day-11 tests: `15/15 PASS`.
- Full public Python regression: `122/122 PASS`.
- Task-010R tests remain included and green.
- Node regression: `22/22 PASS`.
- Python compile: `PASS`.
- JSON validation, `git diff --check`, secret/private-data scan, and provider-write
  reachability scan are required before commit.
- final exact-origin Profit Engine CI is recorded after push.

Fixtures and synthetic execution do not constitute a provider write or evidence
of live profitability. Central Brain alone performs Task-011 acceptance and may
then authorize the separate Direct Reading-to-Editing access step.

## Files changed

- `profit-engine/runtime/profit_engine_runtime/direct_controller.py`
- `profit-engine/runtime/tests/test_direct_controller.py`
- `profit-engine/runtime/README.md`
- `profit-engine/evidence/TASK-011-GUARDED-DIRECT-CONTROLLER.md`
