# PROFIT ENGINE — IMPLEMENTATION PLAN

Status: CANONICAL v0.1
Updated: 2026-08-25

## Operating rule

Always work from current `main` and the first incomplete milestone below. Do not restart architectural discussion unless an authority decision changes.

## M0 — Access and measurement inventory

Outcome: we know exactly what already exists and can collect all required data read-only.

Tasks:

1. Audit production Dilivox for Metrica counters and current event/tag setup.
2. Inventory Dilivox YAN/RСЯ resources and ad units.
3. Inventory Direct account/campaigns used or intended for Dilivox.
4. Define dedicated technical Yandex identity and delegated permissions where supported.
5. Register OAuth application(s) and API scopes/access.
6. Connect YAN monetization reports to the correct Metrica counter if not already connected.
7. Record current weekly budgets and site/account owner caps.
8. Produce an access matrix and credential-name map (no secret values in GitHub).

Gate M0: all three providers can be queried read-only and identifiers are mapped to `site_id=dilivox`.

## M1 — Cloud foundation

Outcome: secure, reproducible production foundation in Yandex Cloud.

Tasks:

1. Create Cloud folder/project for Profit Engine.
2. Create service accounts with least privilege.
3. Provision Lockbox secrets.
4. Provision Managed PostgreSQL.
5. Provision private Object Storage bucket for raw provider snapshots.
6. Configure Serverless Containers and scheduled triggers.
7. Configure logging, monitoring, and cost alarms.
8. Add infrastructure-as-code before production expansion (Terraform preferred).

Gate M1: a hello/health service can read its allowed secret and DB, write a raw test object, and emit monitored logs without broad admin rights.

## M2 — Data ingestion and canonical schema

Outcome: automated hourly/daily ingestion of Direct, Metrica, YAN, and first-party events.

Tasks:

1. Implement Direct read connector.
2. Implement Metrica report connector, including YAN monetization dimensions/metrics.
3. Implement YAN Partner Statistics connector.
4. Implement immutable raw snapshot archive.
5. Implement normalized PostgreSQL fact/dimension schema.
6. Add ingestion idempotency, freshness checks, retries, and provider error handling.
7. Add per-site credential/config resolver.

Gate M2: all daily data can be reproduced from archived raw snapshots and every row is scoped by `site_id`.

## M3 — Dilivox instrumentation

Outcome: Profit Engine understands what acquired readers actually do on Dilivox.

Tasks:

1. Implement approved first-party event taxonomy.
2. Add stable story/content IDs.
3. Preserve Direct/UTM attribution identifiers through landing and event flow.
4. Validate mobile and desktop event delivery.
5. Add content recirculation measurements.
6. Build baseline dashboard by story/source/device/campaign.

Gate M3: event counts are internally consistent and can be joined to acquisition cohorts without collecting unnecessary personal data.

## M4 — Revenue attribution and reconciliation

Outcome: every traffic cohort has trustworthy observed revenue and an explicit uncertainty state.

Tasks:

1. Build Metrica YAN revenue attribution by source/campaign/content/device.
2. Reconcile against YAN Partner Statistics.
3. Implement `YAN_ROAS_1D`, `YAN_ROAS_7D`, `YAN_ROAS_30D`.
4. Implement revenue/user, revenue/visit, CPMV, request/render/show diagnostics.
5. Add `DATA_QUALITY_HOLD` on stale or divergent data.
6. Create owner dashboard showing observed vs forecast economics.

Gate M4: historical cohorts can be recomputed and Direct spend vs YAN revenue is reliable enough for controlled decisions.

## M5 — Shadow optimizer

Outcome: engine makes recommendations but does not change money automatically.

Tasks:

1. Implement scoring for campaign/ad/group/landing/device/region/time segments.
2. Add sample-size and statistical-confidence requirements.
3. Add anomaly detection.
4. Implement decision states LEARN/TEST/SCALE/HOLD/REDUCE/STOP/QUARANTINE.
5. Replay historical data and compare recommendations to later realized outcomes.
6. Calibrate forecast model for 7d/30d YAN LTV.

Gate M5: shadow decisions show stable economic improvement in replay/forward observation without hidden leakage.

## M6 — Guarded Direct autopilot

Outcome: bounded, auditable automatic campaign control.

Tasks:

1. Implement write-enabled Direct Controller.
2. Put Budget Governor between optimizer and provider API.
3. Implement owner approval object/workflow.
4. Enforce hard rule: any weekly budget increase above +20% is blocked pending explicit owner approval.
5. Add site/account/campaign caps and emergency stops.
6. Add before/after action audit log and rollback/recovery procedure.
7. Begin with narrow campaign scope and small controlled budgets.

Gate M6: controller cannot exceed policy in tests, including adversarial/erroneous optimizer recommendations.

## M7 — Yield and recirculation optimization

Outcome: maximize YAN revenue per acquired real reader without degrading content/product quality.

Tasks:

1. Optimize landing-story selection.
2. Build next-story recommendation engine.
3. Run controlled site-owned UX/content-sequencing experiments.
4. Evaluate supported YAN ad-layout experiments through official mechanisms.
5. Optimize for cohort YAN revenue and engagement, not ad-click CTR.
6. Introduce Bayesian/bandit allocation after measurement validity is proven.

Gate M7: improvements survive holdout testing and do not reduce long-term reader value.

## M8 — Multi-site onboarding

Outcome: second owner site can be connected without changing the shared core.

Tasks:

1. Select next site.
2. Create `sites/<site_id>/SITE_STATE.md`.
3. Configure isolated credentials, counters, YAN resources, Direct scopes, event mapping, caps, and target.
4. Run S0-S6 onboarding contract in `SITE_ONBOARDING.md`.
5. Verify cross-site data and approval isolation.

Gate M8: second site reaches guarded autopilot using the same engine core.

## Owner vs Central Brain vs Codex

Owner:

- approves decisions that require owner authority;
- approves any weekly budget increase above +20%;
- grants account/service permissions when required.

Central Brain / project lead:

- maintains canonical state and architecture;
- determines next milestone/task from actual repository and provider state;
- validates implementation and economics;
- prepares exact Codex tasks.

Codex / engineering executor:

- implements code/infrastructure/tests;
- performs repository changes under task contract;
- reports exact commits, tests, deployment evidence, and blockers;
- does not override owner budget authority or architectural invariants.

## Launch definition

Profit Engine is not considered production-autonomous merely because connectors work.

Initial production-autopilot launch requires M0-M6 gates complete. M7 continuously improves economics toward the 5.0 target. M8 proves the architecture is genuinely multi-site.
