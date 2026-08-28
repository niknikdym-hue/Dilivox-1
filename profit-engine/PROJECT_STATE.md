# PROFIT ENGINE — PROJECT STATE

Status: IMPLEMENTATION ACTIVE / DAY 10 — TWO-REPO PROFIT ALLOCATOR + GUARDRAILS
Updated: 2026-08-28
Canonical public branch: `profit-engine`
Private core branch: `main`

## Current objective

Launch a guarded-production, machine-operated, multi-site Profit Engine whose first closed loop is:

`Yandex Direct -> Dilivox -> user behavior -> YAN revenue -> attribution/reconciliation -> Profit Engine -> guarded Direct + Dilivox actions -> measured outcome`.

First production site: `site_id=dilivox` / `dilivox.ru`.

Primary optimization target:

`1 RUB Yandex Direct spend -> 5 RUB YAN advertising revenue attributable to the acquired Dilivox audience`.

This is a target, not a claimed current result.

## Locked governance

- PROFIT-FIRST: `PROTECT CAPITAL -> MEASURE MONEY -> STOP LOSSES -> FIND PROFIT -> SCALE PROFIT -> REPEAT`.
- Weekly automatic budget increase above +20% requires explicit Owner approval.
- Routine advertising operation is intended to be machine-operated.
- Dilivox is site #1; architecture remains multi-site/provider-neutral.
- Chat is not source of truth.
- No provider/site write is authorized before the Day-11 guarded controller gate.

## Tasks 001–009 — ACCEPTED

Canonical evidence exists under `profit-engine/evidence/`.

Task 007 was accepted after a Central Brain reconciliation/K5 hotfix.
Task 008 Campaign/Creative Factory dry-run is accepted.
Task 009 Acquisition Strategy Lab public contracts is accepted at:

`668680fdbd214854b16307e68f1ad8c7207f645c`

Final Task-009 Profit Engine CI run `33155891533`: GREEN.

Accepted Task-009 invariants:
- only reconciled/mature/consumable evidence can become experiment-eligible;
- C/E/UNJOINABLE or otherwise weak attribution cannot masquerade as proven cohort linkage;
- public Strategy Lab validates cells/experiments but does not rank/select/allocate;
- provider requests/spend/write authority remain zero/false.

## Private core — GATE COMPLETE

Private repository:

`niknikdym-hue/profit-engine-core`

Visibility: PRIVATE.
Connected GitHub integration: read/write available.
Owner Gate #11: COMPLETED.

Private core now contains:
- `PROJECT_AUTHORITY.md`;
- `PROJECT_STATE.md`;
- `PUBLIC_CONTRACT_VERSION.md`;
- secret-safe `.gitignore`;
- Python package skeleton/tests;
- private CI.

Private Core CI run `33157344499`: GREEN.

Hard split:
- public repo owns measurement, provider/site adapters, public safety contracts, Budget Governor and guarded execution boundary;
- private core owns proprietary ranking, learned/private thresholds, expected-value/LTV calibration and owner-specific allocation heuristics;
- private core outputs proposals only and never writes to providers.

## External provider credentials — parallel blocker

Live certification remains:
- Direct: `BLOCKED_MISSING_CREDENTIAL`;
- Metrica: `BLOCKED_MISSING_CREDENTIAL`;
- YAN Statistics: `BLOCKED_MISSING_CREDENTIAL`.

Classification: `BLOCKED_EXTERNAL_PROVIDER_CREDENTIAL`.

This does not block Day-10 fixture/contracts work, but must be resolved before real closed-loop production launch.

## Immediate active task — Task 010 / Day 10

Canonical design:

`profit-engine/DAY10_PROFIT_ALLOCATOR_AND_GUARDRAILS_DESIGN.md`

Canonical coordinated task:

`profit-engine/tasks/TASK-010-TWO-REPO-PROFIT-ALLOCATOR.md`

Private mirror:

`profit-engine-core/tasks/TASK-010-PRIVATE-PROFIT-ALLOCATOR.md`

Mandatory phase order:

1. PUBLIC Phase A:
   - attribution-aware Metrica materialization;
   - deterministic ledger materializer;
   - ActionProposal v1;
   - Budget Governor v1;
   - public data-quality/kill-switch/stop-loss structural guards;
   - site experiment action-intent contract;
   - GREEN public CI.
2. Pin exact public Phase-A SHA in private `PUBLIC_CONTRACT_VERSION.md`.
3. PRIVATE Phase B:
   - sensitive strategy ranking/winner selection;
   - private expected-value/confidence model;
   - private scale/reduce/stop/test thresholds;
   - allocation proposal logic;
   - public-safe ActionProposal adapter;
   - GREEN private CI.

Hard budget boundary:
- `<= +20%` weekly increase can only become ready for Day-11 controller when all public evidence/safety guards pass;
- `> +20%` is always `PENDING_OWNER_APPROVAL` until explicit Owner approval exists.

Day 10 never performs provider writes or spend.

## Public materialization gap — included in Task 010

Task 007 defined Metrica attribution semantics, but the accepted earlier Metrica collector still materializes generic dimensions rather than a dedicated named campaign-attribution fact.

Task 010 Phase A must close this gap before real production money can feed private decisions. No date-only or campaign-name inference is allowed.

## Expected Task 011 boundary

Day 11:
- guarded Direct Controller;
- Budget Governor integration with real controller intents;
- kill switches / audit / rollback;
- Owner may upgrade Direct access from Reading to Editing only after the write gate is ready;
- no action >20% weekly increase without explicit Owner approval.

## Launch definition

Target engineering launch = Day 12 `GUARDED_PRODUCTION_LAUNCHED`.

Launch still requires provider read certification, Dilivox production instrumentation, reconciled live money, accepted Day-10 decision/proposal chain, Day-11 guarded write controller and one bounded auditable real closed-loop action.

Stable proof of `K5 >= 5.0` requires reconciled live money after launch; fixtures never prove the target.

## Resume protocol

Read `PROJECT_HANDOFF.md`, verify actual public/private HEADs, inspect active Task 010 contracts, preserve the repository split, and continue the first incomplete gate.
