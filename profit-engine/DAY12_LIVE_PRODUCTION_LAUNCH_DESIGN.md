# PROFIT ENGINE — DAY 12 LIVE PRODUCTION LAUNCH DESIGN

Status: CANONICAL
Updated: 2026-08-28
Depends on: Task 011/011R accepted

## Objective

Day 12 converts the accepted dry-run controller into one bounded real closed-loop action:

`accepted decision -> Owner permission gate -> live provider certification -> exact live preflight -> one guarded Direct mutation -> read-back -> immutable audit -> launch decision`.

Engineering launch is achieved only if exactly one bounded real mutation is applied and verified.

## Mandatory pre-write gates

1. Task 011/011R accepted by Central Brain.
2. Owner explicitly changes relevant Direct access from Reading to Editing.
3. Direct live credential/read doctor passes using secret-safe local credential loading.
4. Metrica read certification passes for exact counter/site scope.
5. YAN Statistics read/reconciliation certification passes or the relevant money action is held.
6. Exact provider target is selected from trusted provider identity, never by name/URL/date/fuzzy match.
7. Fresh provider preflight snapshot passes integrity/freshness/DQ gates.
8. Current ActionProposal and Governor evidence are integrity-valid.
9. If weekly increase >20%, exact trusted OwnerApprovalEvidence is present/current.
10. Integrity-valid current-day mutation cadence is clean.
11. Exact per-target execution lock is acquired.
12. Fresh pre-dispatch provider snapshot matches expected state (TOCTOU gate).
13. Kill switches are rechecked immediately before dispatch.
14. Exactly one normalized request object is derived from immutable ControllerPlan and bound to exact provider target/action/budget.
15. Production writer is explicitly armed only for this bounded accepted plan.

Any failed gate => zero dispatches.

## First real mutation selection

Central Brain selects the live candidate only from current accepted evidence.

Preferred order:

1. reversible STOP/suspend action justified by safety/stop-loss evidence;
2. bounded resume only when exact prior/current state proves it is intended;
3. bounded campaign budget update only when money evidence is accepted and proposal is inside approved envelope;
4. never create/add/delete/archive/moderate/strategy-migrate for the first launch write.

No fixture or planning document preselects a production campaign.

## Direct provider constraints

Current Direct API contract is modeled with launch rules stricter than provider capability:

- exactly one provider object per mutation request;
- maximum one autonomous campaign budget mutation per campaign/day;
- provider daily-budget mapping must be explicit and exact;
- provider strategy/capability incompatibility blocks execution;
- response `RequestId` and `Units` are retained as secret-safe audit metadata when available.

## Credential boundary

Secrets remain outside Git/chat/evidence:

- local: macOS Keychain;
- production target: Yandex Lockbox;
- configuration contains references only, never token values.

Direct, Metrica and YAN token semantics remain distinct and least-privilege.

## Execution sequence

Immediately before write:

`candidate -> credential/scope certification -> preflight -> proposal/governor/approval revalidation -> cadence -> lock -> fresh TOCTOU read -> runtime kill-switch recheck -> exact request derivation -> bounded writer arming -> DISPATCH_STARTED`.

Then:

`one provider request -> per-object result -> read-back -> plan-derived expected-state comparison -> terminal classification -> disarm/release lock`.

## Uncertain result rule

Timeout/ambiguous result never triggers immediate retry.

Required sequence:

`dispatch once -> read-back -> applied / unchanged / unexpected classification`.

- desired state already present => recovered-applied;
- unchanged state => a new explicit bounded retry plan may be considered later;
- unexpected state => stop as execution uncertain.

## Rollback

Rollback is separate guarded execution, not an automatic inverse call.

It requires exact immutable prior state, fresh current state, separate lock/kill/preflight/authorization/audit gates, and read-back verification.

## Terminal launch states

- `GUARDED_PRODUCTION_LAUNCHED`
- `PRODUCTION_WRITE_BLOCKED`
- `PRODUCTION_EXECUTION_UNCERTAIN`
- `PRODUCTION_ROLLBACK_VERIFIED`
- `PRODUCTION_ROLLBACK_BLOCKED`

Only the first state counts as engineering closed-loop launch.

## Economic proof boundary

One guarded mutation proves engineering launch only.

It does not prove the target `K5 >= 5.0`.
Economic proof requires later reconciled live Direct spend + Metrica-attributed YAN revenue + YAN control-total evidence over mature periods/cohorts.