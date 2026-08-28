from __future__ import annotations
from dataclasses import replace
from datetime import datetime,timedelta,timezone
from decimal import Decimal
import inspect,unittest
from profit_engine_runtime.money_ledger import AttributionGrade,MoneyState,ReconciliationState,cohort_k5,period_k5
from profit_engine_runtime import strategy_lab as lab

START=datetime(2026,8,1,tzinfo=timezone.utc)
def measurement(grade=AttributionGrade.A,reconciliation=ReconciliationState.MATCHED,link=True):
 return cohort_k5(7,Decimal("4"),Decimal("12"),cohort_ref="fixture-cohort",grade=grade,link_proven=link,as_of=START+timedelta(days=40),cohort_start=START,reconciliation=reconciliation)
def request(key="cell-a",strategy="cpc",link=True,maturity=lab.MaturityState.MATURE,proxy=None,evidence=("fixture-money",)):
 return lab.StrategyCellRequest("1.0","dilivox",key,"preview:fixture","a"*64,"text",strategy,"content-fixture",{"device":"all"},"measurement:fixture",evidence,link,maturity,"goal:fixture" if proxy else None,proxy)
def cell(key="cell-a",grade=AttributionGrade.A,**kwargs): return lab.evaluate_cell(request(key=key,**kwargs),measurement(grade=grade,link=kwargs.get("link",True)))

class StrategyLabTests(unittest.TestCase):
 def test_a_b_and_valid_d_are_eligible(self):
  for grade,evidence in ((AttributionGrade.A,("fixture-money",)),(AttributionGrade.B,("fixture-money",)),(AttributionGrade.D,("fixture-money","private-map-evidence"))):
   c=lab.evaluate_cell(request(evidence=evidence),measurement(grade=grade));self.assertTrue(c.eligible)
 def test_c_period_diagnostic_and_cohort_are_not_autonomous(self):
  period=period_k5(Decimal("2"),Decimal("10"),grade=AttributionGrade.C)
  c=lab.evaluate_cell(request(link=False),period);self.assertEqual(lab.LabState.CELL_HELD_ATTRIBUTION,c.eligibility_state)
  cohort=lab.evaluate_cell(request(link=False),measurement(AttributionGrade.C,link=False));self.assertIn("metrica_only_cohort_forbidden",cohort.hold_reasons)
 def test_e_and_unjoinable_are_held(self):
  for grade in (AttributionGrade.E,AttributionGrade.UNJOINABLE):self.assertEqual(lab.LabState.CELL_HELD_ATTRIBUTION,lab.evaluate_cell(request(link=False),measurement(grade,link=False)).eligibility_state)
 def test_all_nonmatched_reconciliation_states_are_held(self):
  for state in (ReconciliationState.PENDING,ReconciliationState.DRIFT,ReconciliationState.BASIS_BLOCKED,ReconciliationState.SOURCE_MISSING):
   c=lab.evaluate_cell(request(),measurement(reconciliation=state));self.assertFalse(c.eligible);self.assertIn("reconciliation_not_matched",c.hold_reasons)
 def test_not_computable_and_upstream_nonconsumable_are_held(self):
  bad=replace(measurement(),state=MoneyState.NOT_COMPUTABLE);c=lab.evaluate_cell(request(),bad);self.assertIn("measurement_not_computable",c.hold_reasons)
  held=replace(measurement(),hold_reasons=("fixture_hold",));self.assertIn("measurement_not_optimizer_consumable",lab.evaluate_cell(request(),held).hold_reasons)
 def test_maturity_and_late_arrival_are_held(self):
  for state in (lab.MaturityState.IMMATURE,lab.MaturityState.LATE_ARRIVAL_OPEN):self.assertEqual(lab.LabState.CELL_HELD_MATURITY,lab.evaluate_cell(request(maturity=state),measurement()).eligibility_state)
 def test_missing_provenance_and_incompatible_measurement(self):
  no_refs=lab.evaluate_cell(request(evidence=()),replace(measurement(),numerator_source=()));self.assertIn("missing_provenance",no_refs.hold_reasons)
  incompatible=lab.evaluate_cell(request(),replace(measurement(),kind="diagnostic_ctr"));self.assertIn("measurement_kind_incompatible",incompatible.hold_reasons)
 def test_unaccepted_source_state_is_held(self):
  held=lab.evaluate_cell(replace(request(),source_state="STALE"),measurement());self.assertFalse(held.eligible);self.assertIn("source_state_not_accepted",held.hold_reasons)
 def test_strategy_capability_and_all_five_kinds(self):
  self.assertEqual(lab.LabState.CELL_BLOCKED_PROVIDER_CAPABILITY,lab.evaluate_cell(request(strategy="unsupported"),measurement()).eligibility_state)
  self.assertTrue(lab.evaluate_cell(request(strategy="cpc"),measurement()).eligible)
  supported=lab.ProxyState.PROXY_MONEY_ASSOCIATION_SUPPORTED
  for kind in ("conversion_click","pay_for_conversion","value_crr"):
   self.assertTrue(lab.evaluate_cell(request(strategy=kind,proxy=supported),measurement()).eligible)
  maximum=replace(request(strategy="maximum_profit",proxy=supported),campaign_type="unified_performance");self.assertTrue(lab.evaluate_cell(maximum,measurement()).eligible)
 def test_proxy_states_do_not_invent_money_or_unlock(self):
  for state in (lab.ProxyState.PROXY_UNPROVEN,lab.ProxyState.PROXY_EVIDENCE_PENDING,lab.ProxyState.PROXY_REJECTED):
   self.assertFalse(lab.evaluate_cell(request(strategy="conversion_click",proxy=state),measurement()).eligible)
  supported=lab.evaluate_cell(request(strategy="conversion_click",proxy=lab.ProxyState.PROXY_MONEY_ASSOCIATION_SUPPORTED),measurement());self.assertTrue(supported.eligible);self.assertFalse(hasattr(supported,"proxy_money_value"))
 def test_cell_digest_deterministic_and_material_change(self):
  one=cell();two=cell();self.assertEqual(one.cell_digest,two.cell_digest);self.assertNotEqual(one.cell_digest,cell(key="cell-b").cell_digest)
 def test_valid_experiment_preview_is_deterministic_and_inert(self):
  control=cell("control");treatment=cell("treatment",grade=AttributionGrade.B)
  args=dict(experiment_key="experiment-fixture",control=control,treatments=(treatment,),hypothesis_label="public fixture",primary_measurement_kind="K5_7D",observation_contract=lab.ObservationContract(7,True,2,("reconciled-money",)),campaign_preview_refs=("preview:fixture",),budget_proposal_refs=("budget:inert",),guardrail_refs=("guardrail:data-quality",),holdout_declared=True)
  one=lab.build_experiment_preview(**args);two=lab.build_experiment_preview(**args);self.assertEqual(lab.LabState.EXPERIMENT_PREVIEW_VALID,one.state);self.assertEqual(one.preview_digest,two.preview_digest);self.assertEqual((0,0,False),(one.provider_requests,one.advertising_spend,one.provider_write_allowed))
 def test_held_treatment_and_missing_holdout_invalidate_preview(self):
  control=cell("control");held=lab.evaluate_cell(request(key="held",maturity=lab.MaturityState.IMMATURE),measurement())
  p=lab.build_experiment_preview(experiment_key="e",control=control,treatments=(held,),hypothesis_label="fixture",primary_measurement_kind="K5_7D",observation_contract=lab.ObservationContract(7,True,2,("money",)),campaign_preview_refs=("preview:fixture",),budget_proposal_refs=("budget:inert",),guardrail_refs=("guardrail",),holdout_declared=False)
  self.assertEqual(lab.LabState.EXPERIMENT_PREVIEW_INVALID,p.state);self.assertIn("treatment_cell_not_eligible",p.prerequisite_errors);self.assertIn("holdout_control_required",p.prerequisite_errors)
 def test_evidence_package_is_versioned_deterministic_and_safe(self):
  control=cell("control");treatment=cell("treatment",grade=AttributionGrade.B);obs=lab.ObservationContract(7,True,2,("money",));p=lab.build_experiment_preview(experiment_key="e",control=control,treatments=(treatment,),hypothesis_label="fixture",primary_measurement_kind="K5_7D",observation_contract=obs,campaign_preview_refs=("preview:fixture",),budget_proposal_refs=("budget:inert",),guardrail_refs=("guardrail",),holdout_declared=True)
  one=lab.build_evidence_package((control,treatment),p);two=lab.build_evidence_package((control,treatment),p);self.assertEqual(one.package_digest,two.package_digest);self.assertEqual({"provider_write_allowed":False,"provider_requests":0,"advertising_spend":0},one.safety_state)
 def test_sensitive_decisions_fail_closed(self):
  for action in lab.SENSITIVE_DECISION_REQUESTS:self.assertEqual(lab.LabState.BLOCKED_PRIVATE_CORE_REQUIRED,lab.private_decision_boundary(action))
  self.assertEqual(lab.LabState.BLOCKED_PRIVATE_CORE_REQUIRED,lab.private_decision_boundary("unknown"))
 def test_no_provider_transport_or_commercial_decision_implementation(self):
  source=inspect.getsource(lab).lower();self.assertNotIn("requests.",source);self.assertNotIn("urllib",source);self.assertNotIn("authorization",source)
  funcs=set(name for name,value in vars(lab).items() if inspect.isfunction(value));self.assertFalse(funcs & {"rank","select","winner","allocate","launch","execute","update","delete"})
 def test_allowed_states_exclude_execution_and_outcomes(self):
  values={state.value for state in lab.ALLOWED_LAB_STATES};self.assertFalse(values & {"WINNER","SCALE_SELECTED","ALLOCATED","EXECUTED","LAUNCHED"})

if __name__=="__main__":unittest.main()
