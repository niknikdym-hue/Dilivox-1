# PROFIT ENGINE — PROJECT STATE

Status: P0 SYSTEM COMPLETION / METRICA WRITE + MONEY + SITE GATES
Updated: 2026-09-01
Canonical public branch: `profit-engine`
Private core branch: `main`
Operational authority: `profit-engine/P0_SYSTEM_COMPLETION_BOARD.md`
Tracking issue: `#19 — Profit Engine Task 012 — Live guarded production launch`

## Objective

Build and operate the complete Dilivox profit loop:

`Yandex Direct -> Dilivox -> attributable reader behavior -> YAN/RSYA revenue -> Metrica/YAN reconciliation -> K5 -> proposal/Governor -> guarded Direct and site actions -> measured money outcome`.

First production site: `site_id=dilivox` / `dilivox.ru`.

Economic target:

`1 RUB Direct spend -> 5 RUB attributable YAN/RSYA revenue`.

This is a target, not yet a claimed result.

## Central Brain operating rule

GitHub is source of truth. The project is run as a system, not as isolated tasks.

Every production claim must distinguish:

- `CODE_READY`;
- `LIVE_PROVIDER_VERIFIED`;
- `LIVE_SITE_VERIFIED`;
- `ECONOMICALLY_PROVEN`.

Code/tests alone never imply production completion.

Owner explicitly restored permission to use Codex on 2026-09-01. Codex may now be used as an executor for bounded P0 implementation slices when useful. Central Brain retains architecture, sequencing and acceptance authority.

## Locked governance

- private core is proposal-only and never calls providers;
- exact target identity only; no fuzzy inference;
- no secrets in Git/chat/evidence/logs;
- no blind mutation retry;
- first Direct production write: exactly one provider object;
- first Direct method restricted to `campaign.suspend` or `campaign.resume`;
- no ad-object first smoke without equivalent Ads inventory evidence;
- `campaign.update_budget` is not live-enabled for first launch;
- automatic weekly budget increase through +20.00% may only be eligible after all other gates pass;
- +20.01% or more requires exact explicit Owner approval;
- manual bid automation never silently expands the weekly capital limit;
- no motivated traffic, artificial engagement or incentivized ad clicks.

## Accepted engineering baseline

Tasks 001–010R: accepted public/private data, attribution, money-ledger, campaign-factory and allocator contracts.

Task 011 + 011R: accepted guarded Direct controller:

- exact proposal/Governor/target binding;
- trusted Owner >20% approval boundary;
- fresh provider preflight;
- lock + TOCTOU + kill switch;
- one-object request binding;
- immediate read-back;
- immutable audit;
- no blind retry.

Accepted controller SHA:
`a494d30b49c8d11687be56cdab870a5d83356e02`.

Private core remains:
`niknikdym-hue/profit-engine-core/main` = `76b1b8670690f102a045243760dfe3d1e58513d5`, proposal-only.

## Direct identity and live access — PASS

Technical Managing Account/operator:
`reklamadymova`.

Exact owner advertiser target is distinct and privately bound locally.

Owner changed the exact Managing Account relationship to **Editing**.

Fresh live post-Editing certification subsequently passed:

- Direct operator identity: PASS;
- exact managed target `Campaigns.get`: PASS;
- `Units-Used-Login` exact target check: PASS;
- Metrica counter `110349067`: PASS for reads;
- YAN Statistics `dilivox.ru`: PASS;
- readiness: `READY_FOR_LIVE_CANDIDATE_SELECTION`.

Therefore the old “Owner Editing / fresh certification pending” state is CLOSED and must not be reused.

Canonical evidence:

- `evidence/TASK-012-LIVE-PROVIDER-BINDING.md`;
- `evidence/TASK-012-POST-EDITING-PROVIDER-READ-REWORK.md`;
- `evidence/TASK-012-LIVE-READINESS-AND-CAMPAIGN-INVENTORY-PASS.md`.

## Exact Direct inventory — PASS

Fresh read-only inventory returned 46 campaigns.

Only current exact Dilivox candidate pair:

- `712203524` — `Dilivox` — last read `SUSPENDED` / `ACCEPTED`;
- `712791195` — `dilivox.ru` — last read `ACTIVE` / `ACCEPTED`.

Other active campaigns belong to other sites/products and are excluded from the first Dilivox smoke.

## YAN → Metrica monetization — OWNER CONFIGURED / TECHNICAL PASS PENDING

The first money preflight reached Metrica and returned HTTP 400 on `ym:s:yanPartnerPrice`.

A bounded six-request compatibility probe proved:

- Direct campaign attribution + ordinary visits: HTTP 200, 50 rows, unsampled;
- every monetization probe: HTTP 400;
- exact provider message: `partner is not enabled for 110349067`.

Owner then enabled YAN reports in Metrica for Dilivox and bound counter `110349067`.

Provider propagation/read-back is still required. Owner UI state is not substituted for API evidence.

Runtime classifies this condition fail-closed instead of traceback.

Evidence:
`evidence/TASK-012-METRICA-YAN-MONETIZATION-LINK-BLOCKER.md`.

## Money preflight — CODE READY / LIVE RE-RUN PENDING

Canonical Day-12 money authority:

- Direct spend from official `/json/v501/reports`, exact campaign filter, explicit completed period, RUB basis;
- Metrica exact counter/campaign attribution at full accuracy;
- independent YAN Statistics exact-domain revenue control total;
- zero spend never becomes fake/infinite K5;
- sampled/sensitive/identity/reconciliation failures hold closed.

Money states:

- `READY_FOR_CANDIDATE_EVALUATION`;
- `NO_DIRECT_SPEND`;
- `HOLD_DATA_QUALITY`.

No money-preflight result itself grants provider write authority.

Next live money step is blocked on YAN→Metrica monetization technical read-back, not on Metrica goal creation.

## Production Direct writer — READY IN CODE / NO LIVE WRITE YET

One-shot JSON v501 production writer and execution harness are accepted in code.

It enforces:

- exact arm/plan/preflight binding;
- maximum five-minute arm TTL;
- target lock;
- fresh state read;
- coherent transition (`ACTIVE -> suspend`, `SUSPENDED -> resume`);
- TOCTOU check;
- runtime kill switch;
- `DISPATCH_STARTED` audit before send;
- exactly one network mutation attempt;
- exactly one provider object;
- immediate read-back;
- no blind retry;
- uncertainty classification instead of guessing.

No real Direct mutation has yet been sent.

## Weekly budget — READ/SHADOW ONLY

Current Direct budget truth is strategy-aware `WeeklySpendLimit`; old `DailyBudget` launch assumption is retired.

Read-only planner/probe and Governor bridge are accepted.

`campaign.update_budget` remains NOT live-enabled.

Manual-search first learning will keep `WeeklySpendLimit` Owner-fixed while bid logic is developed separately.

## Dilivox site workstream — OWNER APPROVED / PRODUCTION INCOMPLETE

Owner approved the full site-side workstream on 2026-08-26 in:
`OWNER_APPROVAL_DILIVOX_SITE_WORKSTREAM.md`.

Production truth:

- source hooks/placement/content registries exist;
- Task-005 SiteAgent exists;
- Task-006 event layer exists;
- historical Task-006 evidence explicitly says Tilda publication was not performed and production dispatch was not configured;
- therefore production SiteAgent/event stream is NOT yet launch evidence.

Current site authority:
`sites/dilivox/SITE_STATE.md`.

## Canonical Metrica goals — LIVE AUDIT COMPLETE / WRITE SCOPE REQUIRED

Registry:
`sites/dilivox/metrica-goals.json`.

Exact proxy goals:

- `pe_story_progress_75`;
- `pe_version_selected`;
- `pe_story_completed`;
- `pe_next_story_clicked`;
- `pe_return_visit`.

All begin `native_bidding_eligible=false`. They may be promoted only after revenue validation; K5 remains economic truth.

Live audit on 2026-09-01:

- GET goals: HTTP 200;
- provider has 22 existing goals;
- all five PE goals: `MISSING`;
- duplicate canonical identifiers: 0;
- invalid/wrong-type canonical identifiers: 0.

First create compatibility attempt exposed two separate issues and both are now modeled explicitly:

1. optional `goal.is_favorite` was rejected by the live provider; create payload is now minimal `name + type + conditions`;
2. minimal create then reached provider and returned HTTP 403 `Access is denied`, proving the current read credential is not accepted for goal administration.

Current credential architecture is provider/authority-specific:

- Direct read/control credential stays on its existing Direct Keychain reference;
- Metrica reads use `providers.metrica.token_source_ref`;
- Metrica configuration writes use separate `providers.metrica.write_token_source_ref`;
- default write Keychain service: `ProfitEngine-MetricaOAuth-Write`, account `profit-engine`;
- YAN Statistics retains its own credential.

The working Direct OAuth app/token must not be expanded merely to create Metrica goals. P0 uses a separate Yandex OAuth API-access application with only `metrika:read` + `metrika:write`.

Guided local installer:
`scripts/install-metrica-write-token-mac.sh`.

Expected missing/scope failures are structured fail-closed states and do not blind-retry.

## Production Tilda goal bridge — CODE READY / NOT PUBLISHED

Artifact:
`sites/dilivox/tilda/dilivox-metrica-goals-v1.js`.

Uses existing `data-dv-*` hooks and Metrica `reachGoal` only.

It does not mutate YAN blocks, story content, choice/reveal behavior or provider budgets/campaigns.

Emergency kill:
`window.PROFIT_ENGINE_METRICA_GOALS_KILL=true`.

Current project tools do not provide a Tilda write connector. One final Tilda external UI paste/publish step remains unavoidable after the exact production package is accepted.

## Local Profit Engine control panel — INSTALLED / RUSSIAN UI / WRITE LOCKED

Owner Mac now has:
`~/Applications/Profit Engine.app`.

The first bundle packaging defect (`CFBundleExecutable` missing) was fixed and regression-tested.

Panel properties:

- bind `127.0.0.1:8765` only;
- Russian Owner-facing labels/statuses;
- technical codes retained only for diagnostics;
- reads Keychain/private config;
- shows provider/link/goals/campaign/money/K5/P0-search state;
- local snapshots mode 0600;
- provider write endpoints do not exist;
- writer shown as locked;
- installer reuses the local runtime repo and restarts the Profit Engine panel process after upgrades.

## Manual Search Profit Control — P0 DEVELOPMENT PRIORITY

Owner decision: a dedicated search-only manually-bid campaign is the primary acquisition-controller development path because it is closer to direct K5 control.

Canonical strategy authority:
`ACQUISITION_STRATEGY_LAB.md`.

Dedicated concept:
`DILIVOX | SEARCH | PROFIT ENGINE`.

Accepted code state:

- MS1 exact read model: accepted;
- MS2 defensible attribution-grain boundary: accepted;
- MS3 non-executable shadow bid controller: accepted;
- MS5 dedicated search-only campaign dry-run: accepted;
- MS4 panel integration: next build slice;
- MS6 guarded campaign create: not authorized;
- MS7 guarded `KeywordBids.set`: not implemented/authorized.

Target provider shape:

- Unified Campaign;
- Search only;
- `HIGHEST_POSITION`;
- network `SERVING_OFF`;
- explicit Owner-fixed `WeeklySpendLimit` initially;
- `KeywordBids.get` read model;
- shadow Profit Engine bid controller;
- later separately accepted guarded `KeywordBids.set` / `SearchBid`;
- K5/confidence are primary decision truth.

Task:
`tasks/TASK-014-MANUAL-SEARCH-PROFIT-CONTROLLER.md`.

## Current P0 workstreams

### Task 012 — close first guarded Direct engineering launch

Remaining order:

1. technical PASS of YAN→Metrica monetization after Owner enable;
2. exact money preflight for both Dilivox candidates;
3. Central Brain chooses exactly one lowest-downside reversible campaign action;
4. rebuild exact ActionProposal/Governor/ControllerPlan;
5. one-shot arm;
6. exactly one `campaign.suspend` or `campaign.resume` mutation attempt;
7. exact read-back/audit;
8. terminal classification.

### Task 013 — production site instrumentation + goals

- live goal audit: COMPLETE, five PE goals missing;
- install separate `metrika:write` credential;
- create only missing exact goals + read-back;
- publish accepted Task-006 event layer;
- publish Metrica goal bridge;
- validate production goals/site/YAN regressions;
- first-party dispatch stays disabled until endpoint acceptance.

### Task 014 — manual search controller

- MS1 read model: accepted;
- MS2 attribution grain: accepted;
- MS3 shadow controller: accepted;
- MS4 panel integration: next;
- MS5 campaign dry-run: accepted;
- MS6 guarded campaign creation: not authorized;
- MS7 guarded bid writer: not authorized;
- supervised live learning only after those gates;
- later fair benchmark vs native strategies.

## Single operational authority

Use:
`P0_SYSTEM_COMPLETION_BOARD.md`.

Resume order:

1. `PROJECT_STATE.md`;
2. `P0_SYSTEM_COMPLETION_BOARD.md`;
3. `sites/dilivox/SITE_STATE.md`;
4. `ACQUISITION_STRATEGY_LAB.md`;
5. Task 012/013/014 specs;
6. latest accepted evidence;
7. issue #19.

## Completion definition

The first-site ecosystem is complete only when:

- paid acquisition is exactly attributable;
- production site behavior is instrumented;
- YAN monetization is measurable/reconcilable;
- K5 is computable on mature evidence;
- goals are live and revenue-validated before bidding use;
- Direct actions are guarded and read back;
- site actions are guarded/kill-switchable and measured;
- local control panel shows current money/control truth;
- manual-search controller can move from shadow to supervised to bounded automatic bids without bypassing capital governance.
