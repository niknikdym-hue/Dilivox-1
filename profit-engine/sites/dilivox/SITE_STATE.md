# DILIVOX SITE STATE

Status: P0 PRODUCTION INSTRUMENTATION INCOMPLETE
Updated: 2026-08-31
Site: `dilivox.ru`
Site ID: `dilivox`
Platform: Tilda + custom T123/HTML/JS
Canonical operational board: `profit-engine/P0_SYSTEM_COMPLETION_BOARD.md`

## Product role

Dilivox is the first complete site-side node of Profit Engine, not merely a landing page.

Required closed loop:

`Direct -> Dilivox -> attributable visitor -> behavior/content path -> YAN ads/revenue -> Metrica/YAN reconciliation -> K5 -> Profit Engine decision -> guarded Direct/site action -> measured outcome`

The Owner approved this entire site workstream on 2026-08-26 in `OWNER_APPROVAL_DILIVOX_SITE_WORKSTREAM.md`.

## Production truth

### Live and verified

- public `dilivox.ru` is live;
- YAN/RSYA domain statistics are readable through YAN Statistics API;
- Metrica counter `110349067` is readable with edit permission;
- Direct attribution dimensions are readable in Metrica;
- existing story/T123 source hooks are inventoried;
- existing YAN placements are inventoried in provider-neutral placement registry;
- exact site/content registries and event schemas exist.

### Owner action completed / provider propagation pending

Owner enabled **YAN reports in Metrica** for Dilivox and bound counter `110349067` on 2026-08-31.

Before this change Metrica returned exact provider error:

`partner is not enabled for 110349067`

for every `ym:s:yanPartnerPrice` query, while ordinary Direct campaign attribution returned HTTP 200. Technical monetization PASS must be re-read after provider propagation; Owner UI confirmation is not substituted for API evidence.

### Implemented in code but NOT yet published on production Tilda

Task-005/006 site instrumentation was historically accepted as code but its evidence explicitly recorded no Tilda publication.

Unpublished accepted successor:

`profit-engine/sites/dilivox/tilda/dilivox-event-layer-task006.js`

It contains SiteAgent + first-party event controller. Production event dispatch is still disabled/not configured.

New production-safe Metrica bridge:

`profit-engine/sites/dilivox/tilda/dilivox-metrica-goals-v1.js`

It maps existing Dilivox hooks to canonical `reachGoal` events and does not modify YAN blocks, story content or choice/reveal behavior.

### First-party event endpoint

NOT CONFIGURED in production.

The event layer can currently create/queue events but there is no accepted production endpoint/transport. Therefore event-stream persistence is not yet a production fact.

## Canonical Metrica goals

Registry:
`profit-engine/sites/dilivox/metrica-goals.json`

Counter: `110349067`.

Required exact JavaScript-event goals:

- `pe_story_progress_75` — reader reaches ~75% of story;
- `pe_version_selected` — a story choice/version is selected;
- `pe_story_completed` — completion/reveal reaches accepted terminal condition;
- `pe_next_story_clicked` — recirculation to another story;
- `pe_return_visit` — later browser session return.

These are proxy goals. They are not revenue and are not automatically eligible for Direct optimization. They must first prove a relationship to later reconciled YAN revenue.

Audit/apply runtime:

`python3 -m profit_engine_runtime.metrica_goals_cli`

Default is read-only audit. `--apply-missing` may create only missing canonical exact goals, never update/delete, and requires read-back PASS.

## Existing site hooks / invariants

Source inventory confirms current custom T123 contract includes hooks such as:

- `data-dv-page`;
- `data-dv-story-slug`;
- `data-dv-story-text`;
- `data-dv-choice`;
- `data-dv-reveal`;
- `data-dv-goal`;
- `data-dv-ad-block`.

Production instrumentation must consume these hooks without renaming/breaking current story code.

Existing YAN block configuration must remain untouched during Task 013.

## Site kill switches

Required independent safety:

- Task-006 event dispatch stays disabled until endpoint acceptance;
- `window.PROFIT_ENGINE_METRICA_GOALS_KILL=true` disables the new Metrica goal bridge;
- existing SiteAgent/event-layer kill switches remain authoritative;
- removal of the injected global scripts + republish is the hard rollback.

## Production publication gate

Task 013 must publish the site instrumentation globally through Tilda custom code.

Current project tools do not have a Tilda write connector. Tilda officially supports site-wide custom head code via `Site Settings -> More -> HTML code for the head section`, and T123 for page-body custom code. Therefore one final external Tilda UI paste/publish step is unavoidable; Central Brain owns the exact tested package and validation, Owner should only perform that external UI action.

Production acceptance requires:

1. event layer loaded exactly once;
2. Metrica goal bridge loaded exactly once;
3. story navigation/choice/reveal unchanged;
4. YAN blocks unchanged and rendering;
5. canonical goals actually arrive in Metrica;
6. no duplicate goal storm;
7. no new console/network errors from Profit Engine;
8. rollback verified/documented.

## Money/optimization state

K5 target remains:

`YAN revenue / Direct spend >= 5.0`

No current site behavior metric can replace K5.

Landing routing, recirculation and ad-placement experiments remain blocked from autonomous production optimization until instrumentation + money attribution are live and their causal/economic evidence is sufficient.

## P0 site next order

1. re-read YAN→Metrica monetization propagation;
2. audit/create canonical Metrica goals;
3. publish Task-006 event layer + Metrica goal bridge globally in Tilda;
4. live-validate goals and site regressions;
5. deploy first-party event ingestion endpoint;
6. enable event dispatch only after endpoint acceptance;
7. materialize behavior/cohort evidence;
8. use that evidence in manual-search controller and later site experiments.

## Acceptance state

`DILIVOX_SITE_WORKSTREAM_OWNER_APPROVED = true`

`DILIVOX_PRODUCTION_INSTRUMENTATION_LIVE = false`

`DILIVOX_METRICA_GOALS_LIVE_VERIFIED = false`

`DILIVOX_FIRST_PARTY_EVENT_ENDPOINT_LIVE = false`

Until those production facts change with evidence, the complete first-site ecosystem is not launch-complete.
