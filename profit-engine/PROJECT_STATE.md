# PROFIT ENGINE — PROJECT STATE

Status: IMPLEMENTATION ACTIVE / DAY 12 — LIVE GUARDED PRODUCTION LAUNCH GATE
Updated: 2026-08-28
Canonical public branch: `profit-engine`
Private core branch: `main`

## Current objective

Launch a guarded-production, machine-operated, multi-site Profit Engine whose first closed loop is:

`Yandex Direct -> Dilivox -> behavior -> YAN revenue -> attribution/reconciliation -> private decision core -> public ActionProposal -> Budget Governor -> guarded Direct controller -> measured outcome`.

First production site: `site_id=dilivox` / `dilivox.ru`.

Primary target:

`1 RUB Yandex Direct spend -> 5 RUB YAN advertising revenue attributable to the acquired Dilivox audience`.

This remains a target, not a claimed result.

## Locked governance

- `PROTECT CAPITAL -> MEASURE MONEY -> STOP LOSSES -> FIND PROFIT -> SCALE PROFIT -> REPEAT`;
- automatic weekly budget increase above +20% requires exact explicit Owner approval;
- private core emits proposals only and never writes to providers;
- one autonomous campaign budget mutation per campaign/day at launch;
- exactly one provider object per first launch write;
- no blind retry;
- chat is not source of truth.

## Tasks 001–010R — ACCEPTED

Day-10 final public contract:
`98c6d3f0c0105c30cfc90a6d5fdf653c2aceb8d6`

Public CI `33180647500`: GREEN.

Private core accepted contract:
`1709925f5b2d29f9c038dde7caca8054b51eea6f`

Private CI `33180767637`: GREEN.

Accepted Day-10 chain includes period-vs-cohort truth, `CohortRevenueEvidence v1`, ActionProposal v1, Budget Governor, exact +20.00/+20.01 Owner boundary and private ProfitAllocator in private core only.

## Task 011 + 011R — ACCEPTED / DAY 11 COMPLETE

Central Brain acceptance:

`profit-engine/evidence/TASK-011-CENTRAL-BRAIN-ACCEPTANCE.md`

Accepted controller implementation chain:
- initial Task 011: `d8d3a9887d4a3e38d90ac0cfb7567092aaf3997a`;
- final Task 011R rework: `a494d30b49c8d11687be56cdab870a5d83356e02`.

Final Profit Engine CI `33187660342`: GREEN.

Accepted controller properties include:
- exact proposal/Governor binding;
- trusted Owner approval >20%;
- exact provider identity;
- fresh preflight + actual dispatch-path TOCTOU;
- runtime kill-switch recheck;
- integrity/current-day cadence evidence;
- exact per-target lock acquire/release;
- exact one-object request target/budget binding;
- plan-derived read-back;
- no blind retry;
- rollback from immutable preflight only;
- hash-linked audit/redaction;
- production writer disabled by default;
- zero real provider requests/spend during Day 11.

Issues #17 and #18 are completed.

## Immediate active task — Day 12

Canonical design:

`profit-engine/DAY12_LIVE_PRODUCTION_LAUNCH_DESIGN.md`

Canonical provider certification:

`profit-engine/DAY12_PROVIDER_LIVE_CERTIFICATION.md`

Canonical first-write matrix:

`profit-engine/DAY12_FIRST_WRITE_ACCEPTANCE_MATRIX.md`

Canonical task:

`profit-engine/tasks/TASK-012-LIVE-GUARDED-PRODUCTION-LAUNCH.md`

## Owner permission gate — CURRENT FIRST BLOCKER

Central Brain has accepted the controller as ready for permission upgrade.

The next Owner action may now be:

`Yandex Direct access: Reading -> Editing`.

This permission change is necessary for Day-12 readiness but DOES NOT authorize a write by itself.

After the change, exact account/client permission state must be re-read and live certification must run before any mutation.

## External provider credential/live-certification gate

Before the first real write:
- Direct OAuth/read doctor must pass for exact advertiser/client/target;
- Metrica read doctor must pass for exact counter/site;
- YAN Statistics uses separate OAuth and must pass exact partner/site reconciliation scope where required;
- token values remain outside Git/chat/issues/logs/screenshots;
- local secrets use Keychain; production target is Lockbox.

Current historic classification before Day-12 certification was `BLOCKED_EXTERNAL_PROVIDER_CREDENTIAL`; Day 12 must replace that with live doctor evidence rather than assumptions.

## First real mutation boundary

After Editing and live doctors:

1. Central Brain selects exactly one live candidate from accepted evidence;
2. fresh provider preflight;
3. current proposal/Governor/Owner approval revalidation;
4. current-day cadence;
5. exact execution lock;
6. fresh TOCTOU read;
7. runtime kill-switch recheck;
8. exact one-object request derived from immutable plan;
9. narrow single-plan production writer arming;
10. one Direct dispatch;
11. read-back;
12. immutable audit;
13. rollback only if separately guarded/authorized.

Any failed gate => zero dispatches.

## Launch states

- `GUARDED_PRODUCTION_LAUNCHED`
- `PRODUCTION_WRITE_BLOCKED`
- `PRODUCTION_EXECUTION_UNCERTAIN`
- `PRODUCTION_ROLLBACK_VERIFIED`
- `PRODUCTION_ROLLBACK_BLOCKED`

Only a real bounded mutation that is applied and verified counts as engineering launch.

## Economic proof boundary

Engineering launch does not prove `K5 >= 5.0`.
Economic proof requires later reconciled live Direct spend + Metrica-attributed YAN revenue + YAN control totals over mature periods/cohorts.

## Resume protocol

Read `PROJECT_HANDOFF.md`, verify actual `origin/profit-engine` HEAD, then read:
1. `profit-engine/PROJECT_STATE.md`;
2. `profit-engine/evidence/TASK-011-CENTRAL-BRAIN-ACCEPTANCE.md`;
3. `profit-engine/DAY12_LIVE_PRODUCTION_LAUNCH_DESIGN.md`;
4. `profit-engine/DAY12_PROVIDER_LIVE_CERTIFICATION.md`;
5. `profit-engine/DAY12_FIRST_WRITE_ACCEPTANCE_MATRIX.md`;
6. `profit-engine/tasks/TASK-012-LIVE-GUARDED-PRODUCTION-LAUNCH.md`.

Current first incomplete gate: Owner Direct permission transition Reading -> Editing.