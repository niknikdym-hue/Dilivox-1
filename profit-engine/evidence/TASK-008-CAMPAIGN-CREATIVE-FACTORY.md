# TASK 008 — Campaign + Creative Factory dry-run

## Status and repository

- Engineering status: `COMPLETE`; acceptance remains with Central Brain.
- Baseline: `3ee086a3a7e12c1d28a238768c527ff320a32520`.
- Implementation SHA: `0edc97eb62208a602dbf4c2596fcc8f49be73ded`.
- Evidence-publication/final origin SHA: reported in the final Task-008 report because a commit cannot contain its own SHA.
- Branch: `profit-engine`.
- Workspace: `/Users/elenadymova/Documents/New project/Profit Engine/Dilivox-1`.
- Separate Dilivox/Tilda workspace was not modified.

## CampaignSpec

`CampaignSpec` v1 is a frozen strict-constructor, provider-neutral model containing site/provider identity, stable campaign key, provider subtype, objective, canonical `landing_content_id`, destination, strategy request, inert budget proposal, geo/schedule, tracking, goals, groups, creative references, experiment/evidence references, and safety fields.

Landing identity resolves only through `sites/dilivox/content-registry.json`. Missing, inactive, or non-canonical destinations fail closed as `BLOCKED_MISSING_CONTENT_ID`. `provider_write_allowed` cannot become true in a valid Day-8 preview.

## Creative Factory

`CreativeSpec` carries template and variant versions, deterministic identity, stable `content_id`, synthetic headline/body, destination, provider format, asset refs, provenance, validation state, and rejection reasons. Required fields and format-specific limits come from capability metadata. Duplicate creative/variant identities and silent overwrites are rejected. There is no learned ranking or winner selection.

## Asset registry

`AssetSpec` records immutable ID, source/content references, SHA-256, MIME type, dimensions, usage scope, provider compatibility, version/replacement relation, and optional versioned transformation intent. Same-content replay is idempotent; conflicting identity, unknown replacement, invalid metadata, unversioned transformation, and incompatible state are rejected. No download, transformation, or image upload occurs.

## Provider capability model

Versioned `direct-v5-v501-preview-1` metadata models compatible text and unified-performance campaign/group shapes, public-safe strategy eligibility, creative limits, supported tracking substitutions, and future service names. It is inert metadata: the module imports no HTTP transport, accepts no credentials, and exposes no executable provider mutation functions. Unknown combinations fail closed.

## Tracking plan and allowlist proof

The output allowlist exactly follows accepted acquisition identity keys: `yclid`, `campaign_id`, `ad_id`, `group_id`, `criterion_id`, `phrase_id`, `keyword_id`, and the five standard UTM fields. The valid fixture uses supported Direct substitutions plus synthetic UTM values. Arbitrary keys, unsupported dynamic substitutions, and collisions yield `BLOCKED_TRACKING_CONTRACT`. Campaign names are not provider identity.

## Strategy model

Capability metadata represents CPC, conversion-click, pay-for-conversion, value/CRR, and Maximum Profit where campaign eligibility permits. Day 8 validates request shape and goal requirements only; it performs no commercial comparison or selection. Unsupported combinations return `BLOCKED_PROVIDER_CAPABILITY`.

## Budget safety

The synthetic budget is a Decimal-compatible string proposal with currency, period, basis, evidence/baseline reference, `requires_budget_governor=true`, `owner_approval_required=true`, and `provider_write_allowed=false`. Missing governor enforcement returns `BLOCKED_BUDGET_GOVERNOR_REQUIRED`. There is no budget mutation path.

## Valid fixture preview

- State: `PREVIEW_VALID`.
- Preview digest: `448a3120d1e1f2ea94969aff5d0c67659e9943f915b4925044cf730d8c9fef51`.
- Inert intents: 13 total — campaign 1, ad group 1, targeting 1, asset 1, ad 1, tracking 1, readiness 1, rollback 6.
- Rollback graph: 6 real inert rollback intent records in reverse dependency order.
- Every intent: `executable=false`.
- `provider_requests=0`.
- `advertising_spend=0`.
- `provider_write_allowed=false`.

Identical semantic input produces the same digest; a material geo change produces a different digest.

## Invalid fixture states

| Fixture | State | Evidence |
|---|---|---|
| missing content | `BLOCKED_MISSING_CONTENT_ID` | unknown registry ID and mismatched content refs |
| invalid tracking | `BLOCKED_TRACKING_CONTRACT` | non-allowlisted key and unsupported substitution |
| invalid capability | `BLOCKED_PROVIDER_CAPABILITY` | incompatible Maximum Profit request and missing goal |

Additional tests cover inactive/non-canonical landing, tracking collisions, campaign/group mismatch, invalid strategy parameters, missing Budget Governor, invalid creatives, duplicate identities, and asset conflicts.

## Dependency and rollback graph

Forward order is campaign → group → targeting/asset → ad → tracking → readiness. Every dependency appears earlier in canonical order. Rollback records follow readiness and are chained in reverse forward-dependency order. They contain only target references and `future_rollback` audit metadata; all are non-executable.

## Safety invariants

- `provider_requests=0` for all fixture results.
- `advertising_spend=0` for all fixture results.
- `provider_write_allowed=false` for all preview artifacts.
- All planned mutations/uploads are inert data with `executable=false`.
- No token, provider request, image upload, moderation submission, budget change, production site change, or advertising launch occurred.
- The result enum contains only the seven canonical Task-008 states.

## Tests and checks

- Python: `72/72 PASS`, including 12 Task-008 tests and all prior suites.
- Node: `22/22 PASS`.
- CLI valid and three invalid fixture scenarios: PASS.
- `git diff --check`, secret/private-data scan, provider-write reachability scan, and proprietary-logic scan: required before commit and recorded in final report.
- GitHub Actions `Profit Engine CI` run `33146171153` on implementation SHA `0edc97eb62208a602dbf4c2596fcc8f49be73ded`: `GREEN` ([run](https://github.com/niknikdym-hue/Dilivox-1/actions/runs/33146171153)).
- The evidence-publication commit must independently finish GREEN before the final report.

## Files changed

- `profit-engine/runtime/profit_engine_runtime/campaign_factory.py`
- `profit-engine/runtime/profit_engine_runtime/campaign_factory_cli.py`
- `profit-engine/runtime/tests/test_campaign_factory.py`
- `profit-engine/runtime/README.md`
- `profit-engine/evidence/TASK-008-CAMPAIGN-CREATIVE-FACTORY.md`

The unrelated untracked `profit-engine/evidence/TASK-001-M0-INVENTORY 2.md` remains untouched and excluded.

## Blockers

- No Task-008 engineering blocker.
- Live provider credentials remain an external read-certification blocker and are irrelevant to this credential-free dry-run.
- Sensitive Day-9 strategy selection requires the private-core repository boundary before implementation.

## Recommended Task 009 boundary

Define public-safe strategy-cell and experiment contracts over reconciled money evidence while returning `BLOCKED_PRIVATE_CORE_REQUIRED` for learned weights, commercial ranking, or winner selection. Keep Direct operations inert; do not introduce provider writes before Budget Governor and guarded-controller gates.
