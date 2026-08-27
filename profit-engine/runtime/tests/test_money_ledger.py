from __future__ import annotations
import json,tempfile,unittest,uuid
from datetime import datetime,timezone,timedelta
from decimal import Decimal
from pathlib import Path
from profit_engine_runtime.money_ledger import *

def registration(campaign="campaign-a"):
 return {"schema_version":"1.0","site_id":"dilivox","acquisition_id":str(uuid.UUID("11111111-1111-4111-8111-111111111111")),"cohort_ref":"fixture-cohort","acquired_at":"2026-08-01T00:00:00+00:00","landing_content_id":"fixture-content","provider":"direct","attribution":{"campaign_id":campaign,"utm_source":"fixture"},"expires_at":"2026-08-31T00:00:00+00:00","deployment_version":"fixture","provenance":{"source":"synthetic"}}

class MoneyLedgerTests(unittest.TestCase):
 def test_acquisition_replay_and_conflict(self):
  r=AcquisitionRegistry();self.assertEqual("created",r.register(registration())[0]);self.assertEqual("idempotent",r.register(registration())[0]);self.assertIn("conflicting_acquisition_registration",r.register(registration("campaign-b"))[1]);self.assertEqual(1,len(r.records))
 def test_acquisition_rejects_arbitrary_and_pii(self):
  r=AcquisitionRegistry();x=registration();x["email"]="x@test";self.assertEqual("held",r.register(x)[0]);y=registration();y["attribution"]["arbitrary"]="x";self.assertEqual("held",r.register(y)[0])
 def test_attribution_grades(self):
  campaigns={"campaign-a"}
  self.assertEqual(AttributionGrade.A,classify_attribution(first_party_campaign="campaign-a",metrica_campaign="campaign-a",direct_campaigns=campaigns).grade)
  self.assertEqual(AttributionGrade.B,classify_attribution(first_party_campaign="campaign-a",metrica_campaign=None,direct_campaigns=campaigns).grade)
  c=classify_attribution(first_party_campaign=None,metrica_campaign="campaign-a",direct_campaigns=campaigns);self.assertEqual(AttributionGrade.C,c.grade);self.assertFalse(c.cohort_link_proven)
  self.assertEqual(AttributionGrade.D,classify_attribution(first_party_campaign=None,metrica_campaign=None,direct_campaigns=campaigns,utm_campaign="public-label",private_mapper=lambda _:"campaign-a").grade)
  self.assertEqual(AttributionGrade.E,classify_attribution(first_party_campaign=None,metrica_campaign=None,direct_campaigns=campaigns,source_direct=True).grade)
 def test_contradiction_holds_no_date_fallback(self):
  x=classify_attribution(first_party_campaign="a",metrica_campaign="b",direct_campaigns={"a","b"});self.assertEqual(AttributionGrade.UNJOINABLE,x.grade);self.assertFalse(x.optimizer_consumable)
  self.assertEqual(AttributionGrade.UNJOINABLE,classify_attribution(first_party_campaign=None,metrica_campaign=None,direct_campaigns=set()).grade)
 def test_reconciliation_match_drift_and_basis(self):
  args=dict(metrica_scope="site-day",yan_scope="site-day",currency_a="RUB",currency_b="RUB",basis_a="vat-known",basis_b="vat-known",timezone_a="Europe/Moscow",timezone_b="Europe/Moscow",tolerance=Decimal("0.01"))
  self.assertEqual(ReconciliationState.MATCHED,reconcile(Decimal("10"),Decimal("10.005"),**args).state)
  self.assertEqual(ReconciliationState.DRIFT,reconcile(Decimal("10"),Decimal("11"),**args).state)
  self.assertEqual(ReconciliationState.BASIS_BLOCKED,reconcile(Decimal("10"),Decimal("10"),**(args|{"currency_b":"USD"})).state)
  self.assertEqual(ReconciliationState.SOURCE_MISSING,reconcile(None,Decimal("10"),**args).state)
 def test_period_k5_decimal_zero_missing_and_hold(self):
  m=period_k5(Decimal("2.50"),Decimal("12.50"));self.assertEqual(Decimal("5"),m.value);self.assertEqual("period_K5",m.kind)
  self.assertIsNone(period_k5(Decimal(0),Decimal("1")).value);self.assertIsNone(period_k5(Decimal("1"),None).value)
  self.assertFalse(period_k5(Decimal("1"),Decimal("5"),upstream_held=True).optimizer_consumable)
 def test_period_cannot_masquerade_as_cohort(self):
  p=period_k5(Decimal("2"),Decimal("10"));self.assertNotIn(p.kind,{"K5_1D","K5_7D","K5_30D"})
  c=cohort_k5(7,Decimal("2"),Decimal("10"),cohort_ref="c",grade=AttributionGrade.C,link_proven=False,as_of=datetime(2026,9,1,tzinfo=timezone.utc),cohort_start=datetime(2026,8,1,tzinfo=timezone.utc));self.assertIn("NOT_COMPUTABLE_ATTRIBUTION_HOLD",c.hold_reasons)
 def test_cohort_windows_original_denominator_and_maturity(self):
  start=datetime(2026,8,1,tzinfo=timezone.utc);spend=Decimal("4")
  for days,revenue,expected in [(1,"4","1"),(7,"12","3"),(30,"20","5")]:
   m=cohort_k5(days,spend,Decimal(revenue),cohort_ref="c",grade=AttributionGrade.A,link_proven=True,as_of=start+timedelta(days=40),cohort_start=start);self.assertEqual(Decimal(expected),m.value);self.assertEqual(spend,m.denominator)
  immature=cohort_k5(30,spend,Decimal("20"),cohort_ref="c",grade=AttributionGrade.A,link_proven=True,as_of=start+timedelta(days=10),cohort_start=start);self.assertIn("late_arrival_window_open",immature.hold_reasons);self.assertNotEqual(MoneyState.FINAL,immature.state)
 def test_late_arrival_versions_without_rewrite(self):
  store=DerivedVersions();a=period_k5(Decimal("2"),Decimal("8"));b=period_k5(Decimal("2"),Decimal("10"));v1=store.recompute("p",a);v2=store.recompute("p",b);self.assertEqual((1,2),(v1.version,v2.version));self.assertEqual(Decimal("4"),store.values["p"][0].value)
 def test_double_count_prevention(self):
  self.assertEqual(Decimal("10"),select_revenue(Decimal("10"),Decimal("10"))[0]);value,holds=select_revenue(Decimal("10"),Decimal("10"),combine=True);self.assertIsNone(value);self.assertIn("attempted_metrica_yan_double_count",holds)
 def test_unit_ratios_scope_and_zero(self):
  self.assertEqual(Decimal("2"),unit_revenue("revenue_per_visit",Decimal("10"),5,True).value)
  self.assertIsNone(unit_revenue("revenue_per_user",Decimal("10"),0,True).value);self.assertIsNone(unit_revenue("revenue_per_visit",Decimal("10"),5,False).value)
 def test_metrica_profile_contract(self):
  p=MetricaAttributionProfile();response={"query":{"dimensions":list(p.dimensions),"metrics":list(p.metrics)},"currency":"RUB","sampled":False,"data_lag":0};self.assertEqual((),p.validate(response));self.assertIn("metrica_attribution_dimensions_missing",p.validate({"query":{"dimensions":[],"metrics":[]},"currency":"RUB"}))
 def test_schema_migration_decimal_and_site_scope(self):
  root=Path(__file__).resolve().parents[2];sql=(root/"data/migrations/0002_money_ledger_reconciliation.sql").read_text().lower();
  for table in ("acquisitions","acquisition_attribution_evidence","reconciliation_runs","money_ledger_facts","k5_measurements"):self.assertIn(f"create table profit_engine.{table}",sql)
  self.assertIn("numeric(20,6)",sql);self.assertNotIn("double precision",sql)
 def test_direct_spend_contract_requires_decimal_basis_and_provenance(self):
  good=DirectSpendInput("campaign-a","2026-08-01",Decimal("2.5"),"RUB",True,True,False,"raw-fixture",True,"FINAL");self.assertEqual((),good.validate())
  bad=DirectSpendInput("campaign-a","2026-08-01",None,None,None,None,None,None,False,"UNKNOWN");self.assertIn("missing_direct_spend",bad.validate());self.assertIn("missing_raw_provenance",bad.validate())

if __name__=="__main__":unittest.main()
