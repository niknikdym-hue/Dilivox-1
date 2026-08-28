from __future__ import annotations
from dataclasses import replace
from datetime import datetime,timedelta,timezone
from decimal import Decimal
import unittest
from profit_engine_runtime.day10_public import *
from profit_engine_runtime.money_ledger import DirectSpendInput,MoneyState,ReconciliationState

DAY="2026-08-01"; NOW=datetime(2026,9,15,tzinfo=timezone.utc); START=datetime(2026,8,1,tzinfo=timezone.utc)
def payload(dimensions=ATTRIBUTION_DIMENSIONS,campaign="campaign-a",revenue="12.00"):
 vals=[DAY,campaign,"group-a","yandex","cpc","fixture","variant","term"]
 return {"query":{"dimensions":list(dimensions),"metrics":list(ATTRIBUTION_METRICS)},"data":[{"dimensions":[{"name":v} for v in vals[:len(dimensions)]],"metrics":[revenue,20,18,16]}],"currency":"RUB","money_basis":"explicit","timezone":"Europe/Moscow","sampled":False,"sample_size":100,"sample_space":100,"accuracy":"full","data_lag":0,"contains_sensitive_data":False}
def acquisition(campaign="campaign-a"):
 return {"schema_version":"1.0","site_id":"dilivox","acquisition_id":"11111111-1111-4111-8111-111111111111","cohort_ref":"fixture-cohort","acquired_at":"2026-08-01T00:00:00+00:00","landing_content_id":"fixture-content","provider":"direct","attribution":{"campaign_id":campaign},"expires_at":"2026-09-01T00:00:00+00:00","deployment_version":"fixture","provenance":{"source":"fixture"}}
def fact():return normalize_metrica_attribution(site_id="dilivox",payload=payload(),raw_source_ref="raw-metrica",source_state="FINAL")[0]
def direct():return DirectSpendInput("campaign-a",DAY,Decimal("10"),"RUB",True,True,False,"raw-direct",True,"FINAL")
def yan():return YanControlInput(Decimal("12"),"RUB",f"site-day:{DAY}","explicit","Europe/Moscow","raw-yan")
def cohort(days,revenue,**changes):
 value=build_cohort_revenue_evidence(site_id="dilivox",cohort_ref="fixture-cohort",window_days=days,window_start=DAY,window_end=(START+timedelta(days=days-1)).date().isoformat(),attributed_cohort_revenue=Decimal(revenue),currency="RUB",money_basis="explicit",timezone="Europe/Moscow",source_state="FINAL",reconciliation_state=ReconciliationState.MATCHED,source_refs=(f"raw-cohort-{days}",),linkage_evidence_refs=(f"cohort-link-{days}",),linkage_basis="first-party-acquisition-cohort",mature=True)
 return replace(value,**changes)
def proposal(kind=ProposalKind.SCALE,current="100",proposed="110"):
 return build_action_proposal(proposal_id="proposal-fixture",site_id="dilivox",kind=kind,target_refs={"campaign_spec":"fixture"},strategy_evidence_digest="a"*64,measurement_refs=("measurement",),provenance_refs=("raw",),current_weekly_budget=current,proposed_weekly_budget=proposed,private_decision_ref="private:fixture",private_decision_digest="b"*64,audit_metadata={"source":"fixture"})
def clean(owner=None):return GuardContext(False,ReconciliationState.MATCHED,MoneyState.RECONCILED,True,True,False,True,owner)

class Day10PublicTests(unittest.TestCase):
 def test_named_metrica_attribution_fact(self):
  f=fact();self.assertEqual(("campaign-a","group-a",Decimal("12.00")),(f.direct_campaign_ref,f.direct_group_ref,f.attributed_yan_revenue));self.assertEqual("fixture",f.utm_dimensions["utm_campaign"]);self.assertTrue(f.optimizer_consumable);self.assertFalse(f.sampled)
 def test_missing_named_dimension_holds_without_inference(self):
  dims=tuple(x for x in ATTRIBUTION_DIMENSIONS if "DirectClickOrder" not in x);f=normalize_metrica_attribution(site_id="dilivox",payload=payload(dims),raw_source_ref="raw",source_state="FINAL")[0]
  self.assertIn("metrica_named_attribution_dimensions_missing_or_incompatible",f.hold_reasons);self.assertIsNone(f.direct_campaign_ref);self.assertFalse(f.optimizer_consumable)
 def test_materializer_deterministic_replay_and_no_double_count(self):
  m=LedgerMaterializer();args=dict(acquisition=acquisition(),direct=direct(),metrica=fact(),yan=yan(),direct_campaigns={"campaign-a"},as_of=NOW,cohort_start=START)
  one=m.materialize(**args);two=m.materialize(**args);self.assertEqual(one.materialization_digest,two.materialization_digest);self.assertEqual(1,one.derived_version);self.assertEqual(Decimal("1.2"),one.period_measurement.value);self.assertEqual(Decimal("12"),one.period_measurement.numerator);self.assertTrue(all(x.value is None for x in one.cohort_measurements))
 def test_late_arrival_new_source_creates_derived_version(self):
  m=LedgerMaterializer();base=dict(acquisition=acquisition(),direct=direct(),yan=yan(),direct_campaigns={"campaign-a"},as_of=NOW,cohort_start=START)
  one=m.materialize(metrica=fact(),**base);later=normalize_metrica_attribution(site_id="dilivox",payload=payload(revenue="13"),raw_source_ref="raw-metrica-v2",source_state="FINAL")[0];two=m.materialize(metrica=later,**base);self.assertEqual((1,2),(one.derived_version,two.derived_version));self.assertEqual(Decimal("1.2"),one.period_measurement.value)
 def test_unproven_cohort_and_nonmatched_reconciliation_not_consumable(self):
  m=LedgerMaterializer();out=m.materialize(acquisition=acquisition("other"),direct=direct(),metrica=fact(),yan=replace(yan(),revenue=Decimal("20")),direct_campaigns={"campaign-a","other"},as_of=NOW,cohort_start=START)
  self.assertFalse(out.period_measurement.optimizer_consumable);self.assertTrue(all(not x.optimizer_consumable for x in out.cohort_measurements))
 def test_daily_period_revenue_never_masquerades_as_cohort(self):
  out=LedgerMaterializer().materialize(acquisition=acquisition(),direct=direct(),metrica=fact(),yan=yan(),direct_campaigns={"campaign-a"},as_of=NOW,cohort_start=START)
  self.assertEqual(Decimal("12"),out.period_measurement.numerator)
  for item in out.cohort_measurements:self.assertIsNone(item.numerator);self.assertIsNone(item.value);self.assertIn("NOT_COMPUTABLE_ATTRIBUTION_HOLD",item.hold_reasons)
 def test_explicit_1d_only_computes_1d(self):
  out=LedgerMaterializer().materialize(acquisition=acquisition(),direct=direct(),metrica=fact(),yan=yan(),direct_campaigns={"campaign-a"},as_of=NOW,cohort_start=START,cohort_evidence=(cohort(1,"4"),))
  self.assertEqual(Decimal("0.4"),out.cohort_measurements[0].value);self.assertTrue(all(x.value is None for x in out.cohort_measurements[1:]))
 def test_each_cohort_window_uses_own_revenue_same_denominator(self):
  evidence=(cohort(1,"4"),cohort(7,"12"),cohort(30,"20"));out=LedgerMaterializer().materialize(acquisition=acquisition(),direct=direct(),metrica=fact(),yan=yan(),direct_campaigns={"campaign-a"},as_of=NOW,cohort_start=START,cohort_evidence=evidence)
  self.assertEqual([Decimal("0.4"),Decimal("1.2"),Decimal("2")],[x.value for x in out.cohort_measurements]);self.assertEqual({Decimal("10")},{x.denominator for x in out.cohort_measurements})
 def test_wrong_cohort_or_money_basis_holds(self):
  variants=(cohort(7,"12",cohort_ref="wrong"),cohort(7,"12",currency="USD"),cohort(7,"12",money_basis="other"),cohort(7,"12",timezone="UTC"))
  for evidence in variants:
   out=LedgerMaterializer().materialize(acquisition=acquisition(),direct=direct(),metrica=fact(),yan=yan(),direct_campaigns={"campaign-a"},as_of=NOW,cohort_start=START,cohort_evidence=(evidence,));self.assertIsNone(out.cohort_measurements[1].value);self.assertIn("NOT_COMPUTABLE_ATTRIBUTION_HOLD",out.cohort_measurements[1].hold_reasons)
 def test_nonmatched_and_immature_cohort_evidence_holds(self):
  variants=(cohort(7,"12",reconciliation_state=ReconciliationState.DRIFT,hold_reasons=("cohort_reconciliation_not_matched",)),cohort(7,"12",mature=False,hold_reasons=("cohort_window_immature",)),cohort(7,"12",late_arrival_open=True,hold_reasons=("late_arrival_window_open",)))
  for evidence in variants:
   out=LedgerMaterializer().materialize(acquisition=acquisition(),direct=direct(),metrica=fact(),yan=yan(),direct_campaigns={"campaign-a"},as_of=NOW,cohort_start=START,cohort_evidence=(evidence,));self.assertFalse(out.cohort_measurements[1].optimizer_consumable)
 def test_late_cohort_evidence_versions_without_rewrite(self):
  m=LedgerMaterializer();args=dict(acquisition=acquisition(),direct=direct(),metrica=fact(),yan=yan(),direct_campaigns={"campaign-a"},as_of=NOW,cohort_start=START)
  first=m.materialize(**args);second=m.materialize(**args,cohort_evidence=(cohort(7,"12"),));self.assertEqual((1,2),(first.derived_version,second.derived_version));self.assertIsNone(first.cohort_measurements[1].value);self.assertEqual(Decimal("1.2"),second.cohort_measurements[1].value)
 def test_action_proposal_is_public_safe_and_deterministic(self):
  one=proposal();two=proposal();self.assertEqual(one.proposal_digest,two.proposal_digest);self.assertTrue(one.requires_budget_governor);self.assertFalse(one.provider_write_allowed);self.assertFalse(hasattr(one,"private_score"))
 def test_governor_10_and_20_percent_ready(self):
  self.assertEqual(GovernorState.GOVERNOR_READY_FOR_DAY11_CONTROLLER,govern(proposal(proposed="110"),clean()).state)
  self.assertEqual(GovernorState.GOVERNOR_READY_FOR_DAY11_CONTROLLER,govern(proposal(proposed="120.00"),clean()).state)
 def test_governor_20_01_requires_owner(self):
  p=proposal(proposed="120.01");self.assertEqual(GovernorState.PENDING_OWNER_APPROVAL,govern(p,clean()).state);self.assertEqual(GovernorState.GOVERNOR_READY_FOR_DAY11_CONTROLLER,govern(p,clean("owner-approval-fixture")).state)
 def test_missing_or_malformed_budget_blocks(self):
  self.assertEqual(GovernorState.BLOCKED_BUDGET_BASELINE,govern(proposal(current=None,proposed="100"),clean()).state)
  self.assertEqual(GovernorState.BLOCKED_BUDGET_BASELINE,govern(proposal(current="bad",proposed="100"),clean()).state)
 def test_quality_reconciliation_maturity_consumption_block_scale_test(self):
  variants=(replace(clean(),data_quality_hold=True),replace(clean(),reconciliation_state=ReconciliationState.DRIFT),replace(clean(),money_state=MoneyState.NOT_COMPUTABLE),replace(clean(),mature=False),replace(clean(),optimizer_consumable=False))
  for guards in variants:
   for kind in (ProposalKind.SCALE,ProposalKind.TEST):self.assertEqual(GovernorState.BLOCKED_DATA_QUALITY,govern(proposal(kind),guards).state)
 def test_safety_kinds_structurally_ready_but_kill_switch_blocks(self):
  dirty=replace(clean(),data_quality_hold=True,optimizer_consumable=False)
  for kind in (ProposalKind.STOP,ProposalKind.HOLD,ProposalKind.QUARANTINE):self.assertEqual(GovernorState.GOVERNOR_READY_FOR_DAY11_CONTROLLER,govern(proposal(kind,None,None),dirty).state)
  self.assertEqual(GovernorState.BLOCKED_KILL_SWITCH,govern(proposal(ProposalKind.STOP,None,None),replace(dirty,global_kill_switch=True)).state)
 def test_site_intent_is_inert(self):
  i=build_site_experiment_intent(intent_id="site-intent",action="activation",experiment_ref="experiment",variant_refs=("a","b"),kill_switch_ref="kill",action_proposal_ref="proposal")
  self.assertEqual((False,0,0),(i.executable,i.provider_requests,i.site_requests));self.assertEqual(i.intent_digest,build_site_experiment_intent(intent_id="site-intent",action="activation",experiment_ref="experiment",variant_refs=("a","b"),kill_switch_ref="kill",action_proposal_ref="proposal").intent_digest)

if __name__=="__main__":unittest.main()
