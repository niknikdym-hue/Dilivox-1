from __future__ import annotations
from dataclasses import asdict, replace
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import argparse, json
from .money_ledger import AttributionGrade, ReconciliationState, cohort_k5
from .strategy_lab import MaturityState, StrategyCellRequest, evaluate_cell, private_decision_boundary

def fixture(scenario: str):
    start=datetime(2026,8,1,tzinfo=timezone.utc)
    grade=AttributionGrade.A
    reconciliation=ReconciliationState.MATCHED
    mature=MaturityState.MATURE
    evidence=("fixture-money-v1",)
    if scenario=="b-grade": grade=AttributionGrade.B
    if scenario=="c-grade": grade=AttributionGrade.C
    if scenario=="e-grade": grade=AttributionGrade.E
    if scenario=="pending": reconciliation=ReconciliationState.PENDING
    if scenario=="immature": mature=MaturityState.LATE_ARRIVAL_OPEN
    measurement=cohort_k5(7,Decimal("4"),Decimal("12"),cohort_ref="fixture-cohort",grade=grade,link_proven=grade in {AttributionGrade.A,AttributionGrade.B},as_of=start+timedelta(days=40),cohort_start=start,reconciliation=reconciliation)
    if scenario=="missing-provenance": measurement=replace(measurement,numerator_source=())
    request=StrategyCellRequest("1.0","dilivox","fixture-cell","preview:fixture","a"*64,"text","cpc","content-fixture",{},"measurement:fixture",evidence,grade in {AttributionGrade.A,AttributionGrade.B},mature)
    return evaluate_cell(request,measurement)

def main() -> int:
    parser=argparse.ArgumentParser(description="Build a public-safe StrategyCell fixture")
    parser.add_argument("scenario",choices=("eligible","b-grade","c-grade","e-grade","pending","immature","missing-provenance","private-decision"))
    args=parser.parse_args()
    value=private_decision_boundary("rank") if args.scenario=="private-decision" else fixture(args.scenario)
    print(json.dumps(asdict(value) if hasattr(value,"__dataclass_fields__") else {"state":value},ensure_ascii=False,sort_keys=True,indent=2,default=str))
    return 0
if __name__=="__main__": raise SystemExit(main())
