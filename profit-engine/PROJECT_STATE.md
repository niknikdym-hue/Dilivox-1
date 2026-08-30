# PROFIT ENGINE — PROJECT STATE

Status: IMPLEMENTATION ACTIVE / DAY 12 — OWNER EDITING CONFIRMED / FRESH LOCAL READ-ONLY CERTIFICATION PENDING
Updated: 2026-08-30
Canonical public branch: `profit-engine`
Private core branch: `main`

## Objective

Launch the guarded production loop:

`Yandex Direct -> Dilivox -> behavior -> YAN revenue -> attribution/reconciliation -> private proposal-only core -> ActionProposal -> Budget Governor -> guarded Direct controller -> measured outcome`.

First production site: `site_id=dilivox` / `dilivox.ru`.
Target: `1 RUB Direct spend -> 5 RUB YAN advertising revenue attributable to the acquired Dilivox audience`.
This remains a target, not a claimed result.

## Locked governance

- private core emits proposals only and never writes to providers;
- automatic weekly budget increase above +20% requires exact explicit Owner approval;
- exactly one provider object for the first launch write;
- no blind mutation retry;
- exact target identity only; no fuzzy inference;
- no secret values in Git/chat/issues/logs;
- chat is not source of truth.

## Executor state

Codex is paused because its usage limit is exhausted. Owner instructed Central Brain not to issue new Codex tasks until Owner explicitly reports that the limit has been restored.

No new Codex implementation exists after the previously accepted Day-12 pre-live scaffold. Current launch-critical engineering is being advanced directly by Central Brain on canonical `profit-engine`.

## Accepted baseline

Tasks 001–010R: ACCEPTED.
- public Day-10 contract: `98c6d3f0c0105c30cfc90a6d5fdf653c2aceb8d6`;
- private accepted contract: `1709925f5b2d29f9c038dde7caca8054b51eea6f`.

Task 011 + 011R: ACCEPTED / DAY 11 COMPLETE.
- final controller: `a494d30b49c8d11687be56cdab870a5d83356e02`;
- CI `33187660342`: GREEN;
- exact proposal/Governor binding, trusted Owner >20% gate, preflight, TOCTOU, kill switch, lock, one-object binding, read-back, audit and no-blind-retry invariants accepted.

Private core:
- `niknikdym-hue/profit-engine-core/main` = `76b1b8670690f102a045243760dfe3d1e58513d5`;
- CI `33182663547`: SUCCESS;
- proposal-only / no provider write authority.

## Provider access — VERIFIED

Working credentials are stored locally and have already produced live read success:
- YAN Statistics: live `dilivox.ru` statistics readable;
- Metrica: counter `110349067` readable, permission `edit`;
- Direct: OAuth/operator identity readable.

Canonical live evidence:
`profit-engine/evidence/TASK-012-LIVE-PROVIDER-BINDING.md`.

## Direct identity truth

Technical Direct Managing Account/operator: `reklamadymova`.

The owner advertiser managed target is a distinct private login. The previous bootstrap that treated `reklamadymova` as the managed target is REWORKED and is not valid launch evidence.

Owner confirmed on 2026-08-30 that the exact Managing Account relationship in Yandex Direct was changed in the UI from `Reading` to `Editing`. This Owner confirmation closes the UI-change action but is not by itself provider/API evidence and grants no write authority. Runtime remains fail-closed until fresh local Owner evidence plus read-only provider certification succeed.

Runtime now:
- separates operator and managed target;
- rejects operator/target aliasing;
- requires exact private target binding;
- keeps the Managing Account Reading/Editing relationship fail-closed unless fresh Owner UI evidence exists.

Relevant evidence:
- `TASK-012-DIRECT-PERMISSION-READ-PROBE.md`;
- `TASK-012-PROVIDER-PERMISSION-FAIL-CLOSED-FIX.md`;
- `TASK-012-DIRECT-MANAGER-TARGET-MISBINDING-REWORK.md`;
- `TASK-012-OWNER-UI-PERMISSION-EVIDENCE-GATE.md`.

## Day-12 production writer — VERIFIED / READY IN CODE

The real provider path is implemented but remains disabled until all live gates pass.

Core implementation chain:
- `f3bdae1a0790a955b1d6c4142e013bf38b179ff3` — fail-closed one-shot Direct production writer;
- `6d65812cb2c1ae9fa43c1874ce5780dd12c4b080` — writer tests;
- `c6a8031c5976d9015ac7e4cc9577073f676f910b` + `36b7799dc8f082053ce0c515347aab362fd64ac1` — Direct JSON v501 runtime/bootstrap alignment;
- `5c3c07e577c682f99add9ea1e09804a0b6fbd6f0` — guarded production execution harness;
- `7b8fc3204a770f049fd29952e513a1cb3c7a14a6` — execution regressions;
- `cbd537ea978e1781098bca56442e91f4c7cf56fe` + `c582a2475d64e831e6decd9b47a242e6e9727f91` — complete-audit fix: final outcome validity is calculated only after `EXECUTION_LOCK_RELEASED`;
- `65cd1da650cb9068b93b2cdb7ccb7e1f31023d7a` — live provider state normalization `ON -> ACTIVE` and coherent reversible-transition enforcement;
- `35f9a1ddb449da5acd8d3775a5190f0ff289a6e5` — live-state and transition regressions;
- `449169f8b638437ddf1b2f7a1ac14a753b8a70b6` — writer arm tightened to timezone-aware max-five-minute TTL; id-less single-object Direct ActionResult errors retain provider codes;
- `2f72e646495b44956d5e8d077e4a1bc45f5e4b64` — writer hardening regressions.

Integrated CI `33265790511` on `2f72e646495b44956d5e8d077e4a1bc45f5e4b64`: SUCCESS.

Evidence:
`profit-engine/evidence/TASK-012-PRODUCTION-WRITER-READY.md`.

Production execution enforces:
1. exact integrity-valid arm/plan/preflight binding;
2. arm timestamps timezone-aware, maximum TTL five minutes;
3. exact target lock;
4. fresh provider preflight;
5. provider state normalization (`ON` is internal `ACTIVE`);
6. coherent reversible transition: suspend only from `ACTIVE`, resume only from `SUSPENDED`;
7. TOCTOU comparison;
8. runtime kill-switch recheck;
9. `DISPATCH_STARTED` audit before send;
10. exactly one mutation network attempt;
11. exactly one provider object ID;
12. exact provider error preservation where possible;
13. immediate exact read-back;
14. lock release before final audit-valid outcome;
15. no blind retry.

Production writer default remains disabled. No live mutation was sent while building/testing this path.

## Owner Editing evidence / one-command readiness — VERIFIED

Owner permission evidence can be recorded safely only after the real UI change:
- `b0ad04fe4c60b360c9fa674d029103a2099b021f` — atomic 0600 recorder; explicit Owner confirmation required; plaintext target login never stored;
- `582c6c81b8439e918d011407744f30180af8ae04` — CLI;
- `fd0ba9de197569d0ef3134e7f6a33280826c504a` + `5cff11c52e54c90df10e0416930dc8fe7490b4e2` — macOS one-command confirmation + readiness wrapper;
- `5ccf1db08dcd475e05d72cc262e4cea628f5f103` — recorder regression tests;
- `31fdd29fe70431a1e063273fc30804704a3be45a` — exact campaign inventory CLI redaction boundary repair, preserving public exact campaign IDs without weakening shared secret redaction;
- `7d256a4494adfa52683706048687e2b3761220c1` — one-command read-only chain extended from provider readiness to exact campaign inventory.

CI:
- `33310356480`: SUCCESS;
- `33310521366`: SUCCESS.

Owner has now confirmed the real UI change to Editing. Prepared local entrypoint:
`bash profit-engine/scripts/day12-confirm-editing-and-readiness.sh`

It asks for the exact managed advertiser login if needed, requires explicit Owner confirmation that the UI change already happened, records local evidence, runs the read-only Day-12 provider doctor, and then emits the exact read-only Direct campaign inventory. It cannot change Yandex permission and cannot authorize a provider write by itself.

## Current Direct budget compatibility — READ-ONLY REWORK VERIFIED

Canonical Direct endpoint: `/json/v501`.

The old live assumption around campaign `DailyBudget` is retired. Current budget analysis is strategy-aware and based on observed `WeeklySpendLimit`.

Verified read-only implementation chain:
- `60d8823dbf861ae00c13124fe8f144019bdeaf20` — initial fail-closed `WeeklySpendLimit` planner;
- `1883c38f42f8f0aeb96dec80527a9f0148d2c4a9` — planner tests;
- `4847276189a7695732d29e17d10e6da61d7bdccd` — canonical planner digest fix;
- `9dcba64307b2e3d03ecfd33cb8113121032887ea` — package/portfolio strategy ownership fails closed at campaign scope;
- `bf050ad02f3f18ed9e16f73e5c3c81fd8181adce` — package-strategy tests;
- `0270fd7b2ba68b04ddd552bbd38a7a165547e00e` — exact one-campaign read-only `Campaigns.get` budget probe;
- `734f8a76f10c81f4a3e341fe1019e39feeebe268` — probe tests.

CI:
- `33265419324`: SUCCESS after digest correction;
- `33265550485`: SUCCESS for package-strategy HOLD;
- `33265613094`: SUCCESS for exact read-only provider probe;
- integrated `33265790511`: SUCCESS.

Planner capabilities:
- `EXACT_ONE_SLOT`;
- `NO_WEEKLY_SPEND_LIMIT`;
- `AMBIGUOUS_MULTIPLE_SLOTS`;
- `PACKAGE_STRATEGY_REQUIRES_SEPARATE_SCOPE`;
- `INVALID_PROVIDER_SHAPE`.

The planner/probe:
- never writes to Direct;
- uses only exact campaign IDs;
- reads supported `BiddingStrategy` / `PackageBiddingStrategy` structures;
- requires exact observed budget ownership;
- holds package/portfolio strategies at individual campaign scope;
- preserves exact micros conversion;
- preserves Owner boundary: +20.00% no extra approval, +20.01% requires Owner approval;
- always has `provider_write_allowed=false`.

Canonical evidence:
`profit-engine/evidence/TASK-012-DIRECT-WEEKLY-BUDGET-COMPATIBILITY.md`.
Evidence commit chain was corrected in `12bca0e2d9ce952a95c5f0b8bc56ca00c1579a24`; it contains only verified SHAs.

## WeeklySpendLimit advisory + Governor bridge — VERIFIED / READ-ONLY

Advisory implementation:
- `fa25382faebe94011c56475c83d22b727bdeb208` — exact budget inspection -> shadow/PENDING/HOLD state;
- `828bbe14544efe38236672669b1cee567b2aefe4` — advisory regressions;
- CI `33266082953`: SUCCESS.

Governor bridge:
- `569519bafd144e9e9416849a5dcbb3849d915e89` — exact ProviderTarget + ActionProposal + advisory + Governor binding;
- `acfd0fb7920502383809795b2bada56396deac16` — bridge regressions;
- CI `33266159339`: SUCCESS.

Canonical evidence:
`profit-engine/evidence/TASK-012-WEEKLY-BUDGET-SHADOW-GOVERNOR.md`.

The bridge proves exact identity and money agreement only. It never creates a Direct request and always keeps `provider_write_allowed=false`.

Owner boundary remains exact:
- +20.00% may be `SHADOW_GOVERNOR_READY`;
- +20.01% must remain `PENDING_OWNER_APPROVAL`;
- a ready Governor above +20% is rejected;
- package/portfolio HOLD cannot be overridden by the bridge.

### Live budget decision

`campaign.update_budget` is NOT enabled for the first production write.

No live `Campaigns.update` budget request builder/transport is accepted yet. A future budget-write phase must separately prove exact strategy-specific update shape, package-strategy ownership, fresh provider state, Governor binding, trusted Owner >20% approval, one-shot dispatch, read-back and rollback/recovery.

This does not block engineering launch because the first live mutation remains limited to reversible suspend/resume.

## Day-12 live money preflight — VERIFIED / READY IN CODE

Canonical money runtime:
`profit-engine/runtime/profit_engine_runtime/day12_money_preflight.py`

Implementation:
- `bfd517ab1a654c14edc0880c55bbdc014c6d267e` — exact three-provider read-only money preflight;
- `c3e751c09566ae5871e1d19ad7c928450b6cde63` — initial test harness commit; CI `33266341506` failed before tests executed because the helper name collided with `unittest.TestCase.run`; this failed run is NOT acceptance evidence;
- `a72f9060c6089e12f5647e70840bbdd14beae439` — test harness correction;
- CI `33266404903`: SUCCESS.

Secret-safe CLI:
- `8e6bb52af38c6c02d75c5ef5f361704c4949e4ea` — private-config/Keychain-aware read-only CLI;
- `bc2126e61990d9b230d7677e1c5bd671632c88c3` — CLI regressions proving tokens are not printed and missing bindings fail before provider calls;
- CI `33266505126`: SUCCESS.

Canonical evidence:
`profit-engine/evidence/TASK-012-LIVE-MONEY-PREFLIGHT-READY.md`.

Day-12 Direct spend authority uses the current official JSON Reports endpoint:
`https://api.direct.yandex.com/json/v501/reports`.

It requires:
- exact managed advertiser `Client-Login`;
- exact one-campaign `CampaignId` filter;
- explicit date window;
- RUB cost basis (`returnMoneyInMicros=false`);
- bounded read-only report polling;
- exact campaign identity in every returned row.

Metrica attribution uses exact counter `110349067`, full accuracy and exact last-Direct-click campaign dimension. YAN Statistics supplies the independent exact-domain control total for `dilivox.ru`.

Money states:
- `READY_FOR_CANDIDATE_EVALUATION`;
- `NO_DIRECT_SPEND`;
- `HOLD_DATA_QUALITY`.

Observed K5 is computed only when Direct spend is strictly positive. Zero Direct spend never becomes fake/infinite K5. Sampled/sensitive Metrica data, ambiguous money basis, impossible reconciliation or identity mismatch fail closed.

The older `DirectCollector` Reports URL in `collectors.py` is not Day-12 launch authority until separately reworked; the new money preflight/CLI is canonical for first-launch economics.

No money preflight state grants write authority.

## First-live method allowlist

Writer code supports:
- `campaign.suspend`;
- `campaign.resume`;
- `ad.suspend`;
- `ad.resume`.

Central Brain first-smoke policy is narrower: the first real production mutation must use exactly one campaign from the fresh exact campaign inventory and only `campaign.suspend` or `campaign.resume`. `ad.*` is deferred until equivalent exact Ads inventory evidence exists.

No create/add/delete/archive/moderate/strategy migration and no budget mutation for the first launch write.

Canonical first-write matrix:
`profit-engine/DAY12_FIRST_WRITE_ACCEPTANCE_MATRIX.md`.

## Current first incomplete canonical gate — FRESH LOCAL READ-ONLY CERTIFICATION

The Owner UI action is complete: Owner explicitly confirmed on 2026-08-30 that the exact Managing Account access was changed from Reading to Editing.

This confirmation alone is not accepted provider/API proof and authorizes zero writes. The current first incomplete gate is now:

`Run the prepared local Owner-evidence + read-only readiness + exact campaign inventory flow using the existing private target binding and local Keychain credentials.`

Canonical entrypoint:
`bash profit-engine/scripts/day12-confirm-editing-and-readiness.sh`

Expected fail-closed progression after that local gate succeeds:
1. fresh exact Owner UI Editing evidence is recorded locally;
2. exact Direct operator/target + Metrica + YAN live read certification passes;
3. exact Direct campaign inventory is emitted without selecting a candidate;
4. Central Brain runs the canonical money preflight for exact campaign candidate IDs;
5. Central Brain selects exactly one lowest-downside reversible campaign candidate from accepted state + money evidence;
6. reconstruct exact ActionProposal/Governor/ControllerPlan;
7. arm the one-shot writer for that exact plan only;
8. perform one guarded Direct mutation;
9. exact read-back + immutable audit;
10. classify engineering launch.

Any failed gate => zero dispatches.

## Launch terminal states

- `GUARDED_PRODUCTION_LAUNCHED`;
- `PRODUCTION_WRITE_BLOCKED`;
- `PRODUCTION_EXECUTION_UNCERTAIN`;
- rollback states remain separately guarded if ever needed.

Only an applied and verified bounded real mutation counts as engineering launch.

## Post-launch economic proof

Engineering launch does not prove `K5 >= 5.0`.
Economic proof requires reconciled live Direct spend + Metrica-attributed YAN revenue + YAN control totals over mature periods/cohorts.

M7 after launch continuously optimizes yield, recirculation and acquisition economics toward K5=5 without incentivized clicks or artificial engagement.

## Current launch authority

Tracking issue: `#19 — Profit Engine Task 012 — Live guarded production launch`.

Resume order:
1. this file;
2. `DAY12_LIVE_PRODUCTION_LAUNCH_DESIGN.md`;
3. `DAY12_PROVIDER_LIVE_CERTIFICATION.md`;
4. `DAY12_FIRST_WRITE_ACCEPTANCE_MATRIX.md`;
5. `tasks/TASK-012-LIVE-GUARDED-PRODUCTION-LAUNCH.md`;
6. latest Task-012 evidence;
7. issue #19.
