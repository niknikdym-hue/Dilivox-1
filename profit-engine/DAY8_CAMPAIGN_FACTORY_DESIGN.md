# PROFIT ENGINE — DAY 8 CAMPAIGN FACTORY / CREATIVE FACTORY DESIGN

Status: CANONICAL EXECUTION DESIGN
Updated: 2026-08-27

## Purpose

Build the public-safe, non-spending foundation for machine-operated advertising.

Day 8 is intentionally PREVIEW/DRY-RUN only. It does not authorize Direct Editing, provider writes, campaign creation, moderation submission, budget changes or spend.

## Current Direct provider model

The current Yandex Direct API v5/v501 provider model exposes distinct lifecycle services for:

- Campaigns;
- AdGroups;
- Ads;
- Keywords / autotargeting entities where supported;
- AdImages;
- Unified performance campaign/group contracts through v501.

Tracking plans can use supported Direct dynamic URL parameters such as campaign/ad/group/click identifiers. Actual compatibility must be validated against the selected campaign/entity subtype before any future write gate.

## Public-safe CampaignSpec v1

Provider-neutral model must include at minimum:

- `spec_version`;
- `site_id`;
- `provider_id`;
- `campaign_key`;
- `objective_kind`;
- `landing_content_id`;
- `strategy_kind`;
- `strategy_parameters` with no owner-secret optimizer weights;
- `budget_request` as a proposed bounded amount, never executable permission;
- `geo`;
- `schedule`;
- `tracking_template`;
- `goals` / value-signal references;
- `ad_groups`;
- `creative_refs`;
- `experiment_ref` where applicable;
- source/evidence references;
- `safety_state`;
- `provider_write_allowed=false` by construction for Day 8.

## Entity preview plan

A dry-run plan expands one provider-neutral spec into an ordered inert dependency graph:

1. campaign draft;
2. group draft(s);
3. keyword/autotargeting draft(s) where applicable;
4. creative/image asset upload intents;
5. ad draft(s);
6. tracking parameters;
7. validation/moderation-readiness checks;
8. provider dependency graph;
9. rollback/delete intents for objects that could later be created;
10. immutable preview digest/version.

No executable provider `add/update/delete/suspend/resume` method may exist in the Day-8 public implementation.

## Tracking invariant

Tracking must be compatible with the accepted acquisition ledger and Task-005 attribution allowlist.

Dry-run generator should model supported identifiers such as:

- campaign ID substitution variable;
- ad ID;
- group ID where supported;
- phrase/criterion identity where supported;
- `yclid`;
- `utm_source`;
- `utm_medium`;
- `utm_campaign`;
- `utm_content`;
- `utm_term`.

Generated tracking must remain inside the approved attribution allowlist. No arbitrary user/query data is introduced.

Preview must detect collisions, unsupported variables and missing landing `content_id` before a plan can become valid.

## Campaign strategy abstraction

Day 8 models strategy requests; it does not choose commercial winners.

Public-safe strategy contract may represent:

- click/CPC-oriented strategy;
- conversion-optimized click payment;
- pay-for-conversion;
- CRR/value-style strategy;
- Maximum Profit where supported/eligible;
- provider-native future strategies.

Commercial selection, weights and learned thresholds belong to later private-core/AcquisitionStrategyLab gates.

## Budget safety

Day 8 has no financial authority.

Every plan must carry:

- proposed budget;
- currency;
- source/evidence reference;
- current baseline reference if known;
- `requires_budget_governor=true`;
- `provider_write_allowed=false`;
- owner-approval placeholder for future >20% weekly growth rule.

No provider request may mutate budget during Day 8.

## Creative Factory public-safe layer

Creative Factory foundation may contain:

- creative template IDs/versions;
- title/body/link/source asset inputs;
- content-registry references;
- image asset references/hashes/dimensions;
- provider-format validation;
- policy/quality checks;
- variant identity/versioning;
- deterministic plan generation;
- preview-render metadata;
- rejected-reason list.

It must NOT contain owner-specific learned ranking weights, commercial winner-selection logic or private campaign economics.

## Images/assets

Day-8 preview may model AdImages upload intents but MUST NOT upload anything.

Asset registry must track:

- immutable asset ID;
- source reference;
- content/story relation;
- SHA-256;
- dimensions/mime/type;
- approved usage scope;
- provider compatibility result;
- replacement/version relation.

No source image is silently mutated to satisfy provider requirements. Any transformation intent is explicit and separately versioned.

## Validation gates

A plan cannot be `PREVIEW_VALID` unless it passes generic validation:

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
- no secret/private identifier embedded in public fixtures;
- budget object present but not executable;
- no provider write API invoked.

## Preview evidence

Dry-run emits a machine-readable preview containing:

- spec digest/version;
- generated entity counts;
- dependency order;
- normalized tracking plan;
- proposed strategy;
- proposed budget object;
- creative variants;
- asset refs;
- validation warnings/errors;
- unsupported provider features;
- future provider-call intents represented only as inert data;
- rollback intent graph;
- `provider_requests=0`;
- `advertising_spend=0`.

## Required tests

1. deterministic CampaignSpec -> same preview digest;
2. landing `content_id` must resolve;
3. tracking output uses only approved parameters;
4. unsupported subtype/field rejected;
5. invalid strategy combination rejected;
6. no write HTTP/RPC method reachable;
7. no budget mutation reachable;
8. CreativeSpec length/required-field validation;
9. duplicate creative/entity identities rejected;
10. image asset hash/version stable;
11. no secret/private mapping in public fixtures;
12. complete preview includes rollback intents and zero provider requests/spend;
13. all prior ledger/provider/site tests remain green.

## Relationship to later gates

- Day 8: spec/factory/dry-run only;
- Day 9: AcquisitionStrategyLab compares strategy cells using money evidence; sensitive selection logic requires private core;
- Day 10: ProfitAllocator/stop-loss may propose bounded actions;
- Day 11: only Budget Governor + guarded Direct Controller can convert accepted intents into actual write calls.

Campaign Factory must never become a bypass around financial governance.
