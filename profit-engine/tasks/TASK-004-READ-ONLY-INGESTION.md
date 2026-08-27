# CODEX TASK 004 — READ-ONLY PROVIDER INGESTION

Status: READY FOR EXECUTION
Owner: Central Brain
Executor: Codex
Repository: `niknikdym-hue/Dilivox-1`
Canonical branch: `profit-engine`
Launch day: Day 4

## ROLE

You are the engineering executor for DILIVOX PROFIT ENGINE.
Central Brain is acceptance authority and project brain.
Do not introduce product/economic decisions or proprietary optimizer policy.

## READ FIRST — MANDATORY

Before changing anything, read current origin versions of:

1. `profit-engine/PROJECT_HANDOFF.md`
2. `profit-engine/PROJECT_STATE.md`
3. `profit-engine/OWNER_DECISIONS.md`
4. `profit-engine/HARD_12_DAY_LAUNCH_PLAN.md`
5. `profit-engine/PRIVATE_CORE_BOUNDARY.md`
6. `profit-engine/SECURITY_AND_ACCESS.md`
7. `profit-engine/data/migrations/0001_data_foundation.sql`
8. `profit-engine/data/raw-snapshot-envelope.schema.json`
9. `profit-engine/runtime/README.md`
10. `profit-engine/evidence/TASK-003-DATA-FOUNDATION.md`

Fetch current `origin/profit-engine` first and fast-forward safely. Do not overwrite Central Brain changes. No force push.

## ACCEPTED BASELINE

Task 003 accepted implementation HEAD before Central Brain Task-004 commits:

`3d521ff2d44532035025f31d6de8ea0428dc94fe`

Task 003 established:
- provider-neutral PostgreSQL schema;
- immutable raw snapshot contract/store;
- storage/secret/health/audit interfaces;
- `DATA_QUALITY_HOLD` primitives;
- public/private core gate.

Live provider reads remain `BLOCKED_MISSING_CREDENTIAL` until secure tokens/private mappings are locally available.

## OBJECTIVE

Implement the first repeatable READ_ONLY ingestion pipeline:

`provider read -> immutable raw snapshot -> ingestion metadata -> normalization -> provider-neutral facts -> data-quality state`

Raw-first is mandatory. Normalized facts MUST NOT be produced from a provider response unless the corresponding immutable raw snapshot has been successfully accepted first.

No optimizer and no provider writes are part of this task.

## 1. INGESTION ORCHESTRATOR

Implement a provider-neutral ingestion orchestrator with explicit run lifecycle:

- `started`
- `complete`
- `failed`
- `held`

Requirements:
- deterministic idempotency key per site/provider/source/window/request identity;
- same completed request replay does not duplicate raw snapshots or facts;
- conflicting content for the same immutable identity becomes a quality hold/conflict, never silent overwrite;
- failures preserve enough redacted provenance for diagnosis;
- no secret values or private provider IDs in logs/evidence.

Add a local/in-memory relational implementation suitable for integration tests if a real PostgreSQL instance is unavailable. Do NOT claim live PostgreSQL certification without an actual connection.

## 2. DIRECT READ COLLECTOR

Extend the existing Direct read foundation into a collector that can ingest:

### Campaign metadata
Use the existing Direct v5 read methods to obtain campaign metadata needed for `campaign_snapshots`.

### Spend/performance facts
Implement the current Direct Reports JSON contract for read-only statistics.
Canonical endpoint family:

`https://api.direct.yandex.com/json/v501/reports`

Support a minimal campaign/day report using the provider contract equivalent of:
- `Date`
- `CampaignId`
- `Impressions`
- `Clicks`
- `Cost`

Use an explicit money basis and preserve it in provenance. For the first owner-cash view use `IncludeVAT=YES`, `IncludeDiscount=YES`, and `returnMoneyInMicros: false` unless current provider documentation requires an equivalent setting.

Requirements:
- handle Direct Reports HTTP 200 online completion;
- handle 201/202 offline/not-ready states without fabricating data;
- bounded retry/poll behavior;
- TSV parser with Decimal money, never float money;
- raw response persisted before normalization;
- normalized rows go to `traffic_facts` with site/provider/date/dimensions/clicks/impressions/spend/currency provenance;
- no report result is treated as final beyond the state actually reported/known.

## 3. METRICA READ COLLECTOR

Implement a daily Metrica statistics collector using the current Reports API.

Minimum money/traffic metrics profile should support compatible combinations of:
- `ym:s:visits`
- `ym:s:yanPartnerPrice`
- `ym:s:yanRequests`
- `ym:s:yanRenders`
- `ym:s:yanShows`

Dimensions/query profile must be configurable and source-contract tested; do not silently use an incompatible metric/dimension combination.

Requirements:
- select Dilivox only through private mapping or validated canonical-domain discovery;
- raw JSON persisted before normalization;
- visits/traffic dimensions normalize to provider-neutral facts where appropriate;
- YAN monetization values from Metrica normalize to `monetization_facts` with provider/source provenance identifying Metrica as the measurement source;
- preserve sampling/data-disclosure/accuracy indicators if returned by the provider;
- no claim of reconciliation with YAN Partner Statistics yet.

## 4. YAN PARTNER STATISTICS COLLECTOR

Implement a YAN Statistics collector using the current `statistics2` API.

Requirements:
- obtain/cache the Statistics Tree contract for available fields when live credentials exist;
- build daily report requests through `statistics2/get.json`;
- support `dimension_field=date|day` and private resource filtering when configured;
- support core delivery fields such as `shows`, `hits_render`, `hits` when available;
- monetary/revenue field MUST be discovered from the tree or explicitly configured/validated — do not invent a field name;
- explicitly record currency, timezone and VAT basis in provenance;
- raw response persisted before normalization;
- normalize revenue/delivery facts to `monetization_facts` only when field semantics are known;
- unavailable/ambiguous revenue field => `DATA_QUALITY_HOLD`, not zero revenue.

## 5. RAW-FIRST AND SOURCE FIDELITY

For every provider collection:

1. create ingestion run;
2. build stable request identity/fingerprint;
3. execute read or fixture source;
4. validate provider response shape;
5. store immutable raw snapshot;
6. verify stored hash;
7. only then normalize facts;
8. attach `raw_snapshot_id` / provenance to normalized records;
9. run data-quality checks;
10. mark run complete or held/failed.

A normalizer must be deterministic: the same accepted raw payload must produce the same normalized facts.

## 6. DATA QUALITY / FRESHNESS

Extend quality handling for ingestion with at least:
- missing source;
- stale source window;
- malformed provider response;
- raw snapshot conflict;
- missing/ambiguous currency or money basis;
- Metrica monetization not available;
- YAN revenue-field semantics unavailable;
- Direct report not ready/offline timeout;
- partial pagination/report incompleteness.

Any money-critical ambiguity must propagate `DATA_QUALITY_HOLD` and `optimizer_consumable == False`.

## 7. CLI / EXECUTION SURFACE

Provide one minimal collector CLI/module supporting:

- `direct`
- `metrica`
- `yan`
- `all`

It must support deterministic fixture mode for tests/local development.
Live mode may run only when secure private config/token references are available.

Missing credentials must produce `BLOCKED_MISSING_CREDENTIAL`, not a crash and not fake success.

## 8. LIVE READS IF CREDENTIALS APPEAR

If the required secure tokens/private mapping are available locally during execution:
- rerun provider doctor first;
- only after PASS, run the minimal bounded READ_ONLY collector for that provider;
- store production raw data ONLY in the configured local/private raw store outside Git;
- evidence may contain only redacted counts/statuses, never private IDs/raw payloads/tokens.

If credentials are still absent, fixture/source-contract implementation proceeds and live state remains `BLOCKED_EXTERNAL_PROVIDER_CREDENTIAL`.

## 9. TESTS — REQUIRED

Add tests covering at minimum:
- Direct campaign metadata normalization;
- Direct Reports request shape and TSV parsing;
- Direct 200 vs 201/202 behavior;
- Decimal money and explicit VAT/discount basis;
- Metrica money/visit normalization fixture;
- incompatible/invalid Metrica response => hold;
- YAN tree-driven field selection fixture;
- missing YAN revenue semantics => hold;
- raw-before-normalized invariant;
- same-content replay idempotency;
- conflicting raw identity rejection/hold;
- deterministic normalizer replay;
- pagination/completeness handling;
- missing credentials classification;
- no provider write methods/RPCs;
- secret/redaction checks.

All pre-existing tests must remain green.

## REQUIRED EVIDENCE

Create:

`profit-engine/evidence/TASK-004-READ-ONLY-INGESTION.md`

It must contain no secrets/private provider IDs/raw production payloads and report:
- baseline/final HEAD;
- files changed;
- architecture implemented;
- Direct/Metrica/YAN collector status;
- raw-first/idempotency evidence;
- normalized fact types produced in fixtures;
- data-quality hold coverage;
- test counts/results;
- live provider status;
- exact blockers;
- recommended Task 005 boundary.

Commit and normal fast-forward push to `origin/profit-engine` after secret scan and tests.

## FORBIDDEN

- Direct write API calls;
- campaign/group/ad creation/modification/pause/resume;
- budget changes or spend;
- production Dilivox/Tilda changes;
- paid Yandex Cloud resource creation;
- secrets/private provider IDs/production raw exports in Git;
- proprietary optimizer/scoring/allocation implementation in this public repo;
- force push;
- merge to `main`.

## ACCEPTANCE GATES

Task 004 is accepted only if:
1. all three provider collectors have real source-contract implementations, not stubs;
2. raw snapshot persistence precedes normalization by construction/test;
3. replay is idempotent and conflicts fail safe;
4. normalized facts preserve source provenance and Decimal money;
5. Direct offline report semantics are handled safely;
6. YAN monetary field is tree/config validated rather than invented;
7. money-critical ambiguity causes `DATA_QUALITY_HOLD`;
8. all tests/secret scans pass;
9. no provider/site writes or spend occurred;
10. evidence is pushed to origin.

## FINAL REPORT FORMAT

Return exactly:

- `STATUS: COMPLETE | PARTIAL | BLOCKED`
- `BASELINE_HEAD:`
- `FINAL_HEAD:`
- `ORIGIN_PROFIT_ENGINE:`
- `WORKTREE:`
- `INGESTION_ORCHESTRATOR:`
- `DIRECT_COLLECTOR:`
- `METRICA_COLLECTOR:`
- `YAN_COLLECTOR:`
- `RAW_FIRST:`
- `NORMALIZED_FACTS:`
- `DATA_QUALITY:`
- `LIVE_PROVIDER_STATUS:`
- `SECRET_SAFETY:`
- `FILES_CHANGED:`
- `COMMIT_SHA:`
- `TESTS/CHECKS:`
- `BLOCKERS:`
- `RECOMMENDED_TASK_005:`

Do not self-accept. Central Brain will inspect origin evidence and advance the launch plan.