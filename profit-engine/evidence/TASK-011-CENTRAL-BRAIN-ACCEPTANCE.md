# TASK 011 / 011R — CENTRAL BRAIN ACCEPTANCE

Status: ACCEPTED
Date: 2026-08-28
Acceptance authority: Central Brain

## Accepted implementation

Task 011 initial controller implementation:
`d8d3a9887d4a3e38d90ac0cfb7567092aaf3997a`

Task 011R bounded execution-binding rework final:
`a494d30b49c8d11687be56cdab870a5d83356e02`

Final Profit Engine CI:
`33187660342` — GREEN on exact final SHA.

## Central Brain decision

`TASK_011_ACCEPTED_CONTROLLER_READY_FOR_EDITING_ACCESS_UPGRADE`

Day 11 write-safety gate is complete.

This acceptance does NOT authorize a provider write. It means the controller contract is ready for the next Owner permission transition and Day-12 live certification.

## Independently verified safety properties

Central Brain verified the implementation and negative tests for:

- exact immutable ActionProposal/Governor binding;
- no Budget Governor bypass;
- +20.00% clean boundary without extra approval;
- +20.01% requiring exact trusted OwnerApprovalEvidence;
- trusted Owner authority registry and future/expired/superseded approval rejection;
- exact registered provider target identity;
- immutable fresh preflight snapshot;
- actual pre-dispatch TOCTOU comparison on the dispatch path;
- runtime kill-switch recheck after fresh preflight and before dispatch;
- integrity-bound current-day mutation-cadence evidence;
- maximum one autonomous campaign budget mutation per campaign/day;
- actual per-target execution-lock acquisition before dispatch and audited release;
- exactly one provider object per launch request;
- exact request target/amount/micros binding to ProviderBudgetPlan;
- lifecycle request strict field/state binding;
- plan-derived read-back expectation;
- no blind retry after timeout/uncertain response;
- read-back before retry decision;
- rollback derived from immutable preflight only;
- append-only hash-linked audit and tamper detection;
- secret/log redaction;
- production writer disabled by default;
- no real provider writer reachable under accepted Day-11 configuration.

## Regression and safety evidence

Task-011/011R controller tests: `23/23 PASS`
Full Python suite: `130/130 PASS`
Task-010R regression: `18/18 PASS`
Node suite: `22/22 PASS`
py_compile: PASS
JSON validation: `11/11 PASS`
git diff --check: PASS
secret/private-data scan: PASS
provider-write reachability scan: PASS

Global accepted Day-11 safety state:

- `REAL_PROVIDER_REQUESTS=0`
- `ADVERTISING_SPEND=0`
- `PRODUCTION_WRITER_ENABLED=false`
- Direct remained Reading during implementation/acceptance
- no Yandex/Tilda/site/Cloud mutation

## Day-12 boundary

The next Owner action may now be the explicit Direct permission transition:

`Reading -> Editing`

That permission change is necessary for Day-12 readiness but does NOT itself authorize a write.

Before the first real mutation, Day 12 must still pass:

1. live Direct credential/read doctor and exact advertiser/client identity;
2. live Metrica read certification;
3. live YAN Statistics read/reconciliation certification;
4. exact live target selection from accepted evidence;
5. fresh provider preflight;
6. current ActionProposal/Governor/Owner-approval gates;
7. current-day cadence;
8. actual execution lock;
9. fresh TOCTOU recheck;
10. runtime kill-switch recheck;
11. exact one-object request derived from accepted plan;
12. one bounded dispatch;
13. read-back;
14. immutable audit;
15. safe rollback only if separately authorized and exact prior state proves it.

Only a real bounded mutation that is applied and verified may produce:

`GUARDED_PRODUCTION_LAUNCHED`.

Fixtures and synthetic execution never count as production launch or proof that `K5 >= 5.0`.