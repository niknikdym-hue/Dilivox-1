# PROFIT ENGINE — DAY 9 ACQUISITION STRATEGY LAB DESIGN

Status: CANONICAL EXECUTION DESIGN
Updated: 2026-08-28
Site: `dilivox`

## Purpose

Day 9 creates the public-safe experiment/strategy contract between accepted money evidence and later private decision logic.

Canonical boundary:

`accepted money facts -> StrategyCell evidence -> bounded ExperimentPreview -> private decision boundary -> future action proposal`

Day 9 does NOT choose a commercial winner in the public repository and does NOT execute Direct writes.

## Hard invariants

1. Only evidence with explicit source/reconciliation/attribution state may enter the lab.
2. Held, immature, unjoinable, unreconciled or otherwise non-consumable money may not become strategy evidence.
3. Strategy cells are not ranked in public code.
4. No learned weights, private thresholds, owner-specific scoring or capital allocation heuristics in `Dilivox-1`.
5. Any request to rank/select/win/allocate returns `BLOCKED_PRIVATE_CORE_REQUIRED` until private core is available.
6. Campaign/Creative Factory outputs remain inert preview inputs only.
7. `provider_write_allowed=false`, `provider_requests=0`, `advertising_spend=0` throughout Day 9.
8. A proxy conversion is not treated as value evidence until its relationship to reconciled money is explicitly supported.

## StrategyCell v1

Each cell is a deterministic experiment identity, not a score.

Minimum fields:

- `cell_version`;
- `site_id`;
- `cell_key`;
- `campaign_spec_digest`;
- `strategy_kind`;
- `landing_content_id`;
- optional public-safe dimensions: device class, geo class, schedule class, audience/query class;
- `measurement_kind` (`period_K5`, `K5_1D`, `K5_7D`, `K5_30D`, or approved diagnostic only);
- money evidence references;
- attribution grade;
- reconciliation state;
- source state;
- cohort-link state where required;
- maturity state;
- proxy goal reference/state where applicable;
- experiment eligibility state;
- immutable digest.

No private provider IDs or owner-private mappings in public fixtures.

## Supported acquisition strategy requests

Public contract may represent:

- `cpc`;
- `conversion_click`;
- `pay_for_conversion`;
- `value_crr`;
- `maximum_profit`;
- future provider-native strategy keys through versioned capability metadata.

Day 9 validates compatibility and evidence readiness only. It does not rank strategies.

## Money evidence eligibility

For cohort measurements, cohort linkage must be proven by an accepted acquisition grade/state.

Public-safe default gates:

- `A_STRONG_DIRECT_CROSSCHECK`: eligible if measurement itself is optimizer-consumable;
- `B_DIRECT_ID`: eligible if measurement itself is optimizer-consumable;
- `D_UTM_PRIVATE_MAP`: eligible only through injected private mapping evidence and if measurement itself is optimizer-consumable;
- `C_METRICA_DIRECT`: period diagnostics may be eligible, but must not masquerade as proven acquisition-cohort evidence;
- `E_SOURCE_ONLY`: not eligible for autonomous strategy evidence;
- `UNJOINABLE`: held.

Any `PENDING`, `DRIFT`, `BASIS_BLOCKED`, `SOURCE_MISSING`, `NOT_COMPUTABLE`, late-arrival hold, data-quality hold, missing provenance, or `optimizer_consumable=false` input -> cell held.

## ExperimentPreview v1

A public-safe experiment preview may compare named cells without choosing a winner.

Minimum fields:

- experiment key/version;
- control cell ref;
- treatment cell refs;
- hypothesis label;
- primary measurement kind;
- observation window;
- maturity/late-arrival requirements;
- minimum evidence requirements expressed as generic contract, not private learned thresholds;
- budget proposal refs (still inert and Budget-Governor-gated);
- campaign preview refs;
- guardrails;
- holdout/control declaration;
- start prerequisites;
- stop prerequisites;
- result state;
- immutable preview digest;
- `provider_write_allowed=false`;
- `provider_requests=0`;
- `advertising_spend=0`.

The preview does not launch an experiment.

## Proxy conversion contract

Proxy signals such as completion, next-story click, deep session or return may be referenced only with an explicit proxy state:

- `PROXY_UNPROVEN`;
- `PROXY_EVIDENCE_PENDING`;
- `PROXY_MONEY_ASSOCIATION_SUPPORTED`;
- `PROXY_REJECTED`.

Public code may validate that evidence references exist. It must not fabricate a monetary value or private learned weight.

A proxy cannot make a cell autonomous-strategy-eligible while its state is unproven/pending/rejected.

## Public result states

Allowed Day-9 public states:

- `CELL_ELIGIBLE_FOR_EXPERIMENT_PREVIEW`;
- `CELL_HELD_DATA_QUALITY`;
- `CELL_HELD_ATTRIBUTION`;
- `CELL_HELD_MATURITY`;
- `CELL_BLOCKED_MONEY_EVIDENCE`;
- `CELL_BLOCKED_PROVIDER_CAPABILITY`;
- `EXPERIMENT_PREVIEW_VALID`;
- `EXPERIMENT_PREVIEW_INVALID`;
- `BLOCKED_PRIVATE_CORE_REQUIRED`.

There is no public `WINNER`, `SCALE_SELECTED`, `ALLOCATED`, `EXECUTED` or equivalent Day-9 state.

## Private decision boundary

Canonical future interface direction:

`PublicStrategyEvidencePackage -> private profit-engine-core -> PublicActionProposal`

The public evidence package may include only versioned, non-secret measurement/experiment contracts.

Private core will own:

- ranking;
- expected-value/profit scoring;
- learned thresholds;
- strategy winner selection;
- capital allocation recommendations;
- sensitive creative/landing ranking.

Private core still cannot bypass Budget Governor or write directly to providers.

## Required fixture matrix

At minimum prove:

1. A-grade reconciled mature K5 -> cell eligible;
2. B-grade reconciled mature K5 -> cell eligible;
3. C-grade cannot become proven cohort evidence;
4. E/UNJOINABLE -> held;
5. reconciliation DRIFT/PENDING/BASIS_BLOCKED/SOURCE_MISSING -> held;
6. late/immature cohort -> held;
7. `optimizer_consumable=false` upstream -> held;
8. missing provenance -> held;
9. supported strategy + valid CampaignPreview -> experiment preview valid;
10. unsupported strategy -> provider capability block;
11. unproven proxy -> cannot unlock cell;
12. supported proxy evidence can be referenced without assigning a private monetary weight;
13. experiment preview has explicit control/holdout and maturity requirements;
14. no public ranking/winner/allocate path;
15. sensitive decision request -> `BLOCKED_PRIVATE_CORE_REQUIRED`;
16. identical input -> deterministic cell/experiment digest;
17. provider requests/spend/write permission remain zero/false;
18. all prior Profit Engine tests remain green.

## Parallel live-data rule

Provider OAuth remains an external blocker until credentials are securely installed. Fixture/source-contract engineering continues.

When live reads are eventually available, Strategy Lab must consume only accepted ledger measurements with their actual source/reconciliation/maturity states. It may never upgrade evidence quality itself.

## Day 9 success

Day 9 public scope succeeds when the system can truthfully answer:

`which acquisition strategy cells are sufficiently evidenced to enter a bounded experiment preview, which are held and why, and what evidence package would be sent to the private decision core?`

It must NOT answer `which cell wins?` inside the public repository.
