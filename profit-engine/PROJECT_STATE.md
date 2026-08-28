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

Current reviewed Day-12 rework/evidence HEAD:
`9841c27eff7ce64250d163c78e27b8a2f5dadb13`.

Profit Engine CI run `33221266711`: SUCCESS.

This head includes the fail-closed Direct Managing Account / managed advertiser separation and the evidence that supersedes the previous manager-permission inference.

Private repository: `niknikdym-hue/profit-engine-core`, branch `main`:
`76b1b8670690f102a045243760dfe3d1e58513d5`.

Private CI `33182663547`: SUCCESS.

Private core remains proposal-only, unchanged by Day 12, and has no provider transport or provider write authority.

Open launch-critical issues:
- public: `#19 — Profit Engine Task 012 — Live guarded production launch`;
- private core: none.

No new Codex implementation exists after the previously accepted Day-12 pre-live scaffold. The current permission/identity rework was advanced by Central Brain directly on the canonical public branch.

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

## Live provider read certification — VERIFIED FOR METRICA/YAN AND DIRECT OPERATOR READ ACCESS

Evidence:
`profit-engine/evidence/TASK-012-LIVE-PROVIDER-BINDING.md`.

Recorded Owner-side live proofs, without secret values:
- YAN Statistics API: HTTP 200, exact `dilivox.ru` statistics readable;
- Yandex Metrica: HTTP 200, exact counter `110349067`, provider permission `edit`;
- Yandex Direct: HTTP 200 for the technical Direct identity.

Important correction: the earlier Direct result `Login=reklamadymova` identifies the technical Managing Account/operator, not by itself the distinct managed owner advertiser account. That result proves OAuth/operator read access only and must not be treated as exact owner-target certification.

## Direct Managing Account / managed target gate — REWORKED / FAIL CLOSED

Canonical access setup records:
- main Direct advertiser/chief representative is the owner account;
- technical Direct identity `reklamadymova` is a separate Managing Account;
- the Managing Account relationship was deliberately set to `Reading` during staged rollout.

Evidence:
- `profit-engine/evidence/TASK-012-DIRECT-PERMISSION-READ-PROBE.md`;
- `profit-engine/evidence/TASK-012-PROVIDER-PERMISSION-FAIL-CLOSED-FIX.md`;
- `profit-engine/evidence/TASK-012-DIRECT-MANAGER-TARGET-MISBINDING-REWORK.md`.

Launch-critical finding on 2026-08-29:
- the previous live bootstrap aliased `client_login_ref` to `reklamadymova`;
- that could certify the technical operator's own Direct client instead of the distinct managed owner advertiser;
- `Clients.get` advertiser `Grants` / `Representatives` are not documented as the access-level source for a separate Managing Account relationship;
- therefore the previous claim that Managing Account Editing could be provider-derived from those fields is REWORKED and superseded.

Rework chain:
- `9153f0ee8d9bc5977d52c6459383deef9411d098` — private config separates Direct operator and managed target and rejects aliasing;
- `85a75da129e05e8e171384b39b46c6944d6e8ab0` — live bootstrap requires an explicit managed owner advertiser login and refuses the technical operator as target;
- `d425a72939f2ab5b0fcd79d9800d215308bac0c9` — Direct doctor proves operator and target separately; manager path never infers Editing from managed advertiser grants/representatives;
- `538fe0172f13472735b9a69031f6d209df2d1c4e` — Owner readiness script requires `PROFIT_ENGINE_DIRECT_TARGET_LOGIN` and cannot silently certify the operator as target;
- `a7bc3ae3f70f3c4196d97dc2863e68b9ab3c602f` + `bb858c075a04ad6e4970483bf39680ac786dab00` — regression tests for target separation and manager-permission fail-closed behavior;
- `78430f1b85a726179d14661867b269475202a8cb` — canonical provider certification corrected for the Managing Account boundary;
- `9841c27eff7ce64250d163c78e27b8a2f5dadb13` — rework evidence.

CI `33221266711` on `9841c27eff7ce64250d163c78e27b8a2f5dadb13`: SUCCESS.

Safety interpretation:
- operator identity PASS != managed owner advertiser identity PASS;
- managed owner advertiser read PASS != Managing Account Editing authority;
- Managing Account permission remains an explicit Owner-controlled Direct UI gate;
- runtime remains fail-closed at `UNKNOWN` for manager permission;
- no provider/site mutation, Yandex permission change, real Direct dispatch, budget action or secret disclosure occurred in this rework.

## Current first incomplete canonical gate

The Managing Account relationship is still canonically recorded as `Reading` and no later accepted evidence shows it was changed.

Single next Owner-only action:

`Yandex Direct: for the owner advertiser account managed by reklamadymova, change Managing Account access from Reading to Editing.`

Do not perform any other Direct mutation.

After the Owner confirms that change, Central Brain will continue with private exact managed-target binding, read-only operator/target certification, Metrica/YAN certification, and only then exact live candidate selection. The readiness script must never use `reklamadymova` as `PROFIT_ENGINE_DIRECT_TARGET_LOGIN`.

## First real mutation boundary

Only after accepted Owner Editing evidence, exact managed target binding, all live doctors PASS, exact Central Brain live candidate acceptance and all accepted controller gates:

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
8. `profit-engine/evidence/TASK-012-DIRECT-MANAGER-TARGET-MISBINDING-REWORK.md`;
9. `profit-engine/DAY12_LIVE_PRODUCTION_LAUNCH_DESIGN.md`;
10. `profit-engine/DAY12_PROVIDER_LIVE_CERTIFICATION.md`;
11. `profit-engine/DAY12_FIRST_WRITE_ACCEPTANCE_MATRIX.md`;
12. `profit-engine/tasks/TASK-012-LIVE-GUARDED-PRODUCTION-LAUNCH.md`;
13. issue #19.
