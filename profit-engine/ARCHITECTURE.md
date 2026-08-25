# PROFIT ENGINE — ARCHITECTURE

Status: CANONICAL v0.1
Updated: 2026-08-25

## 1. System boundary

Profit Engine is a multi-site control plane for advertising yield and traffic economics.

The core must never hard-code Dilivox-specific IDs or assumptions. Every fact is scoped by `site_id` and, where relevant, `provider_account_id` / `counter_id` / `campaign_id` / `yan_resource_id`.

## 2. Core loop

`Collect -> Normalize -> Attribute -> Reconcile -> Estimate LTV -> Score -> Decide -> Guard -> Apply -> Observe`

### Collectors

- Direct Connector: campaigns, ads, groups, targeting, spend, clicks, status, strategy/budget state.
- Metrica Connector: sources, UTM/campaign dimensions, behavior, first-party goals/events, YAN monetization metrics.
- YAN Connector: partner-side statistics for independent revenue/inventory reconciliation.
- Site Event Connector: first-party content/product events from each site.

### Normalization

All provider data lands in provider-neutral tables with immutable raw snapshots retained separately.

Important dimensions:

- `site_id`
- event/date/hour
- source/campaign/ad/group
- landing/content item
- device/browser/region
- experiment/variant
- YAN placement/unit identity where available

### Attribution

Primary control metric: YAN revenue attributable to acquired audience cohorts.

Required windows:

- 1 day
- 7 days
- 30 days

The engine must preserve the distinction between directly observed revenue, estimated revenue, and forecast revenue.

### Revenue reconciliation

Metrica monetization data and YAN Partner Statistics are separate sources and must be reconciled before aggressive scale decisions.

If reconciliation error exceeds configured tolerance, system state becomes `DATA_QUALITY_HOLD`; budget growth is disabled until recovered.

## 3. Decision engine

Each traffic/content combination receives one of:

- `LEARN`
- `TEST`
- `SCALE`
- `HOLD`
- `REDUCE`
- `STOP`
- `QUARANTINE`
- `PENDING_OWNER_APPROVAL`

Decisions must include:

- evidence window;
- sample size;
- observed ROAS;
- predicted ROAS;
- uncertainty/confidence;
- expected incremental spend;
- expected incremental YAN revenue;
- reason code.

## 4. Budget Governor

The Budget Governor sits between optimizer and Direct API. Optimizer recommendations have no authority to bypass it.

Hard rule:

`requested_weekly_budget <= current_weekly_budget * 1.20` may be automatically applied when all other guards pass.

Anything above that threshold becomes `PENDING_OWNER_APPROVAL`.

Other default guards:

- global account/site weekly cap;
- experiment spend cap;
- minimum sample size;
- minimum data freshness;
- maximum reconciliation error;
- maximum step-down/up rate;
- emergency stop;
- no action if provider status is inconsistent or API response uncertain.

## 5. Multi-site model

Shared core:

- collectors framework;
- normalized schema;
- attribution engine;
- optimizer;
- budget governor;
- experiment framework;
- anomaly detection;
- dashboard;
- audit log.

Per-site adapter/config:

- site ID/domain;
- Metrica counters;
- YAN resources/placements;
- Direct accounts/campaign scopes;
- event taxonomy;
- content-item taxonomy;
- allowed optimization actions;
- budget caps;
- target ROAS;
- site-specific recirculation/recommendation strategy.

Credentials and raw data are isolated by site/account scope.

## 6. Dilivox first-party event model v0.1

At minimum:

- `story_open`
- `story_progress_25`
- `story_progress_50`
- `story_progress_75`
- `version_section_seen`
- `version_selected`
- `reveal_opened`
- `story_completed`
- `next_story_seen`
- `next_story_clicked`
- `catalog_opened`
- `return_visit`

Do not collect unnecessary personal data. Event payloads should use pseudonymous/session identifiers and content IDs where possible.

## 7. Optimization surfaces

Traffic side:

- campaign/ad/group/creative;
- audience/targeting;
- region;
- device;
- schedule;
- landing story/page;
- allowed Direct strategy and budget parameters.

Site side:

- content sequencing;
- next-story recommendations;
- internal recirculation;
- landing choice;
- site-owned UI experiments;
- permitted YAN placement experiments configured through supported mechanisms.

The engine does not optimize toward ad-click CTR. It optimizes toward real user value/engagement and realized YAN revenue per acquired cohort.

## 8. Experiment model

Use controlled experiments with holdouts where possible. For dynamic allocation, introduce multi-armed bandit/Bayesian methods only after the measurement layer is proven.

No winner can become `SCALE` solely because of one-day variance or tiny sample sizes.

## 9. Auditability

Every automatic write to Direct must create an immutable decision record:

- before state;
- requested change;
- after state/response;
- model/rule version;
- evidence IDs;
- actor = automation/owner;
- approval ID if required;
- timestamp.

Owner must be able to reconstruct why money moved.
