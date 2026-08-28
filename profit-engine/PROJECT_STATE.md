# PROFIT ENGINE — PROJECT STATE

Status: IMPLEMENTATION ACTIVE / DAY 10 REWORK — COHORT MATERIALIZATION TRUTH GATE
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

Key accepted milestones:
- raw-first provider ingestion and data-quality holds;
- stable Dilivox content/placement identity and privacy-minimal attribution;
- first-party event layer;
- reconciled money/K5 contracts with Central Brain reconciliation hotfix;
- Campaign + Creative Factory dry-run;
- Acquisition Strategy Lab public-safe contracts;
- permanent Profit Engine CI.

Task 009 accepted HEAD:

`668680fdbd214854b16307e68f1ad8c7207f645c`

Final Task-009 CI `33155891533`: GREEN.

## Private core — GATE COMPLETE

Private repository:

`niknikdym-hue/profit-engine-core`

Visibility: PRIVATE.
Connected GitHub integration: read/write available.
Owner Gate #11: COMPLETED.

Hard split:
- public repo owns measurement, provider/site adapters, public safety contracts, Budget Governor and guarded execution boundary;
- private core owns proprietary ranking, private thresholds, expected-value/confidence and owner-specific allocation heuristics;
- private core emits proposals only and never writes to providers.

## Task 010 — IMPLEMENTED BUT REWORK REQUIRED BEFORE ACCEPTANCE

Codex reported:

Public implementation:
`739da5d6e4d57b56678cebca2f11502f9dcfe5d2`

Public CI `33166448432`: GREEN.

Private implementation:
`92b58d54793835799dbd1c63f19fccedafbf8a66`

Private CI `33166774369`: GREEN.

Accepted-in-principle Task-010 components that are NOT being redesigned:
- named Metrica campaign/day attribution fact;
- period K5 path;
- ActionProposal v1;
- Budget Governor v1 including exact +20.00% / +20.01% Owner boundary;
- public data-quality / stop-loss / kill-switch structural guards;
- inert site experiment intent;
- private ProfitAllocator/ranking/selection/allocation policy;
- public/private repository split and no provider write authority.

### Launch-critical defect found by Central Brain

Current public `LedgerMaterializer` passes one daily campaign-level `MetricaAttributionFact.attributed_yan_revenue` into all cohort windows `K5_1D`, `K5_7D`, and `K5_30D`.

This violates the canonical Day-7 invariant:

`campaign/day period attribution != proof that later revenue belongs to the original D0 acquisition cohort`.

If later revenue cannot be proven as belonging to the original cohort, cohort K5 MUST be:

`NOT_COMPUTABLE_ATTRIBUTION_HOLD`.

It must never reuse/replicate a daily period numerator as a cohort numerator.

Canonical bounded rework contract:

`profit-engine/tasks/TASK-010-REWORK-COHORT-MATERIALIZATION.md`

Required correction:
- campaign/day Metrica facts feed period K5 only;
- cohort K5 requires explicit immutable cohort-revenue evidence for each 1D/7D/30D window;
- missing/unproven cohort evidence -> value `None`, `NOT_COMPUTABLE`, `NOT_COMPUTABLE_ATTRIBUTION_HOLD`, `optimizer_consumable=false`;
- explicit valid cohort evidence must preserve cohort ref, window, timezone, currency/basis, source/reconciliation/maturity provenance;
- late cohort evidence creates a new derived version without rewriting history;
- after public fix + GREEN CI, private core must pin the new exact public SHA and run GREEN private CI.

Task 010 remains OPEN until Central Brain verifies this correction in both repositories.

## External provider credentials — launch-critical parallel blocker

Live certification remains:
- Direct: `BLOCKED_MISSING_CREDENTIAL`;
- Metrica: `BLOCKED_MISSING_CREDENTIAL`;
- YAN Statistics: `BLOCKED_MISSING_CREDENTIAL`.

Classification: `BLOCKED_EXTERNAL_PROVIDER_CREDENTIAL`.

This does not block the bounded Task-010 rework or Day-11 design prework, but it must be resolved before Day-12 real closed-loop production launch.

## Expected Task 011 boundary

After Task-010 rework acceptance:
- guarded Direct Controller;
- immutable execution intent/audit/rollback;
- kill-switch enforcement;
- exact Owner-approval evidence validation for >20% weekly increase;
- no write can originate from private core;
- Direct Editing remains disabled until the Day-11 controller is accepted.

## Launch definition

Target engineering launch = Day 12 `GUARDED_PRODUCTION_LAUNCHED`.

Launch still requires provider read certification, Dilivox production instrumentation, reconciled live money, accepted Task-010 proposal chain, accepted Day-11 guarded controller, and one bounded auditable real closed-loop action.

Stable proof of `K5 >= 5.0` requires reconciled live money after launch; fixtures never prove the target.

## Resume protocol

Read `PROJECT_HANDOFF.md`, verify actual public/private HEADs, inspect open Task-010 issues and the rework contract, preserve the repository split, and continue the first incomplete gate. Never substitute campaign/day revenue for cohort evidence.
