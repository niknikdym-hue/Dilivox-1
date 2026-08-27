# PROFIT ENGINE — PRIVATE CORE REPOSITORY PREWORK

Status: CENTRAL BRAIN PREWORK / NOT YET CANONICAL
Prepared: 2026-08-27

## Why this exists

The public `niknikdym-hue/Dilivox-1` repository is acceptable for generic provider adapters, schemas, SiteAgent contracts, safety invariants, event contracts, redaction, generic storage and public examples.

It must not become the home of proprietary profit scoring, owner-specific allocation, learned thresholds, sensitive creative ranking, confidential mappings or production datasets.

Mandatory gate already accepted in public repo:

`PRIVATE_CORE_REPOSITORY_REQUIRED_BEFORE_SENSITIVE_OPTIMIZER_IMPLEMENTATION`.

This prework prepares the move before Day 9/10 so it does not become a launch blocker.

## Recommended repository shape

Recommended private repository name:

`niknikdym-hue/profit-engine-core`

Visibility: PRIVATE.

Recommended local path:

`~/Documents/New project/Profit Engine/profit-engine-core`

This is a proposal until the repository is actually created and recorded by Central Brain.

## Public repo responsibilities

`Dilivox-1` / `profit-engine/` keeps:

- provider read/write adapter contracts;
- generic Yandex Direct/Metrica/YAN protocol implementations that reveal no owner strategy;
- provider-neutral data schemas;
- immutable raw/data-quality contracts;
- SiteAgent and event schema contracts;
- public-safe campaign specification interfaces;
- Budget Governor hard safety invariant definitions, including owner approval requirement >20%;
- generic audit/action/approval message schemas;
- Dilivox public/reference adapter and Tilda integration artifacts;
- fixtures containing synthetic data only.

## Private core responsibilities

Future private core owns:

- K5/profit opportunity scoring implementation;
- owner-specific segment weights and thresholds;
- ProfitAllocator implementation;
- learned stop-loss/scale thresholds;
- confidence/sample-size policies when commercially tuned;
- proxy-goal monetary valuation models;
- audience/cohort value models;
- landing/recommendation ranking implementation;
- creative generation/ranking policy where commercially sensitive;
- portfolio capital-allocation heuristics;
- experiment winner-selection implementation beyond generic statistics contracts;
- confidential multi-site/provider mappings;
- production model artifacts/features;
- private deployment configuration.

Secrets still belong in Keychain/Lockbox, not in the private Git repository.

## Interface between public and private components

Use explicit versioned contracts rather than importing internal source across repositories.

Minimum contract groups:

1. `ObservedFactsEnvelope`
   - site ID;
   - cohort/segment references;
   - spend/revenue facts;
   - quality/provenance state;
   - experiment/site context;
   - no raw secret values.

2. `OptimizationRequest`
   - observation window;
   - eligible action/cell refs;
   - budget/safety constraints;
   - allowed strategies;
   - quality status.

3. `OptimizationDecision`
   - opaque decision ID;
   - generic action type (`SCALE`, `HOLD`, `REDUCE`, `STOP`, etc.);
   - target reference;
   - requested parameter/budget delta;
   - confidence/evidence references safe for audit;
   - owner-approval-required flag;
   - expiration/idempotency metadata.

4. `ActionExecutionResult`
   - decision/action IDs;
   - provider result;
   - before/after redacted state;
   - rollback token/reference;
   - realized effect later joined by public data layer.

Public provider controller executes only generic approved decision objects after Budget Governor validation. It never receives private model weights or formulas.

## Contract versioning

Add a shared contract version, e.g. `profit_engine_contract_version`.

Rules:

- public and private services refuse incompatible major versions;
- additive fields only within a minor version;
- unknown optional fields ignored safely;
- every decision records the contract version used;
- rollback always remains possible to the last compatible pair.

## Deployment separation

Preferred first-launch layout:

PUBLIC/GENERIC services:
- collectors;
- event API;
- reconciliation worker;
- generic Direct controller;
- SiteAgent/static integration artifacts.

PRIVATE services:
- audience value worker;
- optimization worker;
- ProfitAllocator;
- private experiment evaluator/ranking;
- private creative/value policy.

Communication should use an authenticated internal API/queue or versioned files/messages in local development; no private-core formulas are shipped to browser/Tilda.

## Data boundary

Public repo contains schemas, never production datasets.

Runtime production data can flow from shared storage into the private service under least privilege, but raw exports/model features must remain outside Git.

Private core should receive only the minimum facts required for a decision; it should not become a new uncontrolled copy of every provider raw payload.

## Day 8 gate

Before Campaign Factory/Creative Factory implementation contains sensitive ranking or owner-specific generation logic:

- private repo exists;
- local clone exists;
- README/authority declares scope;
- contract package/interface is versioned;
- secret policy inherited;
- no optimizer formulas remain in public repo;
- Codex knows which workspace receives which task.

## Day 9/10 hard gate

No proprietary `AcquisitionStrategyLab`, value model or `ProfitAllocator` implementation may be accepted until the private repo is operational.

If private repo is not ready by then, generic interfaces/tests may proceed but sensitive implementation remains blocked as:

`BLOCKED_PRIVATE_CORE_REPOSITORY`.

## Central Brain next action

After Task 005/006 stabilizes public SiteAgent/event contracts, Central Brain should create or direct creation of the private repository before Day 8, then record the exact repo/local path in both project authority states.
