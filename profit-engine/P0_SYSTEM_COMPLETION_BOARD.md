# PROFIT ENGINE — P0 SYSTEM COMPLETION BOARD

Status: CANONICAL OPERATIONAL AUTHORITY
Updated: 2026-09-01
Owner: project Owner
Central Brain: ChatGPT
Source of truth: `niknikdym-hue/Dilivox-1` / `profit-engine`

This board answers what is live, what is only code-ready, what blocks K5, and what happens next. Code/tests alone never equal production completion.

## North-star economics

Target:

`K5 = attributable YAN/RSYA revenue / Yandex Direct spend >= 5.0`

K5 remains a target until mature reconciled live data proves it.

## Current P0 gates

| # | System layer | Current state | Production truth | Required closure |
|---|---|---|---|---|
| 1 | Direct Managing Account Editing | PASS | live exact Direct read passed | keep exact target binding |
| 2 | Direct/Metrica/YAN provider reads | PASS | all provider reads live | keep provider-specific credentials |
| 3 | Exact Dilivox campaign inventory | PASS | 46 campaigns read; exact Dilivox pair isolated | use only exact IDs |
| 4 | YAN → Metrica monetization link | **LIVE TECHNICAL PASS** | post-Owner bootstrap reached `READ_MODEL_READY`; runtime can reach that only when `yan_total_by_date` monetization probe is PASS | keep monitoring freshness; no inference across campaigns |
| 5 | Metrica conversion goals | **LIVE PASS** | 27 provider goals after apply; all five canonical PE goals PASS, missing/invalid/duplicate = 0; `APPLIED_AND_VERIFIED` | validate real arrivals after site publication |
| 6 | Dilivox Metrica goal bridge | RECONCILED / CODE_READY / NOT_PUBLISHED | pre-existing `DILIVOX_SYSTEM_V1` is the sole event source; tested idempotent bridge normalizes it to the five live goals without counter init or duplicate progress/navigation listeners | after acceptance publish one bridge once and live-probe |
| 7 | SiteAgent + event layer | CODE_ACCEPTED / NOT_PUBLISHED SEPARATELY | accepted Task-005/006 artifacts remain source contracts; the Task-006 DOM controller is excluded from this package to prevent duplicate listeners | do not publish separately until a later accepted first-party endpoint requires it |
| 8 | First-party event endpoint | SPECIFIED / NOT_DEPLOYED | raw-first endpoint design exists | Privacy v2 first, then deploy and smoke |
| 9 | Money preflight | **LIVE RAN / CENTRAL-BRAIN REVIEW REQUIRED** | `READ_MODEL_READY` means both exact campaign preflights completed without runtime `ERROR`; exact spend/revenue/K5 outcomes still need review | inspect exact money evidence before any Direct smoke |
| 10 | First reversible Direct smoke | READY_IN_CODE / NOT_AUTHORIZED | one-shot suspend/resume writer accepted; no live mutation sent | choose one lowest-downside exact action from money evidence, rebuild proposal/Governor/plan, explicit Owner authorization, one attempt |
| 11 | Local control panel | INSTALLED / RUSSIAN UI / WRITE LOCKED | `~/Applications/Profit Engine.app`; provider-write endpoint absent | keep refreshed with live truth |
| 12 | Manual Search Profit Control | MS1+MS2+MS3 ACCEPTED | exact read model + attribution boundary + shadow controller | MS4 panel integration next |
| 13 | Dedicated manual-search campaign | MS5 DRY-RUN ACCEPTED / NOT_CREATED | `DILIVOX | SEARCH | PROFIT ENGINE`, Search-only, network off | MS6 guarded create acceptance later |
| 14 | Keyword bid automation | SHADOW READY / WRITER ABSENT | bounded recommendations only | MS7 guarded `KeywordBids.set` later |
| 15 | Site-side optimization experiments | DESIGN/ARTIFACTS ONLY | no production closed loop yet | instrument + establish K5 before experiments |

## Exact current Dilivox campaigns

- `712203524` — `Dilivox` — last live inventory `SUSPENDED` / `ACCEPTED`.
- `712791195` — `dilivox.ru` — last live inventory `ACTIVE` / `ACCEPTED`.

No other campaign is eligible for the first Dilivox smoke without a new exact selection.

## Canonical Metrica goals — LIVE VERIFIED

Counter: `110349067`.

Required and now live/read-back verified:

1. `pe_story_progress_75`;
2. `pe_version_selected`;
3. `pe_story_completed`;
4. `pe_next_story_clicked`;
5. `pe_return_visit`.

All are proxy goals and remain `native_bidding_eligible=false` until later revenue validation.

Credential boundary:

- Direct credential: existing Direct Keychain reference;
- Metrica read credential: `providers.metrica.token_source_ref`;
- Metrica write credential: `providers.metrica.write_token_source_ref`;
- default write service: `ProfitEngine-MetricaOAuth-Write` / `profit-engine`;
- YAN Stats keeps its own credential.

The working Direct OAuth app was not modified. Separate `Profit Engine — Metrica Admin` with `metrika:read` + `metrika:write` is verified.

Evidence:
`evidence/TASK-013-METRICA-GOALS-AND-READ-MODEL-PASS-2026-09-01.md`.

## Site production package — CURRENT MANUAL P0 STEP

Prepared package:
`~/.config/profit-engine/tilda/dilivox-profit-engine-head-v1.html`

Production source artifact:

- `sites/dilivox/tilda/dilivox-metrica-goals-v1.js` — the single idempotent normalizer over existing `DILIVOX_SYSTEM_V1`.

`dilivox-event-layer-task006.js` remains an accepted source contract but is deliberately absent from this production package.

Required publication order:

1. keep the current counter, `DILIVOX_SYSTEM_V1`, and YAN blocks unchanged and exactly once;
2. paste/replace the minimal Profit Engine bridge once immediately after `DILIVOX_SYSTEM_V1`;
3. do not add the Task-006 event-layer file separately;
4. publish all pages after acceptance;
5. run live-site probe and verify one bridge, no duplicate goal dispatch, and no YAN/layout/story regression;
6. validate real canonical goal arrivals.

First-party event dispatch stays disabled until Privacy v2 + endpoint acceptance.

## Direct write governance

First real smoke remains restricted to exactly one campaign object and one transition:

- `campaign.suspend` only if fresh state is ACTIVE; or
- `campaign.resume` only if fresh state is SUSPENDED.

No ad-object first smoke. `campaign.update_budget` is not live-enabled. No blind retry.

Before dispatch:

1. exact money evidence review;
2. fresh ActionProposal;
3. Budget Governor;
4. exact ControllerPlan binding;
5. explicit Owner authorization for the exact action;
6. one-shot arm <= 5 minutes;
7. target lock + fresh preflight + TOCTOU + kill switch;
8. exactly one mutation network attempt;
9. immediate read-back + immutable audit.

## Manual Search priority

`DILIVOX | SEARCH | PROFIT ENGINE` remains the primary acquisition-controller development path.

Target shape:

- Unified Campaign;
- Search only;
- `HIGHEST_POSITION`;
- network `SERVING_OFF`;
- Owner-fixed `WeeklySpendLimit` initially;
- `KeywordBids.get` read model;
- K5/confidence shadow decisions;
- later separately accepted guarded `KeywordBids.set`.

Next build slice: **MS4 — integrate shadow-controller output into the Russian local panel.**

## Owner-authority invariants

- weekly budget auto-growth through +20.00% can only become eligible after all other gates pass;
- +20.01% or more requires exact Owner approval;
- manual bid moves never silently change weekly capital;
- no motivated/artificial/incentivized traffic or clicks;
- exact identity only;
- private core remains proposal-only;
- no secrets in Git/chat/logs;
- no blind mutation retry.

## Next-action resolver

Always take the first unresolved launch item; independent read-only development may proceed in parallel.

1. **publish and live-verify the prepared Tilda site-wide instrumentation package**;
2. **review exact money preflight outcomes for both Dilivox campaigns**;
3. choose and prepare one reversible Direct smoke, but do not dispatch without exact Owner authorization;
4. refresh panel with accepted live truth and complete MS4;
5. publish Privacy v2 + first-party event endpoint;
6. later accept MS6 campaign creation and MS7 guarded bid writer;
7. graduate supervised → bounded automatic operation only on evidence.

## Definition of complete first-site ecosystem

Complete only when acquisition, site behavior, YAN monetization, K5, guarded Direct/site actions, local control panel, and manual-search controller are all live-evidenced and no component can expand capital or mutate providers outside Owner governance.
