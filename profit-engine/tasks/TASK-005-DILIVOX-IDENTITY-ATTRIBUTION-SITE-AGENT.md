# CODEX TASK 005 — DILIVOX IDENTITY + ATTRIBUTION + SITE AGENT FOUNDATION

Status: READY FOR EXECUTION
Owner: Central Brain
Executor: Codex
Repository: `niknikdym-hue/Dilivox-1`
Canonical branch: `profit-engine`
Launch day: Day 5
Accepted Task 004 implementation HEAD: `8e7bb96450e6d878b513f47649929c27a868ea4b`

## ROLE

You are the engineering executor for DILIVOX PROFIT ENGINE.

Central Brain owns product/economic authority and acceptance. Do not invent or change Owner economics, budget authority, provider policy, or private-core boundaries.

## WORKSPACES

Canonical Profit Engine workspace:

`~/Documents/New project/Profit Engine/Dilivox-1`

Separate existing Dilivox/Tilda workspace:

`~/Documents/New project/Dilivox`

Task 005 MAY inspect the separate Dilivox workspace to map the real current Tilda/T123 implementation, but MUST NOT publish to Tilda or modify production. Prefer implementing canonical reusable artifacts in the Profit Engine repository. If a local integration patch against the separate site workspace is useful for validation, keep it reversible/unpublished and mirror the canonical source/patch in the Profit Engine repository evidence.

## READ FIRST — MANDATORY

1. `profit-engine/PROJECT_HANDOFF.md`
2. `profit-engine/OWNER_DECISIONS.md`
3. `profit-engine/PROJECT_STATE.md`
4. `profit-engine/HARD_12_DAY_LAUNCH_PLAN.md`
5. `profit-engine/GOVERNANCE_AND_EXECUTION.md`
6. `profit-engine/DILIVOX_SITE_INTEGRATION.md`
7. `profit-engine/PRIVATE_CORE_BOUNDARY.md`
8. `profit-engine/sites/dilivox/SITE_STATE.md`
9. `profit-engine/evidence/TASK-001-M0-INVENTORY.md`
10. `profit-engine/evidence/TASK-004-READ-ONLY-INGESTION.md`

Before editing:

- `git fetch origin`;
- fast-forward safely to current `origin/profit-engine`;
- verify accepted Task 004 commit is an ancestor;
- no force push;
- preserve unrelated local/untracked work.

## OBJECTIVE

Implement the Day-5 Dilivox identity/attribution foundation so Profit Engine can attach paid acquisition, content identity, monetization placements and future first-party events to one stable site-side context.

Required closed context:

`acquisition -> stable landing content_id -> internal navigation -> stable content_id -> experiment identity -> monetization placement identity -> future event context`

Task 005 does NOT publish production changes and does NOT send first-party events over the network yet. Day 6 owns full event wiring/delivery.

## A. STABLE CONTENT IDENTITY REGISTRY

Create a canonical Dilivox content registry under `profit-engine/sites/dilivox/`.

The registry must cover all currently discoverable active Dilivox content/page routes needed for launch, using the current repository and the separate site workspace as evidence.

At minimum represent:

- home;
- catalog/stories page;
- current story/comic pages discoverable from source/routes;
- any other monetizable page type currently part of the acquisition/content flow.

Required fields per content item:

- `site_id` = `dilivox`;
- immutable opaque `content_id`;
- current canonical URL;
- current/legacy slug where available;
- content/page type;
- category/genre where available;
- active state;
- experiment eligibility;
- monetization eligibility;
- source/version metadata.

Hard identity rule:

`content_id` is assigned once and persisted in the registry. It MUST NOT be recomputed at runtime from title, URL or slug. URL/title/slug changes later must preserve the same `content_id` through registry updates.

Provide tooling/tests that refuse duplicate IDs and duplicate active canonical URLs, and that preserve an existing ID when mutable metadata changes.

## B. GENERIC SITE AGENT CONTRACT + DILIVOX ADAPTER

Implement a reusable browser-side `SiteAgent` contract and first adapter `DilivoxSiteAgent`.

Keep generic behavior outside Dilivox-specific mapping.

The site agent must expose a stable read API equivalent to:

- current `site_id`;
- deployment/schema version;
- current stable content identity;
- page/content type;
- acquisition attribution state/reference;
- pseudonymous session context where enabled;
- experiment/variant identity hooks;
- relevant monetization placement identities;
- event-context builder for Day 6;
- health/fail-safe state.

The adapter should use existing Dilivox hooks where available, including current `data-dv-page`, `data-dv-story-slug`, `data-dv-goal`, `data-dv-ad-block`, choice/reveal hooks, and URL/path evidence, rather than requiring a rewrite of T123 markup.

Hard rule: a SiteAgent failure must never make Dilivox content or YAN blocks unusable.

## C. ACQUISITION ATTRIBUTION PERSISTENCE V1

Implement a privacy-minimal first-party acquisition state.

Required capture support from landing URL when present:

- `yclid`;
- UTM source/medium/campaign/content/term;
- explicit Yandex/Direct campaign/ad/group/criterion/phrase/keyword identifiers only when they are intentionally present as approved query parameters;
- landing `content_id`;
- acquisition timestamp.

Do NOT store arbitrary query parameters.
Do NOT store email, phone, name, free-form form content, full browser fingerprint, or other unnecessary personal data.

Normalize through an explicit allowlist with maximum value lengths and safe character handling.

Required persistence behavior:

- active session attribution survives internal navigation without requiring query-string decoration;
- one opaque `acquisition_id` / cohort reference can be attached to later event context;
- session identity is random/pseudonymous, not provider account identity;
- optional durable anonymous visitor/return reference may use first-party local storage only, with a configurable TTL (default maximum 30 days for the current 1/7/30-day economic windows), no fingerprinting, and a documented production privacy-review gate;
- storage unavailability/corruption must fail safe;
- an organic/direct visit must not silently overwrite a valid paid acquisition state within the configured attribution policy;
- a new explicit paid acquisition may start a new acquisition state according to documented deterministic rules.

Do not use a Metrica client ID as the Profit Engine first-party visitor identity.

## D. MONETIZATION PLACEMENT REGISTRY

Create a provider-neutral placement registry for current Dilivox monetization surfaces.

Use the actual T123/source evidence and enumerate current `data-dv-ad-block` / YAN placements.

Required fields:

- `provider_id` (YAN = first provider);
- `placement_id`;
- `site_id`;
- eligible page/content types;
- location class (`catalog`, `story-start`, `story-inline`, `before-choice`, `after-reveal`, `sidebar`, etc. as actually evidenced);
- device eligibility;
- active state/version;
- experiment eligibility;
- source reference.

Acceptance tooling must detect:

- duplicate active placement identities;
- source `data-dv-ad-block` values with no registry mapping;
- active registry mappings not found in the scanned current source unless explicitly documented as intentionally dormant.

Do NOT alter YAN creative/rendering behavior or provider code in Task 005.

## E. EXPERIMENT IDENTITY HOOKS — NO OPTIMIZER

Prepare a public-safe experiment identity layer only.

Support validated stable:

- `experiment_id`;
- `variant_id`;
- exposure eligibility/context hooks;
- global/experiment kill-switch input;
- event-context inclusion.

Do NOT implement proprietary experiment ranking, traffic allocation, scoring, winner selection, learned thresholds or owner-specific optimizer logic in this public repository.

Task 005 only prepares identity/context. Full site experiment execution belongs to later accepted tasks.

## F. EVENT CONTEXT CONTRACT FOR DAY 6

Define the browser event-envelope/context contract but do NOT implement production network dispatch yet.

It must be able to supply, when applicable:

- event schema version;
- site_id;
- content_id;
- source/destination content_id;
- page/content type;
- session reference;
- acquisition reference/cohort key;
- experiment_id / variant_id;
- placement_id when applicable;
- event timestamp;
- deployment/version metadata.

No sensitive payloads.

Day 6 will wire the canonical event taxonomy (`story_open`, progress, choice, reveal, completion, next-story, return, experiment exposure, etc.) to this context.

## G. TILDA/T123 INTEGRATION ARTIFACT — UNPUBLISHED

Produce a canonical, self-contained integration artifact suitable for later controlled insertion into Dilivox/Tilda.

Requirements:

- no third-party browser dependency unless already unavoidable;
- non-blocking initialization;
- no page content mutation required for basic identity resolution;
- compatible with existing T123 hooks;
- safe no-op fallback;
- explicit global kill switch;
- no provider ad-code mutation;
- no production network event dispatch in this task.

Document exact future installation point(s) and rollback/removal procedure.

Do NOT publish it to Tilda in Task 005.

## H. TESTS / ACCEPTANCE EVIDENCE

Required tests/checks:

1. all previous Python tests remain green (`38/38` baseline or higher);
2. browser/site-agent tests using Node or another already-installed lightweight local runner;
3. stable-ID registry uniqueness;
4. mutable URL/title/slug update does not change existing `content_id`;
5. known current story/page sources resolve to content IDs;
6. paid attribution capture from whitelisted params;
7. unapproved params/PII-like inputs are not stored;
8. attribution survives simulated internal navigation;
9. new paid acquisition deterministically supersedes previous state according to policy;
10. organic navigation does not erase active paid state;
11. TTL/return reference behavior;
12. storage-disabled/corrupt-storage fail-safe;
13. experiment IDs validated and kill-switch respected;
14. current `data-dv-ad-block` source coverage against placement registry;
15. no YAN rendering/provider code mutation;
16. no event network dispatch;
17. `git diff --check` PASS;
18. secret/private-ID/production-data scan PASS;
19. no proprietary optimizer/scoring logic introduced;
20. no Tilda publication / production site mutation.

## REQUIRED EVIDENCE

Create:

`profit-engine/evidence/TASK-005-DILIVOX-IDENTITY-ATTRIBUTION.md`

Evidence must include:

- baseline/final/origin SHAs;
- content registry item counts by type;
- stable-ID validation result;
- discovered current placement count and coverage result;
- existing Dilivox hooks used;
- SiteAgent API summary;
- attribution allowlist and persistence policy;
- privacy-minimization statement;
- experiment identity/kill-switch behavior;
- unpublished Tilda integration artifact path;
- all tests/checks;
- files changed;
- blockers;
- recommended Task 006 boundary.

## FORBIDDEN

- Tilda publication;
- production Dilivox mutation;
- Direct writes/campaign changes/budget changes/spend;
- YAN block/creative manipulation outside supported existing rendering;
- secrets/private provider IDs/production raw exports in Git;
- arbitrary query-string capture;
- fingerprinting;
- proprietary profit optimizer/scoring/allocation implementation in this public repo;
- paid Cloud resource creation;
- force push;
- merge to `main`;
- self-acceptance.

## TASK 005 ACCEPTANCE GATE

Central Brain accepts Task 005 only when it can verify from repository evidence that:

`a paid Dilivox landing can be mapped to an immutable content_id, acquisition state survives internal navigation, current monetization placements have stable provider-neutral identities, and the same context is ready for Day-6 event instrumentation without production deployment.`

## EXPECTED TASK 006 BOUNDARY

After acceptance, Day 6 should wire the canonical first-party event taxonomy to the SiteAgent/event context, add local/portable event ingestion, mobile/desktop validation, performance/JS-error signals, dedupe semantics and site kill-switch behavior, then prepare a controlled production deployment gate. No autonomous money scaling until the site events and provider data reconcile.
