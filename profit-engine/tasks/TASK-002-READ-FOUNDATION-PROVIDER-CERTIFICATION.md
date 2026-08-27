# CODEX TASK 002 — READ-ONLY PROVIDER/DATA FOUNDATION + PROVIDER CERTIFICATION

Status: READY FOR EXECUTION
Owner: Central Brain
Executor: Codex
Repository: `niknikdym-hue/Dilivox-1`
Canonical branch: `profit-engine`
Canonical local workspace: `~/Documents/New project/Profit Engine/Dilivox-1`
Existing Dilivox site workspace: `~/Documents/New project/Dilivox` — READ-ONLY for this task

## ROLE

You are the engineering executor for DILIVOX PROFIT ENGINE.

Central Brain is the project lead and acceptance authority. Do not change Owner decisions, economic targets, budget authority or launch architecture.

## READ FIRST — MANDATORY

Read current `origin/profit-engine`, then at minimum:

1. `profit-engine/PROJECT_HANDOFF.md`
2. `profit-engine/OWNER_DECISIONS.md`
3. `profit-engine/PROJECT_STATE.md`
4. `profit-engine/HARD_12_DAY_LAUNCH_PLAN.md`
5. `profit-engine/GOVERNANCE_AND_EXECUTION.md`
6. `profit-engine/SECURITY_AND_ACCESS.md`
7. `profit-engine/ACCESS_SETUP_CHECKLIST.md`
8. `profit-engine/OAUTH_API_SETUP.md`
9. `profit-engine/sites/dilivox/SITE_STATE.md`
10. `profit-engine/evidence/TASK-001-M0-INVENTORY.md` once synchronized

## OBJECTIVE

Advance Day 2 without waiting idly for provider credentials:

1. safely synchronize the accepted Task 001 evidence into `origin/profit-engine`;
2. build the minimal read-only provider/data foundation;
3. establish a secret-safe local configuration contract;
4. implement deterministic diagnostic clients for Yandex Direct, Yandex Metrica and YAN Partner Statistics;
5. run authenticated READ-ONLY certification for every provider whose token is securely available;
6. identify the exact minimal Owner/provider action for any token/access that remains unavailable;
7. do NOT modify production Dilivox or advertising state.

No advertising writes or spend are authorized.

---

# STEP 0 — SYNCHRONIZE TASK 001 EVIDENCE SAFELY

Known local Task 001 evidence commit:

`dd0f3025335ed174077e9e84b568baa58e21120a`

It was created on top of old origin:

`51eb6be7d7fe6cc06d795d33ae2a64c0c965010c`

Central Brain has since advanced `origin/profit-engine` (including a root `.gitignore`).

Required procedure:

1. `git fetch origin`;
2. record current local HEAD and current `origin/profit-engine`;
3. verify `dd0f302...` changes only the accepted non-secret evidence artifact and run secret-pattern checks again;
4. preserve the evidence content while rebasing/cherry-picking it cleanly onto current `origin/profit-engine`;
5. NO force push;
6. resolve only mechanical conflicts; if an authority/state conflict occurs, STOP and report it instead of choosing silently;
7. push the resulting fast-forward `profit-engine` branch to origin;
8. report the new origin HEAD.

Do not drop or rewrite the evidence content merely to make sync easier.

---

# STEP 1 — VERIFY SECRET HYGIENE

Central Brain added a root `.gitignore` after Task 001. Verify it is present after sync and that it excludes at least:

- `.env` and local variants;
- local Profit Engine private config/state;
- credential/token files;
- key/certificate files;
- Python virtual environments/caches;
- Node dependencies/caches;
- macOS junk.

Do not weaken the ignore rules.

Run a repository secret-pattern scan before any push made by this task.

---

# STEP 2 — CREATE MINIMAL READ-ONLY RUNTIME FOUNDATION

Create a small production-oriented Python foundation under a clear path such as:

`profit-engine/runtime/`

Keep it minimal and provider-neutral. Python target: 3.12+; local Python 3.14 is acceptable for execution but code must not rely on 3.14-only behavior unless justified.

Required structure/concepts:

- provider-neutral read client interface;
- `YandexDirectReadClient`;
- `YandexMetricaReadClient`;
- `YanPartnerStatsReadClient`;
- common HTTP/error result model;
- explicit READ_ONLY capability flag;
- redacted structured logging;
- request IDs/status codes captured without tokens;
- timeouts and bounded retries for safe transient failures;
- dependency injection/transport abstraction so fixture tests never call live providers;
- no write methods in Task 002 runtime.

Prefer a small explicit dependency set. If third-party dependencies are introduced, pin/declare them and explain why. Do not install Docker/Terraform/Yandex Cloud CLI in this task.

---

# STEP 3 — SECRET-SAFE CONFIGURATION CONTRACT

Create a public example/schema only; real provider/account IDs and tokens remain local/private.

Required concepts:

- `site_id=dilivox`;
- canonical domain;
- private Metrica counter reference;
- private Direct account/client/campaign mapping reference;
- private YAN resource/placement mapping reference;
- provider read endpoint selection;
- token source reference;
- optional Direct client-login/operator context when actually required;
- rollout mode fixed to `READ_ONLY` for this task.

Create a documented private local path such as:

`~/.config/profit-engine/sites/dilivox.json`

or an equivalently secure path outside Git.

Rules:

- public repository contains schema/example with placeholders only;
- actual private registry file must not be committed;
- if created locally, permissions should be restricted where practical (for example `0600`);
- tokens must not be stored in the public site registry;
- tokens are read from an approved local secret source (environment for ephemeral testing and/or macOS Keychain/secret manager adapter);
- never print token values.

Document exact environment variable / secret-reference names used by the runtime, but never values.

---

# STEP 4 — PROVIDER DIAGNOSTIC CLIENTS

Implement a single CLI/doctor entrypoint capable of reporting:

`PASS | BLOCKED_MISSING_CREDENTIAL | BLOCKED_ACCESS | PROVIDER_ERROR | NOT_ATTEMPTED`

for each provider.

## 4A. Yandex Direct — READ ONLY

Use the current Yandex Direct API v5 production contract.

Minimum safe live checks when OAuth token is available:

1. authenticated identity/client metadata read or equivalent lightweight read;
2. campaigns `get` limited to minimal fields needed to prove access;
3. no add/update/delete/suspend/resume methods;
4. capture `RequestId`/status and provider unit headers where available without private token output.

Authorization is `Authorization: Bearer <OAuth token>`.

Do not assume legacy v4/Live 4 points prove v5 readiness; report actual v5 result.

If a `Client-Login` is truly required by the account role, read it only from private local configuration and do not commit it.

## 4B. Yandex Metrica — READ ONLY

Minimum safe live checks when OAuth token is available:

1. `GET https://api-metrika.yandex.net/management/v1/counters`;
2. identify Dilivox counter using private local mapping/domain/name without committing private IDs;
3. verify current authorized permission for the selected counter where supported;
4. run one minimal reporting/monetization-read probe sufficient to establish whether YAN monetization metrics are visible to this identity.

Authorization is `Authorization: OAuth <token>`.

Do not create/update counters/goals in Task 002.

## 4C. YAN Partner Statistics — READ ONLY

Use the current Partner Statistics API and its statistics-specific OAuth token.

Minimum safe live checks when token is available:

1. statistics tree/resource discovery request;
2. minimal statistics report for a narrow harmless period/field sufficient to prove access to Dilivox data;
3. map discovered Dilivox resource/placement identities into PRIVATE local registry only;
4. no block-configuration API writes.

Authorization is `Authorization: OAuth <statistics token>`.

Do not confuse Statistics API token with in-app/block-configuration token.

---

# STEP 5 — CREDENTIAL BOOTSTRAP SUPPORT WITHOUT SECRET EXPOSURE

Task 001 found no safely available OAuth/YAN statistics tokens.

Therefore implement/document a safe bootstrap path, but do not ask for passwords and do not write secrets to Git.

Required output:

- exact secret names/types required for Direct/Metrica shared OAuth read token, if one token can cover configured scopes;
- exact secret name/type required for YAN Statistics API token;
- local command/doctor behavior when each is absent;
- exact minimal Owner action required to obtain each missing token from Yandex UI/OAuth;
- safe local storage method for testing (macOS Keychain and/or ephemeral environment), with no token in shell history if avoidable;
- no token value in report/evidence.

If an OAuth token becomes securely available during execution, immediately run the corresponding live READ-ONLY checks. If not, do not block fixture implementation/testing.

---

# STEP 6 — FIXTURE AND SAFETY TESTS

Create tests that prove without live credentials:

- Direct client sends correct HTTP method/path/header shape with redacted auth in logs;
- Metrica client sends correct read request shape;
- YAN statistics client sends correct read request shape;
- token values never appear in logs/exceptions/snapshots;
- missing token returns `BLOCKED_MISSING_CREDENTIAL` rather than crashing;
- 401/403 provider responses classify as access blockers;
- retryable errors are bounded;
- no write HTTP path/method exists in Task 002 provider clients;
- private registry path is outside tracked files or ignored;
- public examples contain no real IDs/secrets.

Run `git diff --check` and all available tests.

---

# STEP 7 — EVIDENCE

Create/update non-secret evidence:

`profit-engine/evidence/TASK-002-READ-FOUNDATION.md`

Include:

- date/time;
- baseline origin SHA after Step 0 sync;
- final local HEAD;
- files changed;
- runtime architecture summary;
- public/private config boundary;
- each provider status;
- safe live request result if attempted;
- exact credential/access blocker type if blocked;
- tests/checks and results;
- secret scan result;
- whether Task 001 evidence is now visible on origin;
- exact Owner action required, if any;
- recommended Task 003 boundary.

Do not include real private provider/account/counter/resource IDs unless authority explicitly permits publication. Prefer redacted aliases.

Commit and push Task 002 changes to `origin/profit-engine` only after tests and secret scan pass. No force push.

---

# DO NOT

- do not modify existing `~/Documents/New project/Dilivox`;
- do not publish through Tilda;
- do not alter production Dilivox behavior;
- do not create/modify/start/pause/resume advertising campaigns;
- do not enable Direct Editing;
- do not change budgets;
- do not spend money;
- do not create Yandex Cloud resources;
- do not commit tokens, OAuth client secrets, passwords or private registry values;
- do not expose provider identifiers unnecessarily in public evidence;
- do not implement competitive/scoring algorithms in the public repository in this task;
- do not merge to `main`;
- do not force-push `profit-engine`.

---

# ACCEPTANCE GATES

Task 002 is accepted only if:

1. Task 001 evidence is safely synchronized to origin;
2. root `.gitignore`/secret hygiene is verified;
3. provider-neutral read-only runtime foundation exists;
4. public example + private configuration boundary exists;
5. Direct/Metrica/YAN diagnostic clients exist and are fixture-tested;
6. logs/errors redact secrets;
7. safe live reads are attempted for every securely available credential;
8. absent credentials become explicit blockers with exact minimal Owner action;
9. no provider write/spend/production-site mutation occurred;
10. evidence is committed and pushed to `origin/profit-engine`;
11. origin HEAD and worktree state are exact and clean.

Day 2 provider gate may remain `BLOCKED_EXTERNAL_PROVIDER_CREDENTIAL` for a provider whose token genuinely requires Owner/UI action, but Task 002 engineering foundation can still be accepted if all code/tests/evidence gates pass and the blocker is isolated precisely.

---

# FINAL REPORT FORMAT

Return one compact report:

- `STATUS: COMPLETE | PARTIAL | BLOCKED`
- `LOCAL_PATH:`
- `BASELINE_ORIGIN:`
- `TASK001_EVIDENCE_SYNC:`
- `FINAL_HEAD:`
- `ORIGIN_PROFIT_ENGINE:`
- `WORKTREE:`
- `RUNTIME_FOUNDATION:`
- `CONFIG_BOUNDARY:`
- `DIRECT:`
- `METRICA:`
- `YAN:`
- `LIVE_READS:`
- `SECRET_SAFETY:`
- `FILES_CHANGED:`
- `COMMIT_SHA:`
- `TESTS/CHECKS:`
- `OWNER_ACTION_REQUIRED:`
- `BLOCKERS:`
- `RECOMMENDED_TASK_003:`

Do not self-accept. Central Brain will review evidence and advance the launch plan.
