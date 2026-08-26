# CODEX TASK 001 — PROFIT ENGINE LOCAL BOOTSTRAP + M0 INVENTORY

Status: READY FOR EXECUTION
Owner: Central Brain
Executor: Codex
Repository: `niknikdym-hue/Dilivox-1`
Canonical branch: `profit-engine`

## ROLE

You are the engineering executor for DILIVOX PROFIT ENGINE.

You are NOT the project brain. Do not change product/economic authority. Central Brain accepts/rejects the work.

## READ FIRST — MANDATORY

Before changing anything, read:

1. `profit-engine/PROJECT_HANDOFF.md`
2. `profit-engine/OWNER_DECISIONS.md`
3. `profit-engine/PROJECT_STATE.md`
4. `profit-engine/HARD_12_DAY_LAUNCH_PLAN.md`
5. `profit-engine/GOVERNANCE_AND_EXECUTION.md`
6. `profit-engine/DILIVOX_SITE_INTEGRATION.md`
7. `profit-engine/MACHINE_ADVERTISING_OPERATIONS.md`
8. `profit-engine/ACCESS_SETUP_CHECKLIST.md`
9. `profit-engine/OAUTH_API_SETUP.md`
10. `profit-engine/sites/dilivox/SITE_STATE.md`

## OBJECTIVE

Create/verify the canonical local working copy on the Owner's Mac and produce a precise M0 technical inventory so Central Brain can immediately issue Task 002.

No advertising spend or Direct write operation is allowed in this task.

## OWNER-APPROVED LOCAL WORKSPACE SEPARATION

There are two separate local workspaces. They MUST NOT be conflated.

### Existing Dilivox site workspace

`~/Documents/New project/Dilivox`

This is the existing working folder for the Dilivox site. Do NOT delete, move, reset, overwrite or repurpose it as the Profit Engine workspace. It may be inspected read-only if required to understand the current Dilivox implementation.

### Canonical Profit Engine workspace

`~/Documents/New project/Profit Engine/Dilivox-1`

This is the required local clone for the Profit Engine workstream.

## LOCAL FOLDER

Canonical local path:

`~/Documents/New project/Profit Engine/Dilivox-1`

Rules:
- create `~/Documents/New project/Profit Engine` if missing;
- if the target path does not exist, clone `https://github.com/niknikdym-hue/Dilivox-1.git` there;
- if it already exists and is the correct Git clone, do NOT reclone or destroy anything: fetch and verify it;
- if it exists but is not the correct repository, STOP before overwriting/deleting and report the conflict;
- checkout `profit-engine` and sync it safely from `origin/profit-engine`;
- do not reset or discard unknown local work without reporting it first;
- do not modify the separate `~/Documents/New project/Dilivox` workspace during bootstrap.

## BASELINE VERIFICATION

Report:
- absolute local path;
- `git remote -v`;
- current branch;
- current HEAD SHA;
- `origin/profit-engine` SHA;
- working-tree status;
- macOS version;
- Python/Node/npm versions if installed;
- relevant available tooling (`git`, `python3`, `node`, `npm`, `docker`, `terraform`, `yc`) without installing large dependencies yet unless trivially required.

## M0 REPOSITORY/SITE INVENTORY

Inspect the current repository and identify the actual implementation surface for Dilivox.

Report, with paths/evidence:
- current site source files and how Dilivox is deployed/built from this repository;
- where the homepage/catalog/story page code lives;
- current analytics/Metrica snippets or hooks;
- current YAN block code/config/placement references in repository files;
- any existing UTM/Direct tracking handling;
- any current first-party event instrumentation;
- any current stable story/content IDs;
- current scripts/tests/build/deploy tooling;
- any existing API/Profit Engine code beyond the canonical docs;
- any `.env`, credential config names or secret references, WITHOUT printing secret values;
- whether there is a `.gitignore` adequate to prevent common secret files from being committed.

If implementation/deployment information exists only in `~/Documents/New project/Dilivox`, inspect it read-only and record findings without mutating that workspace.

## PROVIDER ACCESS PRECHECK — NO SECRET EXPOSURE

Using credentials already securely available on the Mac ONLY if they exist and can be used without revealing them:

1. determine whether an OAuth access token suitable for Direct/Metrica already exists;
2. determine whether a YAN Statistics API token already exists;
3. do NOT print token values;
4. do NOT paste secrets into git, logs, task report or issue;
5. if safe authenticated read tests can already be run, perform minimal read-only checks:
   - Direct: authenticated lightweight read/list request;
   - Metrica: list/read accessible counters and identify Dilivox counter;
   - YAN: lightweight statistics/resource read.
6. if a credential is absent, report only the missing credential name/type and the exact next owner/provider action.

## REQUIRED NEW LOCAL ARTIFACT

Create a local execution evidence file under:

`profit-engine/evidence/TASK-001-M0-INVENTORY.md`

It must contain no secrets and include:
- date/time;
- local path;
- branch/SHAs;
- environment/tool versions;
- inventory findings;
- provider-read results as PASS/BLOCKED/NOT_ATTEMPTED;
- exact blockers;
- recommended Task 002 boundary.

Commit this evidence file to `profit-engine` only if it contains no sensitive identifiers that the repository authority says should remain private. If account/counter IDs are considered private, redact them and refer to private deployment config names instead.

## DO NOT

- do not enable Direct Editing/write access;
- do not create/modify/launch advertising campaigns;
- do not spend money;
- do not modify production Dilivox site behavior in this task;
- do not create Yandex Cloud resources yet;
- do not commit tokens/client secrets/passwords/private credentials;
- do not merge anything into `main`;
- do not rewrite canonical Owner decisions;
- do not invent missing access;
- do not delete/reset/overwrite/repurpose `~/Documents/New project/Dilivox`.

## ACCEPTANCE GATES

Task 001 is accepted only if:

1. canonical local clone exists at `~/Documents/New project/Profit Engine/Dilivox-1` and `profit-engine` is checked out;
2. existing site workspace `~/Documents/New project/Dilivox` remains separate and unmodified by bootstrap;
3. branch/HEAD/origin evidence is exact;
4. repository/site implementation surface is mapped;
5. current tracking/YAN/attribution instrumentation is inventoried;
6. credential presence is classified without exposing secrets;
7. any safe available read-only provider checks are reported accurately;
8. no provider writes/spend occurred;
9. no secrets entered the repository;
10. evidence file exists and is complete enough for Central Brain to issue Task 002.

## FINAL REPORT FORMAT

Return one compact report with:

- `STATUS: COMPLETE | PARTIAL | BLOCKED`
- `LOCAL_PATH:`
- `BRANCH:`
- `HEAD:`
- `ORIGIN_PROFIT_ENGINE:`
- `WORKTREE:`
- `ENVIRONMENT:`
- `SITE_IMPLEMENTATION_MAP:`
- `METRICA:`
- `YAN:`
- `DIRECT:`
- `ATTRIBUTION/TRACKING:`
- `SECRET_SAFETY:`
- `FILES_CHANGED:`
- `COMMIT_SHA:` if committed
- `TESTS/CHECKS:`
- `BLOCKERS:`
- `RECOMMENDED_TASK_002:`

Do not claim project acceptance. Central Brain will review the evidence and set the next task.
