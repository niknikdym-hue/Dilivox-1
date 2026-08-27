BEGIN;
CREATE TABLE profit_engine.acquisitions (
  acquisition_id uuid PRIMARY KEY, site_id text NOT NULL REFERENCES profit_engine.sites(site_id), cohort_ref text NOT NULL,
  acquired_at timestamptz NOT NULL, landing_content_id text, provider text, expires_at timestamptz NOT NULL,
  registration_sha256 char(64) NOT NULL, schema_version text NOT NULL, deployment_version text NOT NULL,
  provenance jsonb NOT NULL, UNIQUE(site_id, cohort_ref), UNIQUE(site_id, registration_sha256)
);
CREATE TABLE profit_engine.acquisition_attribution_evidence (
  evidence_id uuid PRIMARY KEY, site_id text NOT NULL REFERENCES profit_engine.sites(site_id), acquisition_id uuid NOT NULL REFERENCES profit_engine.acquisitions(acquisition_id),
  evidence_type text NOT NULL, provider_entity_ref text, attribution_grade text NOT NULL,
  source_fact_ref text NOT NULL, observed_at timestamptz NOT NULL, provenance jsonb NOT NULL,
  UNIQUE(site_id, acquisition_id, evidence_type, source_fact_ref)
);
CREATE TABLE profit_engine.reconciliation_runs (
  reconciliation_run_id uuid PRIMARY KEY, site_id text NOT NULL REFERENCES profit_engine.sites(site_id),
  window_start timestamptz NOT NULL, window_end timestamptz NOT NULL, timezone_basis text NOT NULL,
  currency_code char(3), money_basis text, status text NOT NULL,
  tolerance_amount numeric(20,6) NOT NULL, tolerance_version text NOT NULL,
  metrica_source_ref text, yan_source_ref text, metrica_amount numeric(20,6), yan_control_amount numeric(20,6),
  absolute_delta numeric(20,6), relative_delta numeric(20,12), provenance jsonb NOT NULL,
  idempotency_key text NOT NULL, version integer NOT NULL, UNIQUE(site_id,idempotency_key,version)
);
CREATE TABLE profit_engine.money_ledger_facts (
  money_fact_id uuid PRIMARY KEY, site_id text NOT NULL REFERENCES profit_engine.sites(site_id),
  fact_kind text NOT NULL, cohort_ref text, window_start timestamptz NOT NULL, window_end timestamptz NOT NULL,
  amount numeric(20,6), currency_code char(3), money_basis text, attribution_grade text NOT NULL,
  source_state text NOT NULL, source_fact_refs jsonb NOT NULL, provenance jsonb NOT NULL,
  idempotency_key text NOT NULL, version integer NOT NULL, UNIQUE(site_id,idempotency_key,version)
);
CREATE TABLE profit_engine.k5_measurements (
  measurement_id uuid PRIMARY KEY, site_id text NOT NULL REFERENCES profit_engine.sites(site_id),
  measurement_kind text NOT NULL, cohort_ref text, window_start timestamptz NOT NULL, window_end timestamptz NOT NULL,
  numerator_amount numeric(20,6), denominator_amount numeric(20,6), value numeric(20,12), currency_code char(3),
  attribution_grade text NOT NULL, source_state text NOT NULL, reconciliation_state text NOT NULL,
  calculation_version text NOT NULL, derived_version integer NOT NULL, source_refs jsonb NOT NULL,
  hold_reasons jsonb NOT NULL, optimizer_consumable boolean NOT NULL DEFAULT false,
  idempotency_key text NOT NULL, UNIQUE(site_id,idempotency_key,derived_version)
);
COMMIT;
