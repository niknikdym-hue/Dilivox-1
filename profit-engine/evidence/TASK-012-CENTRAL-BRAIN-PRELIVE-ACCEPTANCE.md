# TASK 012 — CENTRAL BRAIN PRE-LIVE ACCEPTANCE

Status: ACCEPTED — PRE-LIVE SCAFFOLD ONLY / LIVE WRITE STILL BLOCKED
Reviewed: 2026-08-28

## Exact reviewed code chain

Public branch reviewed from previous verified state `6afc5397546f52977b517738e9f0c6a50f82a314` through:

- `e09731a277c68acd9426f3a9d296444cec44a9df` — candidate binding + inert writer-arm contract;
- `a4a0e492e17d4d953195fbf3180293ae9d0654fd` — Day-12 candidate/writer-arm tests;
- `3fbfae2090b89af17813e8d70e9920e90726e8e7` — executor evidence.

Profit Engine CI run `33201727671` on exact reviewed HEAD `3fbfae2090b89af17813e8d70e9920e90726e8e7`: GREEN. Python tests, Node tests, JSON validation and whitespace checks all passed.

Private core remains unchanged at `76b1b8670690f102a045243760dfe3d1e58513d5`; private CI `33182663547`: GREEN. Private core remains proposal-only and has no provider transport/write authority.

## Central Brain review result

ACCEPT for bounded pre-live preparation only.

The reviewed work correctly preserves the canonical Day-12 boundary:

- candidate construction requires integrity-valid Day-12 readiness in `READY_FOR_LIVE_CANDIDATE_SELECTION` state;
- Day-12 readiness itself requires the accepted Task 011R SHA, Direct `EDITING` permission and PASS for Direct/Metrica/YAN doctors;
- candidate is exactly bound to site/provider/target/provider entity/method, ActionProposal digest, Governor evidence digest and ControllerPlan digest;
- measurement and provenance references are mandatory;
- the writer-arm object is explicitly inert: `executable=false`, `armed=false`, `provider_write_allowed=false`;
- `max_dispatch_attempts=1` is preserved;
- `REAL_PROVIDER_REQUESTS=0`, `ADVERTISING_SPEND=0`, `PRODUCTION_WRITER_ENABLED=false` remain unchanged;
- no provider transport/write method was added;
- the accepted ControllerPlan chain continues to enforce the exact trusted Owner approval requirement for weekly budget increases above +20%, exact provider identity, current-day cadence, preflight, lock, kill-switch, request binding and other Day-11 gates.

## Important authority interpretation

`selected_by="CENTRAL_BRAIN"` is an auditable marker, not cryptographic proof of who called the public builder. Therefore this runtime object MUST NOT be treated as independent proof that Central Brain selected a production candidate.

Actual live candidate authority remains external and canonical: Central Brain must select exactly one candidate from accepted live evidence and record the exact accepted selection/evidence identity before any executable writer can be armed. A caller-created `LiveCandidateSelection` object by itself never grants write authority.

This limitation does not block acceptance of the current work because the writer arm is deliberately non-executable and provider write authority remains false.

## What is NOT accepted yet

This acceptance does not satisfy Task 012 live launch and does not authorize any provider/site mutation.

Still required before the first real write:

1. Owner performs the canonical Direct permission transition `Reading -> Editing`;
2. exact permission state is re-read;
3. Direct/Metrica/YAN live read-only certification passes for exact scopes;
4. Central Brain selects exactly one live candidate from accepted evidence;
5. current proposal/Governor/Owner-approval/preflight/cadence/lock/TOCTOU/kill-switch chain is reconstructed and revalidated;
6. an executable writer implementation, if introduced later, must remain separately reviewed and explicitly gated to one accepted plan/target/method and one dispatch attempt;
7. one bounded Direct mutation, read-back and immutable audit are independently accepted.

## Governance preserved

- no provider mutation performed by this review;
- no site mutation performed;
- no secret values recorded;
- no private-core provider calls;
- no >20% weekly budget increase without exact Owner approval;
- no blind retry;
- no Task-012 self-acceptance by executor.

Terminal state after this review: `PRODUCTION_WRITE_BLOCKED` pending the canonical Owner/live-provider gates.
