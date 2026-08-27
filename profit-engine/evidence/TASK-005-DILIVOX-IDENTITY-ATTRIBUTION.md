# TASK 005 — DILIVOX IDENTITY + ATTRIBUTION — EVIDENCE

## Execution identity

- Accepted Task 004 implementation: `8e7bb96450e6d878b513f47649929c27a868ea4b`.
- Central Brain Task 005 baseline/current origin used:
  `975a7c15674f133b66e1df699a803af590627189`.
- Required Central Brain commit ancestor check: PASS.
- Sync: `git fetch origin profit-engine` then `git merge --ff-only origin/profit-engine`.
- Final HEAD: evidence-bearing Task 005 commit; exact SHA is in the final report.
- Separate `~/Documents/New project/Dilivox` workspace: READ_ONLY inspection only;
  no Tilda publication or production mutation.

## Content identity registry

Canonical file: `profit-engine/sites/dilivox/content-registry.json`.

- Total immutable identities: 61.
- Core pages: home 1, catalog 1, about 1, contacts 1, privacy 1.
- Stories: 54.
- Comics: 2.
- Active canonical URLs: 55 (5 core + 50 catalog-discoverable content routes).
- Source-present but not catalog-discoverable: stories 51–56, recorded inactive
  rather than represented as published.
- Source story/comic coverage: 56/56.
- Discoverable active story/comic coverage: 50/50.
- Duplicate IDs: 0; duplicate active canonical URLs: 0.

IDs are randomly assigned UUIDs persisted in the registry. Runtime never derives
them from title, URL, slug, order, or category. The validator keys preservation
to stable source references and rejects reassignment; mutation tests change URL,
title and slug while retaining the original ID, then prove a changed ID fails.

## Source hooks and placements

Read-only source inventory used:

- `data-dv-page`;
- `data-dv-story-slug`;
- `data-dv-goal`;
- `data-dv-ad-block`;
- `data-dv-choice`;
- `data-dv-reveal`;
- current URL/path evidence.

Canonical placement registry: `placement-registry.json`.

- Unique current source `data-dv-ad-block` values: 12 (`R-A-19563496-3` through
  `R-A-19563496-14` as actually evidenced).
- Active registry entries: 12.
- Source values mapped: 12/12.
- Duplicate active placement identities: 0.
- Unsupported active mappings: 0.
- Dormant unsupported mappings: 0.

Entries identify provider, site, eligible content types, catalog/story-start/
inline/before-choice/after-reveal/sidebar location, device eligibility, version,
experiment eligibility, and source reference. No YAN rendering/provider code was
changed.

## Generic SiteAgent and Dilivox adapter

Contract: `SITE_AGENT_CONTRACT.md`.

`createSiteAgent(window, adapter, options)` is generic. An adapter supplies
`site_id`, stable content resolution, and approved placement resolution. The read
API exposes versions, stable content/type, acquisition/cohort, pseudonymous
session/optional return context, experiment/variant, placements, health,
`getContext()` and `buildEventContext()`.

`DILIVOX_ADAPTER` is adapter #1 and uses the existing hooks above. Failures return
a frozen `SAFE_NOOP` agent; normal page/YAN behavior is independent.

## Attribution persistence v1 and privacy

Exact query allowlist:

`yclid`, `utm_source`, `utm_medium`, `utm_campaign`, `utm_content`, `utm_term`,
`campaign_id`, `ad_id`, `group_id`, `criterion_id`, `phrase_id`, `keyword_id`.

Values are NFKC-normalized, control-character stripped, trimmed and length
limited (64–256 characters by field). Arbitrary query keys and PII-like keys such
as email, phone, name, free text and forms are not captured.

- Explicit paid landing creates a fresh opaque acquisition/cohort ID.
- New explicit paid landing deterministically supersedes prior active state.
- Organic/internal navigation preserves valid paid state without URL decoration.
- Session identity is random first-party pseudonymous state.
- Optional anonymous return ID is disabled unless both feature enablement and
  `privacyReviewApproved` are true.
- Attribution/return TTL is configurable but hard-capped at 30 days.
- Corrupt/unavailable storage safely degrades; ephemeral session operation can
  continue without persistence.
- No fingerprinting and no Metrica ClientID identity.

Production privacy review remains mandatory before durable return identity or
production installation.

## Experiment and event context

Experiment/variant IDs are syntax/length validated. Global and per-experiment
kill switches suppress identity/exposure context. There is no allocation,
ranking, scoring, winner selection, learned threshold, or commercial policy.

`event-context.schema.json` and `buildEventContext()` provide Day-6 context:
schema/site/content/source/destination/type/session/acquisition/cohort/experiment/
variant/placement/timestamp/deployment. No production network dispatch exists.

## Unpublished Tilda artifact

Artifact:
`profit-engine/sites/dilivox/tilda/dilivox-site-agent-task005.js`.

Installation/rollback:
`profit-engine/sites/dilivox/tilda/INSTALLATION.md`.

The artifact is self-contained, dependency-free, non-blocking, safe-no-op and
globally killable. It performs no content mutation, YAN call/mutation, or event
dispatch. Installation was not performed and Tilda was not published.

## Tests and checks

- Registry validator: PASS — 61 IDs / 55 active URLs / 56 source content /
  50 discoverable active / 12 source placements / 12 active mappings.
- Node browser simulations: 11/11 PASS.
- Previous Python suite: 38/38 PASS.
- Stable identity mutation/reassignment test: PASS.
- Allowlist, PII-like exclusion, navigation persistence, paid supersession,
  organic preservation, TTL/privacy gate, corrupt/disabled storage: PASS.
- Experiment/global kill switches and generic adapter isolation: PASS.
- Artifact network dispatch/YAN mutation scan: PASS.
- `git diff --check`: PASS.
- Secret/private mapping/production-data scan: PASS.
- Proprietary optimizer/scoring scan: PASS.
- Tilda publication/production mutation: NOT PERFORMED.

## Files changed

- `profit-engine/sites/dilivox/content-registry.json`
- `profit-engine/sites/dilivox/placement-registry.json`
- `profit-engine/sites/dilivox/source-hooks-inventory.json`
- `profit-engine/sites/dilivox/event-context.schema.json`
- `profit-engine/sites/dilivox/SITE_AGENT_CONTRACT.md`
- `profit-engine/sites/dilivox/validate-registries.mjs`
- `profit-engine/sites/dilivox/tilda/dilivox-site-agent-task005.js`
- `profit-engine/sites/dilivox/tilda/INSTALLATION.md`
- `profit-engine/sites/dilivox/tests/site-agent.test.cjs`
- `profit-engine/evidence/TASK-005-DILIVOX-IDENTITY-ATTRIBUTION.md`

Unrelated untracked `profit-engine/evidence/TASK-001-M0-INVENTORY 2.md` was
preserved unchanged and excluded.

## Blockers and recommended Task 006

Task 005 engineering has no internal blocker. Production installation remains
deliberately unperformed; durable return identity requires privacy review.

Recommended Task 006: wire canonical first-party event taxonomy to the SiteAgent
context, add local/portable ingestion and dedupe, mobile/desktop and performance/
JS-error validation, and controlled deployment/rollback gates. Keep production
network dispatch disabled until that contract authorizes and validates it.
