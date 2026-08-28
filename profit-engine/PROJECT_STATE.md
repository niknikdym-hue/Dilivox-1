# PROFIT ENGINE — PROJECT STATE

Status: IMPLEMENTATION ACTIVE / DAY 12 — LIVE GUARDED PRODUCTION LAUNCH GATE
Updated: 2026-08-29
Canonical public branch: `profit-engine`
Private core branch: `main`

## Current objective

Launch a guarded-production, machine-operated, multi-site Profit Engine whose first closed loop is:

`Yandex Direct -> Dilivox -> behavior -> YAN revenue -> attribution/reconciliation -> private decision core -> public ActionProposal -> Budget Governor -> guarded Direct controller -> measured outcome`.

First production site: `site_id=dilivox` / `dilivox.ru`.

Primary target: `1 RUB Yandex Direct spend -> 5 RUB YAN advertising revenue attributable to the acquired Dilivox audience`.

This remains a target, not a claimed result.

## Locked governance

- `PROTECT CAPITAL -> MEASURE MONEY -> STOP LOSSES -> FIND PROFIT -> SCALE PROFIT -> REPEAT`;
- private core emits proposals only and never writes to providers;
- automatic weekly budget increase above +20% requires exact explicit Owner approval;
- one autonomous campaign budget mutation per campaign/day at launch;
- exactly one provider object per first launch write;
- no blind retry;
- no provider/site mutation before the canonical Day-12 live gates pass;
- no secret values in Git/chat/issues/logs;
- chat is not source of truth.

## Current verified repository state

Public repository: `niknikdym-hue/Dilivox-1`, branch `profit-engine`.

Latest code HEAD verified by CI:
`b66050fc8dc7b5b42e8b19ebbb2f8043b5869b37` — provider-only Day-12 permission authority reflected through launch-gate tests.

Profit Engine CI run `33218249298`: all Python tests, Node tests, JSON validation and diff whitespace checks SUCCESS.

Follow-up evidence commit:
`d64bef6aaf964dceb7336ea8d4db22a9881913bd` — records the fail-closed Direct permission fix; no provider mutation or secret value.

Private repository: `niknikdym-hue/profit-engine-core`, branch `main`:
`76b1b8670690f102a045243760dfe3d1e58513d5`.

Private CI `33182663547`: SUCCESS.

Private core remains proposal-only, unchanged by Day 12, and has no provider transport or provider write authority.

Open launch-critical issues:
- public: `#19 — Profit Engine Task 012 — Live guarded production launch`;
- private core: none.

No new Codex implementation exists after the previously accepted Day-12 pre-live scaffold. The current permission/readiness hardening was advanced by Central Brain directly on the canonical public branch.

## Tasks 001–010R — ACCEPTED

Day-10 final public contract:
`98c6d3f0c0105c30cfc90a6d5fdf653c2aceb8d6`.

Private core accepted contract:
`1709925f5b2d29f9c038dde7caca8054b51eea6f`.

Accepted Day-10 chain includes period-vs-cohort truth, `CohortRevenueEvidence v1`, ActionProposal v1, Budget Governor, exact +20.00/+20.01 Owner boundary and private ProfitAllocator in private core only.

## Task 011 + 011R — ACCEPTED / DAY 11 COMPLETE

Central Brain acceptance:
`profit-engine/evidence/TASK-011-CENTRAL-BRAIN-ACCEPTANCE.md`.

Accepted controller implementation chain:
- initial Task 011: `d8d3a9887d4a3e38d90ac0cfb7567092aaf3997a`;
- final Task 011R rework: `a494d30b49c8d11687be56cdab870a5d83356e02`.

Final Profit Engine CI `33187660342`: GREEN.

Accepted controller properties include exact proposal/Governor binding, trusted Owner approval >20%, exact provider identity, fresh preflight + TOCTOU, kill-switch recheck, current-day cadence, per-target lock, exact one-object request binding, read-back, no blind retry, immutable-preflight rollback source, audit/redaction and production writer disabled by default.

## Immediate active task — Day 12

Tracking issue:
`#19 — Profit Engine Task 012 — Live guarded production launch`.

Canonical authority:
- `profit-engine/DAY12_LIVE_PRODUCTION_LAUNCH_DESIGN.md`;
- `profit-engine/DAY12_PROVIDER_LIVE_CERTIFICATION.md`;
- `profit-engine/DAY12_FIRST_WRITE_ACCEPTANCE_MATRIX.md`;
- `profit-engine/tasks/TASK-012-LIVE-GUARDED-PRODUCTION-LAUNCH.md`.

## Day-12 pre-live scaffold — ACCEPTED

Evidence:
- `profit-engine/evidence/TASK-012-PRE-EDITING-READINESS-HARNESS.md`;
- `profit-engine/evidence/TASK-012-CENTRAL-BRAIN-PRELIVE-ACCEPTANCE.md`.

Accepted scope remains deliberately non-authorizing:
- exact candidate/ControllerPlan/digest binding;
- measurement/provenance refs required;
- public runtime candidate structure is non-authorizing;
- writer-arm intent remains inert/non-executable;
- provider requests/spend remain 0;
- production writer remains disabled;
- `selected_by="CENTRAL_BRAIN"` is only an audit marker, not authentication;
- >20% weekly budget increases remain gated by exact trusted Owner approval.

## Live provider read certification — VERIFIED FOR CREDENTIAL/IDENTITY ACCESS

Evidence:
`profit-engine/evidence/TASK-012-LIVE-PROVIDER-BINDING.md`.

Recorded Owner-side live proofs, without secret values:
- YAN Statistics API: HTTP 200, exact `dilivox.ru` statistics readable;
- Yandex Metrica: HTTP 200, exact counter `110349067`, provider permission `edit`;
- Yandex Direct: HTTP 200, exact client `reklamadymova` / ClientId `100716697` visible.

Credential/read availability is therefore no longer the blocker. These read proofs do not authorize a Direct mutation.

## Direct permission gate — PROVIDER-OBSERVED AND API-ENFORCED

Evidence:
- `profit-engine/evidence/TASK-012-DIRECT-PERMISSION-READ-PROBE.md`;
- `profit-engine/evidence/TASK-012-PROVIDER-PERMISSION-FAIL-CLOSED-FIX.md`.

Permission/readiness implementation chain:
- `1b79bcd941ef01d81c761734407978500634f3a9` — Direct doctor derives `direct.permission=EDITING|READING|UNKNOWN` from provider data;
- `756fb0980a6e5038096559cf5eda611ccbf33166` — CLI removes manual permission assertion;
- `696e9c41515f2f0ce77b3300620fd2143a6c221a` — one-command live read-only probe;
- `86d917cc8b3165a6b7b2da1749fe044a122b0183` — Owner entrypoint;
- `4dd17793283961fe1df99a9cc1ea60e1affc09e9` — remove the remaining internal manual permission fallback; readiness v1.2 now accepts provider-observed permission only;
- `2c94fe7575f954c18591ed89a4e4e702e035d410` — regression tests prove manual override is not an API;
- `b66050fc8dc7b5b42e8b19ebbb2f8043b5869b37` — candidate-selection tests require provider-observed Editing.

CI `33218249298` on `b66050fc8dc7b5b42e8b19ebbb2f8043b5869b37`: SUCCESS across all test/validation steps.

Canonical invariant is now enforced in the runtime API, not merely by the CLI: `UNKNOWN` cannot be promoted by caller assertion, `READING` remains blocked, and only provider-observed `EDITING` can satisfy the permission stage. Readiness still cannot authorize writes: `provider_write_allowed=false`, production writer remains disabled, and no real provider request/spend is introduced by this layer.

## Current first incomplete canonical gate

Execute the read-only Day-12 readiness entrypoint in the Owner environment where the existing Keychain credentials are available:

`bash profit-engine/scripts/day12-live-readiness.sh`

Branching rule:
- observed `READING` => the single Owner-only action is to change the relevant Yandex Direct access to Editing; no other action is authorized;
- observed `EDITING` + all three doctors PASS => Central Brain may advance to exact live candidate selection;
- observed `UNKNOWN` or any provider failure => remain blocked and diagnose read-only; zero dispatches.

Until that provider-observed result exists, production write remains blocked and no permission change should be assumed necessary.

## First real mutation boundary

Only after provider-observed Editing, all live doctors PASS, exact Central Brain live candidate acceptance and all accepted controller gates:

1. exact candidate selection from accepted evidence;
2. fresh provider preflight;
3. proposal/Governor/Owner approval revalidation;
4. current-day cadence;
5. exact execution lock;
6. fresh TOCTOU read;
7. runtime kill-switch recheck;
8. exact one-object request from immutable plan;
9. narrow single-plan production writer arming;
10. one Direct dispatch;
11. read-back;
12. immutable audit;
13. rollback only if separately guarded/authorized.

Any failed gate => zero dispatches.

## Launch states

- `GUARDED_PRODUCTION_LAUNCHED`;
- `PRODUCTION_WRITE_BLOCKED`;
- `PRODUCTION_EXECUTION_UNCERTAIN`;
- `PRODUCTION_ROLLBACK_VERIFIED`;
- `PRODUCTION_ROLLBACK_BLOCKED`.

Only a real bounded mutation that is applied and verified counts as engineering launch.

## Economic proof boundary

Engineering launch does not prove `K5 >= 5.0`.

Economic proof requires reconciled live Direct spend + Metrica-attributed YAN revenue + YAN control totals over mature periods/cohorts.

## Resume protocol

Verify actual public/private HEADs first, then read:
1. `profit-engine/PROJECT_STATE.md`;
2. `profit-engine/evidence/TASK-011-CENTRAL-BRAIN-ACCEPTANCE.md`;
3. `profit-engine/evidence/TASK-012-PRE-EDITING-READINESS-HARNESS.md`;
4. `profit-engine/evidence/TASK-012-CENTRAL-BRAIN-PRELIVE-ACCEPTANCE.md`;
5. `profit-engine/evidence/TASK-012-LIVE-PROVIDER-BINDING.md`;
6. `profit-engine/evidence/TASK-012-DIRECT-PERMISSION-READ-PROBE.md`;
7. `profit-engine/evidence/TASK-012-PROVIDER-PERMISSION-FAIL-CLOSED-FIX.md`;
8. `profit-engine/DAY12_LIVE_PRODUCTION_LAUNCH_DESIGN.md`;
9. `profit-engine/DAY12_PROVIDER_LIVE_CERTIFICATION.md`;
10. `profit-engine/DAY12_FIRST_WRITE_ACCEPTANCE_MATRIX.md`;
11. `profit-engine/tasks/TASK-012-LIVE-GUARDED-PRODUCTION-LAUNCH.md`;
12. issue #19.
