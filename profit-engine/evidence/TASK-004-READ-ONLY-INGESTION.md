# TASK 004 — READ-ONLY PROVIDER INGESTION — EVIDENCE

## Execution identity

- Accepted Task 003 implementation: `3d521ff2d44532035025f31d6de8ea0428dc94fe`.
- Task 004 Central Brain baseline and implementation base:
  `e5d72814553bbcb2240ad59f48d84b62f33ca3c3`.
- Required Central Brain commit was verified as an ancestor of
  `origin/profit-engine` before work.
- Synchronization used `git fetch origin profit-engine` and
  `git merge --ff-only origin/profit-engine`.
- Final HEAD is the evidence-bearing Task 004 commit containing this file; its
  exact SHA is reported in the final Task 004 report and pushed normally.
- Separate Dilivox/Tilda workspace was not modified.

## Architecture implemented

The provider-neutral orchestrator implements:

`started -> provider/fixture read -> validation -> immutable raw put -> raw get/hash verification -> deterministic normalization -> quality evaluation -> complete|held|failed`

Request identity, ingestion run ID, raw snapshot ID, and normalized fact keys are
deterministic hashes. The in-memory relational test adapter applies set-if-absent
fact semantics, records raw metadata/provenance, lifecycle, quality state, and an
operation log. It is not represented as live PostgreSQL certification.

Raw conflict returns `held` with `raw_snapshot_conflict`; it never overwrites raw
content and never emits facts from the conflicting payload. Same-content replay
is idempotent and produces identical facts without duplicate rows.

## RAW FIRST proof

`IngestionOrchestrator` owns raw persistence. A collector cannot ask it to record
normalized facts directly. The orchestrator performs immutable `put`, then `get`
and SHA-256 verification, records raw metadata, and only then invokes
`normalize`. The integration operation log test asserts `raw:accepted` precedes
`facts:normalized`.

## Direct collector

- `campaigns.get` read contract for campaign metadata.
- Reports endpoint: `https://api-direct.yandex.com/json/v501/reports`.
- Report: `CAMPAIGN_PERFORMANCE_REPORT`, daily custom range, TSV fields `Date`,
  `CampaignId`, `Impressions`, `Clicks`, `Cost`.
- Explicit owner-cash basis: `IncludeVAT=YES`, `IncludeDiscount=YES`,
  `returnMoneyInMicros=false`, currency provenance `RUB`.
- HTTP 200 completes; 201/202 are polled within a fixed bound. Exhaustion is
  `direct_report_not_ready_timeout` and `DATA_QUALITY_HOLD`.
- TSV money is normalized with `Decimal`, never float.

Fixture output: one `campaign_snapshot`, one `traffic_fact`.

## Metrica collector

- READ_ONLY Reports API source contract for visits, YAN partner price, requests,
  renders, and shows.
- Dimensions are configurable but validated against the public allowlist.
- Counter selection uses a private mapping when configured, otherwise validated
  canonical-domain discovery.
- Sampling, sample size/space, data lag, and disclosure indicators are preserved
  in provenance.
- Missing monetization metric or ambiguous currency produces a hold.

Fixture output: one `traffic_fact`, one Metrica-measured `monetization_fact`.
No reconciliation with Partner Statistics is claimed.

## YAN Statistics collector

- READ_ONLY `statistics2/tree.json` discovery and `statistics2/get.json` daily
  report contracts.
- Daily `date|day` dimension and optional private resource filter.
- Delivery fields: `shows`, `hits_render`, and `hits` where available.
- Revenue field is accepted only when the tree marks it with revenue semantics;
  an explicitly configured field must still validate against that tree.
- Currency, timezone, VAT basis, selected field, and tree-validation state are
  preserved in provenance.
- Missing/ambiguous revenue semantics produces `yan_revenue_semantics_unavailable`
  hold and zero monetization facts—not guessed or zero-valued revenue.

Fixture output: one tree-validated `monetization_fact`.

## Data quality coverage

Implemented/tested hold states include:

- missing source and stale source window;
- malformed provider/integrity response;
- raw snapshot conflict;
- incomplete pagination/report;
- ambiguous currency or money basis;
- Direct offline/not-ready timeout;
- unavailable Metrica monetization;
- invalid Metrica dimensions;
- unknown YAN revenue semantics.

Any hold sets `optimizer_consumable=false`. No optimizer implementation exists.

## CLI and fixture execution

CLI module: `profit_engine_runtime.collector_cli` with `direct`, `metrica`, `yan`,
and `all`. Deterministic `--fixture` mode needs no credential.

Executed `all --fixture` using a temporary raw root outside Git:

- raw snapshots accepted: 3;
- campaign snapshots: 1;
- traffic facts: 2;
- monetization facts: 2;
- provider runs complete: 3;
- holds: 0.

All fixture identities and payloads are synthetic.

## Live provider status

Provider doctor ran before any possible live collection:

- Direct: `BLOCKED_MISSING_CREDENTIAL`;
- Metrica: `BLOCKED_MISSING_CREDENTIAL`;
- YAN Statistics: `BLOCKED_MISSING_CREDENTIAL`.

Private registry is absent. Live CLI returned `BLOCKED_MISSING_CREDENTIAL` before
collector execution. Live provider requests: zero. Production raw payloads: zero.
Overall external state: `BLOCKED_EXTERNAL_PROVIDER_CREDENTIAL`.

Minimum Owner action is unchanged: securely provide the shared Direct/Metrica
read OAuth reference, separate YAN Statistics OAuth reference, and private local
provider mappings/config semantics. Never paste values into chat or Git.

## Tests and safety checks

- Full test suite: `38/38 PASS`.
- Task 004 adds 17 ingestion/source-contract tests; all 21 prior tests remain
  green.
- `git diff --check`: PASS.
- tracked/candidate secret signature scan: PASS.
- provider-write method/RPC scan: PASS; only GET, Direct read RPC `get`, and
  Direct Reports POST exist.
- public fixtures/config contain synthetic values or placeholders only.
- no provider/site writes, advertising spend, Cloud apply, or Tilda publication.

## Files changed

- `profit-engine/config/site-registry.schema.json`
- `profit-engine/config/sites/dilivox.example.json`
- `profit-engine/evidence/TASK-004-READ-ONLY-INGESTION.md`
- `profit-engine/runtime/README.md`
- `profit-engine/runtime/profit_engine_runtime/collector_cli.py`
- `profit-engine/runtime/profit_engine_runtime/collectors.py`
- `profit-engine/runtime/profit_engine_runtime/config.py`
- `profit-engine/runtime/profit_engine_runtime/fixtures.py`
- `profit-engine/runtime/profit_engine_runtime/ingestion.py`
- `profit-engine/runtime/profit_engine_runtime/transport.py`
- `profit-engine/runtime/tests/test_ingestion.py`

The unrelated untracked `profit-engine/evidence/TASK-001-M0-INVENTORY 2.md` was
preserved and excluded from staging.

## Blockers and Task 005 boundary

Only live certification/collection is externally blocked by missing secure
credentials and private mappings. The fixture/source-contract engineering scope
is complete.

Recommended Task 005: implement stable Dilivox story/page IDs, first-party event
and attribution persistence, a provider-neutral monetization placement registry,
experiment identity hooks, and the first `DilivoxSiteAgent` adapter against the
existing Tilda/T123 surface. Keep the site workspace read-only until an explicit
deployment contract authorizes controlled production changes.
