# CODEX TASK 012 — LIVE GUARDED PRODUCTION LAUNCH

Status: OWNER GATE BEFORE LIVE EXECUTION
Owner: Central Brain
Executor: Codex
Launch day: Day 12

## Repository

`niknikdym-hue/Dilivox-1`
branch `profit-engine`
local `~/Documents/New project/Profit Engine/Dilivox-1`

## Read first

1. `profit-engine/PROJECT_STATE.md`
2. `profit-engine/evidence/TASK-011-CENTRAL-BRAIN-ACCEPTANCE.md`
3. `profit-engine/DAY12_LIVE_PRODUCTION_LAUNCH_DESIGN.md`
4. `profit-engine/DAY12_PROVIDER_LIVE_CERTIFICATION.md`
5. `profit-engine/DAY12_FIRST_WRITE_ACCEPTANCE_MATRIX.md`
6. accepted Day-10 money/decision evidence
7. current provider access/security docs

## Owner gate

DO NOT execute Task 012 live write until Central Brain records that Owner has explicitly changed the relevant Yandex Direct access from Reading to Editing.

Editing access is necessary but not sufficient for write authorization.

## Phase A — live certification, no mutation

After Owner permission transition:

- load Direct/Metrica/YAN credentials from secret-safe local storage without printing values;
- run Direct READ_ONLY doctor;
- prove exact acting login/client/advertiser identity and exact registered target visibility;
- run Metrica READ_ONLY doctor for exact site/counter scope;
- run YAN Statistics READ_ONLY doctor for exact partner/site scope;
- produce secret-safe evidence with status/timestamps/scope refs/provider RequestId/Units where available;
- keep production writer disabled;
- provider mutation count remains 0.

If any required live scope is missing/ambiguous, stop `PRODUCTION_WRITE_BLOCKED`.

## Phase B — live candidate selection

Central Brain selects exactly one production candidate from accepted live evidence.

No fixture may select the target.
No campaign-name/URL/date/fuzzy inference.

Preferred first action is the most reversible and lowest-downside accepted action, with safety STOP/suspend considered before budget growth.

## Phase C — final guarded authorization

For the selected candidate, reconstruct/revalidate the exact accepted chain:

- current public/private decision refs;
- ActionProposal digest;
- Governor evidence;
- trusted Owner approval if >20%;
- exact registered provider target;
- fresh provider preflight;
- integrity-valid current-day cadence if budget update;
- exact execution lock;
- fresh pre-dispatch TOCTOU comparison;
- runtime kill-switch recheck;
- exact one-object normalized request derived from immutable plan;
- production writer arming scoped to exact plan/target/method and one dispatch attempt.

Any failed gate => zero dispatches.

## Phase D — one bounded real mutation

Send exactly one Direct mutation request containing exactly one provider object.

No create/add/delete/archive/moderate/strategy migration for first launch write.

Before send append `DISPATCH_STARTED` audit record.

Capture secret-safe:
- transport/HTTP state;
- per-object provider result;
- Direct RequestId/Units where returned.

No blind retry.

## Phase E — read-back and classification

Immediately perform READ_ONLY read-back.

Expected state must be plan-derived.

Classify:
- exact desired state verified -> `GUARDED_PRODUCTION_LAUNCHED`;
- dispatch prevented -> `PRODUCTION_WRITE_BLOCKED`;
- uncertain/unverifiable -> `PRODUCTION_EXECUTION_UNCERTAIN`;
- rollback, if separately authorized and verified -> `PRODUCTION_ROLLBACK_VERIFIED`;
- unsafe/unavailable rollback -> `PRODUCTION_ROLLBACK_BLOCKED`.

## Rollback

Never blind/automatic. Use exact immutable prior preflight only. Rollback is a separate guarded mutation requiring current authorization/kill/lock/preflight/audit/read-back gates.

## Global safety

- no secrets in Git/chat/issues/evidence/logs;
- no multi-object writes;
- no automatic retry loops;
- no private-core provider calls;
- no Tilda/site mutation in this task unless separately accepted;
- no paid Cloud apply without explicit Owner authorization;
- weekly budget increase >20% requires exact trusted Owner approval;
- at most one autonomous campaign budget mutation per campaign/day.

## Evidence

Create:

`profit-engine/evidence/TASK-012-LIVE-GUARDED-PRODUCTION-LAUNCH.md`

Evidence must state whether a real provider request was sent, exact terminal classification, secret-safe RequestId/Units where available, read-back result, audit digest and rollback disposition.

## Acceptance

Codex does not self-accept.
Central Brain independently verifies live evidence and decides whether engineering launch is `GUARDED_PRODUCTION_LAUNCHED`.

A successful write does not prove `K5 >= 5.0`; economic proof is post-launch reconciled live measurement.