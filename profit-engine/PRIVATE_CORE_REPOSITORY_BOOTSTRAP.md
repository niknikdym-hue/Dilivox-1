# PROFIT ENGINE — PRIVATE CORE REPOSITORY BOOTSTRAP

Status: CANONICAL PRE-DAY-9 GATE
Updated: 2026-08-27

## Required private repository

Canonical private-core repository name:

`niknikdym-hue/profit-engine-core`

Visibility:

`PRIVATE`

Recommended local clone path:

`~/Documents/New project/Profit Engine/profit-engine-core`

## Why it exists

The public repository `niknikdym-hue/Dilivox-1` remains the public-safe site/provider adapter, schema, safety, measurement and dry-run contract repository.

The private repository is required before commercially sensitive optimizer implementation begins.

Mandatory gate:

`PRIVATE_CORE_REPOSITORY_REQUIRED_BEFORE_SENSITIVE_OPTIMIZER_IMPLEMENTATION`

## Public repo keeps

- provider-neutral/public-safe contracts;
- Direct/Metrica/YAN read adapters;
- schemas and generic storage interfaces;
- Dilivox SiteAgent/event contracts;
- content/placement registries that are safe to disclose;
- attribution/reconciliation/K5 measurement primitives;
- generic data-quality/safety invariants;
- Campaign/Creative Factory public-safe specs and deterministic dry-run validation;
- Budget Governor public safety invariants may be mirrored publicly later when they reveal no private strategy.

## Private core owns

- proprietary profit scoring formulas and weights;
- learned thresholds;
- owner-specific capital allocation heuristics;
- strategy-cell ranking/winner selection;
- proprietary expected-value/LTV calibration;
- commercially sensitive creative ranking/generation policy;
- private multi-site operating configuration/mappings;
- production model artifacts/features where not appropriate for the public repo;
- sensitive experiment/allocation policy;
- private action-proposal logic that feeds the guarded public/provider execution boundary.

Secrets themselves still belong in Keychain/Lockbox or a secret manager, not Git, even in the private repository.

## Interface boundary

The private core must depend on versioned public-safe input/output contracts rather than importing Dilivox-specific page code.

Canonical direction:

`public normalized facts + accepted measurement contracts -> private decision engine -> public-safe action proposal/intent contract -> Budget Governor -> guarded provider/site controller`.

The private core must not bypass Budget Governor or write directly to providers.

## Initial repository skeleton after Owner creates it

Central Brain/Codex should create:

- `README.md`;
- `PROJECT_AUTHORITY.md`;
- `PROJECT_STATE.md`;
- `PUBLIC_CONTRACT_VERSION.md`;
- `src/profit_engine_core/`;
- `tests/`;
- `.gitignore`;
- CI;
- no production secrets;
- no provider credentials.

## Owner action

The current GitHub connector cannot create a new repository. Before sensitive Day-9 implementation, Owner must create the private repository in GitHub with the exact name:

`profit-engine-core`

and keep it Private.

Then grant the existing ChatGPT/Codex GitHub integration access to that repository.

No other architectural decision is required from Owner for this bootstrap.

## Acceptance

This gate is complete only when:

1. `niknikdym-hue/profit-engine-core` exists and is private;
2. Central Brain can read/write it through the connected GitHub integration;
3. Codex can work with it;
4. public/private contract versioning is established;
5. no sensitive optimizer implementation is committed to the public `Dilivox-1` repository.
