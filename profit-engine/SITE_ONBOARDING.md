# PROFIT ENGINE — SITE ONBOARDING CONTRACT

Status: CANONICAL v0.1
Updated: 2026-08-25

## Goal

Connect additional owner sites without changing the shared optimization core.

Each connected site receives a stable `site_id` and a site adapter/config package.

## Required site registration

For every new site define:

- `site_id`
- canonical domain(s)
- site owner/operator scope
- Metrica counter ID(s)
- YAN resource/site/placement IDs as applicable
- Direct account/client/campaign scopes
- traffic attribution parameters
- first-party event taxonomy
- content/page/item taxonomy
- target YAN ROAS
- budget caps and approval policy
- allowed automated Direct actions
- site-specific recommendation/recirculation capabilities
- data retention/privacy settings
- rollout state (`SHADOW`, `GUARDED_AUTOPILOT`, `AUTOPILOT`, `PAUSED`)

## Isolation

Every fact, decision, approval, experiment, and action must include `site_id`.

Credentials must be isolated by provider account/site scope. The system must not assume that multiple sites share the same Metrica, Direct, YAN, or Cloud credentials.

## Onboarding stages

### S0 — Register

Create site metadata and access mapping. No writes to Direct.

### S1 — Observe

Collect Metrica/YAN/Direct data read-only. Establish baseline and freshness.

### S2 — Instrument

Deploy first-party events and verify attribution.

### S3 — Reconcile

Validate revenue/spend reconciliation and produce stable 1d/7d/30d cohort metrics.

### S4 — Shadow decisions

Optimizer produces decisions but applies nothing. Compare recommendations with realized outcomes.

### S5 — Guarded autopilot

Enable bounded automatic Direct actions under Budget Governor and site-level caps.

### S6 — Full approved autopilot

Expand action scope only after quality gates pass. Owner approval remains mandatory for any weekly budget increase above +20%.

## Site adapter interface

A site adapter should expose at least:

- content/page identity resolver;
- event schema/version;
- landing-page inventory;
- recommendation candidates;
- experiment surfaces;
- health check;
- deployment/version metadata.

The optimizer consumes these through generic interfaces, not site-specific branching in the core.

## New-site acceptance gate

No new site may enter write-capable autopilot until:

- spend data is fresh;
- YAN revenue data is connected;
- attribution keys are validated;
- raw data archive is working;
- reconciliation is within tolerance;
- owner budget cap is recorded;
- emergency pause is tested;
- owner approval workflow is tested.
