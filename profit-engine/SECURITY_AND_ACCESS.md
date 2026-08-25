# PROFIT ENGINE — SECURITY AND ACCESS

Status: CANONICAL v0.1
Updated: 2026-08-25

## Principles

1. Never share or automate with the owner's primary Yandex password.
2. Prefer a dedicated technical Yandex ID for API operations where service delegation permits it.
3. Use OAuth tokens/scoped delegated access, not passwords.
4. Store production secrets only in Lockbox or equivalent secret manager.
5. Use least privilege and separate read/write capabilities.
6. Keep site/account isolation so compromise of one connected site does not automatically expose all sites.
7. Every money-changing Direct API action must be audited.

## Access model

### Direct

- dedicated technical identity / representative where supported;
- OAuth application with Direct API access;
- separate write-enabled controller credential from read-only analytics where practical;
- controller may modify only explicitly registered accounts/campaign scopes.

### Metrica

- dedicated technical identity receives the minimum access required to read counter analytics and YAN monetization reports;
- counters are registered per `site_id`;
- no unrelated owner counters are pulled into the engine by default.

### YAN / Partner Statistics

- use OAuth/token access required by the Partner Statistics API;
- restrict usage to statistics collection;
- do not place credentials in source code, CI variables stored in plain text, documentation, or issue comments.

### Yandex Cloud

Use service accounts for runtime components. Separate roles for:

- secret reading;
- database access;
- Object Storage write/read;
- logging/monitoring;
- deployment administration.

Production application services should not have broad cloud-admin permissions.

## Approval security

An owner approval for a weekly budget increase above +20% must be represented as an auditable object containing:

- site/account/campaign scope;
- previous weekly budget;
- requested weekly budget;
- percentage change;
- expiration time for approval;
- owner actor identity;
- approval timestamp;
- decision/evidence reference.

Approval must be single-purpose and cannot be reused for a later unrelated increase.

## Emergency controls

Required:

- global `AUTOPILOT_OFF` switch;
- per-site pause;
- per-account pause;
- per-campaign pause;
- global maximum spend cap;
- API write circuit breaker after repeated provider errors;
- automatic `DATA_QUALITY_HOLD` on stale/unreconciled revenue data.

## Public repository warning

This repository is currently public. Therefore:

- no credentials;
- no secret values;
- no private account identifiers unless intentionally public;
- no raw production exports that may contain user/account data;
- no operational tokens in commits, PRs, issues, Actions logs, or screenshots.

Before production code contains competitively sensitive algorithms or operational configuration, evaluate moving shared multi-site engine implementation to a dedicated private repository while keeping site adapters/interfaces synchronized.
