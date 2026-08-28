# TASK 010 — CENTRAL BRAIN ACCEPTANCE

Status: ACCEPTED
Accepted: 2026-08-28

## Accepted public state

Repository: `niknikdym-hue/Dilivox-1`
Branch: `profit-engine`
Accepted Task-010R public contract SHA:

`98c6d3f0c0105c30cfc90a6d5fdf653c2aceb8d6`

Public CI run `33180647500`: GREEN.

Accepted public chain includes:
- named Metrica Direct/UTM attribution facts;
- period K5 materialization;
- explicit immutable `CohortRevenueEvidence v1`;
- cohort K5 1D/7D/30D only from per-window proven cohort revenue;
- missing cohort evidence => `NOT_COMPUTABLE_ATTRIBUTION_HOLD`;
- no campaign/day revenue masquerading as cohort revenue;
- append-versioned late cohort evidence;
- public-safe `ActionProposal v1`;
- `Budget Governor v1`;
- +20.00% clean boundary vs +20.01% Owner-approval boundary;
- data-quality, stop-loss and kill-switch structural guards;
- inert site experiment intents.

## Accepted private state

Repository: `niknikdym-hue/profit-engine-core`
Branch: `main`
Accepted private SHA:

`1709925f5b2d29f9c038dde7caca8054b51eea6f`

Private CI run `33180767637`: GREEN.

`PUBLIC_CONTRACT_VERSION.md` and private allocator constant both pin the exact accepted public Task-010R SHA.

Private ranking, confidence, thresholds and allocation policy remain private and proposal-only. Private core has no provider/site write authority.

## Safety

- provider requests during Task 010/010R: `0`;
- advertising spend: `0`;
- provider write allowed: `false`;
- no production K5>=5 claim is made from synthetic fixtures.

## Decision

`TASK_010_ACCEPTED_DAY10_COMPLETE`

Next canonical gate: Day 11 — Guarded Direct Controller dry-run/write-safety acceptance. Direct Editing remains disabled until Central Brain accepts Task 011.
