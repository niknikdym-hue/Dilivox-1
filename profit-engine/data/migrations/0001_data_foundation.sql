BEGIN;

CREATE SCHEMA IF NOT EXISTS profit_engine;

CREATE TABLE profit_engine.sites (
    site_id text PRIMARY KEY,
    display_name text NOT NULL,
    active boolean NOT NULL DEFAULT true,
    created_at timestamptz NOT NULL
);

CREATE TABLE profit_engine.provider_accounts (
    provider_account_ref uuid PRIMARY KEY,
    site_id text NOT NULL REFERENCES profit_engine.sites(site_id),
    provider text NOT NULL,
    private_mapping_ref text NOT NULL,
    active boolean NOT NULL DEFAULT true,
    created_at timestamptz NOT NULL,
    UNIQUE (site_id, provider, private_mapping_ref)
);

CREATE TABLE profit_engine.ingestion_runs (
    ingestion_run_id uuid PRIMARY KEY,
    site_id text NOT NULL REFERENCES profit_engine.sites(site_id),
    provider text NOT NULL,
    source_object_type text NOT NULL,
    idempotency_key text NOT NULL,
    status text NOT NULL CHECK (status IN ('started', 'complete', 'failed', 'held')),
    started_at timestamptz NOT NULL,
    completed_at timestamptz,
    error_code text,
    UNIQUE (site_id, provider, source_object_type, idempotency_key)
);

CREATE TABLE profit_engine.raw_snapshots (
    raw_snapshot_id uuid PRIMARY KEY,
    ingestion_run_id uuid NOT NULL REFERENCES profit_engine.ingestion_runs(ingestion_run_id),
    site_id text NOT NULL REFERENCES profit_engine.sites(site_id),
    provider text NOT NULL,
    source_object_type text NOT NULL,
    captured_at timestamptz NOT NULL,
    source_window_start timestamptz,
    source_window_end timestamptz,
    request_fingerprint char(64) NOT NULL,
    payload_sha256 char(64) NOT NULL,
    provider_request_id text,
    data_state text NOT NULL CHECK (data_state IN ('estimated', 'final', 'reconciled')),
    storage_key text NOT NULL,
    UNIQUE (site_id, provider, source_object_type, request_fingerprint),
    UNIQUE (storage_key)
);

CREATE TABLE profit_engine.campaign_snapshots (
    campaign_snapshot_id uuid PRIMARY KEY,
    site_id text NOT NULL REFERENCES profit_engine.sites(site_id),
    raw_snapshot_id uuid NOT NULL REFERENCES profit_engine.raw_snapshots(raw_snapshot_id),
    provider text NOT NULL,
    provider_entity_ref text NOT NULL,
    observed_at timestamptz NOT NULL,
    state jsonb NOT NULL,
    UNIQUE (site_id, provider, provider_entity_ref, observed_at)
);

CREATE TABLE profit_engine.traffic_facts (
    traffic_fact_id uuid PRIMARY KEY,
    site_id text NOT NULL REFERENCES profit_engine.sites(site_id),
    raw_snapshot_id uuid NOT NULL REFERENCES profit_engine.raw_snapshots(raw_snapshot_id),
    provider text NOT NULL,
    occurred_on date NOT NULL,
    dimensions jsonb NOT NULL,
    impressions bigint,
    clicks bigint,
    visits bigint,
    spend_amount numeric(20,6),
    currency_code char(3),
    idempotency_key text NOT NULL,
    UNIQUE (site_id, provider, idempotency_key)
);

CREATE TABLE profit_engine.site_events (
    event_id uuid PRIMARY KEY,
    site_id text NOT NULL REFERENCES profit_engine.sites(site_id),
    occurred_at timestamptz NOT NULL,
    event_type text NOT NULL,
    stable_content_id text,
    attribution jsonb NOT NULL DEFAULT '{}'::jsonb,
    properties jsonb NOT NULL DEFAULT '{}'::jsonb,
    idempotency_key text NOT NULL,
    UNIQUE (site_id, idempotency_key)
);

CREATE TABLE profit_engine.monetization_facts (
    monetization_fact_id uuid PRIMARY KEY,
    site_id text NOT NULL REFERENCES profit_engine.sites(site_id),
    raw_snapshot_id uuid REFERENCES profit_engine.raw_snapshots(raw_snapshot_id),
    provider text NOT NULL,
    occurred_on date NOT NULL,
    dimensions jsonb NOT NULL,
    revenue_amount numeric(20,6) NOT NULL,
    currency_code char(3) NOT NULL,
    data_state text NOT NULL CHECK (data_state IN ('estimated', 'final', 'reconciled')),
    idempotency_key text NOT NULL,
    UNIQUE (site_id, provider, idempotency_key)
);

CREATE TABLE profit_engine.cohorts (
    cohort_id uuid PRIMARY KEY,
    site_id text NOT NULL REFERENCES profit_engine.sites(site_id),
    cohort_key text NOT NULL,
    definition jsonb NOT NULL,
    created_at timestamptz NOT NULL,
    UNIQUE (site_id, cohort_key)
);

CREATE TABLE profit_engine.experiments (
    experiment_id uuid PRIMARY KEY,
    site_id text NOT NULL REFERENCES profit_engine.sites(site_id),
    experiment_key text NOT NULL,
    status text NOT NULL,
    definition jsonb NOT NULL,
    starts_at timestamptz,
    ends_at timestamptz,
    UNIQUE (site_id, experiment_key)
);

CREATE TABLE profit_engine.decisions (
    decision_id uuid PRIMARY KEY,
    site_id text NOT NULL REFERENCES profit_engine.sites(site_id),
    decision_type text NOT NULL,
    input_provenance jsonb NOT NULL,
    proposed_at timestamptz NOT NULL,
    status text NOT NULL CHECK (status IN ('proposed', 'held', 'approved', 'rejected', 'expired')),
    idempotency_key text NOT NULL,
    UNIQUE (site_id, idempotency_key)
);

CREATE TABLE profit_engine.approvals (
    approval_id uuid PRIMARY KEY,
    site_id text NOT NULL REFERENCES profit_engine.sites(site_id),
    decision_id uuid NOT NULL REFERENCES profit_engine.decisions(decision_id),
    authority_ref text NOT NULL,
    outcome text NOT NULL CHECK (outcome IN ('approved', 'rejected')),
    recorded_at timestamptz NOT NULL,
    UNIQUE (site_id, decision_id, authority_ref)
);

CREATE TABLE profit_engine.actions_audit (
    audit_event_id uuid PRIMARY KEY,
    site_id text NOT NULL REFERENCES profit_engine.sites(site_id),
    occurred_at timestamptz NOT NULL,
    actor_type text NOT NULL,
    action_type text NOT NULL,
    target_ref text,
    outcome text NOT NULL,
    correlation_id text NOT NULL,
    redacted_detail jsonb NOT NULL DEFAULT '{}'::jsonb,
    UNIQUE (site_id, correlation_id, action_type)
);

CREATE TABLE profit_engine.data_quality_checks (
    data_quality_check_id uuid PRIMARY KEY,
    site_id text NOT NULL REFERENCES profit_engine.sites(site_id),
    raw_snapshot_id uuid REFERENCES profit_engine.raw_snapshots(raw_snapshot_id),
    checked_at timestamptz NOT NULL,
    check_type text NOT NULL,
    status text NOT NULL CHECK (status IN ('pass', 'warn', 'fail', 'hold')),
    hold_code text,
    redacted_detail jsonb NOT NULL DEFAULT '{}'::jsonb,
    CHECK (status <> 'hold' OR hold_code = 'DATA_QUALITY_HOLD')
);

COMMIT;
