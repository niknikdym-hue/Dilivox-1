# TASK-001 — M0 Local Bootstrap and Inventory Evidence

- Timestamp: 2026-08-26 23:51:17 MSK
- Canonical local path: `/Users/elenadymova/Documents/New project/Profit Engine/Dilivox-1`
- Existing site workspace inspected read-only: `/Users/elenadymova/Documents/New project/Dilivox`
- Branch: `profit-engine`
- HEAD: `51eb6be7d7fe6cc06d795d33ae2a64c0c965010c`
- `origin/profit-engine`: `51eb6be7d7fe6cc06d795d33ae2a64c0c965010c`
- Remote: `origin https://github.com/niknikdym-hue/Dilivox-1.git` (fetch/push)
- Initial worktree: clean, tracking `origin/profit-engine`
- Synchronization: `git fetch origin profit-engine` followed by `git merge --ff-only origin/profit-engine`; already up to date

## Environment

- macOS 26.5.2 (Build 25F84), Apple Silicon `arm64`
- Git 2.50.1 (Apple Git-155)
- Python 3.14.0
- Node.js v22.23.2
- npm 10.9.8
- Docker: not installed
- Terraform: not installed
- Yandex Cloud CLI (`yc`): not installed

No dependency installation was required or performed.

## Authority/state review

All ten files mandated by the Task 001 contract were read before creating this artifact:

1. `profit-engine/PROJECT_HANDOFF.md`
2. `profit-engine/OWNER_DECISIONS.md`
3. `profit-engine/PROJECT_STATE.md`
4. `profit-engine/HARD_12_DAY_LAUNCH_PLAN.md`
5. `profit-engine/GOVERNANCE_AND_EXECUTION.md`
6. `profit-engine/DILIVOX_SITE_INTEGRATION.md`
7. `profit-engine/MACHINE_ADVERTISING_OPERATIONS.md`
8. `profit-engine/ACCESS_SETUP_CHECKLIST.md`
9. `profit-engine/OAUTH_API_SETUP.md`
10. `profit-engine/sites/dilivox/SITE_STATE.md`

The separate existing site workspace was not deleted, moved, reset, overwritten, or modified.

## Repository implementation inventory

### Canonical repository

The repository is currently a content/source package plus the Profit Engine authority/specification package. It does not yet contain a runnable Profit Engine application, provider connector, database schema, infrastructure definition, CI workflow, package manifest, or deployment automation.

Relevant current site/content surfaces:

- Homepage T123 source: `dilivox-glavnaya-t123.txt`
- Catalog T123 source: `dilivox-istorii-t123.txt`
- Story 48 package: `48-pansionat-tikhiy-uzhas:/`
- Comic/story 49 package: `49-ona-vyshla-na-stsenu-dvazhdy:/`
- Comic/story 50 source and assets: `50-pechat-na-bagrovom-voske/`
- Profit Engine authority/state: `profit-engine/*.md`
- Dilivox state: `profit-engine/sites/dilivox/SITE_STATE.md`

There is no automated build/deploy mechanism in this repository. The T123 sources are fragments intended for Tilda rather than a standalone application.

### Existing site workspace (read-only findings)

The fuller current Dilivox implementation exists under `/Users/elenadymova/Documents/New project/Dilivox` and contains 655 files, including 54 story directories under `08-stories-content:`.

Implementation map:

- Homepage: `01-home:/dilivox-glavnaya-t123.txt`
- Catalog: `06-istorii:/dilivox-istorii-t123.txt`
- Story template: `07-story-template:/dilivox-story-template-t123.txt`
- Individual stories: `08-stories-content:/<number-slug>/...-t123.txt`, with companion HEAD/SEO/content files
- Global header/footer: `02-header-footer:/dilivox-header-t123-links.txt` and `dilivox-footer-t123-links.txt`
- Global Metrica/UX hook: `02-header-footer:/dilivox-metrika-goals-global-head-after-counter.txt`
- Tilda upload/deployment map: `09-codex-tz:/dilivox-tilda-upload-map.txt`
- URL registry/map: `00-project:/dilivox-url-map.txt` and `09-codex-tz:/dilivox-url-registry-for-codex.txt`
- YAN placement registry: `00-project:/dilivox-ad-slots-plan.txt`

Deployment is manual through Tilda: page-specific SEO and HEAD settings plus T123 fragments are copied into mapped Tilda pages/blocks, while the counter and global UX/Metrica code are placed once in global HEAD. There is no repository-driven production deployment pipeline.

Current local scripts directly relevant to the site are:

- `09-codex-tz:/build-stories-19-48-t123.js`
- `09-codex-tz:/audit-stories-19-48-t123.js`

Other Python/JS scripts found in the site workspace belong to image preparation or an unrelated EGE subtree and are not part of the Dilivox production build.

## Analytics / Metrica

Status: **PASS (implementation inventory only)** / **BLOCKED (API read)**

- Existing site documentation states that one Metrica counter is installed in Tilda global HEAD. Its numeric identifier is intentionally redacted here.
- `02-header-footer:/dilivox-metrika-goals-global-head-after-counter.txt` calls `ym(..., 'reachGoal', goalId)` through a guarded sender and implements page/reading interaction goals.
- Observed goals include homepage scroll milestones, homepage-to-catalog/story clicks, story-card clicks, choice/reveal interactions, reading milestones, next/previous story clicks, and return-to-catalog clicks.
- The same global layer stores story status, reading progress, and selected choice in `localStorage` using URL slug-derived keys.
- This is useful client-side behavioral instrumentation, but it is not yet the canonical Profit Engine event envelope/taxonomy and does not provide a first-party event collector.
- No safely usable OAuth access token was present in process environment variables or repository/local site configuration filenames.
- Therefore no authenticated Metrica counter-list/statistics request was attempted.

Blocker/next owner action: securely provide the existing OAuth access token with `metrika:read` to a local secret store/runtime (later Lockbox), then run a counters list and Dilivox traffic/monetization read without logging token or private identifiers.

## YAN / RСЯ

Status: **PASS (code/placement inventory)** / **BLOCKED (API read)**

The placement integration surface is explicit and reusable:

- Canonical local registry: `00-project:/dilivox-ad-slots-plan.txt`
- Catalog slots: upper and lower catalog placements in `06-istorii:/dilivox-istorii-t123.txt`
- Story placements: after opening, several in-text boundaries, before choice, after reveal, and desktop sidebar across individual story T123 files
- Loader: `https://yandex.ru/ads/system/context.js`, guarded to load once
- Render integration: `window.yaContextCb.push(...)` / `Ya.Context.AdvManager.render(...)` against `yandex_rtb_*` containers
- Lazy/viewport behavior and responsive desktop-sidebar rules are embedded in T123 code
- Empty/disabled blocks are styled to avoid large layout gaps
- Placement/resource numeric identifiers are intentionally redacted from this evidence; they remain in pre-existing source and the local registry.

The local registry dated 2026-08-11 says YAN display had been disabled by the network at that time and preserves the placement IDs for possible restoration. Current live/provider status was not independently verified in this task.

No YAN Statistics API token was found in process environment variables or repository/local site credential-like filenames. No authenticated statistics/resource request was attempted.

Blocker/next owner action: obtain or expose to the secure runtime the minimum-scope YAN Statistics API token for the account that can read Dilivox, then verify the resource tree and a lightweight statistics read. Do not enable block editing.

## Direct

Status: **BLOCKED (API read)**

- Repository authority records managing-account UI access at `Reading` level and an OAuth application configured with `direct:api` plus `metrika:read`.
- No safely usable Direct OAuth access token was present in process environment variables or repository/local site credential-like filenames.
- No Direct account/campaign identifiers are mapped in code/config to `site_id=dilivox`.
- No authenticated Direct request was attempted, because inventing or extracting access beyond securely available credentials is forbidden.
- No Direct write/edit request, campaign operation, budget change, or spend occurred.

Blocker/next owner/provider action: complete/confirm current Direct API production access approval if still pending, securely provide the OAuth access token to the local runtime, and run a minimal read/list request while keeping managing-account access at `Reading` through M0-M5.

## Attribution, first-party events, and stable identity

### Current attribution

- No code was found that captures or persists `utm_source`, `utm_medium`, `utm_campaign`, `utm_content`, `utm_term`, `yclid`, or `gclid` across navigation.
- Existing Metrica behavior relies on the installed counter and URL/navigation context; no Profit Engine acquisition envelope or server-side reconciliation bridge exists.

### Current first-party instrumentation

- Existing `ym(... reachGoal ...)` calls and localStorage state are browser-side Metrica/UX hooks.
- No endpoint, queue, durable event log, schema, consent-aware first-party collector, or canonical events such as `page_view_site`, `story_open`, `story_progress_25/50/75`, `experiment_exposure`, etc. are implemented as Profit Engine events.

### Current stable IDs

- Story URL slugs and numeric prefixes in content directory/file names act as practical editorial identifiers.
- UI status/progress keys are derived from the URL slug and `data-dv-story-status="<slug>"` attributes appear in homepage/catalog cards.
- These are not yet a declared immutable machine-readable `content_id`/`story_id` layer independent of title/URL changes.
- No stable placement registry exists in Profit Engine code; the separate site workspace has the human-readable YAN slot registry described above.

## Secrets and ignore safety

Status: **PASS (no exposed values)** / **BLOCKED (repository ignore hardening)**

- No `.env*`, token-, credential-, or secret-named files were found in the canonical repository or existing Dilivox workspace (excluding `.git`).
- No credential-related process environment variable names were present.
- No secret values were printed, copied, committed, or included in this report.
- The canonical repository has no `.gitignore`. It is therefore not adequate to prevent accidental commits of `.env`, OAuth tokens, credentials, macOS metadata, Node/Python artifacts, Terraform state, or local runtime files.
- Pre-existing public source contains Metrica/YAN numeric implementation identifiers. They are redacted in this evidence and should be mapped to private deployment/site configuration where repository authority requires privacy.

## Provider read check summary

| Provider | Result | Reason |
|---|---|---|
| Direct | BLOCKED | No securely available OAuth access token in the inspected runtime; no account mapping |
| Metrica | BLOCKED | No securely available OAuth access token in the inspected runtime |
| YAN Statistics | BLOCKED | No securely available YAN Statistics API token in the inspected runtime |

`NOT_ATTEMPTED` is used operationally for all three network calls: attempting them without credentials would not be an authenticated check. The overall gate is `BLOCKED` pending secure credential injection.

## Checks performed

- Clone path/remote/branch/HEAD/origin/worktree verification
- Safe fetch and fast-forward-only synchronization
- Complete mandated authority/state file read
- Repository and separate-site file inventory
- Focused searches for Metrica, YAN, attribution parameters, first-party events, stable IDs, build/deploy tooling, API code, environment files, and secret references
- Environment/tool version check
- Credential presence check by variable/file **names only**, never values
- Read-only inspection of the existing Dilivox workspace

No production behavior, provider resource, campaign, budget, or existing-site file was changed.

## Exact blockers

1. Secure runtime access tokens are not available for authenticated Direct/Metrica/YAN reads.
2. Direct account/campaign, Metrica counter, and YAN resources are not mapped into a private `site_id=dilivox` deployment configuration.
3. Profit Engine application/connectors/data schemas do not yet exist.
4. UTM/Direct attribution persistence and canonical first-party event ingestion do not exist.
5. Stable immutable content/story identity is not formalized.
6. The repository lacks `.gitignore` secret/artifact protection.
7. Current live YAN serving/moderation status is not API-certified.

## Recommended Task 002 boundary

Task 002 should remain read-only and establish the M0 provider/data foundation without production-site or advertising writes:

1. add a defensive `.gitignore` and secret-safe configuration contract (names/placeholders only);
2. define a private per-site registry/config schema for Direct account/campaign mapping, Metrica counter mapping, and YAN resource/placement mapping;
3. implement minimal read-only Direct, Metrica, and YAN connector skeletons with redacted logging, timeouts, raw immutable snapshots, and fixture-based tests;
4. run authenticated provider reads only after the Owner injects tokens securely;
5. certify the Dilivox counter/monetization view and YAN resource tree;
6. produce the stable content/placement ID migration map and attribution/event implementation plan, but defer production Tilda changes to the separately authorized site-integration task.

This task is evidence completion only. Project acceptance remains with Central Brain.
