# PROFIT ENGINE — DAY 12 FIRST WRITE ACCEPTANCE MATRIX PREWORK

Status: CENTRAL BRAIN PREWORK / NOT CANONICAL
Updated: 2026-08-28
Branch: `central-brain/day12-live-preflight-prework`
Depends on: Task 011R accepted

## Acceptance objective

Day 12 succeeds only if one bounded real Yandex Direct mutation is authorized by the accepted decision chain, dispatched once, verified by read-back, fully audited and kept inside the Owner's capital/safety limits.

No gate may be skipped merely because Direct Editing is enabled or an OAuth token works.

## A. Day-11 prerequisite

PASS only if:

- Task 011R is accepted by Central Brain;
- final public SHA is exact and GREEN;
- execution-lock, TOCTOU, runtime kill-switch, cadence integrity, request binding, trusted Owner authority and plan-derived read-back gates are accepted;
- Task 011/#17 is closed completed only after that acceptance.

FAIL => no Editing request, no write.

## B. Owner permission transition

PASS only if:

- Central Brain has explicitly declared controller ready for Editing access upgrade;
- Owner changes the relevant Direct access from Reading to Editing;
- account/client identity is re-read after the change;
- permission change is recorded without secrets.

Editing enablement alone does not authorize a mutation.

## C. Credential doctor

Direct:

- OAuth loads from secret-safe storage;
- no token value logged;
- read request to intended advertiser/client succeeds;
- acting login/client relationship is exact;
- exact registered target ID is readable;
- current account permission state is confirmed.

Metrica:

- `metrika:read` doctor passes for the intended counter/site;
- exact counter/site identity is proven.

YAN Statistics:

- separate Statistics API OAuth token loads from secret-safe storage;
- exact partner/site scope is proven;
- control-total/reconciliation read path works or is explicitly held.

Any missing/ambiguous credential scope => `PRODUCTION_WRITE_BLOCKED` for SCALE/TEST.

## D. Live money/data-quality gate

For SCALE/TEST action:

- current Direct spend evidence accepted;
- current Metrica attribution accepted;
- YAN reconciliation state compatible/accepted;
- no DATA_QUALITY_HOLD;
- money state computable/accepted;
- measurement mature;
- optimizer_consumable=true;
- public/private contract SHA identities current;
- no campaign/day-to-cohort semantic substitution.

Safety STOP/HOLD/QUARANTINE follows separate structural safety rules but still requires exact target/preflight/write-safety gates.

## E. Candidate selection

Exactly one live candidate is selected by Central Brain from accepted evidence.

Candidate record must bind:

- site_id;
- provider target ref;
- provider entity ID;
- action kind;
- ActionProposal digest;
- Governor evidence digest;
- private decision ref/digest where applicable;
- current live measurement/provenance refs;
- selection reason suitable for audit.

No candidate selection by campaign name, URL, date or intuition.

## F. Owner approval >20%

If weekly budget increase >20%:

- exact trusted OwnerApprovalEvidence required;
- proposal/target/action/amount/currency binding exact;
- approval current, non-future, non-expired, non-superseded;
- trusted Owner authority ref verified;
- one proposal approval cannot authorize another proposal.

Without PASS => zero dispatches.

## G. Fresh provider preflight

Immediately before execution planning:

- exact provider ID fetched read-only;
- state/status current;
- strategy subtype current;
- current provider daily budget current when relevant;
- currency/budget semantics current;
- no DQ holds;
- snapshot digest valid;
- freshness deadline valid;
- RequestId/Units retained if returned.

## H. Mutation cadence

Budget write:

- integrity-valid current-day cadence evidence;
- exact campaign ref;
- exact timezone/day basis;
- prior autonomous mutations = 0;
- audit/source refs present.

Profit Engine limit remains one autonomous campaign budget mutation per campaign/day.

## I. Lock + TOCTOU

Immediately before dispatch:

1. acquire exact per-target execution lock;
2. perform fresh read-only provider fetch;
3. compare fresh snapshot to expected preflight via accepted canonical helper;
4. material difference/stale/held => release/hold appropriately and zero dispatches.

No synthetic/audit-only lock assertion counts.

## J. Runtime kill-switch recheck

Recheck after lock and fresh pre-dispatch read:

- global;
- site;
- provider;
- advertiser/account;
- target;
- experiment/action.

Any active applicable switch => zero dispatches.

## K. Exact request derivation

Exactly one provider mutation object.

Request is derived from immutable accepted ControllerPlan.

Budget update:

- exact provider entity ID;
- exact authorized provider daily amount/micros;
- no extra mutation fields;
- compatible provider strategy/capability.

Suspend/resume:

- exact provider entity ID;
- exact method-compatible state operation;
- no extra mutation fields.

Mismatch => zero dispatches.

## L. Production writer arming

The production writer must be disabled by default.

For the first write, arming must be:

- explicit;
- scoped to the accepted plan digest/target/method;
- single-use or bounded to one dispatch attempt;
- auditable;
- reversible/disarmable;
- incapable of broad generic writes.

Arming is not Owner approval and does not bypass any other gate.

## M. Dispatch

Before network send append `DISPATCH_STARTED` audit record.

Dispatch rules:

- one provider request;
- one provider object;
- no automatic loop;
- capture transport/HTTP status;
- capture per-object provider result;
- capture RequestId/Units when present;
- secrets redacted.

## N. Clear success

PASS only if:

- provider response contains no top-level blocking error;
- intended object result is success;
- read-back is performed;
- read-back exact normalized state equals plan-derived expected state;
- audit chain validates.

Then classify `GUARDED_PRODUCTION_LAUNCHED`.

## O. Timeout/uncertain response

No immediate retry.

Required:

- read-back first;
- desired state present => recovered-applied classification;
- unchanged prior state => no automatic retry; a new explicit bounded retry plan is required;
- unexpected state => `PRODUCTION_EXECUTION_UNCERTAIN` and stop.

## P. Rollback

Rollback is never automatic merely because a write failed.

PASS only if:

- exact prior state known from immutable preflight;
- rollback candidate derived from that preflight;
- current state makes inverse safe;
- rollback separately passes kill-switch/lock/preflight/authorization/audit gates;
- rollback dispatch/read-back separately verified.

## Q. Audit evidence

Required complete chain includes at least:

- candidate selected;
- credential/live scope certified;
- proposal/governor/approval refs;
- preflight captured;
- cadence verified;
- lock acquired;
- TOCTOU revalidated;
- kill switches rechecked;
- request digest bound;
- writer armed;
- dispatch started;
- provider response received;
- read-back verified or uncertain state recorded;
- final launch/blocked classification;
- lock release/disarm record.

Hash/order/tamper validation required.

## R. Secret safety

PASS only if no credential/token value appears in:

- Git;
- issue/comment;
- evidence JSON/Markdown;
- audit payload;
- exception/log output;
- screenshots sent for review.

## S. Final launch outcomes

Only one of:

- `GUARDED_PRODUCTION_LAUNCHED`;
- `PRODUCTION_WRITE_BLOCKED`;
- `PRODUCTION_EXECUTION_UNCERTAIN`;
- `PRODUCTION_ROLLBACK_VERIFIED`;
- `PRODUCTION_ROLLBACK_BLOCKED`.

No fabricated success and no fixture result may count as production launch.

## T. Post-launch proof boundary

One successful guarded mutation proves engineering closed-loop launch only.

It does not prove the economic target `K5 >= 5.0`.

Economic proof requires subsequent reconciled live Direct spend + Metrica-attributed YAN revenue + YAN control-total evidence over mature periods/cohorts.