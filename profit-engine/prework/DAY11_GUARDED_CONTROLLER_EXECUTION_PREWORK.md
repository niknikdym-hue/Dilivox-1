# PROFIT ENGINE — DAY 11 GUARDED DIRECT CONTROLLER EXECUTION PREWORK

Status: CENTRAL BRAIN PREWORK / NOT CANONICAL
Updated: 2026-08-28
Branch: `central-brain/day11-controller-prework-v2`
Depends on: Task 010R acceptance

## Purpose

Prepare the Day-11 guarded Yandex Direct controller without enabling provider writes while Task 010R fixes cohort-materialization truth.

Day 11 is a write-safety gate, not a production-spend day.

The canonical transition is:

`Governor-ready ActionProposal -> immutable preflight snapshot -> ControllerPlan -> execution authorization gates -> READY_FOR_DAY12_EXECUTION`.

There is deliberately no real provider execution in this prework.

## Current provider contract verification

Current Yandex Direct API v5/v501 supports data-changing operations including:

- Campaigns: `add`, `update`, `delete`, `suspend`, `resume`, archive operations;
- Ads: `add`, `update`, `delete`, `suspend`, `resume`, `moderate`, archive operations;
- AdGroups and targeting services with their own lifecycle methods;
- unified performance objects through v501-compatible endpoints.

Important current Direct behavior that the controller must model:

1. data-changing methods may partially succeed when a request contains multiple objects;
2. each API response carries a server `RequestId` and `Units` information;
3. monetary values in v5 are provider integers in currency units multiplied by 1,000,000;
4. `Campaigns.update` currently permits at most 10 campaigns per call and at most 3 daily-budget changes per campaign per day.

For launch safety Profit Engine should be stricter than provider limits.

## Day-11 execution authority

Until Central Brain accepts Task 011:

- Yandex Direct account access remains READ-ONLY;
- no Owner action to enable Direct Editing is requested;
- no real write request may be sent;
- no advertising spend may be created;
- tests use fake/in-memory write transport only;
- production writer runtime flag is hard-disabled.

After Task-011 acceptance, Owner may upgrade Direct access from Reading to Editing. Actual first real mutation belongs to Day 12 and must still pass all Day-12 evidence gates.

## Controller input boundary

The controller accepts only an immutable public `ActionProposal v1` plus the exact `GovernorDecision` generated for that proposal.

Required proposal invariants:

- `requires_budget_governor=true`;
- proposal digest validates;
- `provider_write_allowed=false` at proposal layer;
- site/target refs resolve to registered entities;
- public evidence refs are present;
- opaque private decision ref/digest present when required;
- budget values are Decimal-compatible and exact.

Required governor invariant:

`state == GOVERNOR_READY_FOR_DAY11_CONTROLLER`.

Anything else fails closed.

## Owner approval evidence

For any weekly increase above +20%, controller readiness requires an immutable approval record bound to the exact proposal.

Recommended `OwnerApprovalEvidence v1` fields:

- `approval_version`;
- `approval_id`;
- `proposal_digest`;
- `site_id`;
- `target_ref`;
- approved action kind;
- approved maximum weekly budget / exact proposed amount;
- approval timestamp;
- optional expiry;
- approver role = Owner;
- single-use / supersession state;
- deterministic approval digest.

An approval for another proposal, older amount, different target, expired proposal or superseded proposal does not count.

No chat transcript is an execution credential by itself.

## Preflight remote snapshot

Every future mutation requires a fresh READ_ONLY provider snapshot immediately before authorization.

`ProviderPreflightSnapshot v1` should contain:

- site/provider/advertiser reference;
- entity type and exact provider entity ID;
- selected provider fields relevant to the planned mutation;
- campaign/ad state and status;
- current provider budget where applicable;
- current strategy/subtype;
- fetched timestamp;
- source request ID;
- raw/source provenance ref;
- deterministic snapshot digest;
- freshness state;
- data-quality holds.

No campaign-name or date-based target inference is permitted.

## TOCTOU / stale-state gate

Controller plan binds to an expected provider snapshot digest.

Before Day-12 execution:

1. acquire per-target execution lock;
2. perform fresh provider GET;
3. compare normalized state against the bound expected snapshot;
4. if state changed materially, stop with `BLOCKED_STALE_PROVIDER_STATE`;
5. never silently adapt a private/public proposal to an unexpected remote state.

## Safe initial mutation allowlist

Day-11 controller may model a wider future interface, but Day-12 real-execution allowlist should initially be intentionally narrow:

- campaign suspend;
- campaign resume;
- ad suspend;
- ad resume;
- one bounded campaign budget update when all money/approval gates pass.

Creating new campaigns/ads/assets, moderation submission, destructive delete/archive and complex strategy migration remain disabled for the first real closed-loop action unless separately accepted later.

This minimizes rollback ambiguity at launch.

## Budget mapping contract

Profit Engine governance is expressed as weekly budget, while Direct campaign updates may use `DailyBudget`.

Controller MUST NOT silently divide weekly budget by seven.

A `ProviderBudgetPlan v1` must explicitly bind:

- current/proposed weekly budget;
- current/proposed provider daily budget;
- campaign active-days/time-targeting basis;
- mapping version;
- currency;
- provider micros integer after exact Decimal conversion;
- rounding rule;
- source snapshot ref;
- ActionProposal digest;
- GovernorDecision ref;
- Owner approval ref if required.

The plan must prove that the provider mutation is consistent with the already-approved weekly envelope.

Unknown schedule/budget mapping -> blocked.

## Stricter autonomous budget-change cadence

Direct currently allows up to three daily-budget changes per campaign per day.

Profit Engine launch controller should enforce a stricter autonomous rule:

`MAX_AUTONOMOUS_BUDGET_MUTATIONS_PER_CAMPAIGN_PER_DAY = 1`.

This is a capital-protection invariant, not a provider requirement.

If the audit ledger cannot prove that no autonomous budget change has already occurred for that campaign/day, another autonomous budget change is blocked.

Manual/external changes discovered in provider preflight also trigger stale-state review rather than automatic compensation.

## ControllerPlan v1

An immutable controller plan should include:

- plan version/id/digest;
- ActionProposal digest;
- GovernorDecision digest/ref;
- Owner approval digest/ref when required;
- provider entity ref/type;
- provider service + method;
- exact normalized request payload preview;
- expected preflight snapshot digest;
- provider capability version;
- provider budget plan when applicable;
- execution lock key;
- mutation cadence evidence;
- rollback plan ref;
- kill-switch refs;
- expiry/freshness deadline;
- `provider_write_enabled=false` on Day 11;
- `advertising_spend=0` on Day 11.

## Kill-switch precedence

Execution authorization must fail closed when any applicable kill switch is active.

Recommended precedence:

1. global Profit Engine kill switch;
2. site kill switch;
3. provider kill switch;
4. advertiser/account kill switch;
5. campaign/ad target kill switch;
6. experiment/action-specific kill switch.

A kill switch always overrides private recommendation, public proposal, Owner approval and Governor readiness.

## One-object launch write rule

Yandex Direct can process objects independently in a multi-object mutation request, which can create partial success.

For Day-12 launch:

`MAX_MUTATION_OBJECTS_PER_PROVIDER_REQUEST = 1`.

This makes one request correspond to one audited target mutation and reduces partial-success ambiguity.

Batch mutation support can be introduced only after launch acceptance.

## Retry and uncertain-result safety

Never blindly retry a write after a timeout or ambiguous transport result.

Required future sequence:

1. append `DISPATCH_STARTED` audit event before sending;
2. send at most one object;
3. capture HTTP/provider response, Direct `RequestId` and `Units`;
4. on clear success, perform READ_ONLY read-back verification;
5. on timeout/unknown response, perform read-back BEFORE any retry;
6. if desired state is already present, classify `RECOVERED_APPLIED_AFTER_UNCERTAIN_RESPONSE`;
7. if state is unchanged and all locks/snapshots are still valid, a bounded retry policy may be evaluated;
8. if state is different/ambiguous, stop `EXECUTION_UNCERTAIN_REQUIRES_REVIEW`.

No automatic infinite retries.

## Provider partial-success handling

Even after launch, every response is interpreted per object/result item.

Warnings and errors are stored in audit records with secret-safe redaction.

A top-level HTTP success does not imply that the intended provider object changed successfully.

## RollbackPlan v1

Rollback is based on the exact preflight state, never on guessed inverse operations.

Examples:

- budget update -> restore exact previous provider budget if rollback remains safe and permitted;
- suspend campaign/ad -> resume only if preflight proved it was active and rollback guard passes;
- resume -> suspend only if preflight proved it was suspended;
- unknown prior state -> no automatic inverse rollback.

Rollback itself is a provider mutation and therefore needs its own authorization/audit/kill-switch checks.

A failed mutation does not automatically trigger an unsafe blind rollback.

## Immutable execution audit

Append-only audit states should include at minimum:

- `PLAN_CREATED`;
- `PREFLIGHT_CAPTURED`;
- `AUTHORIZATION_READY`;
- `EXECUTION_LOCK_ACQUIRED`;
- `DISPATCH_STARTED`;
- `PROVIDER_RESPONSE_RECEIVED`;
- `READBACK_VERIFIED`;
- `COMPLETED`;
- `BLOCKED`;
- `EXECUTION_UNCERTAIN`;
- `ROLLBACK_PLANNED`;
- `ROLLBACK_DISPATCHED`;
- `ROLLBACK_VERIFIED`.

Each record carries prior-record hash/ref so audit ordering/tampering can be detected.

Provider `RequestId` and `Units` are audit metadata; OAuth/token values are never logged.

## Execution concurrency

A mutation requires a lease/lock key such as:

`site_id:provider:advertiser:entity_type:entity_id`.

Two concurrent executions for the same target are forbidden.

Lock acquisition/release and expiry are audited.

## Secret boundary

- OAuth token: Keychain locally / Lockbox production;
- provider login/mapping: private config or secret-safe registry;
- no tokens in ActionProposal, ControllerPlan, audit JSON, Git or test fixtures;
- exception/redaction tests remain mandatory.

## Day-11 output states

Public-safe controller states should include:

- `CONTROLLER_PLAN_VALID`;
- `CONTROLLER_PLAN_INVALID`;
- `BLOCKED_GOVERNOR_NOT_READY`;
- `BLOCKED_OWNER_APPROVAL`;
- `BLOCKED_KILL_SWITCH`;
- `BLOCKED_STALE_PROVIDER_STATE`;
- `BLOCKED_PROVIDER_CAPABILITY`;
- `BLOCKED_BUDGET_MAPPING`;
- `BLOCKED_MUTATION_CADENCE`;
- `BLOCKED_EXECUTION_LOCK`;
- `READY_FOR_DAY12_EXECUTION`.

Day 11 contains no `EXECUTED` state.

## Day-11 acceptance prerequisite for Editing access

Owner should be asked to change Direct access from Reading to Editing only after Central Brain independently confirms:

- Task 010R accepted;
- controller plan cannot bypass Budget Governor;
- exact >20% Owner approval binding works;
- kill-switch precedence works;
- stale-snapshot gate works;
- one-object rule enforced;
- safe no-blind-retry behavior present;
- audit chain/readback/rollback contracts tested;
- production writer remains hard-disabled by default;
- full public CI green.

Only then does Editing-access enablement become an Owner action for Day 12 readiness.
