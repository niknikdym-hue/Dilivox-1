# Task 013 — Existing Dilivox Metrika integration reconciliation

Date: 2026-09-01
Status: `CODE_READY / NOT_PUBLISHED / PENDING_CENTRAL_BRAIN_ACCEPTANCE`
Baseline: `2829d719487e1087cdde3d11b04007f24d35019a`

## Safety result

No Tilda publication, Metrica Management API request, Direct request, YAN block
change, paid provider call, or production-site mutation occurred. The five
canonical goals already exist and were not created, deleted, renamed, or edited.

## Complete local inventory

The requested path without a colon did not exist. The actual local directory is:

`/Users/elenadymova/Documents/New project/Dilivox/02-header-footer:/`

All four files were read in full:

| File | SHA-256 | Classification and purpose | Production-source potential |
|---|---|---|---|
| `dilivox-metrika-installation-note.txt` | `290dd47e...0bc9c` | 12-line installation authority: counter 110349067 is already global; do not duplicate; place the UX/goals block once after it | instruction, not executable |
| `dilivox-metrika-goals-global-head-after-counter.txt` | `41186dfa...3a2` | 1300-line CSS/JS global UX + Metrika implementation; catalog filters/status/progress, story image/progress, choice/reveal restoration and legacy goals | authoritative pre-Profit-Engine implementation candidate; local note says global HEAD, but local inspection alone is not proof that the exact bytes are currently live |
| `dilivox-header-t123-links.txt` | `46ce925e...88d7` | global header HTML/CSS/JS, active navigation and mobile menu | T123 production source; no Metrika call |
| `dilivox-footer-t123-links.txt` | `5836330f...c4d8` | global footer HTML/CSS/navigation | T123 production source; no script/Metrika call |

No files were modified, moved, deleted, or copied from this local site workspace.

## Existing architecture before Profit Engine publication

- The counter is not created by the old UX file. It assumes the existing global
  counter and calls `ym(110349067, "reachGoal", ...)`.
- Global duplicate-install guard: `window.DILIVOX_SYSTEM_V1.ready`.
- Per-element binding guards: `data-dv-goal-bound`, `data-dv-choice-bound`,
  filter/format/sort binding flags.
- Per-page goal dedupe: closure-local `sentGoals[goalId]`.
- Story identity: `data-dv-story-slug` or `/istorii/<slug>/` path.
- Persistent state: `localStorage` keys for story status, progress, and choice.
  No cookies or sessionStorage return-visit logic exists in the old source.
- Reading progress: geometry of `[data-dv-story-text]` / `.dv-story-text`, with
  thresholds 10/25/50/75/90/98 and visual progress/state persistence.
- Choice/reveal: trusted UI click is not checked by old code; `[data-dv-choice]`
  click synchronously reveals final+proof, stores choice, marks read, and restores
  state on reload.
- Next story: `[data-dv-goal="next-story"]` / `.dv-next-story` click.
- No separate event bus or SiteAgent exists in the old source.
- No explicit analytics kill switch exists; only duplicate-install and binding
  guards. The canonical bridge retains the Profit Engine kill switch.
- The old source also owns essential UX. Treating it as disposable analytics
  would break catalog, progress, choice/reveal and restoration behavior.

Legacy goals include home time/scroll/visibility/navigation, catalog open/filter/
format/card, story open/time/read milestones, next/previous/back navigation. The
legacy sender is broader than the five canonical Profit Engine proxy goals.

## Five-goal crosswalk

| Canonical goal | Existing authoritative signal | Semantic match | Reconciliation |
|---|---|---|---|
| `pe_story_progress_75` | old `sendGoal("dv_story_read_75")` from article geometry | exact 75% reading threshold | normalize the existing legacy dispatch; no second scroll/resize listener |
| `pe_version_selected` | old `[data-dv-choice]` click that calls `revealStoryChoice` | exact selected version transition | one missing document listener observes the already authoritative trusted click; per-session canonical dedupe |
| `pe_story_completed` | old choice transition synchronously exposes both final and proof and marks story read | canonical completion requires actual choice/reveal transition, not 98% scroll alone | same choice listener verifies final+proof are open after the authoritative handler; no IntersectionObserver duplicate |
| `pe_next_story_clicked` | old `sendGoal("dv_next_story_click")` from next-story hook | exact navigation click | normalize existing legacy dispatch; no second click listener |
| `pe_return_visit` | no old equivalent | missing | add privacy-minimal localStorage durable marker plus sessionStorage once-per-later-session marker |

The 98% legacy `dv_story_read_complete` is deliberately not mapped to
`pe_story_completed`; scroll completion and choice/reveal completion have
different semantics.

## Duplicate risks found and removed

The previously prepared package loaded both `dilivox-event-layer-task006.js` and
`dilivox-metrica-goals-v1.js`. Against `DILIVOX_SYSTEM_V1` that would create:

- a second story progress scroll listener;
- a second choice listener;
- a second next-story listener;
- a separate reveal observer;
- parallel first-party event generation plus direct goal wiring;
- duplicate canonical listener installation if the package were pasted twice.

The reworked package excludes the Task-006 DOM controller. That artifact remains
an accepted source contract for a later first-party endpoint, but is not part of
this production Metrika installation.

## One canonical production contour

`existing Dilivox UI + DILIVOX_SYSTEM_V1 authoritative transitions`
→ `one idempotent Profit Engine legacy/canonical normalization bridge`
→ `one canonical dispatch per accepted transition`
→ `one reachGoal to counter 110349067`.

The bridge never initializes the counter. It wraps only legacy `reachGoal` calls
with exact allowlisted mappings for 75% and next-story; other legacy goals pass
through unchanged. Canonical IDs are deduplicated in one shared install state.
Repeated script execution returns the existing frozen API and adds no listener or
normalizer. Choice/completion dispatch uses the old synchronous transition and
return visit is the only new storage-backed semantic source.

## Canonical provider truth

Five goals are `LIVE PASS / already created`:

- provider goal count `27`;
- missing `0`;
- invalid `0`;
- duplicate `0`;
- read-back HTTP `200`;
- audit `PASS`;
- apply `APPLIED_AND_VERIFIED`.

This task made zero Metrika provider writes.

## Exact Owner action after acceptance

Run `profit-engine/scripts/prepare-dilivox-tilda-production-head.sh`. In Tilda
site-wide HEAD:

1. keep the existing counter 110349067 exactly once;
2. keep the existing `DILIVOX_SYSTEM_V1` UX block exactly once;
3. replace an existing Profit Engine v1 block or paste the generated minimal
   bridge once immediately after `DILIVOX_SYSTEM_V1`;
4. do **not** paste `dilivox-event-layer-task006.js` separately;
5. do not change YAN blocks or story T123 blocks;
6. publish all pages only after Central Brain acceptance, then run the live probe
   and validate real arrivals/no regression.

Latest locally generated, not-published package:

- path: `~/.config/profit-engine/tilda/dilivox-profit-engine-head-v1.html`;
- SHA-256: `6dbffdde811e7aae9983a1a4ecc9fde1a1dd5617fbfa7e189f72977994507e52`;
- bytes: `4025`;
- provider writes: `0`.

## Automated verification

The Node regression proves: no counter initialization; exact legacy mapping;
one canonical goal per transition; repeated load adds no listener/normalizer;
return visit once per later session; kill switch; package excludes the second DOM
controller; existing story/event/SiteAgent/YAN invariants remain green. Full
Python/Node/compile/JSON/diff/scans and exact final CI are recorded in handoff.

Local regression results: Node `28/28 PASS`; Python `290/290 PASS`;
py_compile `PASS`; JSON `12/12 PASS`; `git diff --check` `PASS`.

Canonical live-probe markers were also reconciled: production acceptance now
requires `DILIVOX_SYSTEM_V1` plus the canonical normalizer and no longer requires
the deliberately excluded parallel `ProfitEngineEvents`/SiteAgent bundle.
