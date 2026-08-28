# PROFIT ENGINE — DAY 11 CONTROLLER ACCEPTANCE MATRIX PREWORK

Status: CENTRAL BRAIN PREWORK / NOT CANONICAL
Updated: 2026-08-28
Branch: `central-brain/day11-controller-prework-v2`
Depends on: Task 010R accepted

## Acceptance objective

Task 011 is accepted only if the controller can transform a Governor-ready public ActionProposal into a fully audited, non-executing Day-11 provider mutation plan that cannot bypass money, Owner-approval, kill-switch, freshness, concurrency or rollback safety.

Editing access remains disabled during Task 011 implementation and acceptance.

## A. Proposal / Governor binding

PASS only if:

1. ActionProposal digest validates;
2. controller accepts only `GOVERNOR_READY_FOR_DAY11_CONTROLLER`;
3. proposal and governor refer to the same proposal digest;
4. proposal still has `requires_budget_governor=true`;
5. proposal layer cannot set `provider_write_allowed=true`;
6. held/pending/blocked Governor state cannot produce a Day-12-ready plan.

Required negative tests:

- forged proposal digest;
- mismatched Governor decision;
- `PENDING_OWNER_APPROVAL`;
- `BLOCKED_DATA_QUALITY`;
- `BLOCKED_KILL_SWITCH`;
- missing Governor reference.

## B. Owner approval above +20%

For a weekly increase above +20%:

PASS only if OwnerApprovalEvidence is bound to the exact:

- proposal digest;
- site/target;
- action kind;
- approved budget amount/cap;
- current non-expired approval version.

Required boundaries:

- +20.00%, clean Governor -> no extra Owner approval required;
- +20.01%, no approval -> blocked;
- +20.01%, approval for different proposal -> blocked;
- +20.01%, approval for lower amount -> blocked;
- +20.01%, expired/superseded approval -> blocked;
- +20.01%, exact valid approval -> may continue to remaining gates.

## C. Provider identity and preflight

PASS only if controller target is an exact registered provider ID.

Forbidden target resolution:

- campaign name;
- ad text;
- date;
- URL guess;
- fuzzy matching.

Fresh preflight snapshot must bind target state, budget, status/state/subtype and snapshot digest.

Stale or changed state before execution -> `BLOCKED_STALE_PROVIDER_STATE`.

## D. Provider capability / method allowlist

Initial launch allowlist:

- campaign suspend;
- campaign resume;
- ad suspend;
- ad resume;
- bounded campaign daily-budget update compatible with approved weekly budget plan.

Day-12 launch-ready plan MUST reject:

- delete/archive;
- moderation submission;
- add/create campaign/ad/group/asset;
- complex strategy migration;
- unapproved service/method;
- multi-object mutation request.

## E. Budget conversion truth

PASS only if a ProviderBudgetPlan explicitly proves the conversion between public weekly budget and Direct provider DailyBudget.

Tests:

- active 7-day schedule + exact mapping -> valid;
- explicit reduced active-day schedule + exact mapping -> valid when mathematically consistent;
- unknown active-days basis -> blocked;
- wrong daily amount -> blocked;
- currency mismatch -> blocked;
- non-Decimal public budget -> blocked;
- provider micros conversion not exact under documented rounding -> blocked.

No implicit `weekly / 7` assumption is allowed.

## F. Budget mutation cadence

Launch invariant:

`MAX_AUTONOMOUS_BUDGET_MUTATIONS_PER_CAMPAIGN_PER_DAY = 1`.

Tests:

- first clean mutation plan today -> may continue;
- one prior autonomous mutation today -> blocked;
- missing/ambiguous mutation audit -> blocked;
- different campaign -> independent lock/cadence key.

## G. Kill switches

Controller must model and test:

- global;
- site;
- provider;
- advertiser/account;
- campaign/ad;
- experiment/action kill switch.

Any active applicable switch -> blocked.

Kill switch overrides:

- private winner;
- SCALE recommendation;
- Governor readiness;
- Owner approval.

## H. Concurrency / lock

PASS only if per-target execution lock is required.

Tests:

- lock free -> acquire;
- same target lock already held -> blocked;
- different target lock -> independent;
- stale expired lock -> recover only through audited lease-expiry path;
- lock identity includes site/provider/advertiser/entity type/provider entity ID.

## I. One-object request

For Day 12 launch-readiness:

- exactly one provider object per mutation request;
- zero objects -> invalid;
- two or more -> blocked;
- one ControllerPlan cannot fan out to multiple independent provider mutations.

This prevents Yandex partial-success semantics from producing ambiguous launch actions.

## J. Retry / uncertain result

PASS only if no blind write retry exists.

Tests with fake transport:

1. clear success -> read-back required;
2. timeout after send -> no immediate retry;
3. read-back shows desired state -> recovered applied;
4. read-back shows unchanged expected state -> bounded retry may remain only as a future explicit plan/state, not automatic loop;
5. read-back shows unexpected state -> `EXECUTION_UNCERTAIN_REQUIRES_REVIEW`;
6. maximum retry/attempt state is bounded and audited.

## K. Response / partial object handling

PASS only if controller distinguishes:

- transport/HTTP status;
- provider top-level errors;
- per-object success/error/warning;
- Direct `RequestId`;
- `Units` headers.

HTTP 200 alone never means mutation success.

## L. Read-back verification

Every future successful mutation requires a post-write READ_ONLY fetch proving expected provider state.

No read-back -> no `COMPLETED` audit status.

Budget read-back must verify exact provider amount and normalized public weekly mapping.

## M. Rollback

PASS only if rollback is derived from immutable preflight state.

Tests:

- budget update -> prior exact budget known -> rollback plan possible;
- suspend of active target -> resume rollback candidate;
- resume of suspended target -> suspend rollback candidate;
- unknown prior state -> no automatic rollback;
- rollback blocked by current kill switch/state -> remain held;
- rollback is separately audited and never an unguarded inverse call.

## N. Audit chain

Append-only audit records must include hash/ref chaining.

Mutation plan acceptance requires deterministic evidence for:

`PLAN_CREATED -> PREFLIGHT_CAPTURED -> AUTHORIZATION_READY`.

Synthetic execution tests may additionally model:

`LOCK_ACQUIRED -> DISPATCH_STARTED -> RESPONSE_RECEIVED -> READBACK_VERIFIED`.

Any tampered/reordered record chain -> invalid evidence.

## O. Secret/log safety

PASS only if:

- no OAuth/token in plans/audit/exceptions;
- Client/Login private mappings remain outside public fixtures;
- provider raw responses are redacted before evidence;
- `RequestId` and `Units` may be retained;
- tests intentionally inject token-like strings and verify redaction.

## P. Write authority safety

During Task 011 acceptance:

- current account access expected READ-ONLY;
- real network mutation count = 0;
- advertising spend = 0;
- production writer flag = false;
- no Owner instruction to enable Editing until Central Brain acceptance.

Test should fail if a real Direct writer can be reached under default configuration.

## Q. Regression

Acceptance requires:

- Task 010R tests green;
- all prior Profit Engine Python tests green;
- all prior Node tests green;
- secret scan green;
- provider write reachability scan verifies production write is disabled by default;
- `git diff --check` green;
- final Profit Engine CI green.

## R. Central Brain decision after Task 011

If all gates pass:

`TASK_011_ACCEPTED_CONTROLLER_READY_FOR_EDITING_ACCESS_UPGRADE`

Only then ask Owner to change Direct access from Reading to Editing.

If any safety gate fails:

`TASK_011_REWORK`

Editing remains disabled.
