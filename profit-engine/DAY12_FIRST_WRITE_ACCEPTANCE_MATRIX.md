# PROFIT ENGINE — DAY 12 FIRST WRITE ACCEPTANCE MATRIX

Status: CANONICAL
Updated: 2026-08-29

Day 12 succeeds only if one bounded real Direct mutation is authorized by the accepted decision chain, dispatched once, verified by read-back, fully audited and kept inside Owner capital/safety limits.

## A. Prerequisite

PASS only if Task 011/011R is accepted by Central Brain on exact GREEN SHA.

## B. Owner permission transition

PASS only if:
- Central Brain declared controller ready for Editing upgrade;
- Owner explicitly changed the relevant Managing Account access Reading -> Editing;
- fresh Owner UI evidence is bound to the exact operator/managed-target relationship;
- exact operator and managed advertiser remain separately bound.

Editing does not itself authorize a mutation.

## C. Credential/live scope doctor

Direct: secret-safe OAuth load, intended operator and exact managed advertiser readable, exact target readable, permission evidence accepted through the canonical manager-UI gate.

Metrica: `metrika:read` path passes for intended counter/site and goals are readable.

YAN Statistics: separate Statistics OAuth passes for exact `dilivox.ru` reconciliation scope.

Ambiguous/missing live scope blocks all writes.

## D. Live money/data quality

SCALE/TEST requires accepted current Direct spend, Metrica attribution, YAN reconciliation, no DQ hold, computable accepted money, mature/optimizer-consumable measurement, current public/private contract identity.

Safety STOP/HOLD may proceed on accepted safety evidence without pretending that K5 is already proven.

Campaign/day revenue cannot substitute for cohort K5.

## E. Candidate selection

Exactly one live candidate selected by Central Brain from accepted evidence and bound to exact provider target/action, ActionProposal digest, Governor evidence digest and current provenance.

No name/URL/date/fuzzy selection.

## F. First-live method allowlist — CURRENT API

The first production writer is deliberately narrower than the Day-11 synthetic controller.

Allowed first-live methods only:
- `campaign.suspend`;
- `campaign.resume`;
- `ad.suspend`;
- `ad.resume`.

`campaign.update_budget` is NOT allowed for the first production write.

Reason: the current Yandex Direct API has moved budget control away from legacy campaign `DailyBudget`; strategy-aware budget control uses `WeeklySpendLimit`. The older Day-11 DailyBudget mapping remains useful synthetic safety evidence but must not be used as a live production request.

Budget automation stays fail-closed until a separate strategy-aware `WeeklySpendLimit` implementation, tests and Central Brain acceptance are complete.

## G. >20% Owner approval

When strategy-aware budget automation is later enabled, exact trusted Owner approval remains mandatory for any weekly budget increase above +20%. Proposal/target/action/amount/currency/version/time/supersession/authority must all pass.

Failure => zero dispatches.

## H. Fresh preflight

Exact provider ID, state/status, current strategy where relevant, request/source provenance, freshness and DQ state must pass.

For suspend/resume the prior state must prove that the requested transition is coherent and reversible.

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

Suspend/resume request must contain exactly one provider ID through the documented Direct `SelectionCriteria.Ids` shape.

No extra object, no second ID, no create/add/delete/archive/moderate/strategy migration in the first live write.

## L. Writer arming

Production writer disabled by default.

First-write arming must be explicit, scoped to accepted readiness digest + candidate digest + ControllerPlan digest + exact target + exact method, time-bounded, max one dispatch attempt, auditable and disarmable.

## M. Dispatch

Use the canonical Direct JSON v501 service endpoint.

Append `DISPATCH_STARTED` before send. One provider request, one provider object, no automatic retry. Mutation transport is single-attempt even on timeout/429/5xx.

Capture transport/HTTP, per-object result, RequestId/Units where present, with secret redaction.

## N. Success

Immediately perform exact read-back.

No top-level blocking error; intended object success; read-back exact normalized state equals the plan-derived expectation; audit chain valid.

Then and only then: `GUARDED_PRODUCTION_LAUNCHED`.

## O. Timeout/uncertain

No immediate retry. Read-back first.
- desired state present => recovered applied and may classify as launched;
- unchanged prior state => `PRODUCTION_EXECUTION_UNCERTAIN` until a new explicit bounded retry plan exists;
- unexpected/unreadable state => `PRODUCTION_EXECUTION_UNCERTAIN`.

## P. Rollback

Never blind/automatic. Exact immutable prior state required; rollback separately passes authorization/kill/lock/preflight/audit/read-back gates.

## Q. Audit completeness

Evidence chain includes candidate selection, credential/scope certification, proposal/governor/approval refs, preflight, lock, TOCTOU, kill-switch recheck, request digest, writer arm, dispatch, provider response, read-back/final state, lock release/disarm.

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
