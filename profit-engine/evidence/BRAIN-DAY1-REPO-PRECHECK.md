# CENTRAL BRAIN — DAY 1 REPOSITORY PRECHECK

Status: EVIDENCE / PARTIAL PRECHECK
Updated: 2026-08-26
Branch: `profit-engine`

Purpose: record direct Central Brain inspection performed before Codex Task 001 so Codex evidence can be independently checked.

## Scope checked

- `dilivox-glavnaya-t123.txt`
- `49-ona-vyshla-na-stsenu-dvazhdy:/dilivox-comic-49-ona-vyshla-na-stsenu-dvazhdy-t123.txt`
- GitHub repository text search for obvious Metrica/YAN/UTM markers (search index returned no useful results, so direct file inspection was used instead).

## Findings

### 1. Existing site machine-readable hooks are already present

Homepage source contains reusable attributes including:
- `data-dv-page="home"`;
- `data-dv-goal="home-to-stories"`;
- `data-dv-goal="home-story-card"`;
- `data-dv-story-status="<story-slug>"`.

Implication:
Profit Engine instrumentation should extend these existing conventions rather than introduce an unrelated parallel DOM taxonomy.

### 2. Story pages already expose stable semantic attributes

Story 49 source contains:
- `data-dv-page="story"`;
- `data-dv-story-slug="ona-vyshla-na-stsenu-dvazhdy"`;
- genre/format/story-type attributes;
- `data-dv-comic-frame` / scene identity;
- `data-dv-choice`;
- `data-dv-correct`;
- reveal structure.

Implication:
The planned stable-content/event layer can use existing story slug/frame/choice semantics as migration inputs. A canonical machine content ID still needs to be defined and versioned; slug alone should not become the entire long-term identity contract.

### 3. YAN placement markup is already explicit on Story 49

Story 49 contains multiple YAN/RСЯ slots with:
- `data-dv-ad-block`;
- `data-dv-ad-lazy="true"`;
- placement CSS classes such as comic start / inline / before choice / after reveal / sidebar;
- `yandex_rtb_<block>` render targets;
- lazy render code using `IntersectionObserver`;
- `Ya.Context.AdvManager.render(...)` through `yaContextCb`.

Some placements are context-aware, including a block hidden until after reveal and a desktop-only sidebar.

Implication:
`MonetizationPlacementRegistry` should initially map these existing placement classes/block references into provider-neutral placement IDs and preserve their behavioral conditions.

### 4. No inline Metrica `ym(...)` call was found in the inspected homepage or Story 49 T123 source

This does NOT prove Metrica is absent from production. The source comments explicitly indicate these are page blocks without global header/footer/counter code, and Tilda may load the counter globally.

Implication:
Codex Task 001 must inspect deployment/global Tilda analytics configuration and not infer counter absence from these files.

### 5. Event opportunities are unusually strong

Existing interactive structure already exposes machine-detectable points for:
- story open;
- frame/progress inference;
- choice/version selection;
- correct/incorrect selection;
- reveal;
- previous/catalog/next navigation;
- ad-slot eligibility/render.

Implication:
Dilivox is already structurally suitable for the planned first-party event model. Day 5–6 implementation should be an instrumentation/identity extension, not a page rewrite.

## Preliminary architecture decision from evidence

Do not rebuild Dilivox markup solely for Profit Engine.

Prefer a thin instrumentation adapter that:
1. recognizes existing `data-dv-*` semantics;
2. maps them to canonical SiteAgent/content/event contracts;
3. adds missing stable IDs/experiment/cohort fields;
4. preserves current user experience and ad rendering;
5. emits versioned events;
6. adds kill switches/fallbacks without coupling core page rendering to Profit Engine availability.

## Remaining unknowns for Codex Task 001

- exact global Metrica counter/config and production injection path;
- current global YAN loader placement;
- whether other story templates follow the same data attributes consistently;
- any shared global JS handling `data-dv-goal` / story status;
- current persistence/storage for user story progress;
- current UTM/yclid handling;
- current deployment process from repository files to Tilda/production;
- safe availability of OAuth/YAN statistics credentials on the Mac.

These remain Task 001 evidence requirements.
