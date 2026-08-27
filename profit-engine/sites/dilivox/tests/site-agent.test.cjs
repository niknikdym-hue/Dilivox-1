const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const { pathToFileURL } = require("node:url");

const root = path.resolve(__dirname, "..");
const api = require(path.join(root, "tilda/dilivox-site-agent-task005.js"));
const content = require(path.join(root, "content-registry.json"));
const placements = require(path.join(root, "placement-registry.json"));
const inventory = require(path.join(root, "source-hooks-inventory.json"));

class MemoryStorage {
  constructor(initial={}) { this.values = {...initial}; }
  getItem(key) { return Object.hasOwn(this.values,key) ? this.values[key] : null; }
  setItem(key,value) { this.values[key]=String(value); }
  removeItem(key) { delete this.values[key]; }
}
class BrokenStorage { getItem(){throw Error("disabled");} setItem(){throw Error("disabled");} removeItem(){} }
function doc({slug=null,page=null,placements=[]}={}) {
  return {
    querySelector(selector) {
      if(selector === "[data-dv-story-slug]" && slug) return {getAttribute:()=>slug};
      if(selector === "[data-dv-page]" && page) return {getAttribute:()=>page};
      return null;
    },
    querySelectorAll(selector) { return selector === "[data-dv-ad-block]" ? placements.map(id=>({getAttribute:()=>id})) : []; }
  };
}
function win(url, document, storage={}) {
  return {URL, crypto:globalThis.crypto, location:new URL(url), document,
    sessionStorage:storage.session || new MemoryStorage(), localStorage:storage.local || new MemoryStorage()};
}

test("registry IDs and active URLs are unique and known routes resolve", async () => {
  const mod = await import(pathToFileURL(path.join(root,"validate-registries.mjs")));
  assert.equal(mod.validateContentRegistry(content).items,61);
  assert.ok(api.resolveContent(doc({page:"home"}),new URL("https://dilivox.ru/")).content_id);
  assert.ok(api.resolveContent(doc({slug:"pechat-na-bagrovom-voske"}),new URL("https://dilivox.ru/changed/")).content_id);
});

test("mutable URL/title/slug metadata preserves assigned identity", async () => {
  const mod = await import(pathToFileURL(path.join(root,"validate-registries.mjs")));
  const next=structuredClone(content); next.items[5].canonical_url="/renamed/"; next.items[5].current_slug="renamed"; next.items[5].title="Changed";
  assert.equal(mod.assertIdentityPreserved(content,next),true);
  next.items[5].content_id=crypto.randomUUID();
  assert.throws(()=>mod.assertIdentityPreserved(content,next));
});

test("paid attribution captures allowlist only and truncates safely", () => {
  const w=win("https://dilivox.ru/?yclid=abc&utm_source=yandex&utm_medium=cpc&utm_campaign="+"x".repeat(400)+"&email=a@b.test&phone=123&name=Eve&evil=1",doc({page:"home"}));
  const agent=api.createDilivoxSiteAgent(w,{now:()=>1000});
  assert.equal(agent.attribution.params.yclid,"abc");
  assert.equal(agent.attribution.params.utm_campaign.length,256);
  for(const key of ["email","phone","name","evil"]) assert.equal(agent.attribution.params[key],undefined);
});

test("attribution survives organic internal navigation and paid supersedes", () => {
  const storage={session:new MemoryStorage(),local:new MemoryStorage()};
  const first=api.createDilivoxSiteAgent(win("https://dilivox.ru/?yclid=one",doc({page:"home"}),storage),{now:()=>1000,persistAttribution:true});
  const organic=api.createDilivoxSiteAgent(win("https://dilivox.ru/istorii/",doc({page:"stories-list"}),storage),{now:()=>2000,persistAttribution:true});
  assert.equal(organic.attribution.acquisition_id,first.attribution.acquisition_id);
  const second=api.createDilivoxSiteAgent(win("https://dilivox.ru/istorii/?yclid=two",doc({page:"stories-list"}),storage),{now:()=>3000,persistAttribution:true});
  assert.notEqual(second.attribution.acquisition_id,first.attribution.acquisition_id);
  assert.equal(second.attribution.params.yclid,"two");
});

test("TTL is capped, optional return identity is privacy-gated", () => {
  const storage={session:new MemoryStorage(),local:new MemoryStorage()};
  const w=win("https://dilivox.ru/?yclid=one",doc({page:"home"}),storage);
  const agent=api.createDilivoxSiteAgent(w,{now:()=>1000,attributionTtlMs:99999999999,enableReturnId:true});
  assert.equal(agent.attribution.expires_at,1000+api.MAX_TTL_MS);
  assert.equal(agent.getContext().return_ref,null);
  const approved=api.createDilivoxSiteAgent(w,{now:()=>2000,enableReturnId:true,privacyReviewApproved:true});
  assert.ok(approved.getContext().return_ref);
});

test("disabled or corrupt storage fails safe", () => {
  const corrupt=new MemoryStorage({pe_acquisition_v1:"{broken"});
  const a=api.createDilivoxSiteAgent(win("https://dilivox.ru/",doc({page:"home"}),{session:corrupt,local:new BrokenStorage()}),{now:()=>1000});
  assert.equal(a.attribution,null); assert.equal(a.health.ok,true);
  const b=api.createDilivoxSiteAgent(win("https://dilivox.ru/",doc({page:"home"}),{session:new BrokenStorage(),local:new BrokenStorage()}),{now:()=>1000});
  assert.ok(b.getContext().session_ref);
});

test("experiment identity validates and kill switches win", () => {
  const base=win("https://dilivox.ru/",doc({page:"home"}));
  assert.equal(api.createDilivoxSiteAgent(base,{experiment_id:"exp-1",variant_id:"v:a"}).experiment.variant_id,"v:a");
  assert.equal(api.createDilivoxSiteAgent(base,{experiment_id:"bad space",variant_id:"v"}).experiment,null);
  assert.equal(api.createDilivoxSiteAgent(base,{experiment_id:"exp-1",variant_id:"v",experimentKillSwitches:["exp-1"]}).experiment,null);
  assert.equal(api.createDilivoxSiteAgent(base,{globalKillSwitch:true}).enabled,false);
});

test("generic SiteAgent factory accepts an isolated adapter contract", () => {
  const adapter={site_id:"fixture-site",resolveContent:()=>({content_id:crypto.randomUUID(),content_type:"fixture"}),placementIds:()=>[]};
  const agent=api.createSiteAgent(win("https://example.test/",doc()),adapter,{now:()=>1000});
  assert.equal(agent.site_id,"fixture-site"); assert.equal(agent.getContext().page_type,"fixture");
});

test("placement registry exactly covers current source inventory", async () => {
  const mod = await import(pathToFileURL(path.join(root,"validate-registries.mjs")));
  assert.deepEqual(mod.validatePlacements(placements,inventory),{source_values:12,active_mappings:12});
  const agent=api.createDilivoxSiteAgent(win("https://dilivox.ru/istorii/",doc({page:"stories-list",placements:["R-A-19563496-3","unknown"]})));
  assert.deepEqual(agent.placements,["R-A-19563496-3"]);
});

test("all story sources and discoverable catalog stories have registry identity", async () => {
  const mod = await import(pathToFileURL(path.join(root,"validate-registries.mjs")));
  assert.deepEqual(mod.validateSourceCoverage(content,inventory),{source_stories:56,discoverable_active:50});
});

test("event context is local-only and code has no dispatch or YAN mutation", () => {
  const source=fs.readFileSync(path.join(root,"tilda/dilivox-site-agent-task005.js"),"utf8");
  for(const forbidden of ["fetch(","XMLHttpRequest","sendBeacon","Ya.Context","renderTo("]) assert.equal(source.includes(forbidden),false);
  const agent=api.createDilivoxSiteAgent(win("https://dilivox.ru/",doc({page:"home"})),{now:()=>1000});
  const event=agent.buildEventContext({destination_content_id:content.items[5].content_id});
  assert.equal(event.event_schema_version,"1.0"); assert.equal(event.destination_content_id,content.items[5].content_id);
});
