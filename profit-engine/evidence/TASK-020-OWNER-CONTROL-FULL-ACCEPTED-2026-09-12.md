# TASK 020 — FULL OWNER CONTROL — CENTRAL BRAIN ACCEPTED

Date: 2026-09-12
Repository: `niknikdym-hue/Dilivox-1`
Canonical branch: `profit-engine`
PR: `#22 — Task 020 — Full Owner Control / dual-window project management`

Status: `DILIVOX_OWNER_CONTROL_FULL_CODE_READY / CENTRAL_BRAIN_ACCEPTED`

## Exact acceptance binding

Original Task 020 base:

`c06220299dc700ed442ce53eb364105e12100999`

Exact accepted PR head after Central Brain repair:

`e8e9ca52d785ab0caf0e81688435993032163195`

Merge SHA:

`262ac109bc3dcf1d6b50638d6142e5c8f5adae90`

## Central Brain review

Central Brain inspected the actual implementation rather than accepting the Codex handoff by report alone.

Verified boundaries include:

- one `Profit Engine.app` product surface;
- one localhost backend;
- two separate top-level windows/routes: `/profit` and `/project`;
- money-first Profit window remains separate from project-development controls;
- Project Control includes A-E stages, Critical Path, Whole Project, Adaptive Funnel, Content, Providers & Compliance, Owner Gates, Development and History;
- normal owner development commands operate through the local Project Control backend rather than requiring GitHub web UI;
- Start / Start next / package 1-5 / Pause / Resume / Stop / Refresh are bounded controls;
- package execution is sequential and stops on first failure, blocker, authority movement or bounded budget failure;
- GitHub stays durable source of truth and execution plane;
- browser receives no GitHub token, OpenAI key or provider credentials;
- localhost state-changing controls require exact Origin, per-launch CSRF, JSON-only POST, command allowlists, request idempotency and burst protection;
- Owner Gate decisions are exact task/scope/SHA-bound durable evidence and do not grant generic provider authority;
- provider writes, Tilda publication, merge/deploy authority and production visitor AI are not exposed by generic Project Control commands;
- Development FinOps stays separate from Direct/YAN/K5 economics.

## Central Brain acceptance repair

The submitted Task 020 implementation originally still installed the real app only to:

`~/Applications/Profit Engine.app`

That violated the Owner's explicit requirement for a normal Desktop button.

Central Brain repaired this deterministically in the same PR, with no Codex/OpenAI spend:

- real app bundle: `~/Desktop/Profit Engine.app`;
- compatibility path: `~/Applications/Profit Engine.app`;
- the compatibility path is only a symlink to the same Desktop bundle;
- there is still exactly one real app, one backend and two windows.

Regression coverage now enforces this contract.

## Free end-to-end Owner Control smoke

G0 smoke run:

`34715623912`

Result:

- event: `workflow_dispatch`;
- canonical head at smoke: `c06220299dc700ed442ce53eb364105e12100999`;
- static job: SUCCESS;
- API-key preflight: SUCCESS;
- OpenAI provider calls: `0`;
- actual `DEV_AI_COST`: `$0.00`;
- automatic paid retry count: `0`;
- panel terminal state: `READY_FOR_REVIEW`.

This proves the Owner Panel -> localhost backend -> fixed GitHub control -> workflow -> result reconciliation path without a paid model call.

## Exact PR-head evidence after Desktop repair

Exact PR head:

`e8e9ca52d785ab0caf0e81688435993032163195`

- Profit Engine CI run `34717663393`: SUCCESS;
- DILIVOX dev preflight run `34717663383`: static SUCCESS;
- no review blockers;
- no paid API-Codex smoke;
- no provider/Tilda/production mutation.

## Canonical post-merge evidence

Merge SHA:

`262ac109bc3dcf1d6b50638d6142e5c8f5adae90`

- Profit Engine CI run `34717780270`: test job SUCCESS;
- DILIVOX dev preflight run `34717780289`: static SUCCESS;
- DILIVOX dev preflight run `34717780289`: `api-key-preflight` SUCCESS;
- repository `OPENAI_API_KEY` remains configured without exposing its value.

## Acceptance boundary

Accepted:

`TASK 020 = DILIVOX_OWNER_CONTROL_FULL_CODE_READY`

This acceptance does not claim:

- that the Owner's Mac has already installed the new canonical bundle;
- that a paid API-Codex smoke has run;
- that Task 012 Direct mutation is authorized;
- that Tilda instrumentation has been published;
- that production provider state changed;
- that Adaptive Funnel is live or economically proven.

The next local Owner step for the application itself is to install/update the now-canonical build once; after that ordinary operation is by double-clicking `~/Desktop/Profit Engine.app`.