# TASK 016 — ADAPTIVE BASELINE CONTENT MAP

Status: READY FOR BOUNDED DEVELOPMENT
Execution package: `AF-1`
Executor: Codex development-only under Central Brain acceptance
Depends on: existing DILIVOX content registry; no production write dependency
May run before AF-0 live acceptance: YES

## Objective

Turn the current ~50-story DILIVOX catalog into a deterministic, validated content graph that a future rule-based Adaptive Funnel can safely use without inventing stories, series relations or runtime AI classifications.

## Inputs

Canonical content identity:
`profit-engine/sites/dilivox/content-registry.json`

Authority/plan:
- `profit-engine/PROFIT_ENGINE_AUTHORITY.md`;
- `profit-engine/ADAPTIVE_FUNNEL_EXECUTION_PROJECT.md`;
- `profit-engine/EKSAMIO_PATTERN_ADOPTION_FOR_ADAPTIVE_FUNNEL.md`.

## Required deliverables

1. Machine-readable adaptive metadata file for every active monetizable content ID.
2. Validator that fails closed on unknown/missing registry IDs.
3. Deterministic static/editorial recommendation graph.
4. Baseline aggregation contract for future behavior/money joins.
5. Missing/ambiguous metadata report.
6. Tests and CI gate.

## Minimum metadata

Per content item, where known/curated:
- `content_id`;
- canonical URL/route reference;
- content type/format;
- primary genre/cluster family;
- optional secondary cluster;
- length bucket;
- `series_id` or explicit standalone marker;
- series order when applicable;
- explicit `next_in_series_content_id` where applicable;
- editorial/static recommendation candidate IDs;
- active/adaptive-eligible flags;
- metadata version.

Do not infer a series relationship from title similarity at runtime.

## Validation invariants

- every adaptive metadata ID exists in content registry;
- every candidate/series-next ID exists and is active/eligible;
- no item recommends itself;
- no duplicate candidate IDs per item;
- no series cycle unless explicitly documented as intentional;
- no missing required metadata for adaptive-eligible items;
- unknown fields fail validation or are explicitly version-gated;
- deterministic sorting/output.

## Baseline metric contract

Define only fields needed for later aggregation, not live values:
- opens/eligible sessions;
- progress-75 count/rate;
- completion count/rate;
- recommendation shown/click/open counts;
- stories/session;
- return visits/rate where valid;
- attributable YAN revenue/RPV where provider join is valid;
- Direct spend/CPV/K5 where acquisition join is valid;
- sample/freshness/reconciliation state.

No browser/client code may authoritatively populate money fields.

## Out of scope

- production routing;
- Tilda publication;
- provider writes;
- AI/LLM tagging at request time;
- psychological reader profiling;
- new story generation;
- modifying `DILIVOX_SYSTEM_V1`.

## Acceptance criteria

1. 100% of active adaptive-eligible registry items are represented exactly once.
2. All references validate against the canonical registry.
3. Series links are explicit and deterministic.
4. A static recommendation graph can be produced with no AI and no network access.
5. Missing/ambiguous metadata is surfaced as a report, not silently guessed.
6. Unit/validation tests pass offline.
7. Existing site/runtime behavior is unchanged.
8. No provider/network write path is introduced.

Terminal state:
`ADAPTIVE_AF1_BASELINE_READY`.
