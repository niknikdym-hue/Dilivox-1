# PROFIT ENGINE — DAY 10 PROFIT ALLOCATOR + GUARDRAILS DESIGN

Status: CANONICAL EXECUTION DESIGN
Updated: 2026-08-28

## Purpose

Day 10 converts accepted measurement/Strategy Lab evidence into auditable action proposals while preserving the split between public safety/execution contracts and private commercial decision logic.

Canonical chain:

`immutable provider/event facts -> money ledger -> public Strategy Lab evidence -> PRIVATE decision core -> public ActionProposal -> Budget Governor / stop-loss guards -> Day-11 guarded controller`.

Day 10 does NOT execute provider writes.

## Repository split

### Public `niknikdym-hue/Dilivox-1` / `profit-engine`

Owns:
- attribution-aware READ_ONLY Metrica materialization;
- ledger materializer and maturity/reconciliation scheduler contracts;
- generic `ActionProposal v1` contract;
- generic Budget Governor enforcement;
- data-quality / kill-switch / stop-loss safety gates;
- site-experiment action-intent contract;
- audit/evidence contracts;
- no proprietary ranking/weights.

### Private `niknikdym-hue/profit-engine-core`

Owns:
- strategy-cell ranking and winner selection;
- proprietary scoring/weights;
- expected-value/LTV calibration;
- owner-specific allocation heuristics;
- private stop-loss/scaling thresholds;
- proposal generation from accepted evidence.

Private core outputs proposals only and has `provider_write_allowed=false`.

## Public materialization bridge

Before private decisions can consume real money, public ingestion must expose a dedicated attribution fact rather than infer campaign identity from generic dimensions.

Required Metrica attribution fact fields:
- `site_id`;
- date/window;
- explicit attribution model;
- Direct campaign/group refs when returned;
- bounded UTM fields when returned;
- attributed YAN revenue Decimal;
- delivery metrics;
- currency/sampling/accuracy/lag/disclosure provenance;
- raw/source ref and source state;
- data-quality holds.

Missing/incompatible attribution dimensions -> hold, never date/name inference.

A generic ledger materializer must consume immutable normalized facts and produce deterministic/versioned acquisitions, reconciliation outputs and K5 measurements without rewriting raw history.

## ActionProposal v1

Minimum public-safe fields:
- proposal version/id/digest;
- `site_id`;
- proposal kind: `LEARN`, `TEST`, `SCALE`, `HOLD`, `REDUCE`, `STOP`, `QUARANTINE`;
- target campaign/spec/experiment references;
- source Strategy Lab evidence package digest;
- measurement/provenance refs;
- requested weekly budget amount/delta when applicable, Decimal string;
- current weekly budget reference when known;
- risk/guard requirements;
- owner-approval requirement;
- private decision digest/reference, never private weights;
- created-at/version/audit metadata;
- `requires_budget_governor=true`;
- `provider_write_allowed=false`.

No secret/private ranking details are serialized into the public proposal.

## Budget Governor v1

Hard owner rule:

- automatic weekly budget increase `<= +20%` may be authorized only when every data/safety guard passes;
- weekly increase `> +20%` is ALWAYS `PENDING_OWNER_APPROVAL` until explicit Owner approval exists;
- missing current budget / malformed Decimal / stale or held evidence -> no scale authorization;
- global kill switch -> no execution authorization;
- `DATA_QUALITY_HOLD`, non-MATCHED reconciliation, immature cohort or non-consumable measurement -> `SCALE/TEST` cannot be authorized;
- `STOP/HOLD/QUARANTINE` safety proposals may remain eligible for the later guarded controller if their own safety/audit contract is valid.

Day 10 governor returns authorization state only. It never calls Direct.

Suggested states:
- `GOVERNOR_READY_FOR_DAY11_CONTROLLER`;
- `PENDING_OWNER_APPROVAL`;
- `BLOCKED_DATA_QUALITY`;
- `BLOCKED_BUDGET_BASELINE`;
- `BLOCKED_KILL_SWITCH`;
- `BLOCKED_PROPOSAL_CONTRACT`.

## Private ProfitAllocator

Private core may rank only evidence that public Strategy Lab marked eligible and whose referenced measurement remains consumable/reconciled/mature.

It may generate private decision outcomes such as:
- preferred strategy cell;
- expected contribution / confidence state;
- scale/reduce/stop/test recommendation;
- proposed budget delta;
- private decision digest;
- public-safe rationale codes.

All formulas/weights/thresholds are private.

No private function may invoke provider/site APIs or carry OAuth credentials.

## Stop-loss and safety

Private thresholds decide commercial stop/reduce conditions; public guards enforce structural safety.

A proposal derived from stale/held/contradictory data cannot scale. Data-quality deterioration after a private decision invalidates the public authorization and requires re-evaluation.

## Site experiment action intent

Public contract may represent a future site experiment activation/deactivation/kill intent referencing existing experiment/variant IDs and kill switches.

No Tilda publication or production mutation occurs on Day 10.

## Required fixture acceptance

1. named Metrica Direct dimensions materialize to attribution fact;
2. missing dimension -> hold, no campaign inference;
3. deterministic ledger materialization/replay;
4. private core rejects held/non-consumable evidence;
5. private ranking stays only in private repo;
6. private decision creates a public-safe ActionProposal with no private weights;
7. +10% weekly scale with all guards -> ready for Day-11 controller;
8. +20% exactly with all guards -> ready for Day-11 controller;
9. +20.01% -> `PENDING_OWNER_APPROVAL`;
10. >20% with no Owner approval never becomes ready;
11. data-quality hold blocks SCALE/TEST;
12. STOP/HOLD/QUARANTINE can pass structural safety without spend increase;
13. kill switch blocks execution authorization;
14. no provider request/site mutation in either repo;
15. public and private CI green.

## Day 10 success

Day 10 succeeds when a synthetic accepted evidence package can flow through private ranking/allocation into a public-safe proposal and Budget Governor result, while real provider execution remains impossible until Day 11.

Live provider OAuth remains a parallel external blocker; fixtures do not prove production K5 or authorize spend.
