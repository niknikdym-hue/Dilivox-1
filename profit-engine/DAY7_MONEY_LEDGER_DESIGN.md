# PROFIT ENGINE — DAY 7 MONEY LEDGER / ATTRIBUTION / RECONCILIATION DESIGN

Status: CANONICAL EXECUTION DESIGN
Updated: 2026-08-27
Site: `dilivox`

## 1. Purpose

Day 7 converts accepted raw/provider/event facts into an evidence-ready money map without fabricating attribution or revenue.

Canonical chain:

`Direct spend -> acquisition identity -> Dilivox cohort/behavior -> Metrica-attributed YAN revenue -> YAN control-total reconciliation -> K5 state`.

The ledger is a measurement/control layer, not an optimizer.

## 2. Non-negotiable money rules

1. All money uses `Decimal` / PostgreSQL `numeric`, never binary float.
2. Direct spend and YAN revenue must have explicit currency and money-basis provenance.
3. Zero spend never produces infinite K5; K5 is undefined / not computable.
4. Unknown revenue is never replaced by zero.
5. Metrica YAN revenue and YAN Partner Statistics revenue MUST NOT be added together.
6. Metrica YAN revenue is the first attribution view for traffic/campaign/content slices.
7. YAN Partner Statistics is a provider control total/reconciliation source.
8. First-party DOM/events never create provider revenue.
9. A dashboard value cannot upgrade source state from estimated/final/reconciled.
10. Material attribution, currency, VAT/basis, freshness or reconciliation uncertainty -> `DATA_QUALITY_HOLD`.

## 3. Required inputs

Accepted upstream sources:

- Direct `campaign_snapshots` and `traffic_facts` including spend/click/impression provenance;
- first-party `site_events` including `acquisition_id`, `cohort_ref`, stable `content_id` and event identity;
- Metrica traffic/YAN monetization facts;
- YAN Partner Statistics monetization/control totals;
- immutable raw snapshot provenance for every derived provider fact.

Day 7 also closes the acquisition-dimension gap by defining a strict acquisition registration/ledger contract derived only from the Task-005 allowlisted attribution state.

## 4. Acquisition ledger

A production K5 join may never infer a campaign only from date proximity.

Minimum acquisition record:

- `site_id`;
- opaque `acquisition_id`;
- `cohort_ref`;
- `acquired_at`;
- `landing_content_id`;
- provider = `direct` where evidence says Yandex Direct;
- approved attribution identifiers when actually present: `yclid`, `campaign_id`, `ad_id`, `group_id`, `criterion_id`, `phrase_id`, `keyword_id`, five UTM fields;
- source/deployment/schema provenance;
- raw registration identity/hash;
- expiry/attribution-window metadata.

No arbitrary query parameters, PII, form/free text, fingerprint or Metrica ClientID.

Browser/site code may expose a strict `buildAcquisitionRegistration()` contract, but Task 007 does not authorize production network dispatch or Tilda publication.

## 5. Attribution grades

Every spend/revenue join receives an explicit grade. No hidden fallback.

- `A_STRONG_DIRECT_CROSSCHECK`: first-party Direct campaign identity is present and agrees with Metrica Direct campaign attribution / registered Direct entity.
- `B_DIRECT_ID`: first-party Direct campaign identity joins to Direct spend, but independent Metrica campaign cross-check is not yet available.
- `C_METRICA_DIRECT`: Metrica has Direct campaign attribution, but the first-party acquisition cannot be linked to that provider campaign identity.
- `D_UTM_PRIVATE_MAP`: explicit private/local mapping resolves UTM campaign to a Direct campaign; never store the private mapping in public Git.
- `E_SOURCE_ONLY`: source is known as paid/Direct but campaign-level join is not proven.
- `UNJOINABLE`: attribution evidence is insufficient or contradictory.

Production cohort K5 requires at least a grade allowed by the measurement policy. Until real evidence exists, fixture calculations may test all grades but must never claim production proof.

Contradictory campaign/ad/group evidence -> `DATA_QUALITY_HOLD`.

## 6. Metrica attribution contract

Current Yandex Metrica Reporting API exposes attribution-aware dimensions including Direct campaign ID (`ym:s:<attribution>DirectClickOrder`), Direct group, Direct ad/search-criteria dimensions and UTM dimensions. YAN monetization includes `ym:s:yanPartnerPrice` and related delivery metrics.

Task 007 should add an attribution-report contract that can request compatible slices such as:

- attribution model explicitly recorded (`last_yandex_direct_click` is a first candidate for Direct-attributed return value; other models may be compared later);
- Direct campaign ID / group identity where supported;
- UTM campaign/source where useful;
- report date;
- YAN partner revenue and delivery metrics.

Do not assume dimension/metric compatibility: validate provider response / compatibility and hold on semantic mismatch.

## 7. Period K5 vs cohort K5

These are different metrics and MUST NOT be silently conflated.

### Period K5

For a calendar/reporting interval:

`period_K5 = Direct spend in interval denominator scope /?`

Canonical ratio is:

`period_K5 = YAN revenue attributable to Direct in the same reporting interval / Direct spend in that interval`.

It is useful for operating diagnostics but is not cohort LTV.

### Cohort K5

For acquisitions originating on cohort day D0:

- `K5_1D`: revenue attributable to that acquisition cohort in D0 window / acquisition spend for that cohort;
- `K5_7D`: revenue attributable to the same cohort over D0..D0+6 / original acquisition spend;
- `K5_30D`: revenue attributable to the same cohort over D0..D0+29 / original acquisition spend.

Daily-source implementation uses an explicit site/provider timezone basis. Never guess a cohort window across incompatible timezones.

If current provider data cannot prove that later revenue belongs to the original acquisition cohort, cohort K5 status is `NOT_COMPUTABLE_ATTRIBUTION_HOLD`, not a rolling-period substitute.

## 8. Source-state and late-arrival model

Derived money state is the minimum trustworthy state of its sources.

Required states:

- `ESTIMATED`;
- `FINAL`;
- `RECONCILED`;
- `NOT_COMPUTABLE` / held reason.

Late provider corrections are handled by versioned recomputation from immutable raw/facts, not by mutating raw history.

A closed K5 window requires:

- window elapsed;
- required provider sources present;
- source freshness within configured contract;
- late-arrival grace satisfied or explicitly waived by policy;
- money basis/currency compatible;
- reconciliation state appropriate for the requested output.

Do not hard-code commercially sensitive thresholds. Generic reconciliation/late-arrival tolerances are explicit configuration with evidence/provenance.

## 9. Metrica vs YAN reconciliation

Metrica-attributed YAN revenue is compared against YAN Partner Statistics control totals only on compatible scope:

- same site/provider resource scope;
- same date/timezone basis;
- same currency;
- known VAT/revenue basis;
- compatible finality state.

Required reconciliation outputs:

- Metrica amount;
- YAN control amount;
- absolute delta;
- relative delta when denominator non-zero;
- source states/provenance;
- status: `PENDING`, `MATCHED`, `DRIFT`, `BASIS_BLOCKED`, `SOURCE_MISSING`;
- configured tolerance identity/version.

A drift never silently chooses the larger/smaller value.

YAN control total does not replace campaign-attributed Metrica revenue unless an explicit future allocation model is approved.

## 10. Revenue/user and revenue/visit

Safe diagnostics:

- attributed YAN revenue / acquired users where acquisition count is valid;
- attributed YAN revenue / visits where visit scope matches revenue scope;
- sessions/events/content completion remain diagnostic context only.

Denominator scope/provenance must be recorded. Zero/unknown denominator -> undefined.

## 11. Required Day 7 schema foundation

Add a new versioned migration, without changing prior migrations, for at least:

- acquisition ledger / provider attribution evidence;
- reconciliation runs/checks;
- derived cohort/period money facts;
- K5 measurements / state/provenance.

All records are site-scoped and idempotent/versioned.

Do not put production provider IDs or private mappings in Git fixtures.

## 12. Data quality holds

At minimum:

- missing Direct spend;
- missing/unknown attributed YAN revenue;
- unjoinable/contradictory acquisition identity;
- Metrica/YAN scope mismatch;
- currency mismatch;
- VAT/money-basis ambiguity;
- stale source;
- incomplete source/pagination;
- reconciliation drift outside explicit tolerance;
- late-arrival window still open;
- duplicate/conflicting acquisition registration;
- attempted double-count of Metrica + YAN revenue;
- attempted cohort K5 from period-only evidence.

Any material hold -> `optimizer_consumable=false`.

## 13. Fixture acceptance scenarios

Must prove:

1. strong Direct campaign cross-check -> valid attributed ledger;
2. exact Metrica/YAN control match -> `RECONCILED`;
3. reconciliation drift -> hold;
4. same acquisition replay -> idempotent;
5. contradictory acquisition campaign -> hold;
6. zero spend -> K5 undefined;
7. missing revenue -> K5 undefined, never zero;
8. period K5 cannot masquerade as cohort K5;
9. 1D/7D/30D cohort windows use original denominator;
10. late-arriving revenue upgrades derived version without rewriting raw;
11. Metrica + YAN amounts are not double-counted;
12. held source is never optimizer-consumable.

## 14. Live-data rule

Provider OAuth remains externally blocked at the start of Day 7.

Implement fixture/source-contract path completely. If secure credentials become available:

1. provider doctor first;
2. bounded READ_ONLY collectors;
3. raw-first storage outside Git;
4. generate only redacted counts/status in evidence;
5. do not claim `K5>=5` until reconciled live money actually proves it.

## 15. Day 7 success

Task 007 succeeds when the system can truthfully answer, for fixture or live evidence at its actual confidence/state:

`what did we spend? -> which Direct acquisition/campaign is proven? -> what Dilivox cohort/content behavior belongs to it? -> what YAN revenue is attributed? -> does YAN control reconcile? -> is K5 period/cohort computable? -> what is its source state?`

No optimizer, Direct write, budget mutation or production site publication is part of Day 7.
