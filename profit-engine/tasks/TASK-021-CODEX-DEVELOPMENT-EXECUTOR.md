# TASK 021 — BOUNDED CODEX DEVELOPMENT EXECUTOR

Status: READY FOR BOUNDED DEVELOPMENT
Executor: Codex/OpenAI API implementation under Central Brain acceptance
Authority: `profit-engine/CODEX_DEVELOPMENT_ONLY_POLICY.md`
Purpose: development tooling only

## Objective

Create a minimal, economical and fail-closed development workflow for executing approved DILIVOX engineering tasks with Codex/OpenAI API without making Codex a production dependency or granting it merge/deploy/provider-write authority.

Canonical development flow:

`approved bounded task spec`
`-> exact repository/branch/base SHA`
`-> Codex development execution`
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
- optional maximum API spend/token bound.

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
- no automatic paid retry after provider/API failure;
- changed paths must be validated before acceptance;
- deterministic checks must run before a result can be presented as code-ready.

## Model/cost policy

Use the least expensive model that reliably completes the engineering task.

The execution layer must permit model selection by task class rather than hard-code the most expensive model.

Development AI spend is tracked separately as `DEV_AI_COST`.

A failed/partial paid run is recorded and not automatically retried.

Astra is not required by this task. Independent architecture/review escalation may be performed separately when justified; it is not a permanent step in every development run.

## Output contract

A run must produce a bounded result manifest containing at least:
- task ID;
- base SHA;
- resulting head/patch identity;
- changed paths;
- tests/checks requested;
- tests/checks result;
- scope validation result;
- spend/token accounting if available;
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
4. No automatic paid retry exists.
5. Deterministic checks run before `READY_FOR_REVIEW`.
6. Result manifest is durable and auditable.
7. Draft PR/patch contains only bounded task changes.
8. Development spend is separately attributable as `DEV_AI_COST` where technically available.
9. Central Brain review is required before code-ready acceptance.
10. Tests prove fail-closed behavior for moved SHA, out-of-scope change and missing task contract.

Terminal state:
`DILIVOX_CODEX_DEVELOPMENT_EXECUTOR_READY`.
