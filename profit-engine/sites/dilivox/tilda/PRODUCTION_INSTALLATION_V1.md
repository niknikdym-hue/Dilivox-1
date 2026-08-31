# DILIVOX — PROFIT ENGINE TILDA PRODUCTION INSTALLATION v1

Status: P0 / EXTERNAL UI PUBLICATION REQUIRED
Task: 013

## Purpose

Install the already tested Profit Engine site instrumentation globally on `dilivox.ru` with one Tilda site-level paste, without editing story blocks individually.

## Prepared package

Run locally from current canonical branch:

```bash
bash profit-engine/scripts/prepare-dilivox-tilda-production-head.sh
```

The script:

- composes the accepted Task-006 SiteAgent/event layer;
- adds a DOM-ready bootstrap with `autoStart=true`;
- intentionally supplies **no first-party network transport**;
- adds the canonical Metrica goal bridge;
- writes the exact package to `~/.config/profit-engine/tilda/dilivox-profit-engine-head-v1.html` mode 0600;
- prints SHA-256 and byte count;
- copies the exact package to macOS clipboard when `pbcopy` exists;
- performs zero provider writes.

## Tilda publication

Tilda site-wide custom code path:

`Site Settings -> More -> HTML code for the HEAD section`

Paste the clipboard content once. If a previous Profit Engine v1 block exists, replace only the block bounded by:

- `<!-- PROFIT ENGINE DILIVOX PRODUCTION INSTRUMENTATION v1 -->`
- `<!-- /PROFIT ENGINE DILIVOX PRODUCTION INSTRUMENTATION v1 -->`

Then save and **Publish all pages**.

Do not change:

- existing YAN/RSYA block code or block IDs;
- story T123 content;
- `data-dv-*` attributes;
- current site layout.

## Runtime behavior

### SiteAgent/event controller

The Task-006 controller starts from existing `data-dv-*` hooks and creates first-party event objects in memory.

No production transport is supplied in Task 013, so it cannot send event batches to a Profit Engine endpoint yet. Network dispatch is deferred to Task 015.

### Metrica goal bridge

Counter: `110349067`.

Goals:

- `pe_story_progress_75`;
- `pe_version_selected`;
- `pe_story_completed`;
- `pe_next_story_clicked`;
- `pe_return_visit`.

The bridge calls only Metrica `reachGoal` when `window.ym` is available.

Emergency kill:

```js
window.PROFIT_ENGINE_METRICA_GOALS_KILL = true;
```

## Post-publish QA

Required before Task 013 acceptance:

1. `window.DilivoxSiteAgent` exists;
2. `window.ProfitEngineEvents` exists;
3. `window.DilivoxProfitEngineEventController` exists;
4. `window.ProfitEngineMetricaGoals` exists;
5. story navigation works;
6. choice/reveal works;
7. existing YAN blocks render;
8. no Profit Engine console error storm;
9. one bounded test of each applicable canonical Metrica goal is visible in Metrica;
10. no duplicate goal storm.

## Rollback

Immediate soft stop:

```js
window.PROFIT_ENGINE_METRICA_GOALS_KILL = true;
```

Hard rollback:

1. remove the bounded Profit Engine v1 block from site-wide HEAD code;
2. save;
3. publish all pages;
4. revalidate story and YAN behavior.

## Acceptance

Publication itself is not enough. Task 013 becomes `PRODUCTION_SITE_INSTRUMENTATION_ACCEPTED` only after live site + Metrica verification evidence.
