from __future__ import annotations
from dataclasses import replace
from pathlib import Path
import inspect
import unittest
from profit_engine_runtime import campaign_factory as cf

ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = ROOT / "sites/dilivox/content-registry.json"

def fixture_parts():
    registry = cf.load_content_registry(REGISTRY_PATH)
    active = next(x for x in registry.values() if x["active"] and x["content_type"] == "story")
    asset = cf.AssetSpec("asset-1", "fixture://image", active["content_id"], "b" * 64, "image/png", 1080, 607, "preview", "compatible")
    creative = cf.CreativeSpec("1.0", "story", "1", "creative-1", "variant-1", active["content_id"], "История для теста", "Синтетическое описание истории", active["canonical_url"], "text_ad", (asset.asset_id,), ("fixture",))
    spec = cf.CampaignSpec("1.0", "dilivox", "yandex_direct", "campaign-1", "text", "traffic", active["content_id"], active["canonical_url"], "cpc", {}, cf.BudgetRequest("100.00", "RUB", "daily", "fixture", "fixture"), ("RU",), {"timezone":"Europe/Moscow"}, cf.TrackingPlan({"campaign_id":"{campaign_id}","ad_id":"{ad_id}","group_id":"{gbid}","utm_source":"yandex","utm_medium":"cpc"}), (), (cf.AdGroupSpec("group-1","text","keyword",("fixture",),(creative.creative_id,)),), (creative.creative_id,), ("fixture",))
    return registry, spec, creative, asset

class CampaignFactoryTests(unittest.TestCase):
    def test_deterministic_digest_and_material_change(self):
        r,s,c,a=fixture_parts(); one=cf.build_preview(s,(c,),(a,),r); two=cf.build_preview(s,(c,),(a,),r)
        self.assertEqual(one.preview_digest,two.preview_digest); self.assertEqual(cf.PreviewState.PREVIEW_VALID,one.state)
        changed=cf.build_preview(replace(s,geo=("RU","KZ")),(c,),(a,),r); self.assertNotEqual(one.preview_digest,changed.preview_digest)
    def test_missing_inactive_and_noncanonical_content(self):
        r,s,c,a=fixture_parts()
        self.assertEqual(cf.PreviewState.BLOCKED_MISSING_CONTENT_ID,cf.build_preview(replace(s,landing_content_id="missing"),(c,),(a,),r).state)
        inactive=next(x for x in r.values() if not x["active"]); si=replace(s,landing_content_id=inactive["content_id"],destination_url=inactive["canonical_url"])
        self.assertEqual(cf.PreviewState.BLOCKED_MISSING_CONTENT_ID,cf.build_preview(si,(c,),(a,),r).state)
        self.assertEqual(cf.PreviewState.BLOCKED_MISSING_CONTENT_ID,cf.build_preview(replace(s,destination_url="/guessed/"),(c,),(a,),r).state)
    def test_tracking_allowlist_variables_and_collision(self):
        r,s,c,a=fixture_parts(); p=cf.build_preview(s,(c,),(a,),r); self.assertLessEqual(set(p.tracking_plan),cf.TRACKING_ALLOWLIST)
        bad=replace(s,tracking_plan=cf.TrackingPlan({"email":"x"})); self.assertEqual(cf.PreviewState.BLOCKED_TRACKING_CONTRACT,cf.build_preview(bad,(c,),(a,),r).state)
        bad=replace(s,tracking_plan=cf.TrackingPlan({"campaign_id":"{not_supported}"})); self.assertEqual(cf.PreviewState.BLOCKED_TRACKING_CONTRACT,cf.build_preview(bad,(c,),(a,),r).state)
        collision=replace(s,tracking_plan=cf.TrackingPlan({"campaign_id":"{campaign_id}","ad_id":"{campaign_id}"})); self.assertIn("tracking_dynamic_collision",cf.build_preview(collision,(c,),(a,),r).errors)
    def test_provider_group_and_strategy_fail_closed(self):
        r,s,c,a=fixture_parts(); mismatch=replace(s,ad_groups=(replace(s.ad_groups[0],group_type="performance"),))
        self.assertEqual(cf.PreviewState.BLOCKED_PROVIDER_CAPABILITY,cf.build_preview(mismatch,(c,),(a,),r).state)
        invalid=replace(s,strategy_kind="maximum_profit"); self.assertEqual(cf.PreviewState.BLOCKED_PROVIDER_CAPABILITY,cf.build_preview(invalid,(c,),(a,),r).state)
        unknown=replace(s,strategy_parameters={"winner_score":1}); self.assertEqual(cf.PreviewState.BLOCKED_PROVIDER_CAPABILITY,cf.build_preview(unknown,(c,),(a,),r).state)
    def test_budget_is_inert_and_governor_required(self):
        r,s,c,a=fixture_parts(); p=cf.build_preview(s,(c,),(a,),r)
        self.assertFalse(p.provider_write_allowed); self.assertTrue(p.budget_proposal["requires_budget_governor"])
        unsafe=replace(s,budget_request=replace(s.budget_request,requires_budget_governor=False)); self.assertEqual(cf.PreviewState.BLOCKED_BUDGET_GOVERNOR_REQUIRED,cf.build_preview(unsafe,(c,),(a,),r).state)
    def test_creative_fields_limits_duplicates_and_identity(self):
        r,s,c,a=fixture_parts(); self.assertEqual(c.identity,replace(c).identity)
        missing=replace(c,headline=""); self.assertIn("creative_required_field_missing",cf.build_preview(s,(missing,),(a,),r).errors)
        long=replace(c,headline="x"*57); self.assertIn("creative_provider_limit_exceeded",cf.build_preview(s,(long,),(a,),r).errors)
        self.assertIn("duplicate_creative_identity",cf.build_preview(s,(c,c),(a,),r).errors)
    def test_asset_registry_hash_version_and_transformation(self):
        _,_,_,a=fixture_parts(); reg=cf.AssetRegistry(); self.assertEqual("created",reg.register(a)[0]); self.assertEqual("idempotent",reg.register(a)[0])
        self.assertEqual("rejected",reg.register(replace(a,sha256="c"*64))[0])
        transformed=replace(a,asset_id="asset-2",version=2,replaces_asset_id=a.asset_id,transformation_intent={"transformation_version":"1","kind":"resize"})
        self.assertEqual("created",reg.register(transformed)[0]); self.assertEqual(a.sha256,reg.assets[a.asset_id].sha256)
        self.assertIn("asset_transformation_not_versioned",replace(transformed,asset_id="asset-3",transformation_intent={"kind":"resize"}).errors())
    def test_dependency_order_and_reverse_rollback(self):
        r,s,c,a=fixture_parts(); p=cf.build_preview(s,(c,),(a,),r); by_id={i["intent_id"]:i for i in p.intents}; positions={x:n for n,x in enumerate(p.dependency_order)}
        for item in p.intents:
            for dep in item["dependencies"]: self.assertLess(positions[dep],positions[item["intent_id"]])
        expected=tuple(i["rollback_intent_ref"] for i in reversed(p.intents) if i["rollback_intent_ref"]); self.assertEqual(expected,p.rollback_graph)
        self.assertTrue(all(not i["executable"] for i in p.intents))
    def test_zero_requests_spend_and_allowed_states_only(self):
        p=cf.synthetic_fixture(REGISTRY_PATH,"valid"); self.assertEqual((0,0,False),(p.provider_requests,p.advertising_spend,p.provider_write_allowed))
        self.assertIn(p.state,cf.ALLOWED_STATES); self.assertNotIn(p.state.value,{"EXECUTED","LAUNCHED","SUBMITTED"})
    def test_required_invalid_fixture_states(self):
        self.assertEqual(cf.PreviewState.BLOCKED_MISSING_CONTENT_ID,cf.synthetic_fixture(REGISTRY_PATH,"missing-content").state)
        self.assertEqual(cf.PreviewState.BLOCKED_TRACKING_CONTRACT,cf.synthetic_fixture(REGISTRY_PATH,"invalid-tracking").state)
        self.assertEqual(cf.PreviewState.BLOCKED_PROVIDER_CAPABILITY,cf.synthetic_fixture(REGISTRY_PATH,"invalid-capability").state)
    def test_no_transport_credentials_or_executable_write_functions(self):
        source=inspect.getsource(cf); self.assertNotIn("urllib",source); self.assertNotIn("requests.",source); self.assertNotIn("oauth",source.lower()); self.assertNotIn("token",source.lower())
        forbidden={"add","update","delete","suspend","resume","moderate","submit","launch","execute","upload"}
        functions={name for name,value in vars(cf).items() if inspect.isfunction(value)}; self.assertFalse(functions & forbidden)
    def test_no_private_ranking_logic_in_public_module(self):
        source=inspect.getsource(cf).lower();
        for term in ("profit_score","winner_selection","ranking_weight","learned_threshold","capital_allocation"): self.assertNotIn(term,source)

if __name__ == "__main__": unittest.main()
