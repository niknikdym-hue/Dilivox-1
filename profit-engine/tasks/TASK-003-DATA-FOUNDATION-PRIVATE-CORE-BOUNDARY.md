# CODEX TASK 003 — PROFIT ENGINE DATA FOUNDATION + PRIVATE-CORE BOUNDARY

Status: READY FOR EXECUTION
Owner: Central Brain
Executor: Codex
Repository: `niknikdym-hue/Dilivox-1`
Canonical branch: `profit-engine`
Launch day: Day 3

## ROLE

You are the engineering executor for DILIVOX PROFIT ENGINE.
Central Brain is project brain and acceptance authority.
Do not change Owner economic/product authority.

## READ FIRST — MANDATORY

Before changing anything, read the current versions on `origin/profit-engine`:

1. `profit-engine/PROJECT_HANDOFF.md`
2. `profit-engine/PROJECT_STATE.md`
3. `profit-engine/OWNER_DECISIONS.md`
4. `profit-engine/HARD_12_DAY_LAUNCH_PLAN.md`
5. `profit-engine/GOVERNANCE_AND_EXECUTION.md`
6. `profit-engine/ARCHITECTURE.md`
7. `profit-engine/YANDEX_CLOUD_ARCHITECTURE.md`
8. `profit-engine/SECURITY_AND_ACCESS.md`
9. `profit-engine/evidence/TASK-002-READ-FOUNDATION.md`
10. this task contract.

## LOCAL WORKSPACE

Canonical Profit Engine workspace:

`~/Documents/New project/Profit Engine/Dilivox-1`

Existing Dilivox site workspace:

`~/Documents/New project/Dilivox`

The existing site workspace remains READ-ONLY in Task 003. Do not publish Tilda or change production Dilivox.

## BASELINE

Expected Task 002 evidence-bearing origin HEAD at task creation:

`a5de1b32a8460fb18428625e01b09509686d158a`

Always `git fetch origin` first and use the actual current `origin/profit-engine` if Central Brain has advanced it. Never overwrite newer Central Brain changes. No force push.

## TASK 002 ACCEPTANCE STATE

Engineering foundation is accepted.
Live provider certification remains `BLOCKED_EXTERNAL_PROVIDER_CREDENTIAL` until secure Direct/Metrica and YAN Statistics OAuth tokens are available.

Do not stop Day 3 engineering because of this external credential blocker.

## OBJECTIVE

Build the minimal provider-neutral data/storage/runtime foundation required for Days 4–7 while keeping all provider actions READ_ONLY and keeping competitive optimizer/scoring implementation out of the public repository.

Task 003 is infrastructure/data foundation, not business optimizer implementation.

## A. PRIVATE-CORE BOUNDARY

Create:

`profit-engine/PRIVATE_CORE_BOUNDARY.md`

It must clearly classify what may remain in the current public repository versus what MUST move to a future private core before sensitive implementation expands.

Public-safe examples:
- provider interfaces;
- generic schemas;
- generic safety invariants;
- redaction/security utilities;
- site adapter contracts;
- non-secret example config;
- generic storage/health abstractions.

Private-required before sensitive implementation:
- proprietary scoring formulas/weights;
- profit-pool ranking logic;
- budget allocation heuristics beyond public invariants;
- optimizer thresholds learned from owner economics;
- creative ranking/generation decision logic that reveals commercial strategy;
- confidential provider/account mappings;
- production datasets/raw exports;
- secrets;
- future multi-site commercially sensitive configuration.

Do NOT invent that a private repository already exists. Record the migration gate as `PRIVATE_CORE_REPOSITORY_REQUIRED_BEFORE_SENSITIVE_OPTIMIZER_IMPLEMENTATION`.

## B. POSTGRESQL SCHEMA FOUNDATION

Create a versioned PostgreSQL migration foundation under a clear path such as:

`profit-engine/data/migrations/`

Minimum schema must support provider-neutral multi-site operation and future reconciliation.

Required entities/tables or equivalent normalized design:
- `sites`;
- `provider_accounts` / provider mapping references;
- `ingestion_runs`;
- `raw_snapshots` metadata;
- `campaign_snapshots`;
- `traffic_facts`;
- `site_events`;
- `monetization_facts`;
- `cohorts`;
- `experiments`;
- `decisions`;
- `approvals`;
- `actions_audit`;
- `data_quality_checks`.

Requirements:
- every relevant fact is scoped by `site_id`;
- provider identity is explicit/provider-neutral;
- timestamps are timezone-safe;
- money fields avoid binary floating point;
- raw snapshot provenance is reproducible;
- uniqueness/idempotency keys are defined where appropriate;
- schema does not contain real provider IDs or secrets;
- no Dilivox-only branching in shared schema.

Do not create a production database in this task unless a safe pre-existing development DB is already available and doing so requires no Owner account action. Schema files and tests are required even without a live DB.

## C. IMMUTABLE RAW SNAPSHOT CONTRACT

Create a raw snapshot envelope/schema and runtime interface suitable for future Object Storage.

Required metadata includes at least:
- schema version;
- `site_id`;
- provider;
- source object/report type;
- capture timestamp;
- source time window where applicable;
- request fingerprint/idempotency key;
- payload SHA-256;
- provider request ID when available;
- estimated/final/reconciled state where applicable;
- ingestion run ID.

Suggested logical storage layout:

`raw/{site_id}/{provider}/{yyyy}/{mm}/{dd}/...`

Implement a LOCAL development raw-store adapter outside the Git-tracked production data tree that demonstrates:
- atomic write;
- immutability;
- idempotent same-content re-write;
- reject/conflict on same identity with different payload;
- payload hash verification.

No real production provider payload may be committed.

## D. STORAGE / SECRET / HEALTH INTERFACES

Add provider-neutral runtime contracts for:
- relational store;
- raw object store;
- secret store;
- health/readiness reporting;
- structured audit/log event sink.

Yandex Cloud-specific implementation details must remain behind adapters.

For secrets:
- retain environment/macOS Keychain support for local development;
- define a Lockbox adapter contract/config shape for production;
- do not add secret values;
- do not require the Owner primary password.

## E. MINIMAL DEPLOYMENT STRUCTURE

Create a minimal portable deployment/service layout matching current architecture, without Kubernetes.

At minimum document/structure the first services:
- `collector-direct`;
- `collector-metrica`;
- `collector-yan`;
- later `event-api` and reconciliation worker boundaries.

If Terraform/`yc` are not installed or Cloud credentials are absent:
- do NOT block;
- do NOT make broad system changes merely to install them;
- create validated configuration/contracts/IaC skeleton only where it adds real value;
- clearly mark actual Cloud apply as `BLOCKED_OWNER_CLOUD_ACCESS` or `NOT_ATTEMPTED`.

No Yandex Cloud paid resources may be created in Task 003 without explicit Owner authorization.

## F. DATA QUALITY FOUNDATION

Create generic data-quality primitives/checks that Days 4–7 can use, including at least:
- freshness state;
- missing-source state;
- duplicate/idempotency state;
- malformed snapshot state;
- reconciliation-ready/not-ready state;
- `DATA_QUALITY_HOLD` representation.

No optimizer may consume a dataset marked held/not-ready.

## G. PROVIDER DOCTOR — PARALLEL RETRY ONLY

Do not alter provider credentials.

If the secure tokens have become available locally during Task 003, rerun the existing provider doctor and record READ_ONLY results.

If they remain absent, keep:
- Direct = `BLOCKED_MISSING_CREDENTIAL`;
- Metrica = `BLOCKED_MISSING_CREDENTIAL`;
- YAN Statistics = `BLOCKED_MISSING_CREDENTIAL`;

and continue Task 003.

Never print or commit tokens/private provider mappings.

## TESTS / REQUIRED EVIDENCE

Add automated tests/checks sufficient to prove at least:
- raw-store immutability;
- same-content idempotency;
- conflicting payload rejection;
- SHA-256 verification;
- site/provider path isolation;
- money representation does not use binary floating-point semantics in schema/domain;
- generic data-quality hold behavior;
- secret redaction remains intact;
- no provider write methods are introduced;
- public examples contain placeholders only;
- tracked secret scan passes;
- `git diff --check` passes.

Create:

`profit-engine/evidence/TASK-003-DATA-FOUNDATION.md`

It must record:
- baseline/final HEAD;
- files changed;
- schema/migration design;
- raw snapshot contract;
- storage interfaces;
- private-core boundary status;
- cloud tooling/access status;
- provider doctor status;
- tests/checks;
- blockers;
- recommended Task 004 boundary.

## FORBIDDEN

- no Direct Editing;
- no campaign/ad/group creation or mutation;
- no budget changes/spend;
- no production Dilivox changes;
- no Tilda publication;
- no provider secret disclosure;
- no real raw provider data committed;
- no real private provider/account IDs committed;
- no Yandex Cloud paid resource creation without explicit Owner authorization;
- no proprietary optimizer/scoring implementation in the public repo;
- no force push;
- no merge to `main`;
- do not self-accept.

## ACCEPTANCE GATES

Task 003 engineering foundation is accepted only if:
1. Task starts from current origin and preserves Central Brain changes;
2. PostgreSQL schema foundation is coherent and multi-site/provider-neutral;
3. raw snapshot contract is immutable/reproducible and tested;
4. storage/secret/health interfaces exist behind provider-neutral contracts;
5. data-quality hold primitives exist;
6. private-core boundary and migration gate are explicit;
7. no secrets/private IDs/real raw provider data are committed;
8. no provider writes/spend/site production changes occur;
9. tests and secret scans pass;
10. evidence is committed and pushed to `origin/profit-engine`.

## FINAL REPORT FORMAT

Return one compact report with:
- `STATUS: COMPLETE | PARTIAL | BLOCKED`
- `BASELINE_HEAD:`
- `FINAL_HEAD:`
- `ORIGIN_PROFIT_ENGINE:`
- `WORKTREE:`
- `PRIVATE_CORE_BOUNDARY:`
- `POSTGRES_SCHEMA:`
- `RAW_SNAPSHOT_CONTRACT:`
- `STORAGE_INTERFACES:`
- `DATA_QUALITY:`
- `CLOUD_FOUNDATION:`
- `DIRECT:`
- `METRICA:`
- `YAN:`
- `SECRET_SAFETY:`
- `FILES_CHANGED:`
- `COMMIT_SHA:`
- `TESTS/CHECKS:`
- `BLOCKERS:`
- `RECOMMENDED_TASK_004:`

Central Brain will review evidence and immediately advance the launch plan.