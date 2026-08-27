# CODEX TASK 008 — CAMPAIGN FACTORY + CREATIVE FACTORY DRY-RUN FOUNDATION

Status: READY FOR EXECUTION
Owner: Central Brain
Executor: Codex
Repository: `niknikdym-hue/Dilivox-1`
Canonical branch: `profit-engine`
Launch day: Day 8

## READ FIRST — MANDATORY

1. `profit-engine/PROJECT_HANDOFF.md`
2. `profit-engine/OWNER_DECISIONS.md`
3. `profit-engine/PROJECT_STATE.md`
4. `profit-engine/HARD_12_DAY_LAUNCH_PLAN.md`
5. `profit-engine/DAY8_CAMPAIGN_FACTORY_DESIGN.md`
6. `profit-engine/DAY8_ACCEPTANCE_MATRIX.md`
7. `profit-engine/MACHINE_ADVERTISING_OPERATIONS.md`
8. `profit-engine/PRIVATE_CORE_BOUNDARY.md`
9. `profit-engine/evidence/TASK-007-CENTRAL-BRAIN-ACCEPTANCE.md`
10. `profit-engine/sites/dilivox/content-registry.json`

## BASELINE / SYNC

Accepted Task 007 code state:

`e5b21baa1622e77e5d1e9408f799a5843e51f2d4`

Central Brain verified it through permanent GitHub Actions CI on descendant `7bf092c63c4d04f71eb5d48192395845a110f206` and then advanced `origin/profit-engine` with Task-007 acceptance evidence and Day-8 canonical design.

Therefore:

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

Implement a deterministic, provider-neutral Campaign Factory + Creative Factory that can generate a complete Yandex Direct future-execution preview without making any provider request or spending money.

Canonical flow:

`CampaignSpec -> validation -> Creative/Asset specs -> inert Direct entity intents -> dependency graph -> tracking plan -> rollback graph -> immutable preview digest`.

Day 8 is PREVIEW/DRY-RUN only.

There is deliberately NO `EXECUTED` state.

## HARD SAFETY INVARIANTS

1. `provider_write_allowed=false` by construction on every Day-8 plan.
2. `requires_budget_governor=true` on every plan that contains budget intent.
3. `provider_requests=0` for every Task-008 execution and test.
4. `advertising_spend=0`.
5. No Direct token/credential is required by the factory.
6. No executable `add/update/delete/suspend/resume/moderate` provider path may exist.
7. No image upload occurs; AdImages are inert upload intents only.
8. No campaign/group/ad/keyword/budget mutation occurs.
9. No proprietary profit ranking/winner-selection/learned thresholds in this public repo.
10. Unknown/unsupported provider capability fails closed.

Any violation = Task 008 FAIL.

## CURRENT PROVIDER CONTRACT TO MODEL

Use current Yandex Direct API v5/v501 structure as inert capability metadata only.

Model the future lifecycle/dependency order for supported types using provider-safe contracts such as:

- Campaigns;
- AdGroups;
- Ads;
- Keywords/autotargeting where applicable;
- AdImages;
- unified performance campaign/group v501 capability where explicitly modeled.

Do NOT call these services in Task 008.

Campaign/group type compatibility must be validated before preview is valid.

## REQUIRED IMPLEMENTATION

### A. PROVIDER-NEUTRAL CAMPAIGN SPEC

Create a strict/versioned CampaignSpec model/schema.

Minimum fields:

- `spec_version`;
- `site_id`;
- `provider_id`;
- `campaign_key`;
- `campaign_type` / provider subtype request;
- `objective_kind`;
- `landing_content_id`;
- `strategy_kind`;
- `strategy_parameters`;
- `budget_request`;
- `geo`;
- `schedule`;
- `tracking_plan`;
- `goal_refs` / value-signal refs;
- `ad_groups`;
- `creative_refs`;
- optional `experiment_ref`;
- evidence/source refs;
- safety fields.

Required hard values:

- `provider_write_allowed=false`;
- `requires_budget_governor=true` where budget exists.

Unknown fields should be rejected or explicitly version-gated.

### B. LANDING / CONTENT VALIDATION

CampaignSpec must resolve `landing_content_id` against the canonical Dilivox content registry.

Preview is blocked if:

- content ID is missing;
- content ID is unknown/inactive for the requested launch surface;
- destination URL does not match the canonical/allowed registry entry;
- landing identity is inferred from arbitrary URL/title text rather than registry truth.

### C. TRACKING PLAN

Generate a deterministic URL-parameter plan compatible with the accepted Task-005 acquisition allowlist and Task-007 acquisition ledger.

Approved output parameter keys may include only the existing allowlist:

- `yclid` where provider behavior/capability supports it;
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
- `utm_term`.

Provider dynamic substitutions may model current supported Direct parameters such as `{campaign_id}`, `{ad_id}`, `{gbid}`, and compatible criterion/keyword/click identifiers only when capability metadata says they are supported.

Rules:

- no arbitrary query keys;
- no PII;
- no secrets/private mappings;
- collision detection required;
- unsupported dynamic variable -> `BLOCKED_TRACKING_CONTRACT`;
- generated tracking must be stable/deterministic for identical input.

Do not depend on campaign names for identity.

### D. STRATEGY REQUEST MODEL

Public-safe strategy enum/contract may represent:

- CPC/click-oriented;
- conversion-optimized with click payment;
- pay-for-conversion;
- value/CRR style;
- Maximum Profit where provider capability/eligibility supports it;
- future provider-native strategy placeholder.

Day 8 validates requested shape/required fields only.

Day 8 must NOT choose a winner or estimate private commercial ranking.

Unsupported/invalid combination -> `BLOCKED_PROVIDER_CAPABILITY` or `PREVIEW_INVALID`.

### E. BUDGET REQUEST

Budget is an inert proposal object only.

Minimum:

- amount as Decimal-compatible/string representation;
- currency;
- period/basis;
- baseline/evidence ref if known;
- `requires_budget_governor=true`;
- `provider_write_allowed=false`;
- future `owner_approval_required` placeholder.

No Task-008 code can mutate budget.

Do not implement the +20% calculation as commercial action logic here; Budget Governor owns enforcement on Day 11.

### F. CREATIVE FACTORY

Implement strict/versioned public-safe CreativeSpec/variant model.

Minimum:

- template ID/version;
- creative ID/variant ID;
- source `content_id`;
- title/headline;
- body/description where applicable;
- destination ref;
- optional display text fields as provider model requires;
- asset refs;
- provider format/subtype;
- validation state;
- rejection reasons;
- provenance.

Requirements:

- deterministic variant identity;
- no silent overwrite;
- invalid text/required fields rejected;
- provider limits represented as capability metadata, not scattered magic values;
- no owner-specific learned ranking/winner score.

Use synthetic fixture creative text only. Do NOT expose or add confidential commercial prompts/ranking logic.

### G. ASSET REGISTRY

Implement a generic asset registry/schema.

Each asset:

- immutable asset ID;
- source reference;
- related `content_id` where applicable;
- SHA-256;
- mime/type;
- dimensions;
- usage scope;
- provider compatibility state;
- version/replacement relation;
- transformation intent if needed.

No actual image upload or remote download in Task 008.

If a source asset would require transformation, record a versioned transformation intent; never silently mutate the source.

### H. INERT DIRECT ENTITY INTENTS

Expand valid CampaignSpec into ordered inert intents for:

1. future campaign creation;
2. future ad-group creation;
3. future keyword/autotargeting creation where applicable;
4. future image upload/association;
5. future ad creation;
6. tracking parameters;
7. moderation-readiness checks;
8. rollback/delete intents.

Intent records may name future provider service/method for audit/planning, but they MUST be plain data and MUST NOT be executable provider clients.

Every intent must carry:

- deterministic intent ID;
- dependency IDs;
- entity type;
- proposed operation name;
- sanitized parameters/refs;
- rollback intent ref where meaningful;
- `executable=false`.

### I. DEPENDENCY + ROLLBACK GRAPH

Preview must prove correct dependency ordering and future rollback intent coverage.

Examples:

- group depends on campaign;
- ad depends on group and referenced asset intent;
- keyword/autotargeting depends on compatible group;
- rollback is reverse dependency order.

No rollback intent may itself be executable in Day 8.

### J. IMMUTABLE PREVIEW DIGEST

Generate deterministic canonical JSON preview and SHA-256 digest.

Identical semantic input -> identical digest.

Material spec/creative/asset change -> changed digest.

Preview output includes at minimum:

- preview version;
- state;
- spec digest;
- entity/intent counts;
- dependency order;
- tracking plan;
- strategy request;
- budget proposal;
- creative variants;
- assets;
- warnings/errors;
- unsupported features;
- rollback graph;
- `provider_requests=0`;
- `advertising_spend=0`;
- `provider_write_allowed=false`.

### K. RESULT STATES

Only these Day-8 states are allowed:

- `PREVIEW_VALID`;
- `PREVIEW_INVALID`;
- `BLOCKED_PROVIDER_CAPABILITY`;
- `BLOCKED_MISSING_CONTENT_ID`;
- `BLOCKED_TRACKING_CONTRACT`;
- `BLOCKED_BUDGET_GOVERNOR_REQUIRED`;
- `BLOCKED_PRIVATE_CORE_REQUIRED`.

No `EXECUTED`, `LAUNCHED`, `SUBMITTED`, or equivalent state.

### L. CLI / FIXTURE MODE

Provide a local CLI or deterministic fixture entrypoint that builds at least:

1. one valid synthetic Dilivox/Yandex Direct preview;
2. one invalid missing-content preview;
3. one invalid tracking preview;
4. one invalid provider-capability/strategy preview.

No credentials required.

No provider requests.

## REQUIRED TESTS

At minimum prove:

1. deterministic CampaignSpec -> identical preview digest;
2. material spec change -> different digest;
3. unresolved landing rejected;
4. inactive/invalid landing rejected where applicable;
5. tracking contains only approved keys;
6. unsupported dynamic variable rejected;
7. tracking collisions rejected;
8. provider campaign/group subtype mismatch rejected;
9. invalid strategy combination rejected;
10. no executable provider write method/path exists;
11. no budget mutation path exists;
12. CreativeSpec required fields and provider-limit validation;
13. duplicate creative/entity keys rejected;
14. asset hash/version stability;
15. asset transformation is explicit/versioned;
16. dependency graph order correct;
17. rollback graph reverse/dependency-safe;
18. preview contains zero provider requests;
19. preview contains zero advertising spend;
20. no secrets/private mappings in public fixtures;
21. no proprietary scoring/ranking/winner-selection logic;
22. all prior Python/Node suites remain green;
23. final `Profit Engine CI` workflow is green on the Task-008 origin HEAD.

## LIVE PROVIDER RULE

Even if OAuth credentials become available during Task 008:

- provider doctor/read collectors may be run READ_ONLY separately;
- Campaign Factory remains dry-run;
- NO write provider request is authorized;
- NO image upload;
- NO moderation submission;
- NO budget change;
- NO spend.

## PUBLIC/PRIVATE CORE BOUNDARY

This public repo may contain deterministic public-safe factory/spec/validation/preview code.

Do NOT add:

- proprietary profit score/weights;
- learned creative ranking;
- owner-specific strategy winner selection;
- private campaign economics;
- confidential provider mappings;
- production model data.

If implementation requires such logic, return `BLOCKED_PRIVATE_CORE_REQUIRED` rather than placing it here.

## FORBIDDEN

- Direct provider writes of any kind;
- Campaigns.add/update/delete/suspend/resume/archive/unarchive calls;
- AdGroups.add/update/delete calls;
- Ads.add/update/delete/moderate/suspend/resume/archive/unarchive calls;
- Keywords add/update/delete/suspend/resume calls;
- AdImages add/delete calls;
- budget mutation;
- advertising spend;
- Tilda publication / production Dilivox mutation;
- YAN provider-code mutation;
- paid Cloud apply;
- secrets/private IDs/raw production exports in Git;
- proprietary optimizer/scoring/ranking logic;
- force push;
- merge into `main`.

## EVIDENCE

Create:

`profit-engine/evidence/TASK-008-CAMPAIGN-CREATIVE-FACTORY.md`

Evidence must include:

- baseline/final/origin SHAs;
- CampaignSpec summary;
- CreativeSpec summary;
- asset registry summary;
- provider capability model;
- tracking plan and allowlist proof;
- strategy request model;
- budget safety proof;
- valid fixture preview digest/counts;
- invalid fixture states;
- dependency/rollback graph proof;
- explicit `provider_requests=0`;
- explicit `advertising_spend=0`;
- explicit `provider_write_allowed=false`;
- tests/checks/CI result;
- files changed;
- blockers;
- recommended Task 009 boundary.

## FINAL REPORT FORMAT

Return:

- `STATUS: COMPLETE | PARTIAL | BLOCKED`
- `BASELINE_HEAD:`
- `FINAL_HEAD:`
- `ORIGIN_PROFIT_ENGINE:`
- `WORKTREE:`
- `CAMPAIGN_SPEC:`
- `CREATIVE_FACTORY:`
- `ASSET_REGISTRY:`
- `PROVIDER_CAPABILITY_MODEL:`
- `TRACKING_PLAN:`
- `STRATEGY_MODEL:`
- `BUDGET_SAFETY:`
- `VALID_PREVIEW:`
- `INVALID_PREVIEWS:`
- `DEPENDENCY_ROLLBACK:`
- `PROVIDER_REQUESTS:`
- `ADVERTISING_SPEND:`
- `PROVIDER_WRITE_ALLOWED:`
- `SECRET_SAFETY:`
- `FILES_CHANGED:`
- `COMMIT_SHA:`
- `TESTS/CHECKS:`
- `BLOCKERS:`
- `RECOMMENDED_TASK_009:`

Do not self-accept. Central Brain will inspect origin/evidence/CI and immediately advance the launch plan.
