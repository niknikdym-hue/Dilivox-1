from __future__ import annotations
import tempfile, unittest, uuid
from pathlib import Path
from profit_engine_runtime.site_events import EventBatchIngestor, InMemorySiteEventStore, assess_event_quality
from profit_engine_runtime.raw_store import LocalRawStore

def event(kind="story_open", key="evt_0123456789abcdef", props=None):
    return {"schema_version":"1.0","event_id":str(uuid.uuid4()),"idempotency_key":key,"event_type":kind,"occurred_at":"2026-08-27T12:00:00+00:00","site_id":"dilivox","content_id":"fixture-content","content_type":"story","session_id":"fixture-session","acquisition_id":"fixture-acq","cohort_ref":"fixture-cohort","experiment_id":None,"variant_id":None,"placement_id":None,"source_content_id":None,"destination_content_id":None,"deployment_version":"fixture","properties":props or {}}
def batch(events, batch_id="fixture-batch"):
    return {"schema_version":"1.0","batch_id":batch_id,"site_id":"dilivox","captured_at":"2026-08-27T12:01:00+00:00","events":events}

class SiteEventTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.db=InMemorySiteEventStore(); self.ing=EventBatchIngestor(LocalRawStore(Path(self.tmp.name)/"raw"),self.db)
    def tearDown(self): self.tmp.cleanup()
    def test_raw_first_and_normalize(self):
        out=self.ing.ingest(batch([event()])); self.assertEqual("complete",out.status); self.assertEqual(1,out.accepted); self.assertLess(self.db.operation_log.index("raw:verified"),self.db.operation_log.index("events:normalized")); self.assertEqual(1,len(self.db.events))
    def test_dedupe_replay(self):
        e=event(); self.ing.ingest(batch([e])); out=self.ing.ingest(batch([e])); self.assertEqual(1,out.duplicates); self.assertEqual(1,len(self.db.events))
    def test_atomic_malformed_reject_after_raw(self):
        bad=event(); bad["free_text"]="forbidden"; out=self.ing.ingest(batch([event(),bad],"bad-batch")); self.assertEqual("held",out.status); self.assertEqual(0,out.accepted); self.assertEqual(0,len(self.db.events)); self.assertIsNotNone(out.raw_snapshot_id)
    def test_conflicting_batch_holds(self):
        self.ing.ingest(batch([event()])); changed=batch([event("catalog_opened")]); out=self.ing.ingest(changed); self.assertIn("raw_batch_conflict",out.hold_reasons)
    def test_property_allowlist_and_conversion_evidence(self):
        out=self.ing.ingest(batch([event("version_selected","evt_1111111111111111",{"answer_text":"secret"})],"props")); self.assertIn("property_allowlist_rejection",out.hold_reasons)
        out2=self.ing.ingest(batch([event("experiment_conversion","evt_2222222222222222",{"conversion_key":"k"})],"conversion")); self.assertIn("unapproved_experiment_conversion",out2.hold_reasons)
    def test_quality_hold_signals(self):
        for signal in ("unresolved_content","endpoint_stale","queue_overflow","impossible_sequence","duplicate_anomaly","lost_acquisition","experiment_join_failure","schema_incompatibility","instrumentation_failure"):
            q=assess_event_quality(**{signal:True}); self.assertEqual("DATA_QUALITY_HOLD",q["status"]); self.assertFalse(q["optimizer_consumable"])
        self.assertTrue(assess_event_quality()["optimizer_consumable"])

if __name__=="__main__": unittest.main()
