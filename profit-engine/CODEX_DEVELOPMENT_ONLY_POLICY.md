# DILIVOX PROFIT ENGINE — CODEX DEVELOPMENT-ONLY POLICY

Status: OWNER-APPROVED / CANONICAL COMPANION DECISION
Date: 2026-09-12
Repository: `niknikdym-hue/Dilivox-1`
Branch: `profit-engine`
Parent authority: `profit-engine/PROFIT_ENGINE_AUTHORITY.md`
Implementation plan: `profit-engine/ADAPTIVE_FUNNEL_IMPLEMENTATION_PLAN.md`
Development FinOps: `profit-engine/DEVELOPMENT_FINOPS_POLICY.md`

## OWNER DECISION

Codex and OpenAI API access used for Codex-style software engineering are DEVELOPMENT TOOLS ONLY for DILIVOX Profit Engine.

They may be used to accelerate engineering work such as:
- reading and modifying repository code;
- implementing instrumentation, APIs, data pipelines and Adaptive Funnel components;
- creating tests and fixtures;
- running or repairing CI;
- preparing pull requests and code review;
- refactoring and debugging;
- producing development documentation;
- bounded engineering analysis required to implement the approved architecture.

They must NOT be part of the DILIVOX production visitor path.

In particular Codex/OpenAI development tooling must NOT:
- be called on every visitor, pageview, click or story transition;
- choose production next-story actions for readers;
- participate in production monetization decisions;
- control Yandex Direct spend, bids or budgets;
- replace Profit Engine decision/governance logic;
- become a production dependency required for the site to function;
- be counted as a production AI feature whose runtime cost scales with visitor traffic.

## QUALITY-FIRST DEVELOPMENT ROUTING

Development cost optimization must not reduce engineering quality or unnecessarily slow delivery.

The canonical routing rule is:

> Use the least expensive execution route that is fully sufficient for the required quality, correctness and risk level.

Therefore:
- deterministic/GitHub-native work is preferred when it is genuinely sufficient;
- there is no requirement to attempt a free route first;
- when a task genuinely requires Codex, Codex should be used directly;
- when the task complexity/risk genuinely requires a stronger Codex model, the stronger route may be selected directly;
- a cheaper route that predictably creates low-quality, partial or repair-heavy work is not considered economical.

Detailed routing, budget envelopes and model classes are governed by `DEVELOPMENT_FINOPS_POLICY.md`.

## PRODUCTION ARCHITECTURE REMAINS UNCHANGED

The approved Adaptive Funnel plan remains in force:

`visitor -> measured behavior/state -> allowed candidate set -> cheap rule/statistical ranker -> next content -> measurement -> Profit Engine`

Production AI, if ever tested later, is governed separately by the provider-neutral AI doctrine and Feature Profit Gate in `PROFIT_ENGINE_AUTHORITY.md`. Such a future production AI experiment is NOT Codex and is not authorized by this development-tooling decision.

## COST ACCOUNTING

Codex/OpenAI API engineering spend must be tracked separately as development cost, e.g. `DEV_AI_COST`.

Any future production AI runtime cost must be tracked separately, e.g. `PRODUCTION_AI_COST`.

Development-tooling spend must never be hidden inside visitor-level monetization economics or used to justify a production AI dependency.

## GOVERNANCE

- GitHub remains source of truth.
- Codex may implement approved work but does not redefine project authority.
- Central Brain/Owner-approved architecture, profit gates, provider boundaries and safety rules remain authoritative.
- No production mutation or budget authority is granted to Codex by this policy.
- Quality/correctness outrank model-cost minimization.
- No blind paid retry is allowed; free evidence/logs should diagnose a failed paid run before any retry/escalation.
- All other work proceeds according to `ADAPTIVE_FUNNEL_IMPLEMENTATION_PLAN.md`, `DEVELOPMENT_FINOPS_POLICY.md` and `PROFIT_ENGINE_AUTHORITY.md`.

## EFFECT

This decision narrows Codex to one role: SOFTWARE DEVELOPMENT EXECUTOR.

It does not change the commercial plan, catalog scale gates, genre strategy, Adaptive Funnel sequence, K5 target, Feature Profit Gate, Budget Governor or production AI doctrine.
