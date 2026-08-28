# PROFIT ENGINE — PROJECT STATE

Status: IMPLEMENTATION ACTIVE / DAY 11 — GUARDED DIRECT CONTROLLER WRITE-SAFETY GATE
Updated: 2026-08-28
Canonical public branch: `profit-engine`
Private core branch: `main`

## Current objective

Launch a guarded-production, machine-operated, multi-site Profit Engine whose first closed loop is:

`Yandex Direct -> Dilivox -> user behavior -> YAN revenue -> attribution/reconciliation -> private decision core -> public ActionProposal -> Budget Governor -> guarded Direct/Site controller -> measured outcome`.

First production site: `site_id=dilivox` / `dilivox.ru`.

Primary optimization target:

`1 RUB Yandex Direct spend -> 5 RUB YAN advertising revenue attributable to the acquired Dilivox audience`.

This remains a target, not a claimed current result.

## Locked governance

- `PROTECT CAPITAL -> MEASURE MONEY -> STOP LOSSES -> FIND PROFIT -> SCALE PROFIT -> REPEAT`.
- automatic weekly budget increase above +20% requires explicit Owner approval bound to the exact proposal;
- Dilivox is site #1; architecture remains multi-site/provider-neutral;
- private core can only emit proposals and never writes to providers;
- Chat is not source of truth;
- Direct Editing remains disabled until Central Brain accepts Task 011.

## Tasks 001–009 — ACCEPTED

Accepted foundations include raw-first provider ingestion, first-party Dilivox instrumentation contracts, privacy-minimal attribution, immutable money/K5 rules, Campaign/Creative Factory dry-run, Acquisition Strategy Lab and permanent CI.

## Task 010 + Task 010R — ACCEPTED / DAY 10 COMPLETE

Canonical acceptance evidence:

`profit-engine/evidence/TASK-010-CENTRAL-BRAIN-ACCEPTANCE.md`

Accepted public Task-010R contract SHA:

`98c6d3f0c0105c30cfc90a6d5fdf653c2aceb8d6`

Public CI run `33180647500`: GREEN.

Accepted private core SHA:

`1709925f5b2d29f9c038dde7caca8054b51eea6f`

Private CI run `33180767637`: GREEN.

Accepted Day-10 chain now includes:
- named Metrica campaign/day attribution fact;
- campaign/day revenue feeds `period_K5` only;
- explicit immutable `CohortRevenueEvidence v1` for 1D/7D/30D cohort K5;
- missing/unproven cohort evidence -> `NOT_COMPUTABLE_ATTRIBUTION_HOLD`;
- per-window numerator truth and original acquisition-spend denominator;
- append-versioned late cohort evidence;
- public-safe `ActionProposal v1`;
- `Budget Governor v1`;
- exact +20.00% vs +20.01% Owner approval boundary;
- public data-quality / stop-loss / kill-switch guards;
- private ProfitAllocator ranking/selection/allocation exclusively in private core;
- no provider write authority in private core.

Issues #12 and #13 are completed. Private issue #1 is completed.

## External provider credentials — launch-critical parallel blocker

Live provider certification remains:
- Direct: `BLOCKED_MISSING_CREDENTIAL`;
- Metrica: `BLOCKED_MISSING_CREDENTIAL`;
- YAN Statistics: `BLOCKED_MISSING_CREDENTIAL`.

Classification: `BLOCKED_EXTERNAL_PROVIDER_CREDENTIAL`.

This does not block Day-11 dry-run controller engineering, but must be resolved before Day-12 real closed-loop execution.

## Immediate active task — Task 011 / Day 11

Canonical design:

`profit-engine/DAY11_GUARDED_DIRECT_CONTROLLER_DESIGN.md`

Canonical acceptance matrix:

`profit-engine/DAY11_CONTROLLER_ACCEPTANCE_MATRIX.md`

Canonical task:

`profit-engine/tasks/TASK-011-GUARDED-DIRECT-CONTROLLER-DRY-RUN.md`

Executor: Codex.
Acceptance authority: Central Brain.

Task 011 objective:

`Governor-ready ActionProposal -> exact provider target -> fresh preflight snapshot -> approvals/kill-switch/cadence/lock gates -> ControllerPlan -> READY_FOR_DAY12_EXECUTION`.

Task 011 itself performs ZERO real Direct mutations and ZERO advertising spend.

Hard Day-11 gates:
- Governor cannot be bypassed;
- >20% Owner approval bound to exact proposal/target/amount;
- fresh provider snapshot + stale-state protection;
- exact provider entity identity only;
- initial method allowlist limited to suspend/resume and one bounded campaign budget update;
- explicit weekly-to-provider-budget mapping, no implicit weekly/7;
- max one autonomous campaign budget mutation/day;
- all kill switches override everything;
- per-target execution lock;
- one provider object per request at launch;
- no blind retry after uncertain response;
- read-back required before completion;
- rollback derived only from immutable preflight;
- append-only hash-linked audit;
- secret-safe logging;
- production writer hard-disabled by default;
- no `EXECUTED` state on Day 11.

## Editing-access gate

Only if Central Brain accepts Task 011 with all tests/CI green does the next Owner action become:

`Direct access: Reading -> Editing`.

Until then do not change Direct access.

## Day 12 boundary

After Editing access is explicitly enabled and live credential/read-certification gates pass:
- one bounded real mutation only;
- one provider object;
- all Governor/Owner/kill/preflight/lock/cadence gates revalidated;
- write -> read-back -> immutable audit;
- rollback only if exact prior state and current guards make it safe.

## Launch definition

Target engineering launch = Day 12 `GUARDED_PRODUCTION_LAUNCHED`.

Stable proof of `K5 >= 5.0` requires reconciled live money after launch. Fixtures never prove the target.

## Resume protocol

Read `PROJECT_HANDOFF.md`, verify actual `origin/profit-engine` HEAD, read the Day-11 design/matrix/task and continue the first incomplete gate. Never enable Direct Editing before Central Brain Task-011 acceptance.
