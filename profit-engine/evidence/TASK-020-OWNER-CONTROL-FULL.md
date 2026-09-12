# TASK 020 — FULL OWNER CONTROL / DUAL-WINDOW PROJECT MANAGEMENT

Status: `IMPLEMENTED_AWAITING_DRAFT_PR_EXACT_HEAD_CI`

Central Brain acceptance remains required. This evidence does not declare the task accepted.

## Authority and bounded execution

- Repository: `niknikdym-hue/Dilivox-1`
- Canonical branch: `profit-engine`
- Exact fetched base: `c06220299dc700ed442ce53eb364105e12100999`
- Development branch: `brain/task-020-owner-control-full`
- Required route/model: `G3 / gpt-5.6-sol / high`
- Task hard cap: `$3.00`
- OpenAI provider calls made by this implementation session: `0`
- Actual accepted `DEV_AI_COST` before and after the G0 smoke: `$0.00`
- Provider writes: `0`
- Advertising spend: `0`
- Tilda/production Dilivox mutations: `0`
- Auto retry / merge / deploy: `false / false / false`

All mandatory Task 020 authority/state/design/task/evidence documents were read before implementation. The earlier one-window/read-only assumption in the companion panel requirements and Task 020 was synchronized to the Owner-approved one-app/one-backend/two-window contract without weakening the main Authority.

## Architecture reused and extended

Task 021 remains the accepted development control foundation. Task 020 reuses its routing, cost ledger, budget proxy, preflight, bounded workflow, installer, and no-auto-retry/no-auto-merge/no-auto-deploy boundaries.

The extension adds:

1. one localhost backend with separate `/profit` and `/project` top-level surfaces;
2. a deterministic whole-project projection from all canonical task specs and accepted evidence references, not a second mutable task database;
3. a server-side fixed-scope GitHub CLI adapter for exact repository/branch/workflow operations;
4. an idempotent development controller for refresh/start/start-package/pause/resume/stop;
5. exact-SHA and exact-scope Owner Gate evidence with a local append-only hash chain and canonical GitHub workflow artifact;
6. quality-floor routing, package/cost bounds, checkpoints, stop-on-first-failure, and authority-movement stops;
7. redacted result/PR state, changed paths, checks, costs and unresolved acceptance state in the local panel.

Browser JavaScript receives no GitHub token, OpenAI key, provider credential, arbitrary repository, workflow, branch, or shell string. State-changing requests require exact localhost Origin, per-launch CSRF, JSON, loopback client identity, an allowlisted endpoint, a bounded request ID, and burst control.

## Two-window and board proof

- Existing installed application instances named `Profit Engine*.app`: `1`
- Bundle identifier retained by the installer: `ru.dilivox.profit-engine`
- Backend instances per launcher: `1`, guarded by health reuse plus a local lock
- Profit route: `/profit`, legacy money-first panel preserved without project task controls
- Project route: `/project`, full project/development control surface
- Stage rail: `A / B / C / D / E`
- Project cards: `29`
- Canonical task specs represented exactly once: `24 / 24`
- Additional projection-only cards: one G0 acceptance smoke and four D/E scale milestones
- Completed history visible: `15` tasks at the fetched authority base
- Objective denominator: `29`
- Current truth at smoke time: `BLOCKED`, because six real Critical Path blockers remain; CI is not promoted to live/economic proof
- Current accepted `profit-engine` CI at smoke time: `SUCCESS` on exact canonical SHA `c06220299dc700ed442ce53eb364105e12100999`

Rendered local verification showed all required views: Critical Path, Whole Project, Adaptive Funnel, Content, Providers & Compliance, Owner Gates, Development, and History. Task detail showed status/target, dependencies, blockers, Owner Gate, route/model/reason, quality floor/cap, cost, branch/PR/SHA/CI, live/economic states, current/next action, and evidence references without requiring GitHub web UI.

## Free end-to-end G0 acceptance smoke

The exact `TASK-020-G0-SMOKE` card was selected and started using the local `/project` UI. It traversed:

`Project Control button -> CSRF/Origin-protected localhost backend -> fixed GitHub adapter -> existing Profit Engine Dev Preflight -> lifecycle reconciliation -> panel result`

- GitHub run: `34715623912`
- URL: `https://github.com/niknikdym-hue/Dilivox-1/actions/runs/34715623912`
- Event: `workflow_dispatch`
- Exact head branch: `profit-engine`
- Exact head SHA: `c06220299dc700ed442ce53eb364105e12100999`
- Result: `SUCCESS`
- `static` job: `SUCCESS`
- `api-key-preflight` job: `SUCCESS`
- OpenAI provider calls: `0`
- Reserved maximum: `$0.00`
- Actual cost: `$0.00`
- Accepted shared `DEV_AI_COST` after run: `$0.00`
- Remaining envelope: `$10.00`
- Automatic retry count: `0`
- Files changed by smoke: `[]`
- Scope result: `G0_READ_ONLY_PREFLIGHT`
- Panel terminal state: `READY_FOR_REVIEW`

The preflight checked only secret presence and produced redacted/non-secret evidence; no secret value was read into browser output.

## Automated verification

Pre-final-commit local results:

- Python full regression: `346/346 PASS`.
- Node site regression: `26/26 PASS`.
- New dual-route HTTP security tests, including real ephemeral loopback server: `PASS`.
- Python compileall: `PASS`.
- Development budget proxy self-test: `PASS`.
- GitHub workflow YAML parsing: `PASS`.
- `git diff --check`: `PASS`.

The test matrix covers one app/one backend/two routes, legacy Profit regression, whole-board uniqueness/completeness, honest truth semantics, exact task dispatch and idempotency, exact active pause/resume/stop, package sequencing and fail-stop, Owner Gate binding, quality-floor routing, Astra fail-closed behavior, cost/envelope semantics, foreign Origin/CSRF/JSON rejection, browser credential exclusion, arbitrary command/repository/workflow rejection, Draft-PR-only result behavior, and no provider/deploy controls.

## Owner-gated / deliberately not performed

- No paid API-Codex smoke was started. It remains a separate future action after acceptance of the free smoke.
- No Task 012 Direct mutation was authorized or performed.
- No Tilda publication or live-site mutation was performed.
- No merge or deployment was performed.
- The installed application bundle upgrade is delivered by the updated single-app installer after canonical acceptance; this feature branch is not merged or deployed by Task 020.
- Central Brain acceptance remains required before any project status advances from code-ready evidence.

## Expected terminal after exact-head CI

`DILIVOX_OWNER_CONTROL_FULL_CODE_READY`
