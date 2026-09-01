# DILIVOX SITE STATE

Status: P0 PRODUCTION INSTRUMENTATION INCOMPLETE
Updated: 2026-09-01
Site: `dilivox.ru`
Site ID: `dilivox`
Platform: Tilda + custom T123/HTML/JS
Canonical operational board: `profit-engine/P0_SYSTEM_COMPLETION_BOARD.md`

## Product role

Dilivox is the first full site-side node of Profit Engine.

Required loop:

`Direct -> Dilivox -> attributable reader -> behavior/content path -> YAN revenue -> Metrica/YAN reconciliation -> K5 -> guarded decision/action -> measured money outcome`.

## Live and verified

- public `dilivox.ru` is live;
- YAN Statistics for the domain is readable;
- Metrica counter `110349067` is readable;
- Direct campaign attribution dimensions are readable in Metrica;
- YAN→Metrica monetization has now passed technical read-back: the canonical bootstrap reached `READ_MODEL_READY`, which runtime only permits when monetization probe `yan_total_by_date` is PASS;
- exact two Dilivox campaigns are readable;
- all five canonical Profit Engine Metrica goals are now live and read-back verified;
- Metrica provider goal count is 27; missing/invalid/duplicate canonical IDs are all zero;
- separate Metrica administration OAuth boundary is verified; Direct OAuth was not modified.

Evidence:
`profit-engine/evidence/TASK-013-METRICA-GOALS-AND-READ-MODEL-PASS-2026-09-01.md`.

## Canonical Metrica goals — LIVE PROVIDER VERIFIED

Counter: `110349067`.

- `pe_story_progress_75`;
- `pe_version_selected`;
- `pe_story_completed`;
- `pe_next_story_clicked`;
- `pe_return_visit`.

These remain proxy goals and `native_bidding_eligible=false` until later revenue validation.

## Implemented but NOT yet published on production Tilda

Accepted event layer:
`profit-engine/sites/dilivox/tilda/dilivox-event-layer-task006.js`

Metrica goal bridge:
`profit-engine/sites/dilivox/tilda/dilivox-metrica-goals-v1.js`

Prepared one-paste site-wide HEAD package:
`~/.config/profit-engine/tilda/dilivox-profit-engine-head-v1.html`

Latest live probe still fails closed:

- `site_instrumentation_live=false`;
- `site_probe_exit_code=2`.

Therefore provider-side goals are live, but production browser instrumentation is not yet launch-complete and real goal arrivals are not yet accepted.

## Publication invariants

During Tilda publication:

- keep all existing YAN ad-block code unchanged;
- consume existing `data-dv-*` hooks without renaming them;
- load event layer exactly once;
- load Metrica bridge exactly once;
- first-party dispatch remains disabled;
- story navigation/choice/reveal behavior must remain unchanged;
- no duplicate goal storm;
- no new Profit Engine console/network errors.

Emergency Metrica bridge kill:
`window.PROFIT_ENGINE_METRICA_GOALS_KILL=true`.

Hard rollback: remove injected global Profit Engine code and republish.

## First-party event endpoint

NOT LIVE.

Task 015 remains the authority for a durable raw-first endpoint. Privacy v2 must be published before first-party production event dispatch is enabled.

## Money/optimization state

K5 target remains:

`YAN revenue / Direct spend >= 5.0`

Current bootstrap state is `READ_MODEL_READY`, so money preflight executed without runtime error. Exact spend/revenue/K5 outcomes for the two campaigns still require Central Brain review before any reversible Direct smoke selection.

No site behavior metric replaces K5.

## P0 site next order

1. publish the prepared Profit Engine block into Tilda **site-wide HEAD**;
2. publish all pages;
3. rerun live-site probe;
4. verify real canonical goal arrivals and no site/YAN regression;
5. later publish Privacy v2 + first-party endpoint;
6. enable first-party dispatch only after endpoint acceptance.

## Acceptance state

`DILIVOX_SITE_WORKSTREAM_OWNER_APPROVED = true`

`DILIVOX_METRICA_GOALS_LIVE_VERIFIED = true`

`DILIVOX_YAN_METRICA_MONETIZATION_LIVE_VERIFIED = true`

`DILIVOX_PRODUCTION_INSTRUMENTATION_LIVE = false`

`DILIVOX_FIRST_PARTY_EVENT_ENDPOINT_LIVE = false`

The complete first-site ecosystem is not launch-complete until production instrumentation and subsequent economic/control gates are closed.
