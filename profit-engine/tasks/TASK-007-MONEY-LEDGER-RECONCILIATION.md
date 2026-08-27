# CODEX TASK 007 — MONEY LEDGER + ATTRIBUTION + RECONCILIATION + K5 FOUNDATION

Status: READY FOR EXECUTION
Owner: Central Brain
Executor: Codex
Repository: `niknikdym-hue/Dilivox-1`
Canonical branch: `profit-engine`
Launch day: Day 7

## READ FIRST — MANDATORY

1. `profit-engine/PROJECT_HANDOFF.md`
2. `profit-engine/OWNER_DECISIONS.md`
3. `profit-engine/PROJECT_STATE.md`
4. `profit-engine/HARD_12_DAY_LAUNCH_PLAN.md`
5. `profit-engine/DAY7_MONEY_LEDGER_DESIGN.md`
6. `profit-engine/DILIVOX_SITE_INTEGRATION.md`
7. `profit-engine/PRIVATE_CORE_BOUNDARY.md`
8. Task 006 evidence: `profit-engine/evidence/TASK-006-FIRST-PARTY-EVENTS.md`

## BASELINE / SYNC

Accepted Task 006 implementation:

`ff5b0251daeb90e373aa890e2ca198282a533102`

Central Brain advanced `origin/profit-engine` after acceptance by adding the canonical Day-7 design and this task contract. Therefore:

- `git fetch origin` first;
- safe fast-forward only;
- use current `origin/profit-engine` as actual baseline;
- do not overwrite Central Brain commits;
- no force push.

Canonical local workspace:

`~/Documents/New project/Profit Engine/Dilivox-1`

Separate Dilivox/Tilda workspace remains READ_ONLY:

`~/Documents/New project/Dilivox`

## OBJECTIVE

Implement an evidence-ready money ledger that can truthfully represent:

`Direct spend -> acquisition/campaign evidence -> Dilivox cohort behavior -> Metrica-attributed YAN revenue -> YAN control-total reconciliation -> period/cohort K5 state`.

Task 007 is measurement/reconciliation only. It is NOT optimizer implementation and does not authorize any provider/site write.

## CRITICAL INVARIANTS

### 1. NO FABRICATED ATTRIBUTION

Never join spend to a cohort only because dates are close.

Every money join must carry an explicit `attribution_grade` and provenance.

Canonical grades from `DAY7_MONEY_LEDGER_DESIGN.md`:

- `A_STRONG_DIRECT_CROSSCHECK`;
- `B_DIRECT_ID`;
- `C_METRICA_DIRECT`;
- `D_UTM_PRIVATE_MAP`;
- `E_SOURCE_ONLY`;
- `UNJOINABLE`.

Contradictory identities -> hold.

### 2. NO DOUBLE REVENUE

Metrica YAN revenue and YAN Partner Statistics revenue are NOT two revenue streams.

- Metrica YAN revenue = attribution view;
- YAN Partner Statistics = control/reconciliation total.

Never add them.

### 3. PERIOD K5 != COHORT K5

Implement both as distinct types.

`period_K5 = Direct-attributed YAN revenue in reporting interval / Direct spend in same interval`.

Cohort K5 uses the ORIGINAL acquisition denominator for D0 cohort:

- `K5_1D`: D0 revenue / original acquisition spend;
- `K5_7D`: D0..D0+6 cohort revenue / original acquisition spend;
- `K5_30D`: D0..D0+29 cohort revenue / original acquisition spend.

If later revenue cannot be proven to belong to the original acquisition cohort:

`NOT_COMPUTABLE_ATTRIBUTION_HOLD`.

Never substitute rolling/period K5 and label it cohort K5.

### 4. RAW / SOURCE PROVENANCE

Every money fact/derived measurement must reference source facts/raw provenance and source state.

### 5. DECIMAL MONEY ONLY

Use Python `Decimal` / PostgreSQL `numeric`; no float money arithmetic.

Unknown != zero.
Zero spend -> undefined K5, never infinity.

## REQUIRED IMPLEMENTATION

### A. VERSIONED DATABASE MIGRATION

Create a new migration after `0001_data_foundation.sql`. Do NOT edit the accepted old migration.

Add provider-neutral, site-scoped structures sufficient for:

1. acquisition ledger;
2. acquisition/provider attribution evidence;
3. reconciliation runs/checks;
4. derived period/cohort money facts;
5. K5 measurements/state/provenance.

Recommended tables may include names such as:

- `acquisitions`;
- `acquisition_attribution_evidence`;
- `reconciliation_runs` / `reconciliation_facts`;
- `money_ledger_facts`;
- `k5_measurements`.

Exact naming may differ if the semantics are equivalent.

Requirements:

- `site_id` on every business record;
- idempotency/version constraints;
- timestamps `timestamptz` where applicable;
- money `numeric(20,6)` or stronger compatible Decimal representation;
- explicit source/data-state/provenance;
- no production provider IDs or private mappings in public fixtures.

### B. ACQUISITION REGISTRATION CONTRACT

Task 005 captures allowlisted attribution locally, but Task 006 site events intentionally do not carry all campaign dimensions. Close this gap without weakening privacy.

Implement a strict acquisition-registration schema/model derived ONLY from Task-005 allowlisted state.

Allowed acquisition attributes:

- `site_id`;
- `acquisition_id`;
- `cohort_ref`;
- `acquired_at`;
- `landing_content_id`;
- provider identity when proven;
- `yclid`;
- `campaign_id`;
- `ad_id`;
- `group_id`;
- `criterion_id`;
- `phrase_id`;
- `keyword_id`;
- `utm_source`;
- `utm_medium`;
- `utm_campaign`;
- `utm_content`;
- `utm_term`;
- schema/deployment/provenance/expiry metadata.

No arbitrary params, PII, free text, forms, fingerprint, raw URL or Metrica ClientID.

If browser helper is needed, create an UNPUBLISHED successor helper/API such as `buildAcquisitionRegistration()` and test it. Do NOT enable production dispatch and do NOT publish Tilda.

Runtime ingestion for acquisition registrations must be raw-first/idempotent/conflict-safe or use an equivalent accepted immutable source contract.

Same acquisition + same data -> replay/idempotent.
Same acquisition + conflicting campaign identity -> `DATA_QUALITY_HOLD`.

### C. DIRECT SPEND LEDGER INPUT

Use accepted Direct `traffic_facts`/campaign facts.

Require:

- campaign/day identity;
- spend Decimal;
- currency;
- VAT/discount/money basis provenance;
- raw/source reference;
- source completeness/state.

Do not infer missing spend.

### D. METRICA DIRECT-ATTRIBUTED YAN VIEW

Extend/read the Metrica source contract for attribution-aware YAN revenue without assuming compatibility blindly.

Current official Yandex Metrica dimensions include attribution-aware Direct identities such as:

- `ym:s:<attribution>DirectClickOrder` — Direct campaign ID;
- `ym:s:<attribution>DirectBannerGroup`;
- Direct/search criteria dimensions;
- `ym:s:<attribution>UTMCampaign`, UTM source/medium/content/term.

Current monetization metrics include `ym:s:yanPartnerPrice` plus delivery metrics.

Implement request/fixture semantics that explicitly record attribution model. `last_yandex_direct_click` is a candidate view for Direct-attributed return sessions; do not hard-code it as the only truth without provenance.

Requirements:

- validate returned dimensions/metrics;
- preserve model/currency/sampling/accuracy/lag/disclosure metadata;
- incompatible/missing money semantics -> hold;
- never invent campaign identity from a campaign name string;
- private UTM->campaign mappings, if supported, remain outside public Git.

### E. ATTRIBUTION CROSS-CHECK ENGINE

Implement provider-neutral joining/classification from available evidence.

Minimum checks:

- first-party `campaign_id` against Direct campaign fact;
- Metrica Direct campaign attribution against Direct campaign fact;
- first-party vs Metrica campaign agreement;
- optional ad/group/criterion consistency where both sides have evidence;
- UTM private mapping only via injectable/private interface;
- no date-proximity fallback.

Output must include:

- grade;
- selected provider campaign ref when proven;
- evidence references;
- contradictory/missing reasons;
- `optimizer_consumable` / hold state.

### F. METRICA <-> YAN RECONCILIATION

Implement comparison on compatible scope only:

- same site/resource scope;
- same day/reporting window;
- same timezone basis;
- same currency;
- known VAT/revenue basis;
- compatible source finality.

Output:

- Metrica attributed/control amount as applicable;
- YAN control amount;
- absolute delta;
- relative delta where defined;
- reconciliation state:
  - `PENDING`;
  - `MATCHED`;
  - `DRIFT`;
  - `BASIS_BLOCKED`;
  - `SOURCE_MISSING`;
- tolerance/config version;
- source/raw provenance.

Do not silently choose one source on drift.

Tolerance must be explicit/configurable and generic. Do not hide owner-specific commercial policy in public code.

### G. K5 MEASUREMENT ENGINE

Implement Decimal calculations for:

- period K5;
- cohort `K5_1D`;
- cohort `K5_7D`;
- cohort `K5_30D`;
- revenue/acquired-user where denominator valid;
- revenue/visit where scope matches.

Each measurement must carry:

- `site_id`;
- measurement kind;
- window start/end;
- cohort key/ref if cohort metric;
- numerator amount/source;
- denominator amount/source;
- currency/basis;
- attribution grade;
- source-state minimum;
- reconciliation state;
- calculation/version identity;
- hold reasons;
- `optimizer_consumable`.

K5 source states:

- `ESTIMATED`;
- `FINAL`;
- `RECONCILED`;
- `NOT_COMPUTABLE` / hold.

Never claim real `K5 >= 5.0` from fixtures.

### H. LATE ARRIVAL / RECOMPUTATION

Derived measurements must be safely recomputable when immutable provider sources receive later versions/corrections.

Requirements:

- raw history is never rewritten;
- derived measurement version can advance;
- late-arrival grace/config is explicit;
- open/immature windows remain estimated/held as appropriate;
- 7D/30D cohort values cannot be final before their time/data conditions are satisfied.

### I. DATA_QUALITY_HOLD

At minimum implement/test:

- missing Direct spend;
- missing YAN revenue;
- zero/unknown denominator;
- unjoinable acquisition;
- contradictory first-party/Metrica campaign;
- Metrica/YAN scope mismatch;
- currency mismatch;
- unknown VAT/money basis;
- stale/incomplete source;
- reconciliation drift;
- late-arrival window still open;
- conflicting acquisition registration;
- attempted Metrica+YAN double-count;
- attempted cohort K5 from period-only evidence.

Any material hold:

`optimizer_consumable=false`.

## REQUIRED FIXTURE ACCEPTANCE TESTS

At minimum:

1. strong Direct campaign cross-check -> `A_STRONG_DIRECT_CROSSCHECK`;
2. first-party Direct ID only -> `B_DIRECT_ID`;
3. Metrica-only campaign attribution -> `C_METRICA_DIRECT` and no false cohort linkage;
4. contradictory campaign identities -> hold;
5. exact Metrica/YAN compatible control match -> `MATCHED` / reconciled eligible;
6. reconciliation drift -> hold;
7. currency/basis mismatch -> hold;
8. same acquisition replay -> idempotent;
9. conflicting acquisition replay -> hold;
10. period K5 correct Decimal result;
11. zero spend -> K5 undefined;
12. missing revenue -> undefined, never zero;
13. period K5 cannot be labeled cohort K5;
14. 1D/7D/30D cohort calculations keep the original spend denominator;
15. immature 7D/30D window not FINAL;
16. late revenue creates new derived version without changing raw;
17. Metrica + YAN amounts never double-count;
18. held upstream source -> held downstream measurement;
19. revenue/user and revenue/visit reject incompatible/zero denominator scope;
20. all prior Python/Node suites remain green.

## LIVE PROVIDER STATUS

At task start:

`BLOCKED_EXTERNAL_PROVIDER_CREDENTIAL`.

Direct/Metrica/YAN live OAuth checks remain external blockers only.

If secure credentials become available during Task 007:

1. run provider doctor first;
2. only PASS provider may perform bounded READ_ONLY live collection;
3. production payloads/raw stay outside Git;
4. evidence contains redacted counts/status only;
5. no real K5 claim unless all required live money/reconciliation gates pass.

## PUBLIC/PRIVATE CORE BOUNDARY

This public repository may contain generic ledger, reconciliation, measurement, data-quality and adapter code.

Do NOT add:

- proprietary profit scoring;
- optimizer weights;
- learned thresholds;
- owner-specific capital allocation heuristics;
- confidential mappings;
- private production datasets.

## FORBIDDEN

- Direct writes;
- campaign/group/ad mutation;
- budget mutation;
- advertising spend;
- production Tilda publication;
- production Dilivox mutation;
- YAN provider code mutation;
- paid Yandex Cloud apply;
- secrets/private IDs/raw production exports in Git;
- arbitrary query capture/PII/fingerprinting;
- proprietary optimizer logic in the public repo;
- force push;
- merge into `main`.

## EVIDENCE

Create:

`profit-engine/evidence/TASK-007-MONEY-LEDGER-RECONCILIATION.md`

Evidence must include:

- baseline/final/origin SHAs;
- migration/schema summary;
- acquisition registration schema + privacy allowlist;
- attribution-grade implementation/results;
- period vs cohort K5 distinction proof;
- reconciliation-state proof;
- fixture money map with synthetic values only;
- 1D/7D/30D calculations and states;
- late-arrival/recomputation proof;
- double-count prevention proof;
- data-quality hold matrix;
- live provider status;
- tests/checks;
- files changed;
- blockers;
- recommended Task 008 boundary.

## FINAL REPORT FORMAT

Return:

- `STATUS: COMPLETE | PARTIAL | BLOCKED`
- `BASELINE_HEAD:`
- `FINAL_HEAD:`
- `ORIGIN_PROFIT_ENGINE:`
- `WORKTREE:`
- `DB_MIGRATION:`
- `ACQUISITION_LEDGER:`
- `ATTRIBUTION_GRADES:`
- `METRICA_ATTRIBUTION_VIEW:`
- `RECONCILIATION:`
- `PERIOD_K5:`
- `COHORT_K5_1D_7D_30D:`
- `LATE_ARRIVAL:`
- `DATA_QUALITY:`
- `LIVE_PROVIDER_STATUS:`
- `SECRET_SAFETY:`
- `FILES_CHANGED:`
- `COMMIT_SHA:`
- `TESTS/CHECKS:`
- `BLOCKERS:`
- `RECOMMENDED_TASK_008:`

Do not self-accept. Central Brain will inspect origin/evidence and immediately advance the launch plan.
