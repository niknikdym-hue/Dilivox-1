# PROFIT ENGINE — OWNER DECISIONS

Status: CANONICAL / ACTIVE
Updated: 2026-08-25

## OD-001 — Economic target

Initial Dilivox optimization target is:

`1 RUB traffic acquisition spend -> 5 RUB YAN/RСЯ advertising revenue`

Equivalent target: `YAN ROAS = 5.0` / `DRR = 20%`.

This target remains active until explicitly superseded by the owner.

## OD-002 — Revenue scope

For this engine, the target revenue stream is revenue from standard YAN/RСЯ advertising blocks placed on connected sites. Other monetization streams are outside this engine's target metric unless separately added later.

## OD-003 — Legal/white-hat operation

The project is a normal lawful optimization and analytics system for high-quality sites and real users. No bots, click stimulation, motivated ad interactions, artificial impressions, or manipulation of ad systems are part of the design.

## OD-004 — Independence

Profit Engine is an independent owner-controlled system. Yandex services are external infrastructure/data/control providers. Yandex does not define the engine's architecture, optimization policy, ownership, or business logic.

## OD-005 — Automation priority

Maximum practical automation is required, including automated data collection, attribution, analysis, forecasting, anomaly detection, experiment evaluation, Direct campaign control, budget redistribution, and recommendations.

## OD-006 — Budget authority

Automatic weekly budget increase is permitted only up to +20% against the applicable current weekly budget baseline.

Any increase above +20% MUST:

1. be proposed by the engine;
2. show supporting evidence, expected impact, and risk;
3. receive explicit owner approval;
4. remain blocked until that approval is recorded.

This is a hard invariant and cannot be bypassed by any optimizer or administrator automation.

## OD-007 — Multi-site platform

The engine must support multiple owner sites from the beginning. Dilivox is the first connected site only.

New sites must be onboarded via site configuration/adapters and isolated credentials/data partitions, without forking or rewriting the optimization core.

## OD-008 — Cloud direction

Preferred production environment is Yandex Cloud for operational simplicity, locality of the surrounding ecosystem, managed database/secrets/observability, and straightforward integration. Business logic remains portable and provider-neutral where practical.

## OD-009 — Chat is not source of truth

Repository authority files are the source of truth for project decisions and state. Material decisions must be committed. Replaced decisions are marked `SUPERSEDED`, not silently deleted.
