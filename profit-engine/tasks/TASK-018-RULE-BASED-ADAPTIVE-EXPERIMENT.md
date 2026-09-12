# TASK 018 — RULE-BASED ADAPTIVE EXPERIMENT

Status: DESIGNED / PRODUCTION EXECUTION BLOCKED UNTIL AF-0 LIVE ACCEPTANCE
Execution package: `AF-3`
Executor: Codex development-only for implementation; Central Brain for acceptance
Depends on:
- Task 017 routing core;
- Task 013 production instrumentation live verification;
- Task 015 Privacy v2 + first-party endpoint acceptance for first-party outcome dispatch.

## Objective

Run the first bounded production comparison of current/static editorial next-story behavior versus the transparent rule-based Adaptive Funnel, without AI and without making the adaptive service a dependency of reading.

## Experiment arms

### Control

Current/static editorial recommendation behavior.

### Treatment

Task 017 deterministic `NextContentDecision` policy v0.1.

No arm may optimize for ad clicks or modify YAN ad behavior.

## Required deliverables

1. Stable experiment assignment contract.
2. Treatment recommendation adapter integrated around existing `DILIVOX_SYSTEM_V1` without installing a second progress/navigation controller.
3. Exact decision-to-outcome linkage.
4. Outcome events:
   - `SHOWN`;
   - `CLICKED`;
   - `OPENED`;
   - `COMPLETED`;
   - `ABANDONED`.
5. Policy/experiment version identifiers.
6. Production kill switch.
7. Automatic static fallback.
8. Experiment audit/evidence export.
9. Tests proving failure isolation and no provider mutation.

## Assignment invariants

- assignment must be reproducible for the valid experiment unit;
- control/treatment identity must not silently change mid-session;
- experiment version changes must be explicit;
- no client-side assignment may claim monetary outcomes;
- assignment must not require registered-reader identity;
- privacy-safe pseudonymous/session identity only.

## Site integration invariants

- `DILIVOX_SYSTEM_V1` remains authoritative for current reading UX/events;
- no duplicate progress observer/controller;
- no duplicate next-story click handler that inflates canonical events;
- adaptive recommendation UI must fail open to normal editorial/static navigation;
- adaptive failure must not block content, ads or existing site navigation;
- no synchronous Direct/Metrica/YAN provider call in recommendation path.

## Money/evidence boundary

Task 018 records treatment/control behavior and decision identity.

It does not declare an arm profitable.

Economic truth is evaluated in Task 019 using compatible reconciled windows.

Allowed diagnostics during experiment:
- recommendation continuation rate;
- stories/session;
- completion;
- return where valid;
- sample/exposure;
- errors/fallback rate.

These are not scale authority by themselves.

## Stop rules

Immediate or early stop is allowed when:
- reader flow breaks;
- event duplication/inflation is detected;
- treatment materially degrades a primary reader metric at meaningful exposure;
- kill/fallback path fails;
- privacy/compliance violation occurs;
- data integrity is uncertain;
- unexpected provider-write path is observed.

Economic stop/scale decision belongs to Task 019.

## Sample discipline

Do not scale from tiny lucky samples.

The strategic planning default is roughly 3,000 eligible sessions per arm for moderate continuation-rate lifts when that approximation is relevant. This is not a promise that every economic test requires exactly that number. Revenue/ARPU evidence, variance, traffic volume and downside may require a different window.

## Out of scope

- AI/LLM routing;
- content-wave production;
- Direct bid/budget changes caused by the experiment;
- provider monetization mutations;
- registered reader accounts;
- cross-device identity system.

## Acceptance criteria — CODE

1. Control and treatment are deterministic/reproducible.
2. Every treatment recommendation has a valid `decision_id`.
3. Outcome events can be joined to that decision.
4. Kill switch forces control/static fallback.
5. Endpoint/routing failure leaves reading operational.
6. No duplicate DOM controller exists.
7. No production AI call exists.
8. No provider write occurs from routing/event request paths.
9. Tests/CI pass.

## Acceptance criteria — LIVE

Live experiment may start only after AF-0 live acceptance and exact production smoke proves:
1. instrumentation events are not duplicated;
2. first-party outcome endpoint accepts bounded production events;
3. control/treatment state is visible in evidence;
4. kill switch works;
5. static fallback works;
6. reader flow remains unaffected by service failure.

Terminal state after usable experiment evidence exists:
`ADAPTIVE_AF3_EXPERIMENT_EVIDENCE_READY`.
