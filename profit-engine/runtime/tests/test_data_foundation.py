from __future__ import annotations

import json
import tempfile
import unittest
from dataclasses import replace
from decimal import Decimal
from pathlib import Path

from profit_engine_runtime.clients import YanPartnerStatsReadClient, YandexDirectReadClient, YandexMetricaReadClient
from profit_engine_runtime.contracts import LockboxAdapterConfig, Money
from profit_engine_runtime.data_quality import (
    DATA_QUALITY_HOLD, DataQualityAssessment, DuplicateState, FreshnessState,
    MissingSourceState, ReconciliationState, SnapshotShapeState,
)
from profit_engine_runtime.raw_store import (
    DataState, LocalRawStore, RawSnapshotConflict, RawSnapshotEnvelope,
    RawSnapshotIntegrityError, SourceWindow, request_fingerprint, sha256_json,
)

def envelope(site="example-site", provider="fixture-provider", payload=None):
    payload = {"rows": []} if payload is None else payload
    return RawSnapshotEnvelope(
        schema_version="1.0", site_id=site, provider=provider,
        source_object_type="fixture-report", captured_at="2026-08-27T10:00:00+00:00",
        source_window=SourceWindow("2026-08-26T00:00:00+00:00", "2026-08-27T00:00:00+00:00"),
        request_fingerprint=request_fingerprint({"fixture": "identity"}),
        payload_sha256=sha256_json(payload), provider_request_id=None,
        data_state=DataState.ESTIMATED, ingestion_run_id="fixture-run",
    )

class DataFoundationTests(unittest.TestCase):
    def test_raw_store_create_and_same_content_idempotency(self):
        payload = {"rows": [{"metric": 1}]}
        with tempfile.TemporaryDirectory() as directory:
            store = LocalRawStore(Path(directory) / "raw")
            first = store.put(envelope(payload=payload), payload)
            second = store.put(envelope(payload=payload), payload)
            self.assertTrue(first.created); self.assertTrue(second.idempotent)
            self.assertEqual(payload, store.get(first.logical_key)[1])

    def test_raw_store_rejects_conflicting_payload(self):
        first_payload, second_payload = {"rows": [1]}, {"rows": [2]}
        with tempfile.TemporaryDirectory() as directory:
            store = LocalRawStore(Path(directory) / "raw")
            first = envelope(payload=first_payload)
            store.put(first, first_payload)
            with self.assertRaises(RawSnapshotConflict):
                store.put(replace(first, payload_sha256=sha256_json(second_payload)), second_payload)

    def test_raw_store_verifies_hash_on_write_and_read(self):
        payload = {"rows": [1]}
        with tempfile.TemporaryDirectory() as directory:
            store = LocalRawStore(Path(directory) / "raw")
            item = envelope(payload=payload)
            with self.assertRaises(RawSnapshotIntegrityError):
                store.put(replace(item, payload_sha256="0" * 64), payload)
            result = store.put(item, payload)
            path = Path(directory) / result.logical_key
            document = json.loads(path.read_text())
            document["payload"] = {"rows": [999]}
            path.write_text(json.dumps(document))
            with self.assertRaises(RawSnapshotIntegrityError): store.get(result.logical_key)

    def test_site_and_provider_paths_are_isolated(self):
        payload = {"rows": []}
        a = envelope(site="site-a", provider="provider-a", payload=payload).logical_key
        b = envelope(site="site-b", provider="provider-b", payload=payload).logical_key
        self.assertIn("raw/site-a/provider-a/", a)
        self.assertIn("raw/site-b/provider-b/", b)
        self.assertNotEqual(a, b)

    def test_money_requires_decimal(self):
        self.assertEqual(Decimal("1.230000"), Money(Decimal("1.230000"), "RUB").amount)
        with self.assertRaises(TypeError): Money(1.23, "RUB")  # type: ignore[arg-type]

    def test_data_quality_hold_blocks_optimizer_consumption(self):
        held = DataQualityAssessment(FreshnessState.STALE, MissingSourceState.PRESENT,
            DuplicateState.UNIQUE, SnapshotShapeState.VALID, ReconciliationState.NOT_READY)
        self.assertEqual(DATA_QUALITY_HOLD, held.status)
        self.assertFalse(held.optimizer_consumable)
        ready = DataQualityAssessment(FreshnessState.FRESH, MissingSourceState.PRESENT,
            DuplicateState.IDEMPOTENT_REPLAY, SnapshotShapeState.VALID, ReconciliationState.READY)
        self.assertTrue(ready.optimizer_consumable)

    def test_no_provider_write_methods(self):
        forbidden = {"add", "update", "delete", "suspend", "resume", "create", "mutate"}
        for client in (YandexDirectReadClient, YandexMetricaReadClient, YanPartnerStatsReadClient):
            self.assertTrue(forbidden.isdisjoint(client.__dict__))

    def test_public_examples_are_placeholder_only(self):
        root = Path(__file__).resolve().parents[2]
        for path in (root / "config").rglob("*.example.json"):
            text = path.read_text()
            self.assertIn("PRIVATE_LOCAL_VALUE", text)
            self.assertNotIn("fixture-super-secret-token-value", text)

    def test_lockbox_config_accepts_only_opaque_references(self):
        config = LockboxAdapterConfig("https://example.invalid", "lockbox-ref:PRIVATE_LOCAL_VALUE", "identity-ref:PRIVATE_LOCAL_VALUE")
        self.assertTrue(config.secret_reference.startswith("lockbox-ref:"))
        with self.assertRaises(ValueError):
            LockboxAdapterConfig("https://example.invalid", "literal-secret", "identity-ref:placeholder")

    def test_postgres_schema_has_required_tables_and_decimal_money(self):
        root = Path(__file__).resolve().parents[2]
        sql = (root / "data/migrations/0001_data_foundation.sql").read_text().lower()
        tables = ("sites", "provider_accounts", "ingestion_runs", "raw_snapshots",
            "campaign_snapshots", "traffic_facts", "site_events", "monetization_facts",
            "cohorts", "experiments", "decisions", "approvals", "actions_audit", "data_quality_checks")
        for table in tables: self.assertIn(f"create table profit_engine.{table}", sql)
        self.assertIn("numeric(20,6)", sql)
        self.assertNotIn("double precision", sql); self.assertNotIn(" real", sql)

if __name__ == "__main__": unittest.main()
