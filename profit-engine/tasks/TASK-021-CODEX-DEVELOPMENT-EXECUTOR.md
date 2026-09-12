# TASK 021 — BOUNDED CODEX DEVELOPMENT EXECUTOR

Status: READY FOR BOUNDED DEVELOPMENT
Executor: Codex/OpenAI API implementation under Central Brain acceptance
Authority: `profit-engine/CODEX_DEVELOPMENT_ONLY_POLICY.md`
FinOps authority: `profit-engine/DEVELOPMENT_FINOPS_POLICY.md`
Purpose: development tooling only

## Objective

Create a minimal, economical and fail-closed development workflow for executing approved DILIVOX engineering tasks with GitHub-native tooling and Codex/OpenAI API without reducing engineering quality, making Codex a production dependency, or granting it merge/deploy/provider-write authority.

Canonical development flow:

`approved bounded task spec`
`-> classify minimum sufficient quality/capability route`
`-> exact repository/branch/base SHA`
`-> GitHub-native OR API-Codex execution`
`-> changed-path/scope validation`
`-> deterministic tests/checks`
`-> Draft PR or reviewable patch`
`-> Central Brain acceptance`

No production visitor/commercial runtime path may depend on this workflow.

## Inputs

Each run must bind to:
- repository;
- exact base branch;
- exact base SHA;
- task ID;
- allowed paths or explicit scope;
- required checks;
- prohibited actions;
- expected evidence/artifacts;
- `quality_floor`;
- selected `execution_route` (`G0|G1|G2|G3|G4`);
- selected `model_route` (`none|luna|terra|sol|astra`);
- `routing_reason`;
- `why_not_cheaper` for paid/stronger routes;
- hard API budget cap for paid routes.

## Required protections

- fail closed if base SHA moved unexpectedly;
- fail closed on dirty/out-of-scope workspace;
- no secret values in prompts/logs/artifacts;
- no automatic merge;
- no deploy;
- no Tilda publication;
- no Direct/Metrica/YAN provider mutation;
- no production data mutation;
- no autonomous budget/spend authority;
- no blind automatic paid retry after provider/API failure;
- changed paths must be validated before acceptance;
- deterministic checks must run before a result can be presented as code-ready.

## Model / quality / cost policy

Follow `DEVELOPMENT_FINOPS_POLICY.md`.

The route is chosen by the least expensive capability that is confidently sufficient for the required quality and risk level.

Important:
- GitHub-native is preferred only where it can meet the same required quality;
- there is NO requirement to attempt the free route first;
- if a task clearly requires normal code synthesis, route directly to Terra;
- if a task is clearly complex/security/money-sensitive, route directly to Sol when justified;
- do not force Luna/Terra attempts that are likely to reduce quality or create repair work;
- Astra remains exceptional and OFF by default unless separately admitted.

Initial shared development envelope for AF-0/AF-1/AF-2 + executor + read-only panel slices:

`INITIAL_OPENAI_DEV_ENVELOPE_USD = 10.00`

Default hard OpenAI package cap:

`$3.00`

Planning soft caps are guidance, not artificial stop conditions:
- G1 / Luna: ~`$0.15` per task;
- G2 / Terra: ~`$0.75` per task;
- G3 / Sol: ~`$1.50` per task.

Development AI spend is tracked separately as `DEV_AI_COST`.

A failed/partial paid run is recorded. Before another paid attempt, use free logs/tests/evidence to classify whether the cause is task specification, stale base, deterministic failure, provider/tool failure, or actual model capability gap. Only a real capability gap normally justifies model escalation.

## Quality floor

Every task must declare or derive a `quality_floor` from acceptance criteria.

A cheaper execution route is invalid when it is reasonably expected to:
- lower code correctness;
- omit required tests/evidence;
- produce brittle or incomplete implementation;
- increase security/privacy/money risk;
- create predictable manual repair/rework;
- materially slow the critical path.

The executor must optimize total development economics, not API price in isolation.

## Routing examples

- exact JSON status update with complete declarative contract -> G0 / GitHub-native;
- Task 016 deterministic registry projection -> mostly G0, with G1 only for bounded non-deterministic assistance if actually needed;
- Task 017 NextContentDecision implementation -> G2 / Terra by default;
- Task 015 complex endpoint/idempotency/security slice -> G2 or G3 based on exact risk;
- Direct/money/reconciliation safety logic -> G3 / Sol review where materially justified;
- fundamental authority/architecture rewrite -> consider G4/Astra only under separate approval/envelope.

## Output contract

A run must produce a bounded result manifest containing at least:
- task ID;
- base SHA;
- resulting head/patch identity;
- changed paths;
- execution route;
- model route;
- routing reason;
- why-not-cheaper reason where applicable;
- quality floor;
- hard budget cap;
- actual spend/token accounting if available;
- tests/checks requested;
- tests/checks result;
- scope validation result;
- blocked/partial/complete state;
- prohibited actions confirmed not executed;
- Draft PR URL/number when a PR is created.

## Run states

At minimum:
- `PLANNED`;
- `RUNNING`;
- `PAUSED`;
- `PARTIAL`;
- `FAILED_CLOSED`;
- `CHECKS_FAILED`;
- `READY_FOR_REVIEW`;
- `ACCEPTED_CODE_READY`.

`ACCEPTED_CODE_READY` is not live/provider/economic acceptance.

## First intended consumers

Use this executor for bounded implementation of:
- Task 016;
- Task 017;
- Task 020 read-only/project slices;
- later Task 018/019 code only after their dependencies permit it.

## Out of scope

- production next-story selection;
- commercial decisioning;
- runtime AI personalization;
- automatic task invention outside approved specs;
- merge/deploy/provider execution;
- replacing GitHub as source of truth.

## Acceptance criteria

1. Exact repo/base SHA is required for a run.
2. Scope/allowed-path violations fail closed.
3. No production/provider writes are possible from the normal workflow.
4. No blind automatic paid retry exists.
5. Deterministic checks run before `READY_FOR_REVIEW`.
6. Result manifest is durable and auditable.
7. Draft PR/patch contains only bounded task changes.
8. Development spend is separately attributable as `DEV_AI_COST` where technically available.
9. Central Brain review is required before code-ready acceptance.
10. Tests prove fail-closed behavior for moved SHA, out-of-scope change and missing task contract.
11. GitHub-native all-free packages force OpenAI budget to `$0`.
12. Paid routes can start directly when the task quality floor justifies them; no failed-free-attempt prerequisite exists.
13. Route/model selection and `why_not_cheaper` are visible in the result manifest.
14. The executor cannot silently downgrade a task to a cheaper model when doing so would violate its declared quality floor.

Terminal state:
`DILIVOX_CODEX_DEVELOPMENT_EXECUTOR_READY`.
