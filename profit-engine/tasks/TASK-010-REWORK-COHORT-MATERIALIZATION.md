# CODEX TASK 010 REWORK — COHORT MATERIALIZATION TRUTH GATE

Status: REWORK REQUIRED
Owner: Central Brain
Executor: Codex
Repository: `niknikdym-hue/Dilivox-1`
Branch: `profit-engine`
Private companion repository: `niknikdym-hue/profit-engine-core`

## Why this rework exists

Task 010 otherwise passed, but Central Brain found one launch-critical semantic defect in the public `LedgerMaterializer`.

Current implementation takes one daily `MetricaAttributionFact.attributed_yan_revenue` and passes that same amount into `cohort_k5()` for 1D, 7D, and 30D.

This violates the already-canonical Day-7 rule:

> If current provider data cannot prove that later revenue belongs to the original acquisition cohort, cohort K5 must be `NOT_COMPUTABLE_ATTRIBUTION_HOLD`, never a rolling/period substitute.

A Metrica campaign/day attribution fact proves campaign attribution for that reporting row. It does NOT by itself prove D0 cohort membership for revenue across D0..D0+6 or D0..D0+29.

## Scope

Bounded rework only. Preserve accepted Task-010 components:

- named Metrica attribution fact;
- period K5 path;
- ActionProposal v1;
- Budget Governor v1;
- public stop-loss/data-quality/kill-switch guards;
- site experiment intents;
- private ProfitAllocator logic.

Do not redesign those components unless required for compatibility with this fix.

## Required public fix

### 1. Separate period evidence from cohort evidence

`MetricaAttributionFact` (campaign/day) may continue to feed `period_K5` when all existing gates pass.

It MUST NOT automatically feed `K5_1D`, `K5_7D`, or `K5_30D`.

### 2. Add explicit cohort-revenue evidence contract

Add a public-safe immutable contract such as `CohortRevenueEvidence v1` (exact class name may differ) with at least:

- `site_id`;
- `cohort_ref`;
- `window_days` exactly 1, 7, or 30;
- `window_start` / `window_end`;
- attributed cohort revenue as Decimal;
- currency;
- money basis;
- timezone;
- source-state/finality;
- reconciliation state;
- immutable source/provenance refs;
- explicit linkage evidence/basis proving that this revenue belongs to the named acquisition cohort;
- deterministic evidence digest;
- hold reasons / optimizer-consumable state.

No PII, no Metrica ClientID as first-party identity, no arbitrary mappings, no campaign-name/date-only inference.

### 3. Fail closed when cohort evidence is absent

If explicit cohort-revenue evidence for a requested window is absent, incomplete, contradictory, immature, unproven, non-MATCHED, or source-held:

- cohort measurement value MUST be `None`;
- state MUST be `NOT_COMPUTABLE`;
- hold reasons MUST include `NOT_COMPUTABLE_ATTRIBUTION_HOLD` (plus specific reason as useful);
- `optimizer_consumable=false`;
- a daily/campaign period revenue MUST NOT appear as a cohort numerator masquerading as proof.

### 4. Compute cohort K5 only from explicit cohort evidence

When valid explicit cohort evidence exists:

- `K5_1D` uses D0 cohort revenue for D0 window / original acquisition spend;
- `K5_7D` uses revenue attributable to SAME cohort over D0..D0+6 / original acquisition spend;
- `K5_30D` uses revenue attributable to SAME cohort over D0..D0+29 / original acquisition spend;
- preserve explicit timezone basis;
- preserve late-arrival/maturity rules;
- preserve append-only derived versions;
- preserve non-MATCHED reconciliation blocking.

Never infer missing days or fill unknown revenue with zero.

### 5. Materializer API

Refactor `LedgerMaterializer.materialize()` so that:

- period inputs and cohort inputs are semantically distinct;
- campaign/day Metrica fact alone can produce period measurement but only held/not-computable cohort measurements;
- optional explicit cohort evidence can produce valid 1D/7D/30D measurements only for windows for which proof exists;
- materialization digest/version binds the explicit cohort evidence inputs when present;
- late cohort evidence creates a new derived version without rewriting prior output/raw history.

## Required tests

Add regression tests at minimum:

1. one daily Metrica campaign fact -> valid period K5, but 1D/7D/30D cohort measurements are NOT_COMPUTABLE without explicit cohort evidence;
2. same daily revenue is never copied into all cohort windows;
3. missing cohort evidence includes `NOT_COMPUTABLE_ATTRIBUTION_HOLD`;
4. explicit valid 1D evidence computes only K5_1D; 7D/30D remain held;
5. explicit valid 1D/7D/30D evidence computes each using its own attributed cohort numerator and the SAME original acquisition-spend denominator;
6. wrong `cohort_ref` -> hold;
7. incompatible currency/basis/timezone -> hold;
8. non-MATCHED reconciliation -> hold;
9. immature/late-arrival-open window -> hold;
10. late valid cohort evidence creates a new derived version without rewriting prior version;
11. period K5 behavior remains unchanged;
12. all existing public tests remain green.

## Private companion update

After public rework is committed/pushed and exact public CI is GREEN:

1. update private `PUBLIC_CONTRACT_VERSION.md` to the new exact public SHA;
2. update the private allocator's pinned public SHA constant/reference;
3. do NOT change private scoring/ranking policy unless compatibility requires it;
4. run private tests and CI;
5. private CI must be GREEN.

## Evidence

Update or add:

- public: `profit-engine/evidence/TASK-010-COHORT-MATERIALIZATION-REWORK.md`;
- private: append/record the new public contract pin in Task-010 private evidence or a bounded rework evidence file.

Evidence must state explicitly:

- campaign/day Metrica facts are period evidence, not automatic cohort evidence;
- no production cohort K5 is computable without explicit cohort linkage proof;
- fixtures are synthetic and do not prove live K5.

## Safety

Still forbidden:

- Direct/provider writes;
- budget mutation/spend;
- campaign/ad/group/keyword/image mutation;
- Tilda/site publication;
- paid Cloud apply;
- secrets/private provider IDs/raw production exports in Git;
- force push.

Provider requests: 0.
Advertising spend: 0.

## Acceptance

Task 010 remains REWORK until:

- public cohort truth gate is fixed;
- public final CI GREEN;
- private repo pins the new public SHA;
- private final CI GREEN;
- Central Brain verifies the code and closes both Task-010 issues.
