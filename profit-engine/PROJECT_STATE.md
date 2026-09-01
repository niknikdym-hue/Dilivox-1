# PROFIT ENGINE — PROJECT STATE

Status: P0 SYSTEM COMPLETION / SITE PUBLICATION + MONEY REVIEW
Updated: 2026-09-01
Canonical public branch: `profit-engine`
Private core branch: `main`
Operational authority: `profit-engine/P0_SYSTEM_COMPLETION_BOARD.md`
Tracking issue: `#19 — Profit Engine Task 012 — Live guarded production launch`

## Objective

Build and operate the complete Dilivox profit loop:

`Yandex Direct -> Dilivox -> attributable reader behavior -> YAN/RSYA revenue -> Metrica/YAN reconciliation -> K5 -> proposal/Governor -> guarded Direct/site actions -> measured money outcome`.

First site: `site_id=dilivox` / `dilivox.ru`.
Target: `1 RUB Direct spend -> 5 RUB attributable YAN/RSYA revenue`.
K5=5 is a target, not yet an economically proven result.

## Central Brain rule

GitHub is source of truth. Distinguish `CODE_READY`, `LIVE_PROVIDER_VERIFIED`, `LIVE_SITE_VERIFIED`, and `ECONOMICALLY_PROVEN`.

Owner restored Codex permission on 2026-09-01. Codex may execute bounded P0 implementation slices; Central Brain retains architecture, sequencing and acceptance.

## Locked governance

- private core is proposal-only;
- exact provider identity only;
- no secrets in Git/chat/logs;
- no blind mutation retry;
- first Direct write = exactly one campaign object;
- first method restricted to `campaign.suspend` or `campaign.resume`;
- `campaign.update_budget` not live-enabled for first launch;
- weekly budget increase > +20.00% requires explicit Owner approval;
- manual bid control never silently changes weekly capital;
- no motivated/artificial/incentivized traffic or ad clicks.

## Live provider state

Direct Managing Account/operator `reklamadymova` has Editing access. Fresh exact provider reads passed for Direct, Metrica and YAN.

Exact Dilivox campaigns:

- `712203524` — `Dilivox` — last live `SUSPENDED` / `ACCEPTED`;
- `712791195` — `dilivox.ru` — last live `ACTIVE` / `ACCEPTED`.

Other campaigns are excluded from first Dilivox smoke.

## YAN → Metrica monetization — LIVE TECHNICAL PASS

Owner enabled YAN reports for Metrica counter `110349067` on 2026-08-31.

The 2026-09-01 canonical bootstrap subsequently reached `READ_MODEL_READY`. By runtime definition that state is only reachable after the monetization probe `yan_total_by_date` returns PASS. The old `partner is not enabled for 110349067` propagation blocker is therefore closed.

## Canonical Metrica goals — LIVE PASS

Separate OAuth app: `Profit Engine — Metrica Admin`.
Scopes: `metrika:read` + `metrika:write`.
The working Direct OAuth application was not modified.

Live missing-only apply + read-back result:

- provider goals: 27;
- missing canonical goals: 0;
- invalid canonical IDs: 0;
- duplicate canonical IDs: 0;
- HTTP 200;
- audit `PASS`;
- apply `APPLIED_AND_VERIFIED`;
- terminal marker `METRICA_WRITE_SCOPE_VERIFIED`.

Canonical goals:

- `pe_story_progress_75`;
- `pe_version_selected`;
- `pe_story_completed`;
- `pe_next_story_clicked`;
- `pe_return_visit`.

All remain `native_bidding_eligible=false` until revenue validation.

Evidence:
`evidence/TASK-013-METRICA-GOALS-AND-READ-MODEL-PASS-2026-09-01.md`.

## Money preflight — LIVE RAN / CENTRAL-BRAIN REVIEW REQUIRED

The bootstrap reached `READ_MODEL_READY`, which also means both exact Dilivox campaign money preflights completed without runtime `ERROR`.

This does **not** by itself prove K5>=5 and does not grant Direct write authority. Exact money outcomes still need Central Brain review before choosing any reversible smoke action.

## Production site instrumentation — CURRENT P0 BLOCKER

Provider-side goals and monetization are ready, but browser instrumentation is not published on production Tilda.

The pre-existing Dilivox global UX/Metrica implementation was reconciled before
publication. `DILIVOX_SYSTEM_V1` remains the sole authoritative UX/event source
for reading progress, story choice/reveal and next-story navigation. The Profit
Engine package is now only one idempotent Metrica normalizer: it initializes no
counter, installs no second progress/navigation controller, maps the existing
legacy 75%/next-story signals, and adds only the missing canonical choice,
completion and return-visit mappings.

Latest bootstrap:

- `site_instrumentation_live=false`;
- `site_probe_exit_code=2`;
- prepared package: `~/.config/profit-engine/tilda/dilivox-profit-engine-head-v1.html`.

Current project tools have no Tilda write connector. After Central Brain accepts
the reconciliation, the single Owner step is to keep the existing counter and
`DILIVOX_SYSTEM_V1` once, paste/replace the one minimal Profit Engine bridge once
immediately after it, publish all pages, and rerun live-site verification. Do not
publish `dilivox-event-layer-task006.js` as a second DOM controller.

First-party event dispatch remains disabled until Privacy v2 + endpoint acceptance.

## Local control panel

Installed at `~/Applications/Profit Engine.app`.

- Russian UI;
- localhost only `127.0.0.1:8765`;
- provider-write endpoints absent;
- writer `LOCKED`;
- current bootstrap resolved `state=READ_MODEL_READY`.

## Production Direct writer

Accepted in code, no live Direct mutation has been sent.

First smoke requires fresh exact money review, one ActionProposal/Governor/ControllerPlan, explicit Owner authorization for the exact action, <=5 minute arm, exact target lock, fresh state/TOCTOU/kill-switch checks, exactly one mutation network attempt, immediate read-back and immutable audit.

## Manual Search Profit Control — development priority

Dedicated concept: `DILIVOX | SEARCH | PROFIT ENGINE`.

Accepted:

- MS1 exact read model;
- MS2 attribution-grain boundary;
- MS3 shadow controller;
- MS5 dedicated campaign dry-run.

Next build slice: **MS4 panel integration**.
MS6 guarded campaign create is not authorized.
MS7 guarded `KeywordBids.set` is not implemented/authorized.

## Current next order

1. publish and live-verify Tilda site-wide instrumentation;
2. review exact money preflight outcomes for both Dilivox campaigns;
3. choose/prepare one reversible Direct smoke, without dispatch until exact Owner authorization;
4. refresh/extend Russian panel with MS4 shadow output;
5. Privacy v2 + first-party endpoint;
6. later MS6/MS7 and supervised live learning.

## Completion definition

First-site ecosystem is complete only when paid acquisition, production behavior instrumentation, YAN monetization, reconciled K5, guarded Direct/site actions, local Owner panel and manual-search control are all live-evidenced and capital/provider writes remain inside Owner governance.
