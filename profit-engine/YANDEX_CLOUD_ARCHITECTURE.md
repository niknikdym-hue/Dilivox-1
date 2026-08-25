# PROFIT ENGINE — YANDEX CLOUD ARCHITECTURE

Status: RECOMMENDED v0.1
Updated: 2026-08-25

## Recommendation

Run the first production version in Yandex Cloud, while keeping the application code portable.

Do NOT start with Kubernetes. The initial workload is API/data orchestration, scheduled analytics, lightweight online control, and dashboards; managed/serverless components are sufficient.

## Core production components

### Runtime

Preferred initial runtime: Yandex Serverless Containers.

Services:

- `collector-direct`
- `collector-metrica`
- `collector-yan`
- `event-api`
- `reconciliation-worker`
- `ltv-worker`
- `optimizer-worker`
- `direct-controller`
- `owner-api`

Use scheduled triggers/jobs for hourly/daily collection and optimization cycles.

### Database

Yandex Managed Service for PostgreSQL.

Primary tables/schemas:

- `sites`
- `provider_accounts`
- `campaign_snapshots`
- `traffic_facts`
- `site_events`
- `yan_facts`
- `metrica_yan_facts`
- `cohorts`
- `ltv_estimates`
- `experiments`
- `decisions`
- `approvals`
- `actions_audit`
- `data_quality_checks`

Partition or otherwise isolate high-volume fact tables by date/site as data grows.

### Raw archive

Yandex Object Storage.

Store immutable raw API responses/snapshots by provider/site/date so calculations are reproducible and provider corrections can be reprocessed.

Suggested layout:

`raw/{site_id}/{provider}/{yyyy}/{mm}/{dd}/...`

### Secrets

Yandex Lockbox.

Examples of secret names only (values never committed):

- `profit-engine/direct/oauth/<account>`
- `profit-engine/metrica/oauth/<account>`
- `profit-engine/yan/oauth/<account>`
- `profit-engine/postgres/app`
- `profit-engine/webhook/signing`

Use service accounts and least-privilege IAM to read only the secrets required by each runtime component.

### Observability

Use Yandex Monitoring/Logging for:

- collector failures;
- API rate/error spikes;
- stale data;
- reconciliation drift;
- optimizer failures;
- Direct write failures;
- unauthorized/blocked budget changes;
- cost and resource alarms.

### Dashboard / BI

Use DataLens for analytical dashboards over curated PostgreSQL views.

Owner operational dashboard may later be a custom app; DataLens is sufficient for early validation and deep slice-and-dice analysis.

## Why Yandex Cloud

- managed PostgreSQL reduces operational burden;
- Lockbox provides centralized encrypted secret storage;
- Object Storage is suitable for cheap immutable raw archives;
- Serverless Containers support simple independent services without a cluster;
- Monitoring/Logging provide operational visibility;
- DataLens fits Russian-language analytics workflows and can sit close to the data.

## Portability rule

Do not encode Yandex Cloud SDK types into the business domain.

Use internal interfaces for:

- secret store;
- object store;
- relational store;
- scheduler;
- metrics/logging.

This keeps future migration possible if cost, regulation, scale, or availability requires it.

## Scale path

Stage 1: Serverless Containers + Managed PostgreSQL + Object Storage + Lockbox.

Stage 2: add queue/event infrastructure and dedicated workers if ingestion volume grows.

Stage 3: move hot/long-running workloads to Compute/managed orchestration only when measured load requires it.

Kubernetes is explicitly deferred until there is a demonstrated need.
