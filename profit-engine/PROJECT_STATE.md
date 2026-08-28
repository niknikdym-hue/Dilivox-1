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

Current private-core main:
`76b1b8670690f102a045243760dfe3d1e58513d5`

Private CI `33182663547`: GREEN.

Accepted Day-10 chain includes period-vs-cohort truth, `CohortRevenueEvidence v1`, ActionProposal v1, Budget Governor, exact +20.00/+20.01 Owner boundary and private ProfitAllocator in private core only. The private core remains proposal-only and has no provider write authority.

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

Tracking issue:
`#19 — Profit Engine Task 012 — Live guarded production launch`.

Canonical design:
`profit-engine/DAY12_LIVE_PRODUCTION_LAUNCH_DESIGN.md`

Canonical provider certification:
`profit-engine/DAY12_PROVIDER_LIVE_CERTIFICATION.md`

Canonical first-write matrix:
`profit-engine/DAY12_FIRST_WRITE_ACCEPTANCE_MATRIX.md`

Canonical task:
`profit-engine/tasks/TASK-012-LIVE-GUARDED-PRODUCTION-LAUNCH.md`

## Day-12 pre-Editing readiness harness — VERIFIED / GREEN

Verified readiness implementation:
`4419f14f0f1a74f00077f46bed268f2027b30d44`

Profit Engine CI `33200909842`: GREEN.

Evidence:
`profit-engine/evidence/TASK-012-PRE-EDITING-READINESS-HARNESS.md`

The runtime includes:
- `day12_readiness.py` fail-closed launch-readiness state machine;
- `day12_readiness_cli.py` read-only CLI reusing the existing Direct/Metrica/YAN doctor;
- negative tests for wrong controller SHA, Reading/UNKNOWN permission, missing/failed providers and digest tamper.

Even when all doctor checks pass and Editing is later confirmed, this harness can only produce `READY_FOR_LIVE_CANDIDATE_SELECTION`; it does not grant provider write authority. `provider_write_allowed=false`, real provider requests remain 0, advertising spend remains 0 and the production writer remains disabled.

## Day-12 candidate binding + inert writer-arm scaffold — CENTRAL BRAIN ACCEPTED PRE-LIVE

New implementation chain reviewed after the previous verified state:

- `e09731a277c68acd9426f3a9d296444cec44a9df` — candidate binding + inert writer-arm contract;
- `a4a0e492e17d4d953195fbf3180293ae9d0654fd` — tests;
- `3fbfae2090b89af17813e8d70e9920e90726e8e7` — executor evidence.

Exact reviewed HEAD CI: Profit Engine run `33201727671` — GREEN.

Central Brain acceptance:
`profit-engine/evidence/TASK-012-CENTRAL-BRAIN-PRELIVE-ACCEPTANCE.md`

Acceptance commit:
`d45abca6e6c2311cc4aacb04db27f4cf0a6aef5a`

Accepted scope is deliberately narrow:
- exact candidate/ControllerPlan/digest binding;
- measurement/provenance refs required;
- public runtime candidate structure remains non-authorizing;
- writer-arm intent is one-shot but explicitly inert/non-executable;
- no provider transport added;
- provider requests/spend remain 0;
- production writer remains disabled;
- >20% weekly budget increases remain gated by the already-accepted exact trusted Owner approval chain in the ControllerPlan.

Important interpretation: `selected_by="CENTRAL_BRAIN"` is an audit marker, not cryptographic caller authentication. The runtime object alone is never proof of Central Brain live candidate acceptance. Exact live selection authority must still be recorded separately from accepted live evidence before any executable writer arming.

## Owner permission gate — CURRENT FIRST CANONICAL BLOCKER

Central Brain has accepted the controller, pre-Editing readiness harness and inert pre-live candidate/writer-arm scaffold as ready for the permission upgrade.

The single next canonical Owner action is:

`Yandex Direct access: Reading -> Editing`.

This permission change is necessary for Day-12 live certification but DOES NOT authorize a write by itself.

After the change, exact account/client permission state must be re-read and the prepared read-only Direct/Metrica/YAN certification must run before any live candidate can be selected.

## External provider credential/live-certification gate

Before the first real write:
- Direct OAuth/read doctor must pass for exact advertiser/client/target;
- Metrica read doctor must pass for exact counter/site;
- YAN Statistics uses separate OAuth and must pass exact partner/site reconciliation scope where required;
- token values remain outside Git/chat/issues/logs/screenshots;
- local secrets use Keychain; production target is Lockbox.

Latest redacted Owner-side terminal observation on 2026-08-28:
- Metrica management read returned HTTP `403` with error class `invalid_token` / `Invalid oauth_token`;
- YAN Statistics doctor reported `BLOCKED_MISSING_CREDENTIAL` for its separate OAuth token;
- no token/secret value is recorded here.

These observations mean current provider certification is not PASS. They do not authorize changing Yandex account permissions or credentials automatically. Day 12 must replace blockers with explicit live doctor PASS evidence before candidate selection or write arming.

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

Read `PROJECT_HANDOFF.md`, verify actual `origin/profit-engine` HEAD and private `main`, then read:
1. `profit-engine/PROJECT_STATE.md`;
2. `profit-engine/evidence/TASK-011-CENTRAL-BRAIN-ACCEPTANCE.md`;
3. `profit-engine/evidence/TASK-012-PRE-EDITING-READINESS-HARNESS.md`;
4. `profit-engine/evidence/TASK-012-CENTRAL-BRAIN-PRELIVE-ACCEPTANCE.md`;
5. `profit-engine/DAY12_LIVE_PRODUCTION_LAUNCH_DESIGN.md`;
6. `profit-engine/DAY12_PROVIDER_LIVE_CERTIFICATION.md`;
7. `profit-engine/DAY12_FIRST_WRITE_ACCEPTANCE_MATRIX.md`;
8. `profit-engine/tasks/TASK-012-LIVE-GUARDED-PRODUCTION-LAUNCH.md`;
9. issue #19.

Current first incomplete canonical gate: Owner Direct permission transition Reading -> Editing.
