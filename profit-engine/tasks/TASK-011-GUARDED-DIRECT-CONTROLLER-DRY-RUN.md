# CODEX TASK 011 — GUARDED DIRECT CONTROLLER DRY-RUN / WRITE-SAFETY GATE

Status: READY FOR EXECUTION
Owner: Central Brain
Executor: Codex
Launch day: Day 11

## Repository

`niknikdym-hue/Dilivox-1`

Branch:
`profit-engine`

Local workspace:
`~/Documents/New project/Profit Engine/Dilivox-1`

Private core remains proposal-only and is not modified unless a compatibility-only public-contract pin is explicitly required. Do not change private scoring/ranking policy.

## Read first

1. `profit-engine/PROJECT_STATE.md`
2. `profit-engine/DAY11_GUARDED_DIRECT_CONTROLLER_DESIGN.md`
3. `profit-engine/DAY11_CONTROLLER_ACCEPTANCE_MATRIX.md`
4. `profit-engine/evidence/TASK-010-CENTRAL-BRAIN-ACCEPTANCE.md`
5. accepted `day10_public.py` / Task-010R evidence.

## Objective

Implement a deterministic, non-executing guarded Direct controller that converts an already Governor-ready public ActionProposal into an auditable Day-12-ready plan.

Canonical flow:

`ActionProposal + GovernorDecision + registered provider target + fresh preflight + approvals/guards -> ControllerPlan -> READY_FOR_DAY12_EXECUTION`

Task 011 itself sends ZERO real provider writes and creates ZERO spend.

## Direct Editing

Assume Direct account access is still Reading.

DO NOT ask Owner to enable Editing.
DO NOT require a write credential.
DO NOT send a real mutation.

Production writer must be hard-disabled by default.

## Required implementation

### 1. Controller state model

Canonical states:
- `CONTROLLER_PLAN_VALID`
- `CONTROLLER_PLAN_INVALID`
- `BLOCKED_GOVERNOR_NOT_READY`
- `BLOCKED_OWNER_APPROVAL`
- `BLOCKED_KILL_SWITCH`
- `BLOCKED_STALE_PROVIDER_STATE`
- `BLOCKED_PROVIDER_CAPABILITY`
- `BLOCKED_BUDGET_MAPPING`
- `BLOCKED_MUTATION_CADENCE`
- `BLOCKED_EXECUTION_LOCK`
- `READY_FOR_DAY12_EXECUTION`

No `EXECUTED` state.

### 2. Proposal/Governor binding

Validate:
- ActionProposal digest;
- same proposal identity/digest in Governor evidence;
- Governor state exactly `GOVERNOR_READY_FOR_DAY11_CONTROLLER`;
- `requires_budget_governor=true`;
- proposal `provider_write_allowed=false`.

No Governor bypass path.

### 3. OwnerApprovalEvidence v1

Immutable deterministic record bound to exact proposal/site/target/action/budget.

Above +20%:
- no approval -> blocked;
- wrong proposal/target/action -> blocked;
- insufficient approved amount -> blocked;
- expired/superseded -> blocked;
- exact valid approval -> may continue.

+20.00% clean proposal must not require this extra approval.

Chat text itself is not an execution credential.

### 4. Exact provider identity registry

Controller target must resolve to an exact provider entity ID from a registry/fixture contract.

Reject campaign-name, ad-text, URL, date or fuzzy target inference.

### 5. ProviderPreflightSnapshot v1

Immutable snapshot contains:
- site/provider/advertiser ref;
- exact entity type/id;
- relevant normalized provider state/status;
- current provider budget when relevant;
- strategy/subtype;
- fetched timestamp;
- source/request provenance;
- freshness/DQ state;
- deterministic digest.

Plan binds expected snapshot digest.

Stale/mismatched preflight -> blocked.

### 6. Safe method allowlist

Model only launch-safe future operations:
- campaign suspend;
- campaign resume;
- ad suspend;
- ad resume;
- bounded campaign budget update.

Reject:
- add/create;
- delete/archive;
- moderation submission;
- complex strategy migration;
- asset/group/keyword creation;
- arbitrary provider method;
- multi-object writes.

### 7. ProviderBudgetPlan v1

Explicitly prove public weekly budget -> provider daily budget mapping.

Must bind:
- current/proposed weekly budget Decimal;
- current/proposed daily provider budget Decimal;
- active-day/time-targeting basis;
- mapping version;
- currency;
- provider integer/micros exact conversion;
- rounding rule;
- snapshot/proposal/governor refs;
- Owner approval ref when needed.

NO implicit weekly/7 assumption.

Unknown active-day basis or inexact mapping -> `BLOCKED_BUDGET_MAPPING`.

### 8. Mutation cadence

Hard Profit Engine launch invariant:

`MAX_AUTONOMOUS_BUDGET_MUTATIONS_PER_CAMPAIGN_PER_DAY = 1`

Require immutable audit evidence proving zero prior autonomous budget changes for that campaign/day.

Missing/ambiguous evidence or one prior autonomous change -> `BLOCKED_MUTATION_CADENCE`.

### 9. Kill switches

Support global/site/provider/advertiser/target/experiment-action scopes.

Any applicable active switch -> blocked.

Kill switch overrides Governor readiness, private recommendation and Owner approval.

### 10. Execution lock contract

Per-target lock key:

`site_id:provider:advertiser:entity_type:provider_entity_id`

Same target already locked -> blocked.
Different target independent.
Expired lock recovery must be explicit/audited.

### 11. One-object rule

`MAX_MUTATION_OBJECTS_PER_PROVIDER_REQUEST = 1`

Zero object invalid.
Two or more blocked.
No fan-out from one controller plan.

### 12. Fake transport only

Implement a fake/in-memory provider write transport for tests.

Real provider transport must NOT be reachable by default.

Synthetic execution simulator may model:
- clear success;
- timeout/uncertain response;
- provider top-level error;
- per-object error/warning/success;
- RequestId/Units metadata;
- read-back state.

### 13. No-blind-retry state machine

On timeout/uncertain response:
- do not immediately retry;
- require read-back;
- desired state found -> recovered-applied classification;
- unchanged expected state -> only an explicit bounded future retry-plan state, no automatic loop;
- unexpected state -> uncertain/review stop.

No infinite retry path.

### 14. Read-back verification

Synthetic clear success still requires READ_ONLY read-back before synthetic `COMPLETED` audit evidence.

Budget read-back verifies exact provider amount + weekly mapping.

### 15. RollbackPlan v1

Derive rollback from immutable preflight state only.

Examples:
- budget update -> prior exact budget restore candidate;
- suspend active -> resume candidate;
- resume suspended -> suspend candidate;
- unknown prior state -> no automatic rollback.

Rollback itself remains guarded and inert on Day 11.

### 16. Append-only audit chain

Implement deterministic hash-linked audit records.

At minimum plan path:
`PLAN_CREATED -> PREFLIGHT_CAPTURED -> AUTHORIZATION_READY`.

Synthetic execution path may add:
`EXECUTION_LOCK_ACQUIRED -> DISPATCH_STARTED -> PROVIDER_RESPONSE_RECEIVED -> READBACK_VERIFIED -> COMPLETED/EXECUTION_UNCERTAIN`.

Tamper/reorder -> invalid chain.

Retain secret-safe RequestId/Units metadata only.

### 17. Secret/log redaction

Tests inject token-like/private-login strings and prove they cannot enter plan/audit/evidence/exception output.

No credentials/provider private mapping in public fixtures.

## Hard invariants

During Task 011:
- `real_provider_requests=0`;
- `advertising_spend=0`;
- `production_writer_enabled=false`;
- Direct Editing remains disabled;
- no Tilda/site mutation;
- no paid Cloud apply;
- no secret in Git;
- no force push;
- no merge to main.

## Mandatory acceptance tests

Implement every gate in `DAY11_CONTROLLER_ACCEPTANCE_MATRIX.md` including:
1. clean +10% Governor-ready budget proposal -> READY plan;
2. +20.00% clean -> may be READY without extra approval;
3. +20.01% no approval -> blocked;
4. +20.01% wrong/expired/lower approval -> blocked;
5. +20.01% exact approval -> may continue;
6. Governor pending/blocked/mismatch -> blocked;
7. forged proposal digest -> blocked;
8. fuzzy/unregistered provider target -> blocked;
9. stale preflight -> blocked;
10. unsupported method -> blocked;
11. unknown budget mapping -> blocked;
12. one prior budget mutation today -> blocked;
13. kill switch at every scope -> blocked;
14. lock held -> blocked;
15. >1 request object -> blocked;
16. timeout -> zero blind retry;
17. timeout + desired readback -> recovered-applied synthetic evidence;
18. unexpected readback -> uncertain/review;
19. HTTP 200 + per-object failure != success;
20. missing readback != completed;
21. rollback derives exact prior state;
22. tampered audit chain invalid;
23. token-like log input redacted;
24. default runtime cannot reach real writer;
25. all Task 010R and prior tests remain green.

## Evidence

Create:

`profit-engine/evidence/TASK-011-GUARDED-DIRECT-CONTROLLER.md`

Evidence must include:
- baseline/final SHA;
- controller states;
- method allowlist;
- approval boundary proof;
- budget mapping proof;
- cadence proof;
- kill/lock/stale-state proof;
- retry/readback/rollback proof;
- audit-chain proof;
- real provider requests = 0;
- advertising spend = 0;
- production writer disabled;
- test counts;
- final Profit Engine CI run.

## Completion

Run full public Python tests, Node tests, compile, diff check, JSON if applicable, secret scan, provider-write reachability scan.

Commit and normal fast-forward push to `profit-engine`.
Final `Profit Engine CI` must be GREEN on exact origin HEAD.

Do not self-accept.
Central Brain decides whether Editing-access upgrade is allowed after inspection.
