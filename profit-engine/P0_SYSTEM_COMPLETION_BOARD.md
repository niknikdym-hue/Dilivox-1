# PROFIT ENGINE — P0 SYSTEM COMPLETION BOARD

Status: CANONICAL OPERATIONAL AUTHORITY
Updated: 2026-08-31
Owner: project Owner
Central Brain: ChatGPT
Source of truth: `niknikdym-hue/Dilivox-1` / `profit-engine`

This board is the single operational answer to: **what works in production, what is only implemented in code, what is missing, what blocks K5, and what must happen next.**

No task may be called launch-complete merely because code/tests exist. Production evidence is required for production rows.

## North-star economics

Target:

`K5 = attributable YAN/RSYA revenue / Yandex Direct spend >= 5.0`

K5 is not yet proven. CTR, CPC, visit depth, completion and ad impressions are supporting signals, not the economic objective.

## Current P0 gates

| # | System layer | Current state | Production truth | Required closure |
|---|---|---|---|---|
| 1 | Direct Managing Account Editing | PASS | Owner Editing evidence + live Direct read PASS | keep exact target binding; no action |
| 2 | Direct/Metrica/YAN provider reads | PASS | all three providers returned live PASS | keep health checks in control panel |
| 3 | Exact Dilivox campaign inventory | PASS | 46 campaigns read; exact Dilivox pair isolated | use only exact IDs |
| 4 | YAN → Metrica monetization link | PROPAGATION_PENDING | Owner enabled YAN reports for counter `110349067`; last provider read before enable returned `partner is not enabled` | recheck until `ym:s:yanPartnerPrice` is readable; no Direct write before PASS |
| 5 | Metrica conversion goals | CODE_READY / LIVE_AUDIT_PENDING | canonical 5-goal registry + audit/apply runtime implemented | live audit; create only missing exact goals; read-back PASS |
| 6 | Dilivox Metrica goal bridge | CODE_READY / NOT_PUBLISHED | tested production-safe JS maps existing `data-dv-*` hooks to canonical goals | publish globally in Tilda; verify live goal arrivals |
| 7 | SiteAgent + first-party event layer | CODE_ACCEPTED / NOT_PUBLISHED | Task 005/006 artifacts exist; historical evidence explicitly says publication was not performed | publish accepted event layer in Tilda with dispatch disabled until endpoint is live |
| 8 | First-party event endpoint | SPECIFIED / NOT_DEPLOYED | Task 015 now requires durable raw-first endpoint; current browser controller has no production transport | publish Privacy v2 first; deploy endpoint/persistent store; then bounded live event smoke |
| 9 | Money preflight | CODE_READY / BLOCKED_BY_GATE_4 | Direct spend read works; Metrica monetization read blocked until propagation | run same-window money preflight on both exact Dilivox campaigns |
| 10 | First reversible Direct smoke | READY_IN_CODE / NOT_AUTHORIZED_YET | one-shot suspend/resume writer accepted; no live mutation sent | after money evidence select exactly one candidate, rebuild exact proposal/Governor/plan, arm and dispatch once |
| 11 | Local control panel | CODE_READY / NOT_INSTALLED | localhost-only app + installer/bootstrap exist; provider writes physically absent | run P0 Mac bootstrap; install `~/Applications/Profit Engine.app`; refresh read model |
| 12 | Manual Search Profit Control | MS1+MS2+MS3 CODE_ACCEPTED | read model + attribution grain + non-executable shadow controller are CI-green; no live dedicated campaign exists | MS4 panel integration, then guarded create/bid gates |
| 13 | Dedicated manual-search campaign | MS5 DRY-RUN ACCEPTED / NOT_CREATED | exact inert proposal `DILIVOX | SEARCH | PROFIT ENGINE` is CI-green | MS6 separate guarded create acceptance; Owner-fixed weekly budget first |
| 14 | Keyword bid automation | SHADOW CONTROLLER READY / WRITER ABSENT | controller can `LEARN/HOLD/RAISE/LOWER/PAUSE/QUARANTINE`; `KeywordBids.set` not implemented/authorized | MS7 guarded one/few-bid writer → supervised live learning → only then automation |
| 15 | Site-side optimization experiments | DESIGN/ARTIFACTS ONLY | placement/experiment registries exist, production closed-loop site actions not proven | instrument first, establish K5 data, then controlled landing/recirculation/ad-layout experiments |

## Canonical Dilivox campaigns for current Day-12 closure

- `712203524` — `Dilivox` — last live inventory state `SUSPENDED` / `ACCEPTED`.
- `712791195` — `dilivox.ru` — last live inventory state `ACTIVE` / `ACCEPTED`.

No other campaign is eligible for the first Dilivox smoke without a new exact Central Brain selection.

## Canonical Metrica goals

Counter: `110349067`.

Registry: `profit-engine/sites/dilivox/metrica-goals.json`.

Required exact identifiers:

1. `pe_story_progress_75` — engagement proxy;
2. `pe_version_selected` — interaction proxy;
3. `pe_story_completed` — high-value completion proxy;
4. `pe_next_story_clicked` — recirculation proxy;
5. `pe_return_visit` — return-value proxy.

All are **proxy goals**, initially `native_bidding_eligible=false`. A goal can be promoted into native Direct optimization only after measured revenue validation against later reconciled YAN revenue. K5 remains primary truth.

## Site production package

Existing accepted but unpublished artifact:

`profit-engine/sites/dilivox/tilda/dilivox-event-layer-task006.js`

New goal bridge:

`profit-engine/sites/dilivox/tilda/dilivox-metrica-goals-v1.js`

One-paste global package builder:

`profit-engine/scripts/prepare-dilivox-tilda-production-head.sh`

Required production order:

1. keep current YAN ad-block code unchanged;
2. publish the accepted Task-006 event layer once, globally, with first-party dispatch disabled until endpoint acceptance;
3. publish `dilivox-metrica-goals-v1.js` after Metrica is present;
4. validate no layout/choice/reveal/YAN regression;
5. validate canonical goals in Metrica;
6. later enable first-party event dispatch only after Privacy v2 + endpoint acceptance.

Tilda production publication is an unavoidable external UI step with the currently available project tools. Code preparation, tests and exact publication package are Central Brain responsibility; Owner should only perform the final Tilda paste/publish action when instructed.

## P0 manual-search implementation order

This sequence outranks CPA/DRR/Maximum-Profit feature work until a manual-search baseline exists.

1. **MS0 — money truth:** close YAN→Metrica propagation and K5 preflight. `LIVE PENDING`.
2. **MS1 — read model:** exact campaign/ad-group/keyword inventory, `KeywordBids.get`, auction levels and Direct Reports cost/CPC. `CODE_ACCEPTED`.
3. **MS2 — attribution grain:** exact criterion/query-cluster revenue only; campaign/landing revenue cannot be fabricated into keyword K5. `CODE_ACCEPTED`.
4. **MS3 — shadow bid controller:** bounded deterministic `LEARN/HOLD/RAISE/LOWER/PAUSE/QUARANTINE`; no provider writes. `CODE_ACCEPTED`.
5. **MS4 — operator panel integration:** show current bid, spend, revenue evidence, K5/confidence and recommended move. `NEXT MANUAL-SEARCH BUILD`.
6. **MS5 — dedicated campaign dry-run:** exact inert `DILIVOX | SEARCH | PROFIT ENGINE`, search-only, `HIGHEST_POSITION`, network off, Owner-fixed `WeeklySpendLimit`. `CODE_ACCEPTED`.
7. **MS6 — guarded create:** separately accept campaign/ad-group/ad/keyword creation; Task-012 suspend/resume authority does not cover create. `NOT AUTHORIZED`.
8. **MS7 — guarded `KeywordBids.set`:** exact bounded targets, max-step gate, one-shot/no-blind-retry/read-back/audit. `NOT IMPLEMENTED`.
9. **MS8 — supervised live learning:** Owner-fixed weekly budget, bounded bid movements only. `NOT STARTED`.
10. **MS9 — automatic bid loop:** only after accepted live evidence; budget growth remains independently governed. `NOT STARTED`.
11. **MS10 — benchmark:** compare manual controller to provider-native CPC/CPA/DRR/Maximum Profit by reconciled economics. `NOT STARTED`.

Accepted evidence:

- `evidence/TASK-014-MS1-MANUAL-SEARCH-READ-MODEL.md`;
- `evidence/TASK-014-MS2-MS3-ATTRIBUTION-AND-SHADOW-CONTROLLER.md`;
- `evidence/TASK-014-MS5-DEDICATED-MANUAL-SEARCH-DRY-RUN.md`.

## Control-panel minimum contract

Local only: `127.0.0.1`.

Must show without clutter:

- system/gate status;
- Direct/Metrica/YAN health;
- YAN→Metrica monetization status;
- exact two current Dilivox campaigns;
- spend, YAN revenue and K5 when computable;
- canonical Metrica goals and live audit state;
- manual-search P0 state;
- latest controller recommendation when a dedicated/manual campaign cell exists;
- kill switch / writer lock / latest read-back.

No unguarded provider-write endpoint is allowed in the panel.

## Owner-authority invariants

- automatic weekly budget growth through +20.00% can be eligible only after all other gates pass;
- +20.01% or more requires exact Owner approval;
- manual bid movement never silently changes the weekly capital limit;
- no motivated traffic, artificial engagement or incentivized ad clicks;
- no blind mutation retry;
- exact provider identity only;
- private core remains proposal-only;
- secrets never enter Git/chat/logs.

## Next-action resolver

Always take the first unresolved item below; do not skip forward because a later feature is easier:

1. verify YAN→Metrica propagation;
2. live-audit/apply canonical Metrica goals;
3. publish/verify site instrumentation;
4. restore exact money preflight;
5. complete first reversible Direct smoke;
6. install/refresh local control panel;
7. integrate MS1/MS2/MS3 shadow output into the panel;
8. publish Privacy v2 and deploy first-party event endpoint;
9. accept/create dedicated manual-search campaign under MS6;
10. accept guarded bid writer MS7;
11. graduate bid controller supervised → bounded automatic only on evidence.

## Definition of complete first-site ecosystem

Dilivox Profit Engine is complete only when all of these are simultaneously true:

- acquisition is exactly attributable;
- site behavior is instrumented in production;
- YAN monetization is measurable and reconcilable;
- goals/proxies are live and revenue-validated before optimization use;
- K5 is computable on mature evidence;
- Direct actions pass Governor/safety gates and read-back;
- site changes have independent kill switches and measured outcomes;
- Owner has a local control panel showing current money truth and control state;
- manual-search controller can safely learn and, after evidence, operate bounded bids;
- no component can expand capital or mutate providers outside Owner governance.
