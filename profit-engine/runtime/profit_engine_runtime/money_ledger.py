from __future__ import annotations
from dataclasses import dataclass, field, replace
from datetime import datetime, timedelta
from decimal import Decimal
from enum import StrEnum
from typing import Any, Mapping
from .data_quality import DATA_QUALITY_HOLD
from .raw_store import canonical_json_bytes, sha256_json

class AttributionGrade(StrEnum):
 A="A_STRONG_DIRECT_CROSSCHECK"; B="B_DIRECT_ID"; C="C_METRICA_DIRECT"; D="D_UTM_PRIVATE_MAP"; E="E_SOURCE_ONLY"; UNJOINABLE="UNJOINABLE"
class ReconciliationState(StrEnum):
 PENDING="PENDING"; MATCHED="MATCHED"; DRIFT="DRIFT"; BASIS_BLOCKED="BASIS_BLOCKED"; SOURCE_MISSING="SOURCE_MISSING"
class MoneyState(StrEnum):
 ESTIMATED="ESTIMATED"; FINAL="FINAL"; RECONCILED="RECONCILED"; NOT_COMPUTABLE="NOT_COMPUTABLE"

ACQUISITION_FIELDS=frozenset({"schema_version","site_id","acquisition_id","cohort_ref","acquired_at","landing_content_id","provider","attribution","expires_at","deployment_version","provenance"})
ATTR_FIELDS=frozenset({"yclid","campaign_id","ad_id","group_id","criterion_id","phrase_id","keyword_id","utm_source","utm_medium","utm_campaign","utm_content","utm_term"})

@dataclass
class AcquisitionRegistry:
 records: dict[str,Mapping[str,Any]]=field(default_factory=dict)
 def register(self, value: Mapping[str,Any]) -> tuple[str,tuple[str,...]]:
  if set(value)!=ACQUISITION_FIELDS or set(value.get("attribution",{}))-ATTR_FIELDS: return "held",("acquisition_schema_rejected",)
  key=str(value["acquisition_id"]); digest=sha256_json(dict(value)); old=self.records.get(key)
  if old and sha256_json(dict(old))!=digest: return "held",("conflicting_acquisition_registration",)
  if old: return "idempotent",()
  self.records[key]=dict(value); return "created",()

@dataclass(frozen=True)
class AttributionResult:
 grade: AttributionGrade; campaign_ref: str|None; evidence_refs: tuple[str,...]; hold_reasons: tuple[str,...]=(); cohort_link_proven: bool=False
 @property
 def optimizer_consumable(self): return not self.hold_reasons and self.grade!=AttributionGrade.UNJOINABLE

def classify_attribution(*,first_party_campaign:str|None,metrica_campaign:str|None,direct_campaigns:set[str],source_direct=False,utm_campaign=None,private_mapper=None)->AttributionResult:
 if first_party_campaign and metrica_campaign and first_party_campaign!=metrica_campaign: return AttributionResult(AttributionGrade.UNJOINABLE,None,("first-party","metrica"),("contradictory_campaign_identity",),False)
 if first_party_campaign and metrica_campaign and first_party_campaign in direct_campaigns: return AttributionResult(AttributionGrade.A,first_party_campaign,("first-party","metrica","direct"),(),True)
 if first_party_campaign and first_party_campaign in direct_campaigns: return AttributionResult(AttributionGrade.B,first_party_campaign,("first-party","direct"),(),True)
 if metrica_campaign and metrica_campaign in direct_campaigns: return AttributionResult(AttributionGrade.C,metrica_campaign,("metrica","direct"),(),False)
 if private_mapper and utm_campaign:
  mapped=private_mapper(utm_campaign)
  if mapped and mapped in direct_campaigns:return AttributionResult(AttributionGrade.D,mapped,("utm-private-map","direct"),(),True)
 if source_direct:return AttributionResult(AttributionGrade.E,None,("source",),(),False)
 return AttributionResult(AttributionGrade.UNJOINABLE,None,(),("unjoinable_acquisition",),False)

@dataclass(frozen=True)
class Reconciliation:
 state: ReconciliationState; metrica_amount:Decimal|None; yan_control_amount:Decimal|None; absolute_delta:Decimal|None; relative_delta:Decimal|None; hold_reasons:tuple[str,...]; tolerance_version:str="generic-v1"; source_refs:tuple[str,...]=("metrica-attribution-view","yan-control-total")
 @property
 def optimizer_consumable(self):return self.state==ReconciliationState.MATCHED

def reconcile(metrica:Decimal|None,yan:Decimal|None,*,metrica_scope:str,yan_scope:str,currency_a:str,currency_b:str,basis_a:str|None,basis_b:str|None,timezone_a:str,timezone_b:str,tolerance:Decimal)->Reconciliation:
 if metrica is None or yan is None:return Reconciliation(ReconciliationState.SOURCE_MISSING,metrica,yan,None,None,("missing_revenue_source",))
 if metrica_scope!=yan_scope or currency_a!=currency_b or not basis_a or basis_a!=basis_b or timezone_a!=timezone_b:return Reconciliation(ReconciliationState.BASIS_BLOCKED,metrica,yan,None,None,("scope_currency_basis_mismatch",))
 delta=abs(metrica-yan); relative=(delta/yan if yan!=0 else (Decimal(0) if delta==0 else None)); state=ReconciliationState.MATCHED if delta<=tolerance else ReconciliationState.DRIFT
 return Reconciliation(state,metrica,yan,delta,relative,() if state==ReconciliationState.MATCHED else ("reconciliation_drift",))

@dataclass(frozen=True)
class Measurement:
 kind:str; value:Decimal|None; numerator:Decimal|None; denominator:Decimal|None; currency:str; grade:AttributionGrade; state:MoneyState; reconciliation:ReconciliationState; version:int=1; hold_reasons:tuple[str,...]=(); cohort_ref:str|None=None; site_id:str="dilivox"; window_start:str|None=None; window_end:str|None=None; numerator_source:tuple[str,...]=("metrica-attributed-yan",); denominator_source:tuple[str,...]=("direct-spend",); money_basis:str="explicit-compatible"; calculation_version:str="k5-v1"
 @property
 def optimizer_consumable(self):return self.value is not None and not self.hold_reasons and self.state in {MoneyState.FINAL,MoneyState.RECONCILED}

def period_k5(spend:Decimal|None,revenue:Decimal|None,*,currency_spend="RUB",currency_revenue="RUB",grade=AttributionGrade.A,reconciliation=ReconciliationState.MATCHED,upstream_held=False)->Measurement:
 holds=[]
 if spend is None:holds.append("missing_direct_spend")
 elif spend==0:holds.append("zero_denominator")
 if revenue is None:holds.append("missing_yan_revenue")
 if currency_spend!=currency_revenue:holds.append("currency_mismatch")
 if upstream_held:holds.append("held_upstream_source")
 if reconciliation==ReconciliationState.DRIFT:holds.append("reconciliation_drift")
 value=None if holds else revenue/spend
 return Measurement("period_K5",value,revenue,spend,currency_spend,grade,MoneyState.NOT_COMPUTABLE if holds else MoneyState.RECONCILED,reconciliation,hold_reasons=tuple(holds))

def cohort_k5(days:int,original_spend:Decimal|None,cohort_revenue:Decimal|None,*,cohort_ref:str,grade:AttributionGrade,link_proven:bool,as_of:datetime,cohort_start:datetime,late_grace_days=2,reconciliation=ReconciliationState.MATCHED)->Measurement:
 if days not in {1,7,30}:raise ValueError("cohort window must be 1, 7, or 30")
 holds=[]; mature=as_of>=cohort_start+timedelta(days=days+late_grace_days)
 if not link_proven:holds.append("NOT_COMPUTABLE_ATTRIBUTION_HOLD")
 if original_spend is None:holds.append("missing_direct_spend")
 elif original_spend==0:holds.append("zero_denominator")
 if cohort_revenue is None:holds.append("missing_yan_revenue")
 if not mature:holds.append("late_arrival_window_open")
 value=None if holds else cohort_revenue/original_spend
 return Measurement(f"K5_{days}D",value,cohort_revenue,original_spend,"RUB",grade,MoneyState.NOT_COMPUTABLE if holds else MoneyState.RECONCILED,reconciliation,hold_reasons=tuple(holds),cohort_ref=cohort_ref)

def unit_revenue(kind:str,revenue:Decimal|None,count:int|None,scope_compatible:bool)->Measurement:
 holds=[]
 if revenue is None:holds.append("missing_yan_revenue")
 if not count:holds.append("zero_or_unknown_denominator")
 if not scope_compatible:holds.append("incompatible_denominator_scope")
 return Measurement(kind,None if holds else revenue/Decimal(count),revenue,None if count is None else Decimal(count),"RUB",AttributionGrade.A,MoneyState.NOT_COMPUTABLE if holds else MoneyState.FINAL,ReconciliationState.PENDING,hold_reasons=tuple(holds))

@dataclass
class DerivedVersions:
 values:dict[str,list[Measurement]]=field(default_factory=dict)
 def recompute(self,key:str,measurement:Measurement)->Measurement:
  version=len(self.values.get(key,[]))+1; updated=replace(measurement,version=version);self.values.setdefault(key,[]).append(updated);return updated

def select_revenue(metrica_attributed:Decimal|None,yan_control:Decimal|None,*,combine=False)->tuple[Decimal|None,tuple[str,...]]:
 if combine:return None,("attempted_metrica_yan_double_count",)
 return metrica_attributed,(() if metrica_attributed is not None else ("missing_yan_revenue",))

@dataclass(frozen=True)
class MetricaAttributionProfile:
 attribution_model:str="last_yandex_direct_click"
 dimensions:tuple[str,...]=("ym:s:last_yandex_direct_clickDirectClickOrder","ym:s:last_yandex_direct_clickDirectBannerGroup","ym:s:last_yandex_direct_clickUTMCampaign","ym:s:date")
 metrics:tuple[str,...]=("ym:s:yanPartnerPrice","ym:s:yanRequests","ym:s:yanRenders","ym:s:yanShows")
 def validate(self,response:Mapping[str,Any])->tuple[str,...]:
  q=response.get("query",{}); dims=q.get("dimensions",()); metrics=q.get("metrics",())
  if isinstance(dims,str):dims=tuple(dims.split(","))
  if isinstance(metrics,str):metrics=tuple(metrics.split(","))
  holds=[]
  if not set(self.dimensions).issubset(set(dims)):holds.append("metrica_attribution_dimensions_missing")
  if not set(self.metrics).issubset(set(metrics)):holds.append("metrica_money_semantics_missing")
  if response.get("currency") is None:holds.append("currency_missing")
  return tuple(holds)

@dataclass(frozen=True)
class DirectSpendInput:
 campaign_ref:str; day:str; spend:Decimal|None; currency:str|None; include_vat:bool|None; include_discount:bool|None; money_in_micros:bool|None; raw_source_ref:str|None; complete:bool; source_state:str
 def validate(self)->tuple[str,...]:
  holds=[]
  if self.spend is None:holds.append("missing_direct_spend")
  elif not isinstance(self.spend,Decimal):holds.append("non_decimal_money")
  if not self.currency:holds.append("currency_missing")
  if None in {self.include_vat,self.include_discount,self.money_in_micros}:holds.append("unknown_vat_money_basis")
  if not self.raw_source_ref:holds.append("missing_raw_provenance")
  if not self.complete:holds.append("incomplete_source")
  if self.source_state not in {"ESTIMATED","FINAL","RECONCILED"}:holds.append("unknown_source_state")
  return tuple(holds)
