# PROFIT ENGINE — DAY 8 ACCEPTANCE MATRIX

Status: CANONICAL
Updated: 2026-08-27

## Purpose

Define objective acceptance gates for Day 8 Campaign Factory + Creative Factory. Day 8 is PREVIEW/DRY-RUN only and has zero authority to mutate Yandex Direct or spend money.

## A. CampaignSpec contract

PASS only if:
- provider-neutral `CampaignSpec` resolves `site_id`, landing `content_id`, provider, campaign key, objective, strategy request, budget proposal, geo/schedule, tracking plan, groups/creatives and evidence refs;
- `provider_write_allowed` is structurally false for all Day-8 outputs;
- no owner-specific scoring weights or learned commercial thresholds exist in public code;
- deterministic identical input produces identical spec digest.

FAIL if:
- any spec can carry executable Direct credentials or private provider IDs;
- any plan can bypass future Budget Governor;
- unresolved content/landing is silently accepted.

## B. Direct entity preview

PASS only if one CampaignSpec expands into an inert ordered dependency graph for:
- campaign;
- ad group(s);
- keyword/autotargeting entities where applicable;
- image asset upload intents;
- ad drafts;
- tracking parameters;
- moderation/validation readiness;
- rollback/delete intents.

Every planned provider mutation is data only. No live `add`, `update`, `delete`, `suspend`, `resume`, moderation submission or budget mutation may be reachable.

## C. Tracking compatibility

PASS only if generated destination tracking:
- stays within Task-005 acquisition allowlist;
- can carry approved Direct dynamic identifiers such as campaign/ad/group/click identity where supported;
- preserves stable Dilivox `content_id` relation outside arbitrary URL guessing;
- detects unsupported variables and collisions before preview can be marked ready;
- never includes arbitrary query values, PII, secrets or owner-private state.

## D. Creative Factory

PASS only if:
- creative templates and variants have stable IDs/versions;
- text fields validate required provider limits and required fields;
- destination/content source is traceable to Dilivox registry evidence;
- variants are versioned, not silently overwritten;
- invalid/rejected variants retain explicit rejection reasons;
- no ranking/winner-selection/profit score is implemented in the public factory.

## E. Asset registry

PASS only if each asset record includes:
- immutable asset ID;
- source reference;
- SHA-256;
- mime/type and dimensions;
- usage scope;
- provider compatibility result;
- version/replacement relation when transformed.

No Day-8 code may upload an asset. Any future provider upload is an inert intent only.

## F. Strategy modeling

Public-safe strategy enum may model CPC/click, conversion-click, pay-for-conversion, value/CRR and Maximum Profit where provider contracts allow.

PASS only if:
- Day 8 validates syntax/eligibility inputs;
- Day 8 does not choose the commercial winner;
- unknown/unsupported provider combinations fail closed;
- actual selection remains a later strategy/private-core responsibility.

## G. Budget safety

Every preview must contain:
- proposed amount/currency;
- evidence/baseline reference when available;
- `requires_budget_governor=true`;
- `provider_write_allowed=false`;
- owner-approval placeholder for future >20% rule.

PASS requires zero reachable provider budget mutation and zero spend.

## H. Preview artifact

A complete preview must expose:
- spec digest/version;
- entity counts and dependency order;
- normalized tracking plan;
- strategy request;
- proposed budget object;
- creative variants and asset refs;
- validation errors/warnings;
- unsupported features;
- inert future provider-call intents;
- rollback graph;
- `provider_requests=0`;
- `advertising_spend=0`.

## I. Safety scans/tests

Minimum acceptance matrix:
1. deterministic digest;
2. unresolved landing rejected;
3. tracking allowlist enforced;
4. unsupported provider field/subtype rejected;
5. invalid strategy combination rejected;
6. no Direct write method/RPC reachable;
7. no budget mutation reachable;
8. creative required/length checks;
9. duplicate entity/creative keys rejected;
10. asset hash/version stability;
11. public fixtures contain no secret/private mappings;
12. complete preview includes rollback intents and zero provider requests/spend;
13. all prior ledger/provider/site tests remain green;
14. Profit Engine CI must be green on the final Task-008 origin HEAD.

## J. Final Day-8 decision states

Allowed public Day-8 result states:
- `PREVIEW_VALID`;
- `PREVIEW_INVALID`;
- `BLOCKED_PROVIDER_CAPABILITY`;
- `BLOCKED_MISSING_CONTENT_ID`;
- `BLOCKED_TRACKING_CONTRACT`;
- `BLOCKED_BUDGET_GOVERNOR_REQUIRED`;
- `BLOCKED_PRIVATE_CORE_REQUIRED` for sensitive selection logic.

There is deliberately no `EXECUTED` state on Day 8.
