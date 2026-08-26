# PROFIT ENGINE — YANDEX DIRECT API CERTIFICATION SPECIFICATION

Status: APPLICATION SPEC v0.1
Updated: 2026-08-26

## 1. Purpose

Profit Engine is an internal multi-site analytics and advertising-optimization platform for the owner's own websites. Dilivox (`dilivox.ru`) is the first connected site.

The platform combines Yandex Direct campaign/spend data, Yandex Metrica behavioral/attribution data, YAN/RСЯ monetization data, and first-party site events in order to calculate traffic economics and support controlled advertising optimization.

The initial economic target for Dilivox is to optimize toward `YAN ROAS = 5.0` (5 RUB of YAN revenue per 1 RUB of acquisition spend). This is a target, not a claimed current result.

## 2. Direct API use cases

Initial read-only stage:

1. Read campaign/account structure and current campaign settings.
2. Read campaigns, ad groups, ads, statuses and strategies needed for analytics.
3. Obtain statistics and reports for impressions, clicks, spend and other supported advertising dimensions/metrics.
4. Synchronize Direct data with the internal Profit Engine database.
5. Associate Direct spend and traffic with Metrica/YAN revenue analytics.

Later guarded-control stage:

1. Update permitted campaign parameters and weekly budgets.
2. Pause/resume campaigns when Profit Engine risk/quality rules require it.
3. Apply bounded optimization decisions after statistical validation.
4. Record every write action in an immutable audit trail.

## 3. User and account model

The application is an internal tool, not a public SaaS product at the current stage.

Initial Direct account:

- owner advertising account: `DymovaEI`;
- technical integration identity: Yandex Managing Account used by Profit Engine;
- current technical-account access during implementation: Reading.

The technical account will be upgraded to Editing only when guarded write automation is ready and tested.

Future owner websites/accounts may be connected through the same core using isolated `site_id` configurations and credential scopes.

## 4. Planned technology

- Primary language: Python 3.12.
- Direct API protocol: HTTPS + JSON, Direct API v5.
- Authentication: OAuth 2.0 via the registered Yandex OAuth application `Profit Engine`.
- Runtime: Yandex Cloud (initially Serverless Containers / managed services).
- Primary database: Managed PostgreSQL.
- Raw API snapshot archive: Object Storage.
- Secret storage: Yandex Lockbox.
- Monitoring/logging: Yandex Cloud Monitoring and Logging.

The application does not store or use interactive Yandex passwords.

## 5. Direct interaction scheme

### Read flow

1. Scheduled Profit Engine collector starts.
2. Collector reads OAuth token from secure secret storage.
3. Collector sends HTTPS/JSON requests to Yandex Direct API.
4. The application queries required Direct resources/services such as Campaigns, AdGroups, Ads and Reports.
5. Raw responses are archived immutably.
6. Normalized data is written to PostgreSQL.
7. Direct data is joined with Metrica, YAN and first-party site data inside Profit Engine.
8. Profit Engine calculates campaign/segment economics, including YAN-attributed ROAS/LTV and data-quality indicators.

### Write flow (later stage only)

1. Optimizer creates a proposed action.
2. Data-quality and statistical-confidence gates validate the proposal.
3. Budget Governor checks all owner policy limits.
4. If the proposed weekly budget increase is greater than 20%, the action is blocked as `PENDING_OWNER_APPROVAL`.
5. Only an explicitly approved or policy-permitted action reaches the Direct Controller.
6. Direct Controller sends the allowed API request.
7. Before/after state, API response, evidence and actor/approval identity are written to audit log.

## 6. Budget and safety controls

Hard owner policy:

- automatic weekly budget increase up to and including +20% may be applied only when all other guards pass;
- any weekly budget increase above +20% requires explicit owner approval;
- no optimizer/model can bypass this rule.

Additional controls:

- global/site/account/campaign spend caps;
- minimum sample and confidence requirements;
- stale-data and reconciliation holds;
- anomaly detection;
- emergency autopilot-off switch;
- repeated API-error circuit breaker;
- idempotent write handling;
- full audit log for money-changing actions.

## 7. Data sources outside Direct

Yandex Metrica API:

- traffic acquisition and attribution dimensions;
- user/session/content behavior;
- YAN monetization metrics available through the connected Metrica counter.

YAN/RСЯ Partner Statistics API:

- independent ad inventory/revenue statistics for reconciliation.

First-party site events:

- content opens/completion;
- recirculation / next-content transitions;
- return usage;
- experiment variant IDs.

Profit Engine does not optimize toward clicks on YAN advertising. It optimizes real traffic/product economics and realized advertising revenue.

## 8. New capabilities provided by the application

Compared with manual Direct work, Profit Engine provides:

1. automatic consolidation of Direct spend and traffic data with Metrica and YAN revenue data;
2. YAN-attributed ROAS and cohort-LTV calculation for campaigns/ads/content/device/region and other segments;
3. automated detection of profitable and unprofitable traffic combinations;
4. forecasting and shadow recommendations before automated changes are enabled;
5. bounded campaign-control automation with explicit owner budget authority;
6. multi-site operation using one shared analytics/optimization core;
7. reproducible raw data snapshots and an auditable history of every automated decision/action.

## 9. Development stage

Current stage: API access and measurement foundation.

Already configured:

- Yandex OAuth application `Profit Engine`;
- Direct API OAuth scope;
- Metrica read scope;
- technical account read access to the owner Direct account;
- delegated Dilivox access in Metrica and YAN.

The first implementation milestone after API approval is a real read-only Direct collector. Write-capable Direct automation is intentionally deferred until Budget Governor and approval/security gates are implemented and tested.

## 10. Privacy and credential handling

- No passwords are stored in application code.
- OAuth/production secrets are stored in Yandex Lockbox.
- Public GitHub documentation contains no production secret values.
- Data is scoped by site/account and collected only as needed for analytics and optimization.
- Unnecessary personal data is not part of the optimization model.
