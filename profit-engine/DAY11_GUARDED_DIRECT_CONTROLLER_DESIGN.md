# PROFIT ENGINE — DAY 11 GUARDED DIRECT CONTROLLER DESIGN

Status: CANONICAL
Updated: 2026-08-28
Depends on: Task 010 accepted

## Objective

Day 11 is the write-safety gate.

Canonical transition:

`Governor-ready ActionProposal -> immutable provider preflight -> ControllerPlan -> authorization gates -> READY_FOR_DAY12_EXECUTION`

Day 11 itself performs no real Direct mutation and creates no spend.

Direct access remains Reading until Central Brain accepts Task 011.

## Input boundary

Controller accepts only:
- immutable `ActionProposal v1`;
- exact `GovernorDecision` bound to the same proposal;
- registered provider entity identity;
- fresh provider preflight snapshot;
- Owner approval evidence when required;
- kill-switch state;
- mutation-cadence evidence;
- execution-lock evidence.

Required:
- proposal digest valid;
- `requires_budget_governor=true`;
- proposal `provider_write_allowed=false`;
- Governor state exactly `GOVERNOR_READY_FOR_DAY11_CONTROLLER`;
- proposal/governor identity match.

Anything else fails closed.

## Owner approval above +20%

Weekly increase above +20% requires `OwnerApprovalEvidence v1` bound to the exact:
- proposal digest;
- site and provider target;
- action kind;
- approved budget amount/cap;
- approval version/timestamp;
- non-expired/non-superseded state.

Approval for another proposal, target or lower amount is invalid.

+20.00% with clean Governor requires no extra approval.
+20.01% requires exact Owner approval evidence.

## Provider preflight

Every future mutation requires a fresh READ_ONLY provider snapshot.

`ProviderPreflightSnapshot v1` binds:
- provider entity type/id;
- current state/status;
- current provider budget if applicable;
- strategy/subtype;
- fetched timestamp;
- request/source provenance;
- deterministic digest;
- freshness and DQ holds.

No target inference by name, URL, date or fuzzy matching.

## Stale-state / TOCTOU gate

Controller plan binds the expected preflight digest.

Before execution:
1. acquire target lock;
2. fresh provider GET;
3. compare normalized state with expected snapshot;
4. material difference -> `BLOCKED_STALE_PROVIDER_STATE`;
5. never silently adapt proposal to unexpected provider state.

## Initial mutation allowlist

Launch-ready controller may model only:
- campaign suspend;
- campaign resume;
- ad suspend;
- ad resume;
- one bounded campaign budget update.

Disabled at first launch:
- create/add campaign/ad/group/asset;
- delete/archive;
- moderation submission;
- complex strategy migration;
- multi-object mutation requests.

## Budget mapping

Public governance is weekly; Direct provider mutation may use daily budget.

Controller must not silently divide by seven.

`ProviderBudgetPlan v1` binds:
- current/proposed weekly budget;
- current/proposed provider daily budget;
- active-day/time-targeting basis;
- mapping version;
- currency;
- exact provider integer/micros conversion;
- rounding rule;
- preflight ref;
- ActionProposal digest;
- Governor ref;
- Owner approval ref when required.

Unknown schedule/budget mapping -> blocked.

## Autonomous budget cadence

Profit Engine launch invariant:

`MAX_AUTONOMOUS_BUDGET_MUTATIONS_PER_CAMPAIGN_PER_DAY = 1`

If audit cannot prove zero prior autonomous budget changes for the campaign/day, another autonomous budget mutation is blocked.

## One-object launch rule

`MAX_MUTATION_OBJECTS_PER_PROVIDER_REQUEST = 1`

This is stricter than provider capability and prevents ambiguous partial-success at launch.

## Kill-switch precedence

Any applicable active kill switch blocks authorization:
1. global Profit Engine;
2. site;
3. provider;
4. advertiser/account;
5. campaign/ad target;
6. experiment/action.

Kill switch overrides private recommendation, Governor readiness and Owner approval.

## Execution lock

Lock key includes:

`site_id:provider:advertiser:entity_type:provider_entity_id`

Two concurrent executions for the same target are forbidden.

## No blind retry

A future writer must never retry blindly after timeout/uncertain response.

Required model:
- audit `DISPATCH_STARTED` before send;
- at most one object;
- capture response/RequestId/Units;
- clear success -> read-back;
- timeout/unknown -> read-back before retry decision;
- desired state already present -> recovered-applied classification;
- unchanged expected state -> bounded retry may be a future explicit state, never automatic loop;
- unexpected state -> review/uncertain stop.

## Read-back

No future mutation can become COMPLETED without READ_ONLY verification of expected provider state.

Budget read-back verifies exact provider amount and public weekly-budget mapping.

## Rollback

Rollback is derived from immutable preflight state, never guessed inverse logic.

Examples:
- budget update -> restore exact prior budget if safe;
- suspend active target -> resume candidate;
- resume suspended target -> suspend candidate;
- unknown prior state -> no automatic rollback.

Rollback itself requires authorization, audit and kill-switch checks.

## Immutable audit

Append-only hash-linked audit states include:
- `PLAN_CREATED`;
- `PREFLIGHT_CAPTURED`;
- `AUTHORIZATION_READY`;
- `EXECUTION_LOCK_ACQUIRED`;
- `DISPATCH_STARTED`;
- `PROVIDER_RESPONSE_RECEIVED`;
- `READBACK_VERIFIED`;
- `COMPLETED`;
- `BLOCKED`;
- `EXECUTION_UNCERTAIN`;
- rollback states.

OAuth/token values are never logged.

## Day-11 public states

- `CONTROLLER_PLAN_VALID`;
- `CONTROLLER_PLAN_INVALID`;
- `BLOCKED_GOVERNOR_NOT_READY`;
- `BLOCKED_OWNER_APPROVAL`;
- `BLOCKED_KILL_SWITCH`;
- `BLOCKED_STALE_PROVIDER_STATE`;
- `BLOCKED_PROVIDER_CAPABILITY`;
- `BLOCKED_BUDGET_MAPPING`;
- `BLOCKED_MUTATION_CADENCE`;
- `BLOCKED_EXECUTION_LOCK`;
- `READY_FOR_DAY12_EXECUTION`.

There is deliberately no `EXECUTED` state on Day 11.

## Editing-access gate

Owner is asked to switch Direct access from Reading to Editing only after Central Brain verifies Task 011:
- Budget Governor cannot be bypassed;
- >20% approval binding works;
- kill-switch precedence works;
- stale-snapshot gate works;
- one-object rule works;
- no-blind-retry/read-back/rollback/audit contracts work;
- production writer is hard-disabled by default;
- all tests and Profit Engine CI are green.
