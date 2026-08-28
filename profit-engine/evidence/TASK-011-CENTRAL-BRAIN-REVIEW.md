# TASK 011 — CENTRAL BRAIN REVIEW

Status: `REWORK_REQUIRED`
Reviewed implementation SHA: `d8d3a9887d4a3e38d90ac0cfb7567092aaf3997a`

Task 011 is not accepted yet. The implementation is structurally strong, but Central Brain found launch-critical execution-binding gaps that can bypass the intended Day-11 write-safety gate.

## Accepted portions preserved during rework

- canonical controller state model with no real `EXECUTED` state;
- proposal/governor digest binding;
- basic >20% proposal/target/amount/expiry approval binding;
- exact provider identity registry;
- preflight snapshot contract;
- method allowlist;
- explicit weekly-to-daily budget mapping;
- one-object limit;
- kill-switch model at plan time;
- no-blind-retry synthetic model;
- read-back concept;
- preflight-derived rollback;
- hash-linked audit chain;
- secret redaction;
- default real writer disabled;
- zero real provider requests and spend.

## Launch-critical gaps

1. `locks=None` can still produce `READY_FOR_DAY12_EXECUTION`, while fake execution records lock acquisition without actually acquiring the lock.
2. pre-dispatch TOCTOU comparison exists as a helper but is not enforced on the fake dispatch path.
3. mutation cadence evidence lacks integrity binding and current-day validation.
4. request object is not bound to the exact provider entity and authorized budget amount, so an approved plan can theoretically carry a different mutation payload.
5. >20% Owner approval authority is self-declarable through an arbitrary authority string; trusted Owner-authority resolution is not enforced.
6. read-back completion can depend on caller-supplied expected state instead of a state derived from the immutable mutation plan.

Canonical bounded rework:

`profit-engine/tasks/TASK-011-REWORK-EXECUTION-BINDINGS.md`

Direct Editing remains disabled until Central Brain accepts the rework.
