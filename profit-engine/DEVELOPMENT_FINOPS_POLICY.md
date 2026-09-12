# DILIVOX PROFIT ENGINE — DEVELOPMENT FINOPS POLICY

Status: OWNER-APPROVED / CANONICAL COMPANION DECISION
Date: 2026-09-12
Repository: `niknikdym-hue/Dilivox-1`
Branch: `profit-engine`
Parent authority: `profit-engine/PROFIT_ENGINE_AUTHORITY.md`
Development boundary: `profit-engine/CODEX_DEVELOPMENT_ONLY_POLICY.md`
Execution project: `profit-engine/ADAPTIVE_FUNNEL_EXECUTION_PROJECT.md`

## 1. PURPOSE

Control development cost without slowing delivery or reducing engineering quality.

Canonical principle:

> Use the least expensive execution route that is fully sufficient for the required quality, correctness and risk level. Cost optimization must never force an underpowered route.

This policy is `QUALITY-FIRST / COST-AWARE`.

It is not `FREE-AT-ANY-COST` and not `AI-BY-DEFAULT`.

A free route is preferred only when it can produce the same required result quality, evidence and safety as the paid route for that task.

If a task genuinely requires Codex, Codex works. If it genuinely requires Sol, the project must not first waste time or quality on Luna/Terra merely to appear cheaper.

## 2. PRIMARY ROUTING RULE

Before execution, classify the task by the minimum capability needed for a correct result.

Routing question:

`What is the least expensive route that is confidently sufficient for this task?`

Not:

`Can we somehow force this task through the free path?`

The selected route must consider:
- task complexity;
- code-generation needs;
- number of interacting modules;
- ambiguity of the implementation;
- security/privacy sensitivity;
- money/accounting/provider-write sensitivity;
- availability of deterministic acceptance tests;
- consequences of a wrong result;
- previous evidence that a cheaper model is or is not sufficient for this task class.

## 3. EXECUTION ROUTES

### G0 — GitHub-native / deterministic

Use GitHub Actions, Python, repository scripts, tests and registered declarative playbooks when the work is deterministic and does not benefit materially from model reasoning.

Examples:
- lint / type / schema / unit tests;
- deterministic validation and CI;
- exact text replacement;
- bounded JSON/YAML updates;
- generated reports from structured data;
- registry consistency checks;
- status/board projection;
- deterministic calculations;
- static build/render checks;
- evidence collection/comparison;
- mechanical migration already completely specified by a trusted contract.

OpenAI API target: `$0`.

G0 must NOT be used when doing so would materially reduce implementation quality, create brittle code, hide design decisions or delay a task that clearly needs reasoning/code synthesis.

There is no requirement to attempt G0 first.

### G1 — API-Codex / Luna

Use for small bounded reasoning/code tasks where Luna is known to be sufficient, for example:
- small single-file transformation;
- narrow test/fixture generation;
- simple bug repair with an already-localized cause;
- low-risk documentation-to-code adaptation;
- small repetitive code changes that are not safely expressible as a deterministic playbook.

Planning soft cap: approximately `$0.15` per task.

Do not route a task to Luna when its complexity or risk profile indicates Terra/Sol is more appropriate.

### G2 — API-Codex / Terra

Default paid development route for normal software engineering.

Use for:
- new bounded modules;
- ordinary multi-file features;
- implementation plus tests;
- non-trivial bug fixing;
- API/data-pipeline/UI work;
- normal Adaptive Funnel implementation;
- Owner Panel feature work.

Planning soft cap: approximately `$0.75` per task.

If a task clearly belongs here, route directly to Terra. Do not require a failed free/Luna attempt first.

### G3 — API-Codex / Sol

Use for genuinely complex or high-consequence engineering, including:
- difficult multi-module integration;
- state/concurrency/idempotency problems;
- security/privacy-sensitive implementation;
- money/accounting/reconciliation logic;
- provider-write guardrails;
- difficult root-cause debugging after deterministic evidence has localized the problem;
- critical review where stronger reasoning materially reduces risk.

Planning soft cap: approximately `$1.50` per task.

Route directly to Sol when the task class clearly requires it. Do not degrade quality by forcing Terra first.

### G4 — Astra

Astra is exceptional and OFF by default.

Use only where its additional reasoning value is material, such as:
- fundamental architecture change;
- independent review of a critical money/security/governance boundary;
- disputed architecture where Central Brain/Sol evidence is insufficient;
- a task explicitly marked `astra_allowed=true` under an Owner-approved Astra budget envelope.

Astra is not the normal coder and is not inserted before/after every task.

If no Astra envelope is already approved, Astra use is an Owner Gate.

## 4. QUALITY FLOOR

Every task has a `quality_floor` derived from its acceptance criteria.

The route is acceptable only if it can plausibly meet that floor without hidden manual repair.

Examples:
- deterministic registry check: G0 is sufficient;
- new NextContentDecision engine: G2/Terra is appropriate;
- privacy-safe event ingestion with idempotency and money-sensitive joins: G2 or G3 depending on exact slice;
- critical Direct mutation safety: G3/Sol review is justified;
- architecture rewrite affecting multiple owner-approved invariants: consider G4/Astra.

A cheaper route that repeatedly produces partial, low-confidence or repair-heavy work is not cheaper in economic terms and must be reclassified.

## 5. NO-WASTE AUDIT FIELDS

Every task records:
- `execution_route`: `G0|G1|G2|G3|G4`;
- `model_route`: `none|luna|terra|sol|astra`;
- `routing_reason`;
- `quality_floor`;
- `why_not_cheaper` when a paid/stronger route is selected;
- hard budget cap for paid routes;
- actual `DEV_AI_COST` where available.

Examples of `why_not_cheaper`:
- `NEW_NONTRIVIAL_CODE_SYNTHESIS`;
- `MULTIFILE_REASONING_REQUIRED`;
- `SECURITY_OR_MONEY_SENSITIVE`;
- `DETERMINISTIC_ROUTE_CANNOT_MEET_QUALITY_FLOOR`;
- `CHEAPER_MODEL_PREVIOUSLY_INSUFFICIENT_FOR_TASK_CLASS`;
- `COMPLEX_ROOT_CAUSE_DEBUGGING`.

These fields are audit data, not extra Owner approval gates.

## 6. INITIAL DEVELOPMENT BUDGET ENVELOPE

For the current initial build covering AF-0/AF-1/AF-2, the development executor and read-only Owner Panel slices:

`INITIAL_OPENAI_DEV_ENVELOPE_USD = 10.00`

This is a hard aggregate ceiling, not a spending target.

Central Brain may select G1/G2/G3 routes and execute bounded development tasks inside this envelope without asking the Owner for approval on every normal call, provided scope, safety and authority rules remain satisfied.

Budget handling:
- G0 consumes `$0` OpenAI budget;
- G1/G2/G3 spend counts against the shared envelope;
- at 80% consumption, Owner Control shows a warning but work does not automatically stop;
- at 100%, new paid development becomes an Owner Gate;
- unused budget is never consumed merely because it is available;
- extending the envelope requires explicit Owner approval.

Astra is excluded from the initial `$10` envelope unless separately approved.

## 7. TASK AND PACKAGE LIMITS

Default package size: up to 3 related bounded tasks.

Maximum package size: 5 tasks when one cumulative branch is clearly more efficient and dependencies are compatible.

Default hard OpenAI package cap: `$3.00`.

Per-task model caps are planning controls, not artificial stop conditions. A task may exceed its soft planning cap when:
- the package remains inside its hard cap;
- the phase envelope remains available;
- execution is making meaningful in-scope progress;
- no authority/safety boundary is crossed.

Do not throw away useful in-scope work merely because a soft estimate was imperfect.

## 8. ESCALATION WITHOUT NEEDLESS STALLS

Automatic route selection/escalation is permitted inside the approved envelope.

Allowed examples:
- deterministic task -> G0;
- obvious ordinary coding task -> G2 directly;
- small bounded reasoning task -> G1;
- obvious complex/security/money-sensitive task -> G3 directly;
- G1 -> G2 when evidence shows a capability gap;
- G2 -> G3 when the task remains in scope and stronger reasoning is justified.

Do not automatically escalate to Astra.

A paid failure does not mean blind paid retry. First inspect free logs/tests/evidence and decide whether the problem is:
- task specification;
- stale base/state;
- deterministic code/test failure;
- provider/tool failure;
- actual model capability gap.

Only the last category normally justifies model escalation.

## 9. STOP CONDITIONS

Development must stop/pause only for real reasons, such as:
- hard budget envelope exhausted;
- base SHA/scope moved incompatibly;
- out-of-scope changes;
- prohibited production/provider action would be required;
- owner-gated action reached;
- security/privacy/capital guardrail conflict;
- repeated evidence that the task contract is underspecified and continuing would create unreliable code.

Do NOT stop merely because:
- a free route is unavailable;
- a paid route is needed;
- a normal bounded Codex task costs a small amount inside the approved envelope;
- the stronger model is justified by task complexity.

## 10. ASTRA POLICY

`ASTRA_DEFAULT = OFF`

Astra is used only when its incremental quality/risk-reduction value justifies its incremental cost.

There is no automatic chain:

`Luna -> Terra -> Sol -> Astra`.

The correct route may start directly at Terra or Sol.

## 11. OWNER PANEL REQUIREMENT

Owner Control must expose development economics separately from production economics:
- GitHub-native task count / `$0` OpenAI cost;
- Luna/Terra/Sol/Astra task counts;
- current route for active task;
- `routing_reason` / `why_not_cheaper`;
- task hard cap;
- actual DEV_AI_COST;
- current phase envelope;
- remaining envelope;
- 80% warning state;
- whether Astra is enabled/disabled.

Development cost must never be mixed into visitor-level `PRODUCTION_AI_COST` or hidden inside K5.

## 12. ACCEPTANCE PRINCIPLE

The successful policy is not the one with the lowest API bill.

It is the one that minimizes total development cost while preserving required engineering quality and delivery speed.

Canonical priority:

`QUALITY & CORRECTNESS -> DELIVERY SPEED -> COST EFFICIENCY -> MODEL MINIMIZATION`

Cost efficiency matters, but never above correctness or the approved quality floor.
