# TASK 012 — Candidate binding and inert writer-arm evidence

Status: CENTRAL BRAIN IMPLEMENTATION / PENDING FINAL CI
Updated: 2026-08-28

## Scope

This evidence records the pre-live Day-12 candidate-binding and writer-arming preparation. It does not authorize or perform a provider mutation.

## Implemented contracts

`profit-engine/runtime/profit_engine_runtime/day12_launch_gate.py` adds:

- `LiveCandidateSelection v1` — binds exactly one Central-Brain/private-core-selected candidate to the accepted Day-12 readiness state and immutable `ControllerPlan`;
- exact site/provider/target/provider entity/method/proposal/governor/controller-plan binding;
- required private decision reference and digest without exposing private ranking logic;
- required live measurement/provenance references;
- public runtime is forbidden from self-selecting a commercial winner (`selected_by` must be `CENTRAL_BRAIN`);
- integrity digest/tamper detection;
- `WriterArmIntent v1` — an inert, exact-plan-bound, one-shot arming preparation with `max_dispatch_attempts=1`;
- writer-arm intent is deliberately `executable=false`, `armed=false`, `provider_write_allowed=false`;
- `REAL_PROVIDER_REQUESTS=0`, `ADVERTISING_SPEND=0`, `PRODUCTION_WRITER_ENABLED=false` remain preserved.

## Fail-closed boundary

Candidate construction fails if:
- Day-12 readiness is not integrity-valid;
- readiness is not `READY_FOR_LIVE_CANDIDATE_SELECTION`;
- readiness itself claims provider write permission;
- controller plan is not integrity-valid / Day12-ready;
- private decision identity is absent or malformed;
- measurement/provenance evidence is absent;
- public runtime attempts to self-select a commercial winner.

Writer-arm preparation fails if:
- candidate integrity is invalid;
- plan integrity/state is invalid;
- candidate and ControllerPlan do not match exactly;
- target/method/proposal/governor identity mismatches;
- expiry is not strictly after preparation time.

## Tests

`profit-engine/runtime/tests/test_day12_launch_gate.py` covers:
- blocked readiness cannot create a candidate;
- public runtime cannot self-select commercial winner;
- exact candidate binding and integrity;
- candidate tamper detection;
- writer arm remains inert, non-executable and one-shot;
- tampered plan / invalid expiry fail closed.

## Safety

No provider transport or write method was added by this work.
No credential/token/provider-private mapping value is stored here.
No real Direct request was sent.
No advertising spend was created.

The first real writer remains a separate later gate after Owner Editing confirmation, live provider certification, exact live candidate selection, current authorization evidence, lock/TOCTOU/kill-switch checks and explicit one-plan writer arming.
