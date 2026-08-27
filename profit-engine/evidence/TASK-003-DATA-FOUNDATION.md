# TASK 003 — DATA FOUNDATION + PRIVATE-CORE BOUNDARY — EVIDENCE

## Execution identity

- Baseline local HEAD before synchronization: `a5de1b32a8460fb18428625e01b09509686d158a`.
- Baseline/current `origin/profit-engine` used for implementation:
  `9056fb682bfc2a4e0a5470106a8ed88308812735`.
- Synchronization: `git fetch origin profit-engine`, followed by safe
  `git merge --ff-only origin/profit-engine`.
- Final HEAD: the evidence-bearing Task 003 commit containing this file; exact
  SHA is reported in the Task 003 completion report and pushed normally.
- Worktree: canonical local Profit Engine checkout. The separate Dilivox site
  workspace was not modified.

## Private-core boundary

`profit-engine/PRIVATE_CORE_BOUNDARY.md` classifies public-safe interfaces,
schemas, invariants, adapters and utilities separately from proprietary scoring,
ranking, allocation, learned thresholds, confidential mappings, secrets, and
production data. No private repository is claimed to exist. Gate:

`PRIVATE_CORE_REPOSITORY_REQUIRED_BEFORE_SENSITIVE_OPTIMIZER_IMPLEMENTATION`

No optimizer/scoring implementation was added.

## PostgreSQL schema foundation

Migration `data/migrations/0001_data_foundation.sql` creates a provider-neutral
`profit_engine` schema with: `sites`, `provider_accounts`, `ingestion_runs`,
`raw_snapshots`, `campaign_snapshots`, `traffic_facts`, `site_events`,
`monetization_facts`, `cohorts`, `experiments`, `decisions`, `approvals`,
`actions_audit`, and `data_quality_checks`.

Facts and governance records are site-scoped; provider identity and provenance
are explicit; timestamps use `timestamptz`; monetary columns use
`numeric(20,6)`; and uniqueness/idempotency constraints are defined. The schema
contains no actual provider IDs, secrets, or site-specific branches. No database
or paid Cloud resource was created.

## Immutable raw snapshot contract

- JSON Schema: `data/raw-snapshot-envelope.schema.json`.
- Runtime: `runtime/profit_engine_runtime/raw_store.py`.
- Logical layout: `raw/{site_id}/{provider}/{yyyy}/{mm}/{dd}/{source_type}/{request_fingerprint}.json`.
- Metadata includes version, site/provider/source, timezone-aware capture time,
  optional source window, request fingerprint, payload SHA-256, optional provider
  request ID, estimated/final/reconciled state, and ingestion run ID.
- Local default root: `~/.local/share/profit-engine/raw`, outside Git.
- Write path uses a same-directory temporary file, `fsync`, and atomic create-only
  hard link. Same-content repetition is idempotent; different content at the same
  identity conflicts; read and write both verify the canonical payload hash.
- Tests use synthetic fixture payloads only. No production payload was created or
  committed.

## Runtime interfaces and data quality

`contracts.py` defines provider-neutral Protocols for relational storage, raw
objects, secrets, health/readiness, and audit events. It also defines Decimal-only
money and a placeholder-reference Lockbox adapter configuration boundary.
Environment and macOS Keychain secret resolution from Task 002 remain available.

`data_quality.py` represents freshness, source presence, idempotent replay versus
conflict, malformed snapshot state, reconciliation readiness, and
`DATA_QUALITY_HOLD`. Held/not-ready input has `optimizer_consumable == False`.

## Portable deployment boundary

`deploy/` documents/configures placeholder-only boundaries for
`collector-direct`, `collector-metrica`, `collector-yan`, later `event-api`, and
`reconciliation-worker`, without Kubernetes. `terraform`, `yc`, and `docker`
were not present in PATH. Cloud apply was not attempted and remains
`BLOCKED_OWNER_CLOUD_ACCESS`; no Yandex Cloud resource was created.

## Provider doctor

Executed:

`PYTHONPATH=profit-engine/runtime python3 -m profit_engine_runtime.doctor`

- Direct: `BLOCKED_MISSING_CREDENTIAL`.
- Metrica: `BLOCKED_MISSING_CREDENTIAL`.
- YAN Statistics: `BLOCKED_MISSING_CREDENTIAL`.
- Rollout mode: `READ_ONLY`.
- Private registry: absent; defaults used.
- Live provider requests: zero.

Minimum Owner action remains unchanged from Task 002: securely authorize/expose
the shared Direct/Metrica read OAuth token and the distinct YAN Statistics API
OAuth token through environment or macOS Keychain references, plus private local
mapping values. Token values must never be sent in chat or committed.

## Tests and safety checks

- `PYTHONPATH=profit-engine/runtime python3 -m unittest discover -s profit-engine/runtime/tests -v`
  — `21/21 PASS`.
- Covered raw-store create-only behavior, same-content idempotency, conflict,
  SHA-256 write/read validation, site/provider path isolation, Decimal money,
  quality holds, placeholder configs, and absence of provider write methods.
- Existing redaction, request-shape, access-classification, bounded retry, and
  private-config tests remain green.
- `git diff --check` — PASS.
- Tracked/candidate secret scan — PASS; no credential value, private provider ID,
  or production raw payload detected.
- Existing unrelated untracked `TASK-001-M0-INVENTORY 2.md` was not modified or
  staged.

## Files changed

- `profit-engine/PRIVATE_CORE_BOUNDARY.md`
- `profit-engine/config/lockbox.example.json`
- `profit-engine/data/README.md`
- `profit-engine/data/migrations/0001_data_foundation.sql`
- `profit-engine/data/raw-snapshot-envelope.schema.json`
- `profit-engine/deploy/README.md`
- `profit-engine/deploy/services.example.json`
- `profit-engine/runtime/README.md`
- `profit-engine/runtime/profit_engine_runtime/contracts.py`
- `profit-engine/runtime/profit_engine_runtime/data_quality.py`
- `profit-engine/runtime/profit_engine_runtime/raw_store.py`
- `profit-engine/runtime/tests/test_data_foundation.py`
- `profit-engine/evidence/TASK-003-DATA-FOUNDATION.md`

## Blockers and Task 004 boundary

External blocker: secure provider credentials/private mappings remain absent.
This did not block Task 003 engineering. Cloud apply requires separate Owner
authorization and access.

Recommended Task 004: implement read-only collectors and ingestion orchestration
against these interfaces, writing immutable raw snapshots first and metadata/facts
second; propagate `DATA_QUALITY_HOLD`; use synthetic fixtures until credentialed
live reads are available. Keep provider mutation, optimization policy, Cloud
resource creation, and production site changes out of scope.
