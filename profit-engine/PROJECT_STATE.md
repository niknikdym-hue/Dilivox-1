# PROFIT ENGINE — PROJECT STATE

Status: IMPLEMENTATION ACTIVE / DAY 12 — PRODUCTION WRITER READY / OWNER EDITING GATE
Updated: 2026-08-29
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

Codex is currently paused because its usage limit is exhausted. Owner instructed Central Brain not to issue new Codex tasks until Owner explicitly reports that the limit has been restored.

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

The previously missing real provider path is implemented but remains disabled until live gates pass.

Runtime/test chain:
- `f3bdae1a0790a955b1d6c4142e013bf38b179ff3` — fail-closed one-shot Direct production writer;
- `6d65812cb2c1ae9fa43c1874ce5780dd12c4b080` — writer tests;
- `c6a8031c5976d9015ac7e4cc9577073f676f910b` + `36b7799dc8f082053ce0c515347aab362fd64ac1` — Direct v501 runtime/bootstrap alignment;
- `5c3c07e577c682f99add9ea1e09804a0b6fbd6f0` — guarded production execution harness;
- `7b8fc3204a770f049fd29952e513a1cb3c7a14a6` — execution regressions;
- `cbd537ea978e1781098bca56442e91f4c7cf56fe` + `c582a2475d64e831e6decd9b47a242e6e9727f91` — complete-audit fix: final outcome validity is calculated only after `EXECUTION_LOCK_RELEASED` is appended.

CI:
- `33264804958` on `7b8fc3204a770f049fd29952e513a1cb3c7a14a6`: SUCCESS;
- `33264960239` on `c582a2475d64e831e6decd9b47a242e6e9727f91`: SUCCESS.

Evidence:
`profit-engine/evidence/TASK-012-PRODUCTION-WRITER-READY.md`.

Production execution enforces:
1. exact integrity-valid arm/plan binding;
2. exact target lock;
3. fresh provider preflight;
4. TOCTOU comparison;
5. runtime kill-switch recheck;
6. `DISPATCH_STARTED` audit before send;
7. exactly one mutation network attempt;
8. exactly one provider object ID;
9. immediate exact read-back;
10. lock release before final audit-valid outcome;
11. terminal classification with no blind retry.

Production writer default remains disabled. No live mutation was sent while building/testing this path.

## Owner Editing evidence / one-command readiness — VERIFIED

Owner permission evidence can now be recorded safely after the real UI change:
- `b0ad04fe4c60b360c9fa674d029103a2099b021f` — atomic 0600 recorder; explicit Owner confirmation required; plaintext target login never stored;
- `582c6c81b8439e918d011407744f30180af8ae04` — CLI;
- `fd0ba9de197569d0ef3134e7f6a33280826c504a` + `5cff11c52e54c90df10e0416930dc8fe7490b4e2` — macOS one-command confirmation + readiness wrapper, compatible with the system Bash path;
- `5ccf1db08dcd475e05d72cc262e4cea628f5f103` — recorder regression tests.

CI `33265203655` on `5ccf1db08dcd475e05d72cc262e4cea628f5f103`: SUCCESS.

After Owner actually changes the Direct UI relationship to Editing, the prepared entrypoint is:
`bash profit-engine/scripts/day12-confirm-editing-and-readiness.sh`

It prompts for the exact managed advertiser login if not supplied, requires explicit Owner confirmation that the UI change already happened, records local evidence, then runs the read-only Day-12 readiness doctor. It does not itself change any Yandex permission and cannot authorize a provider write.

## Current Direct API compatibility decision

Canonical Direct JSON endpoint is `/json/v501`.

Allowed first-live methods only:
- `campaign.suspend`;
- `campaign.resume`;
- `ad.suspend`;
- `ad.resume`.

`campaign.update_budget` is NOT enabled for the first production write.

Current Direct documentation deprecates the old campaign `DailyBudget` path; strategy-aware budget control uses `WeeklySpendLimit`. The Day-11 DailyBudget mapping remains synthetic safety evidence only.

Budget automation is fail-closed until a separate strategy-aware `WeeklySpendLimit` implementation + tests + Central Brain acceptance are complete. This does not block the Day-12 engineering launch because the first live action is intentionally the lowest-downside reversible accepted suspend/resume action.

Canonical first-write matrix:
`profit-engine/DAY12_FIRST_WRITE_ACCEPTANCE_MATRIX.md`.

## Current first incomplete canonical gate — OWNER ONLY

The Managing Account relationship is still canonically recorded as `Reading`; no accepted evidence shows it changed.

Single next Owner action:

`Yandex Direct: for the exact owner advertiser account managed by reklamadymova, change Managing Account access from Reading to Editing.`

Do not perform any other Direct mutation.

That UI change alone authorizes no provider write.

After Owner explicitly confirms the change, Central Brain will:
1. record fresh exact Owner UI Editing evidence with the prepared one-command flow;
2. run exact Direct operator/target + Metrica + YAN live read certification;
3. obtain current Direct spend/state evidence and accepted money/data-quality inputs;
4. select exactly one reversible live candidate;
5. reconstruct exact ActionProposal/Governor/ControllerPlan;
6. arm the one-shot writer for that exact plan only;
7. perform one guarded Direct mutation;
8. exact read-back + immutable audit;
9. classify engineering launch.

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

Read in this order on resume:
1. this file;
2. `DAY12_LIVE_PRODUCTION_LAUNCH_DESIGN.md`;
3. `DAY12_PROVIDER_LIVE_CERTIFICATION.md`;
4. `DAY12_FIRST_WRITE_ACCEPTANCE_MATRIX.md`;
5. `tasks/TASK-012-LIVE-GUARDED-PRODUCTION-LAUNCH.md`;
6. latest Task-012 evidence;
7. issue #19.
