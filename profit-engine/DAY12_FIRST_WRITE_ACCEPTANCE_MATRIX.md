# PROFIT ENGINE — DAY 12 FIRST WRITE ACCEPTANCE MATRIX

Status: CANONICAL
Updated: 2026-08-28

Day 12 succeeds only if one bounded real Direct mutation is authorized by the accepted decision chain, dispatched once, verified by read-back, fully audited and kept inside Owner capital/safety limits.

## A. Prerequisite

PASS only if Task 011/011R is accepted by Central Brain on exact GREEN SHA.

## B. Owner permission transition

PASS only if:
- Central Brain declared controller ready for Editing upgrade;
- Owner explicitly changed relevant Direct access Reading -> Editing;
- exact account/client permission state is re-read after change.

Editing does not itself authorize a mutation.

## C. Credential/live scope doctor

Direct: secret-safe OAuth load, intended advertiser/client readable, exact target readable, permission state confirmed.

Metrica: `metrika:read` path passes for intended counter/site.

YAN Statistics: separate Statistics OAuth passes for intended partner/site and reconciliation scope.

Ambiguous/missing live scope blocks SCALE/TEST.

## D. Live money/data quality

SCALE/TEST requires accepted current Direct spend, Metrica attribution, YAN reconciliation, no DQ hold, computable accepted money, mature/optimizer-consumable measurement, current public/private contract identity.

Campaign/day revenue cannot substitute for cohort K5.

## E. Candidate selection

Exactly one live candidate selected from accepted evidence and bound to exact provider target/action, ActionProposal digest, Governor evidence digest and current provenance.

No name/URL/date/fuzzy selection.

## F. >20% Owner approval

Exact trusted Owner approval required for >20% increase. Proposal/target/action/amount/currency/version/time/supersession/authority must all pass.

Failure => zero dispatches.

## G. Fresh preflight

Exact provider ID, state/status, strategy subtype, current budget/currency semantics, request/source provenance, freshness and DQ state must pass.

## H. Cadence

Budget write requires integrity-valid current-day evidence for exact campaign/timezone basis and zero prior autonomous mutations.

Max one autonomous campaign budget mutation per campaign/day.

## I. Lock + TOCTOU

Immediately before dispatch:
1. acquire exact target lock;
2. fresh read-only provider fetch;
3. canonical TOCTOU compare;
4. mismatch/stale/held => zero dispatches.

## J. Runtime kill switches

Recheck global/site/provider/advertiser/target/experiment-action after fresh preflight and before dispatch.

Any active applicable switch => zero dispatches.

## K. Exact request

Exactly one mutation object, derived from immutable accepted ControllerPlan.

Budget update: exact provider entity ID + authorized provider daily amount/micros only.
Suspend/resume: exact entity ID + method-derived desired state only.

Any mismatch/extra field => zero dispatches.

## L. Writer arming

Production writer disabled by default. First-write arming must be explicit, scoped to accepted plan digest/target/method, bounded to one dispatch attempt, auditable and disarmable.

## M. Dispatch

Append `DISPATCH_STARTED` before send. One provider request, one provider object, no automatic loop. Capture transport/HTTP, per-object result, RequestId/Units where present, with secret redaction.

## N. Success

No top-level blocking error; intended object success; read-back performed; exact normalized state equals plan-derived expectation; audit chain valid.

Then and only then: `GUARDED_PRODUCTION_LAUNCHED`.

## O. Timeout/uncertain

No immediate retry. Read-back first.
- desired state present => recovered applied;
- unchanged prior state => new explicit bounded retry plan required;
- unexpected state => `PRODUCTION_EXECUTION_UNCERTAIN`.

## P. Rollback

Never blind/automatic. Exact prior state required; rollback separately passes authorization/kill/lock/preflight/audit/read-back gates.

## Q. Audit completeness

Evidence chain includes candidate selection, credential/scope certification, proposal/governor/approval refs, preflight, cadence, lock, TOCTOU, kill-switch recheck, request digest, writer arm, dispatch, provider response, read-back/final state, lock release/disarm.

Hash/order/tamper validation required.

## R. Secret safety

No token/credential value in Git, issue/comments, evidence, audit, logs/exceptions or review screenshots.

## S. Terminal outcomes

Only:
- `GUARDED_PRODUCTION_LAUNCHED`;
- `PRODUCTION_WRITE_BLOCKED`;
- `PRODUCTION_EXECUTION_UNCERTAIN`;
- `PRODUCTION_ROLLBACK_VERIFIED`;
- `PRODUCTION_ROLLBACK_BLOCKED`.

## T. Economic proof boundary

A successful guarded write proves engineering closed-loop launch only. `K5 >= 5.0` requires later reconciled live economic evidence over mature periods/cohorts.