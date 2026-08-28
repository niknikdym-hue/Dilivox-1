# PROFIT ENGINE — PROJECT STATE

Status: IMPLEMENTATION ACTIVE / DAY 11 REWORK — GUARDED DIRECT CONTROLLER EXECUTION BINDINGS
Updated: 2026-08-28
Canonical public branch: `profit-engine`
Private core branch: `main`

## Current objective

Launch a guarded-production, machine-operated, multi-site Profit Engine whose first closed loop is:

`Yandex Direct -> Dilivox -> behavior -> YAN revenue -> attribution/reconciliation -> private decision core -> public ActionProposal -> Budget Governor -> guarded Direct/Site controller -> measured outcome`.

First production site: `site_id=dilivox` / `dilivox.ru`.

Primary target:

`1 RUB Yandex Direct spend -> 5 RUB YAN advertising revenue attributable to the acquired Dilivox audience`.

This remains a target, not a claimed result.

## Locked governance

- `PROTECT CAPITAL -> MEASURE MONEY -> STOP LOSSES -> FIND PROFIT -> SCALE PROFIT -> REPEAT`.
- automatic weekly budget increase above +20% requires explicit Owner approval bound to the exact proposal;
- private core emits proposals only and never writes to providers;
- Direct Editing remains disabled until Central Brain accepts Task 011/011R;
- no real provider/site write is authorized during Day 11;
- chat is not source of truth.

## Tasks 001–010R — ACCEPTED

Day-10 final public contract:

`98c6d3f0c0105c30cfc90a6d5fdf653c2aceb8d6`

Public CI `33180647500`: GREEN.

Private core accepted contract:

`1709925f5b2d29f9c038dde7caca8054b51eea6f`

Private CI `33180767637`: GREEN.

Accepted Day-10 chain includes:
- campaign/day Metrica attribution for `period_K5` only;
- explicit `CohortRevenueEvidence v1` for 1D/7D/30D cohort K5;
- missing/unproven cohort revenue -> `NOT_COMPUTABLE_ATTRIBUTION_HOLD`;
- public `ActionProposal v1`;
- Budget Governor with exact +20.00% / +20.01% Owner boundary;
- private ProfitAllocator exclusively in private `profit-engine-core`;
- no provider write authority in private core.

## Task 011 initial implementation — REWORK REQUIRED

Codex implementation reviewed:

`d8d3a9887d4a3e38d90ac0cfb7567092aaf3997a`

Reported CI `33183653872`: GREEN.

The implementation correctly introduced the Day-11 controller state model, governor/proposal binding, preflight contract, allowlist, budget mapping, kill switches, one-object rule, retry/read-back model, rollback plan, hash-linked audit, secret redaction and a default-disabled production writer.

Central Brain did NOT accept Task 011 because launch-critical execution-binding bypasses remain.

Central Brain review:

`profit-engine/evidence/TASK-011-CENTRAL-BRAIN-REVIEW.md`

Canonical bounded rework:

`profit-engine/tasks/TASK-011-REWORK-EXECUTION-BINDINGS.md`

Tracking issue:

`#18 — Profit Engine Task 011R — execution-binding safety rework`.

Task #17 remains unaccepted until #18 is accepted.

## Task 011R required fixes

1. actual exact-target lock acquisition must be on the dispatch path; `locks=None` cannot bypass it;
2. fresh pre-dispatch snapshot/TOCTOU comparison must be on the actual dispatch path;
3. applicable kill switches must be rechecked immediately before dispatch;
4. mutation-cadence evidence must be immutable/integrity-bound and valid for the current campaign/day;
5. the one normalized mutation object must be bound to the exact provider entity and exact ProviderBudgetPlan amount/micros;
6. >20% Owner approval must resolve through a trusted exact Owner-authority boundary, not an arbitrary self-declared authority string;
7. successful read-back expectation must be derived from the immutable plan/method/request, not arbitrary caller input.

All accepted Task-011 components not required for these fixes should be preserved.

## External provider blockers

Live certification remains:
- Direct: `BLOCKED_MISSING_CREDENTIAL`;
- Metrica: `BLOCKED_MISSING_CREDENTIAL`;
- YAN Statistics: `BLOCKED_MISSING_CREDENTIAL`.

Classification: `BLOCKED_EXTERNAL_PROVIDER_CREDENTIAL`.

These blockers do not stop Task 011R dry-run engineering but must be resolved before any Day-12 real mutation.

## Editing-access gate

Do NOT change Direct access from Reading to Editing yet.

Only after Central Brain accepts Task 011R may the next Owner action become:

`Direct access: Reading -> Editing`.

## Day 12 boundary

After Task 011R acceptance, Editing enablement and live credential/read certification:
- one bounded real mutation only;
- exactly one provider object;
- all Governor/Owner/kill/preflight/lock/cadence gates revalidated immediately before dispatch;
- write -> read-back -> immutable audit;
- rollback only when exact prior state and current guards prove it safe.

## Launch definition

Engineering launch target remains Day 12 `GUARDED_PRODUCTION_LAUNCHED`.

Stable proof of `K5 >= 5.0` requires reconciled live money after launch; fixtures never prove the target.

## Resume protocol

Read `PROJECT_HANDOFF.md`, verify actual `origin/profit-engine` HEAD, then read:
1. `profit-engine/PROJECT_STATE.md`;
2. `profit-engine/evidence/TASK-011-CENTRAL-BRAIN-REVIEW.md`;
3. `profit-engine/tasks/TASK-011-REWORK-EXECUTION-BINDINGS.md`;
4. GitHub issue #18.

Continue Task 011R. Never enable Direct Editing before Central Brain acceptance.
