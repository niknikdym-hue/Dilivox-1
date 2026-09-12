# TASK 019 — ADAPTIVE PROFIT EVALUATION

Status: DESIGNED / REQUIRES TASK 018 EVIDENCE
Execution package: `AF-4`
Executor: Codex development-only for calculations/UI plumbing; Central Brain for economic acceptance
Depends on:
- Task 018 experiment evidence;
- reconciled Direct/Metrica/YAN money evidence;
- full incremental feature-cost ledger.

## Objective

Convert treatment/control Adaptive Funnel evidence into an auditable economic decision. This task determines whether the rule-based Adaptive Funnel is worth keeping, holding, killing or scaling.

## Required outputs

For compatible measurement windows, calculate at minimum:
- eligible sessions by arm;
- recommendation continuation rate by arm;
- stories/session by arm;
- completion by arm;
- return rate by arm where attribution is valid;
- YAN RPV/ARPU by arm where join is valid;
- attributable incremental revenue;
- full incremental feature cost;
- `feature_net_profit`;
- `FEATURE_ROI`;
- sample/freshness/reconciliation state;
- evidence caveats/holds;
- final bounded recommendation.

## Canonical formulas

`feature_net_profit = incremental_attributable_revenue - full_feature_cost`

`FEATURE_ROI = feature_net_profit / full_feature_cost`

Scale threshold:

`FEATURE_ROI >= 3.0`

Equivalent:

`incremental_attributable_revenue >= 4 x full_feature_cost`

## Feature-cost ledger

Include material incremental cost attributable to Adaptive Funnel, such as:
- serverless/runtime compute;
- storage/egress;
- additional third-party services;
- incremental operations/maintenance cost where material;
- amortized build cost where the project chooses to include it in the measurement window.

Do not include unrelated historical Profit Engine costs merely to make the feature look unprofitable.
Do not omit actual incremental recurring costs merely to make the feature look profitable.

## Evidence states

At minimum:
- `READY`;
- `INSUFFICIENT_SAMPLE`;
- `RECONCILIATION_HOLD`;
- `ATTRIBUTION_HOLD`;
- `STALE_DATA`;
- `COST_INCOMPLETE`;
- `NEGATIVE_DOWNSIDE_STOP`.

No scale recommendation may be emitted from a held state.

## Decision vocabulary

- `TEST` — continue bounded evidence collection;
- `KEEP` — useful but not authorized for broad scale yet;
- `HOLD` — evidence/data/cost problem blocks decision;
- `KILL` — feature should be disabled/reverted to static path;
- `SCALE_ALLOWED` — economic gate passed and no other blocking safety/compliance hold exists.

Rules:
- positive CTR alone cannot produce `SCALE_ALLOWED`;
- positive stories/session alone cannot produce `SCALE_ALLOWED`;
- unresolved money reconciliation forces `HOLD`;
- material economic downside may produce `KILL` before full target sample;
- `SCALE_ALLOWED` does not itself authorize a Direct budget increase or content wave; those have separate governance.

## Content-growth handoff

Task 019 must produce an explicit statement for the next catalog gate:
- `CONTENT_WAVE_50_TO_150_ALLOWED_FOR_TEST`;
- `CONTENT_WAVE_HOLD`;
- or `CONTENT_WAVE_REWORK_FIRST`.

This statement is advisory under the existing content-wave ROI rules; it is not permission to mass-produce 100 stories blindly.

## Owner Panel feed

Expose a bounded aggregate snapshot for the existing `Profit Engine.app` containing:
- treatment/control metrics;
- incremental revenue;
- feature cost;
- FEATURE_ROI;
- evidence state;
- decision;
- experiment/policy version;
- generated_at/freshness.

Panel rendering is Task 020. This task owns the economic truth object, not the UI.

## Out of scope

- changing Direct bids/budgets;
- AI routing;
- generating new content;
- provider writes;
- replacing the core Profit Engine money ledger.

## Acceptance criteria

1. Treatment/control windows are compatible and explicit.
2. Provider money remains authoritative.
3. Held/stale/unreconciled evidence cannot become optimistic scale truth.
4. Full incremental feature cost is present or state is `COST_INCOMPLETE`.
5. FEATURE_ROI calculation is deterministic and tested.
6. `SCALE_ALLOWED` requires FEATURE_ROI >= 3.0 and no blocking evidence state.
7. Severe downside can emit `KILL` safely.
8. Output snapshot is bounded/aggregate and contains no secrets/PII.
9. Tests/CI pass.

Terminal state:
`ADAPTIVE_AF4_SCALE_DECISION_READY`.
