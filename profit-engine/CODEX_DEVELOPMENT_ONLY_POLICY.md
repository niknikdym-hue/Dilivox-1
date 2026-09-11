# DILIVOX PROFIT ENGINE — CODEX DEVELOPMENT-ONLY POLICY

Status: OWNER-APPROVED / CANONICAL COMPANION DECISION
Date: 2026-09-11
Repository: `niknikdym-hue/Dilivox-1`
Branch: `profit-engine`
Parent authority: `profit-engine/PROFIT_ENGINE_AUTHORITY.md`
Implementation plan: `profit-engine/ADAPTIVE_FUNNEL_IMPLEMENTATION_PLAN.md`

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
- All other work proceeds according to `ADAPTIVE_FUNNEL_IMPLEMENTATION_PLAN.md` and `PROFIT_ENGINE_AUTHORITY.md`.

## EFFECT

This decision narrows Codex to one role: SOFTWARE DEVELOPMENT EXECUTOR.

It does not change the commercial plan, catalog scale gates, genre strategy, Adaptive Funnel sequence, K5 target, Feature Profit Gate, Budget Governor or production AI doctrine.
