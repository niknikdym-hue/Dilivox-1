const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');

const source = fs.readFileSync(
  path.join(__dirname, '..', 'tilda', 'dilivox-metrica-goals-v1.js'),
  'utf8'
);

function storage(initial = {}) {
  const map = new Map(Object.entries(initial));
  return {
    getItem(k) { return map.has(k) ? map.get(k) : null; },
    setItem(k, v) { map.set(k, String(v)); },
  };
}

function fixture({ returning = false } = {}) {
  const calls = [];
  const handlers = {};
  const docHandlers = {};
  const reveal = { hidden: false, getAttribute() { return null; } };
  const text = { getBoundingClientRect() { return { top: -800, height: 1000 }; } };
  let observerCallback = null;
  const document = {
    readyState: 'loading',
    documentElement: { clientHeight: 800 },
    querySelector(sel) { return sel === '[data-dv-story-text]' ? text : null; },
    querySelectorAll(sel) { return sel === '[data-dv-reveal]' ? [reveal] : []; },
    addEventListener(type, fn) { docHandlers[type] = fn; },
  };
  class IntersectionObserver {
    constructor(fn) { observerCallback = fn; }
    observe() {}
  }
  const window = {
    document,
    innerHeight: 800,
    localStorage: storage(returning ? {'pe_dilivox_goal_v1:visitor_seen': '1'} : {}),
    sessionStorage: storage(),
    IntersectionObserver,
    addEventListener(type, fn) { handlers[type] = fn; },
    ym(counter, method, identifier) { calls.push([counter, method, identifier]); },
    setTimeout(fn) { fn(); },
  };
  const context = vm.createContext({ window, document, setTimeout: window.setTimeout });
  vm.runInContext(source, context);
  docHandlers.DOMContentLoaded();
  return { window, document, handlers, docHandlers, reveal, calls, observer: () => observerCallback };
}

test('bridge is bounded to exact five canonical goal identifiers and no ad/network mutation', () => {
  for (const id of [
    'pe_story_progress_75',
    'pe_version_selected',
    'pe_story_completed',
    'pe_next_story_clicked',
    'pe_return_visit',
  ]) assert.ok(source.includes(id));
  assert.ok(source.includes('PROFIT_ENGINE_METRICA_GOALS_KILL'));
  assert.ok(!source.includes('Ya.Context'));
  assert.ok(!source.includes('data-dv-ad-block'));
  assert.ok(!source.includes('fetch('));
  assert.ok(!source.includes('XMLHttpRequest'));
});

test('progress, trusted choice, next-story and completion each reach once', () => {
  const f = fixture();
  f.handlers.scroll();
  f.handlers.scroll();
  f.docHandlers.click({
    isTrusted: true,
    target: { closest(sel) {
      if (sel === '[data-dv-choice]') return {};
      if (sel === '[data-dv-goal="next-story"]') return {};
      return null;
    } },
  });
  f.docHandlers.click({
    isTrusted: true,
    target: { closest(sel) {
      if (sel === '[data-dv-choice]') return {};
      if (sel === '[data-dv-goal="next-story"]') return {};
      return null;
    } },
  });
  f.observer()([{ target: f.reveal, intersectionRatio: 0.8 }]);
  f.observer()([{ target: f.reveal, intersectionRatio: 0.8 }]);
  const ids = f.calls.map(x => x[2]);
  assert.equal(ids.filter(x => x === 'pe_story_progress_75').length, 1);
  assert.equal(ids.filter(x => x === 'pe_version_selected').length, 1);
  assert.equal(ids.filter(x => x === 'pe_next_story_clicked').length, 1);
  assert.equal(ids.filter(x => x === 'pe_story_completed').length, 1);
  assert.ok(f.calls.every(x => x[0] === 110349067 && x[1] === 'reachGoal'));
});

test('return visit fires once per later browser session and kill switch blocks all goals', () => {
  const returning = fixture({ returning: true });
  assert.equal(returning.calls.filter(x => x[2] === 'pe_return_visit').length, 1);

  const killed = fixture();
  killed.window.PROFIT_ENGINE_METRICA_GOALS_KILL = true;
  const before = killed.calls.length;
  killed.window.ProfitEngineMetricaGoals.reach('pe_story_completed');
  assert.equal(killed.calls.length, before);
});
