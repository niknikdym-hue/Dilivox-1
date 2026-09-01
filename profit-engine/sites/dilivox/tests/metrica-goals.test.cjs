const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');

const source = fs.readFileSync(path.join(__dirname, '..', 'tilda', 'dilivox-metrica-goals-v1.js'), 'utf8');
const prepare = fs.readFileSync(path.join(__dirname, '..', '..', '..', 'scripts', 'prepare-dilivox-tilda-production-head.sh'), 'utf8');

function storage(initial = {}) {
  const map = new Map(Object.entries(initial));
  return { getItem(k) { return map.has(k) ? map.get(k) : null; }, setItem(k,v) { map.set(k,String(v)); } };
}

function fixture({ returning = false } = {}) {
  const calls = [], docHandlers = {}, addCounts = {};
  const reveal = { hidden: false, getAttribute() { return null; } };
  const proof = { hidden: false, getAttribute() { return null; } };
  const root = { querySelector(sel) { return sel.includes('proof') || sel.includes('facts') ? proof : reveal; } };
  const choice = { closest(sel) { return sel === '[data-dv-choice]' ? choice : root; } };
  const document = {
    readyState: 'loading',
    addEventListener(type, fn) { docHandlers[type] = fn; addCounts[type] = (addCounts[type] || 0) + 1; }
  };
  const rawYm = function(counter, method, identifier) { calls.push([counter, method, identifier]); };
  rawYm.a = [];
  rawYm.l = 12345;
  const window = {
    document, ym: rawYm,
    localStorage: storage(returning ? {'pe_dilivox_goal_v1:visitor_seen':'1'} : {}),
    sessionStorage: storage(), setTimeout(fn) { fn(); }
  };
  const context = vm.createContext({ window, document, setTimeout: window.setTimeout, Date });
  function load() {
    vm.runInContext(source, context);
    if (docHandlers.DOMContentLoaded) {
      const ready = docHandlers.DOMContentLoaded;
      delete docHandlers.DOMContentLoaded;
      ready();
    }
  }
  function trustedChoice() { docHandlers.click({ isTrusted:true, target:choice }); }
  return { window, calls, addCounts, load, trustedChoice };
}

test('bridge never initializes counter or contains provider/network writes', () => {
  assert.ok(!source.includes("'init'"));
  assert.ok(!source.includes('Ya.Context'));
  assert.ok(!source.includes('fetch('));
  assert.ok(!source.includes('XMLHttpRequest'));
  assert.ok(!source.includes('metrika:write'));
});

test('legacy authoritative signals normalize to one canonical reachGoal', () => {
  const f = fixture(); f.load();
  f.window.ym(110349067, 'reachGoal', 'dv_story_read_75');
  f.window.ym(110349067, 'reachGoal', 'dv_story_read_75');
  f.window.ym(110349067, 'reachGoal', 'dv_next_story_click');
  f.window.ym(110349067, 'reachGoal', 'dv_next_story_click');
  assert.deepEqual(f.calls.map(x => x[2]), ['pe_story_progress_75','pe_next_story_clicked']);
});

test('choice and revealed completion use existing transition and dispatch once', () => {
  const f = fixture(); f.load(); f.trustedChoice(); f.trustedChoice();
  const ids = f.calls.map(x => x[2]);
  assert.equal(ids.filter(x => x === 'pe_version_selected').length, 1);
  assert.equal(ids.filter(x => x === 'pe_story_completed').length, 1);
});

test('repeated script load installs no second listener or normalizer', () => {
  const f = fixture(); f.load();
  const normalized = f.window.ym; const clickListeners = f.addCounts.click;
  f.load();
  assert.equal(f.window.ym, normalized);
  assert.equal(f.window.ym.l, 12345);
  assert.equal(f.addCounts.click, clickListeners);
  f.window.ym(110349067, 'reachGoal', 'dv_story_read_75');
  assert.equal(f.calls.filter(x => x[2] === 'pe_story_progress_75').length, 1);
});

test('return visit fires once per later session and kill switch blocks dispatch', () => {
  const f = fixture({ returning:true }); f.load(); f.load();
  assert.equal(f.calls.filter(x => x[2] === 'pe_return_visit').length, 1);
  f.window.PROFIT_ENGINE_METRICA_GOALS_KILL = true;
  f.window.ym(110349067, 'reachGoal', 'dv_story_read_75');
  assert.equal(f.calls.filter(x => x[2] === 'pe_story_progress_75').length, 0);
});

test('production package is one bridge and excludes second event controller', () => {
  assert.ok(!prepare.includes('event_js='));
  assert.ok(!prepare.includes('ProfitEngineEvents.install'));
  assert.ok(prepare.includes('existing DILIVOX_SYSTEM_V1'));
  assert.ok(prepare.includes('do not alter YAN blocks or story T123 blocks'));
});
