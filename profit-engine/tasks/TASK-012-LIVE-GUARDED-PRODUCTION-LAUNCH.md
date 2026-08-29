# TASK 012 — LIVE GUARDED PRODUCTION LAUNCH

Status: OWNER GATE BEFORE LIVE EXECUTION
Owner / current executor: Central Brain
Codex: paused; no new Codex work until Owner restores its usage limit
Launch day: Day 12

## Repository

`niknikdym-hue/Dilivox-1`
branch `profit-engine`

## Authority

Read current `profit-engine/PROJECT_STATE.md` first, then:
1. `profit-engine/evidence/TASK-011-CENTRAL-BRAIN-ACCEPTANCE.md`;
2. `profit-engine/DAY12_LIVE_PRODUCTION_LAUNCH_DESIGN.md`;
3. `profit-engine/DAY12_PROVIDER_LIVE_CERTIFICATION.md`;
4. `profit-engine/DAY12_FIRST_WRITE_ACCEPTANCE_MATRIX.md`;
5. latest Task-012 evidence files;
6. issue #19.

## Current Owner gate

DO NOT execute a live write until Owner explicitly changes the exact Yandex Direct Managing Account relationship for the owner advertiser managed by `reklamadymova` from Reading to Editing.

That permission change is necessary but not sufficient for write authorization.

## Phase A — live certification, no mutation

After Owner permission transition:
- bind fresh Owner UI Editing evidence to the exact private managed target;
- load Direct/Metrica/YAN credentials from existing secret-safe local storage;
- prove exact Direct operator + exact distinct managed advertiser + exact target visibility;
- run Metrica doctor for exact Dilivox counter and goals;
- run YAN Statistics doctor for exact `dilivox.ru` scope;
- keep production writer disabled during certification;
- any ambiguity/failure => `PRODUCTION_WRITE_BLOCKED`.

## Phase B — exact live candidate selection

Central Brain selects exactly one live candidate from accepted evidence.

First-launch preference: the lowest-downside, most reversible accepted safety action.

Allowed first-live methods only:
- `campaign.suspend`;
- `campaign.resume`;
- `ad.suspend`;
- `ad.resume`.

No create/add/delete/archive/moderate/strategy migration.
No fuzzy campaign-name/URL/date inference.

`campaign.update_budget` is not live-enabled in this phase. Current Direct budget control is strategy-aware and uses `WeeklySpendLimit`; the legacy Day-11 DailyBudget mapping is synthetic only until separately reworked and accepted.

## Phase C — final guarded authorization

For the selected candidate revalidate:
- current public/private decision refs;
- ActionProposal digest;
- Governor evidence;
- exact registered provider target;
- fresh provider preflight;
- exact execution lock;
- fresh TOCTOU comparison;
- runtime kill-switch recheck;
- exact one-object normalized request;
- one-shot production writer arm bound to readiness + candidate + ControllerPlan + exact target/method.

Any failed gate => zero dispatches.

## Phase D — one bounded real mutation

Send exactly one Direct mutation request with exactly one object ID through JSON v501.

Mutation transport is single-attempt: no automatic retry on timeout, 429 or 5xx.

Append `DISPATCH_STARTED` before send and capture secret-safe provider response / RequestId / Units where available.

## Phase E — read-back and classification

Immediately perform exact read-only state read-back.

Terminal classification:
- exact desired state verified => `GUARDED_PRODUCTION_LAUNCHED`;
- provider rejected and exact prior state remains => `PRODUCTION_WRITE_BLOCKED`;
- timeout/unexpected/unverifiable state => `PRODUCTION_EXECUTION_UNCERTAIN`.

No blind retry.

## Rollback

Never blind/automatic. Use exact immutable prior preflight only. Rollback is a separate guarded mutation with fresh authorization/kill/lock/preflight/audit/read-back gates.

## Global safety

- no secrets in Git/chat/issues/evidence/logs;
- no multi-object writes;
- no automatic retry loops;
- private core remains proposal-only and never calls providers;
- no Tilda/site mutation in Task 012 unless separately accepted;
- weekly budget increase >20% still requires exact explicit Owner approval;
- production writer remains disabled until all live gates pass.

## Evidence

Final live execution creates:
`profit-engine/evidence/TASK-012-LIVE-GUARDED-PRODUCTION-LAUNCH.md`

It must record whether a provider mutation was sent, exact terminal classification, secret-safe RequestId/Units where available, read-back, audit digest and rollback disposition.

## Acceptance

Central Brain independently verifies final live evidence and alone decides whether engineering launch is `GUARDED_PRODUCTION_LAUNCHED`.

A successful engineering write does not prove `K5 >= 5.0`; economic proof is post-launch reconciled live measurement.
