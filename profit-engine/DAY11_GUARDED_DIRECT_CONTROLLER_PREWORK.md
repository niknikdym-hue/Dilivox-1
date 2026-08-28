# PROFIT ENGINE — DAY 11 GUARDED DIRECT CONTROLLER PREWORK

Status: CENTRAL BRAIN PREWORK / NOT YET TASK 011 AUTHORITY
Updated: 2026-08-28

## Purpose

Prepare the guarded execution boundary while Task 010 cohort-materialization rework is being corrected.

Day 11 must convert only a public `GovernorDecision == GOVERNOR_READY_FOR_DAY11_CONTROLLER` plus its bound `ActionProposal` into a fully auditable provider execution plan. It must not allow the private core, Campaign Factory, or any caller to bypass public safety governance.

Direct Editing remains disabled until Task 011 acceptance.

## Non-negotiable execution chain

`private decision digest -> public ActionProposal -> Budget Governor -> Day11 Controller validation -> immutable execution intent -> provider adapter -> post-write verification -> audit/rollback state`.

No step may be skipped.

## Controller input contract

Minimum bound inputs:
- exact `ActionProposal` digest/version;
- exact `GovernorDecision` state/reasons/increase percent;
- public contract version/SHA;
- target provider/entity refs;
- campaign preview/spec digest;
- current provider read snapshot/version;
- requested operation;
- requested budget value where applicable;
- kill-switch state/version;
- owner-approval evidence identity when required;
- execution id / idempotency key;
- request nonce/version;
- audit actor = machine controller;
- timestamp/timezone.

## Allowed Day-11 operation classes

Controller may model only operations required for the guarded launch path, such as:
- campaign/group/ad suspend or resume when explicitly supported by proposal kind;
- bounded budget update;
- future create/update operations only when their accepted Campaign Factory preview/intents are bound exactly;
- STOP/QUARANTINE safety operations;
- read-after-write verification.

Actual provider execution must remain disabled until Task-011 write gate passes and Owner explicitly upgrades Direct access from Reading to Editing.

## Hard preconditions

Before any provider write can be executable:
1. Task 010 accepted;
2. public/private contract pins match;
3. Profit Engine CI green;
4. Direct provider doctor PASS with secure credential;
5. Direct account has Editing access;
6. proposal digest verifies;
7. governor state exactly `GOVERNOR_READY_FOR_DAY11_CONTROLLER`;
8. kill switch is OFF;
9. target snapshot has not drifted since proposal baseline;
10. operation is within accepted capability/preview contract;
11. idempotency key has not already completed;
12. owner-approval evidence is present and exact when increase >20%;
13. audit/rollback plan is persisted before provider mutation.

Any failed precondition -> no provider request.

## Owner approval evidence for >20%

Day 11 must strengthen the Day-10 generic owner-approval string into an immutable evidence envelope with at least:
- approval id;
- proposal digest;
- site id;
- current weekly budget;
- proposed weekly budget;
- computed increase percent;
- approved action kind;
- approved-at timestamp;
- expiry/one-shot semantics;
- owner authority marker;
- evidence digest.

Rules:
- evidence must bind to the exact proposal digest;
- evidence for one proposal cannot authorize another;
- stale/expired/replayed evidence fails closed;
- >20% without valid exact evidence remains `PENDING_OWNER_APPROVAL` and cannot reach provider adapter.

## Idempotency and concurrency

Execution must use a durable state machine, e.g.:
- `PLANNED`
- `PRECONDITIONS_PASSED`
- `EXECUTING`
- `APPLIED_UNVERIFIED`
- `VERIFIED`
- `FAILED_NO_CHANGE`
- `FAILED_PARTIAL_CHANGE`
- `ROLLBACK_REQUIRED`
- `ROLLED_BACK`
- `QUARANTINED`

Rules:
- same execution identity is idempotent;
- concurrent execution of the same target/action is serialized/locked;
- uncertain provider response is never assumed success;
- after timeout/5xx, read current provider state before retrying a mutation;
- retrying must not duplicate spend/action.

## Optimistic drift protection

Before write, controller must compare current provider read snapshot against proposal baseline for fields relevant to the action.

If budget/status/entity version changed unexpectedly:
- `BLOCKED_TARGET_DRIFT`;
- no provider write;
- require re-read/re-proposal.

## Write adapter boundary

Provider adapter should expose an explicit small allowlist of mutation operations. No generic arbitrary JSON write endpoint.

Requirements:
- request schema strictly generated from accepted execution intent;
- no free-form provider payload from private core;
- credentials retrieved only from secret store/keychain boundary;
- redacted audit logging;
- bounded retry policy;
- read-after-write verification;
- response/raw provider evidence stored outside Git.

## Rollback

A rollback plan must exist before mutation.

For reversible fields such as budget/status:
- capture exact pre-write state;
- define inverse operation;
- verify rollback result.

For create operations that are not safely reversible, Task 011 may keep them non-executable for the first guarded launch and limit the first real action to a reversible bounded mutation.

## First production action preference

For Day 12, prefer the smallest reversible action with clear verification, e.g. a bounded <=20% weekly budget change on an already-existing controlled campaign only if live economics and all guards justify it, or a safe STOP/HOLD action if that is the evidence-supported decision.

Never manufacture a SCALE action merely to prove the controller works.

## Audit evidence

Every execution should produce:
- proposal/governor/approval digests;
- pre-write provider snapshot ref;
- exact mutation intent digest;
- provider request identity (redacted, no token);
- attempt count;
- provider response/state classification;
- post-write read snapshot ref;
- verification result;
- rollback state/ref;
- total provider requests;
- spend effect classification;
- timestamps.

## Kill switches

At least:
- global Profit Engine kill;
- site kill (`dilivox`);
- provider write kill (`yandex_direct`);
- campaign/target quarantine;
- optional operation-class kill (e.g. budget increases).

Kill switches are checked immediately before mutation, not only at plan construction.

## Task-011 fixture acceptance targets

At minimum:
1. Governor-ready +10% -> executable plan in mock adapter only;
2. +20.00% -> allowed with all guards;
3. +20.01% without exact approval envelope -> zero provider requests;
4. +20.01% with mismatched proposal approval -> zero provider requests;
5. +20.01% with exact valid approval -> mock execution eligible;
6. kill switch flipped after planning -> zero provider writes;
7. target drift -> zero provider writes;
8. same execution id replay -> one mutation maximum;
9. timeout after ambiguous mutation -> read-before-retry prevents duplicate mutation;
10. partial failure -> rollback-required/quarantine state;
11. read-after-write mismatch -> not VERIFIED;
12. private core cannot call controller/provider adapter directly without public proposal/governor evidence;
13. no arbitrary provider payload path;
14. secret/token not present in logs/evidence;
15. all earlier public/private tests stay green.

## External launch blocker

Live Direct/Metrica/YAN credentials remain external blockers. Task 011 engineering can be completed with a strict mock/fake provider adapter, but real execution must stay disabled until provider doctor PASS and Editing access is explicitly enabled after controller acceptance.
