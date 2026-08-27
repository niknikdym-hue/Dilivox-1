# PROFIT ENGINE — DAY 8 CAMPAIGN FACTORY / CREATIVE FACTORY PREWORK

Status: CENTRAL BRAIN PREWORK / NOT YET CANONICAL
Updated: 2026-08-27
Branch: `central-brain/day8-campaign-prework`

## Purpose

Prepare the public-safe, non-spending foundation for machine-operated advertising before Codex reaches Day 8.

This design is intentionally PREVIEW/DRY-RUN only. It does not authorize Direct Editing, provider writes, campaign creation, moderation submission, budget changes or spend.

## Current Direct provider model verified for design

Current Yandex Direct API v5/v501 supports distinct lifecycle services for:

- Campaigns: add/update/get/suspend/resume/etc.;
- AdGroups: add/update/get/delete;
- Ads: add/update/get/suspend/resume/etc.;
- Keywords: add/update/get/delete, including autotargeting entities where supported;
- AdImages: add/get/delete;
- Unified performance campaigns/groups through the v501 endpoint contract.

Tracking plans can use Direct dynamic URL parameters such as campaign/ad/group/click identifiers. Actual provider compatibility must still be validated against the selected entity/campaign subtype at execution time.

## Public-safe CampaignSpec v1

Provider-neutral model should include at minimum:

- `spec_version`;
- `site_id`;
- `provider_id`;
- `campaign_key`;
- `objective_kind`;
- `landing_content_id`;
- `strategy_kind`;
- `strategy_parameters` with no owner-secret optimizer weights;
- `budget_request` as proposed bounded amount, not executable permission;
- `geo`;
- `schedule`;
- `tracking_template`;
- `goals` / value signal references;
- `ad_groups`;
- `creative_refs`;
- `experiment_ref` where applicable;
- `source/evidence refs`;
- `safety_state`;
- `provider_write_allowed=false` by construction for Day 8.

## Entity plan

A dry-run plan should expand one provider-neutral spec into ordered provider entities/actions:

1. campaign draft;
2. group draft(s);
3. keyword/autotargeting draft(s) where applicable;
4. creative/image asset upload intents;
5. ad draft(s);
6. tracking parameters;
7. validation/moderation readiness checks;
8. provider dependency graph;
9. rollback/delete plan for objects that could later be created;
10. immutable preview digest/version.

No `execute()`/write method may exist in the Day-8 public implementation.

## Tracking invariant

Tracking must be compatible with the accepted Day-7 acquisition ledger.

Dry-run generator should prefer explicit machine-readable identifiers such as:

- campaign ID substitution variable;
- ad ID;
- group ID where supported;
- phrase/criterion identity where supported;
- `yclid`;
- UTM source/medium/campaign/content/term.

The generated URL/query plan MUST remain inside the Task-005 approved attribution allowlist. No arbitrary user/query data is introduced.

The preview must detect collisions, unsupported variables and missing landing `content_id` before any future provider write.

## Campaign strategy abstraction

Day 8 only models strategy requests; it does not select commercial winners.

Public-safe enum/contract may represent:

- click / CPC-oriented strategy;
- conversion-optimized click payment;
- pay-for-conversion;
- CRR/value style strategy;
- Maximum Profit where supported/eligible;
- provider-native future strategies.

Commercial selection/weights belong to later private-core logic and AcquisitionStrategyLab gates.

## Budget safety

Day 8 has no financial authority.

Every plan must carry:

- proposed budget;
- currency;
- source/evidence;
- current baseline reference if known;
- `requires_budget_governor=true`;
- `provider_write_allowed=false`;
- `owner_approval_required` placeholder for future >20% rule.

No provider request may mutate budget during Day 8.

## Creative Factory public-safe layer

Creative Factory foundation may contain:

- creative template IDs/versions;
- title/body/link/source asset inputs;
- content registry references;
- image asset references/hashes/dimensions;
- provider-format validation;
- policy/quality checks;
- variant identity/versioning;
- deterministic plan generation;
- preview render metadata;
- rejected-reason list.

It must NOT contain owner-specific learned ranking weights, commercial winner-selection logic or private campaign economics.

## Images/assets

Day-8 preview can model AdImages upload intents but MUST NOT upload anything.

Asset registry should track:

- immutable asset ID;
- source reference;
- content/story relation;
- SHA-256;
- dimensions/mime/type;
- approved usage scope;
- provider compatibility result;
- replacement/version relation.

No source image should be silently mutated to satisfy provider requirements. Transform intent must be explicit and separately versioned.

## Validation gates

A plan cannot be `READY_FOR_GUARDED_WRITE_GATE` unless it passes generic validation:

- site/content identity resolves;
- destination URL is canonical/allowed;
- attribution/tracking stays inside allowlist;
- campaign/group/ad subtype consistency;
- supported strategy parameters only;
- region/schedule syntactically valid;
- no unsupported provider field;
- no duplicate deterministic entity keys;
- creative text length/required-field checks;
- asset compatibility checks;
- no secret/private identifier embedded in public plan fixture;
- budget object present but not executable;
- no provider write API invoked.

## Preview evidence

Dry-run should emit a complete machine-readable preview with:

- spec digest;
- generated entity counts;
- dependency order;
- normalized tracking string;
- proposed strategy;
- proposed budget object;
- creative variants;
- validation warnings/errors;
- unsupported provider features;
- future write calls that WOULD be needed, represented only as inert intents;
- rollback intent graph;
- `provider_requests=0`;
- `advertising_spend=0`.

## Required tests for eventual Task 008

1. deterministic CampaignSpec -> same preview digest;
2. landing `content_id` must resolve;
3. tracking output uses only approved parameters;
4. unsupported subtype/field rejected;
5. strategy-specific invalid combinations rejected;
6. no write HTTP/RPC methods reachable;
7. no budget mutation reachable;
8. CreativeSpec length/required-field validation;
9. duplicate creative/entity identities rejected;
10. image asset hash/version stable;
11. no secret/private mapping in public fixtures;
12. complete preview contains rollback intents and zero provider requests;
13. existing read/ledger/site tests stay green.

## Relationship to later gates

- Day 8: spec/factory/dry-run only.
- Day 9: AcquisitionStrategyLab compares strategy cells using money evidence; sensitive selection logic must respect private-core boundary.
- Day 10: ProfitAllocator/stop-loss may propose bounded actions.
- Day 11: only Budget Governor + guarded Direct Controller can convert accepted intents into actual write calls.

This prevents Campaign Factory from becoming a hidden bypass around financial governance.
