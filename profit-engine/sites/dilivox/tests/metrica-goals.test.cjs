const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');

const source = fs.readFileSync(
  path.join(__dirname, '..', 'tilda', 'dilivox-metrika-goals-global-head-after-counter-UPDATED.txt'),
  'utf8'
);
const script = source.match(/<script>\s*([\s\S]*?)<\/script>/)[1];

const oldGoals = [
  'dv_back_to_stories_click', 'dv_home_cards_seen', 'dv_home_final_seen',
  'dv_home_first_story_click', 'dv_home_scroll_50', 'dv_home_scroll_75',
  'dv_home_scroll_90', 'dv_home_story_card_click', 'dv_home_time_30',
  'dv_home_time_60', 'dv_home_to_stories_click', 'dv_next_story_click',
  'dv_prev_story_click', 'dv_stories_filter_', 'dv_stories_format_',
  'dv_stories_list_open', 'dv_story_card_click', 'dv_story_open',
  'dv_story_read_25', 'dv_story_read_50', 'dv_story_read_75',
  'dv_story_read_90', 'dv_story_read_complete', 'dv_story_read_start',
  'dv_story_time_180', 'dv_story_time_60',
];

function storage(initial = {}) {
  const values = new Map(Object.entries(initial));
  return {
    getItem(key) { return values.has(key) ? values.get(key) : null; },
    setItem(key, value) { values.set(key, String(value)); },
  };
}

function returnVisitSession(localStorage) {
  const calls = [];
  let ready;
  const document = {
    readyState: 'loading',
    addEventListener(type, callback) { if (type === 'DOMContentLoaded') ready = callback; },
    querySelector() { return null; },
  };
  const context = {
    window: {}, document, location: { pathname: '/not-a-dilivox-page' },
    localStorage, sessionStorage: storage(),
    ym(counter, method, goal) { calls.push([counter, method, goal]); },
  };
  context.window = context;
  vm.runInNewContext(script, context);
  ready();
  return calls;
}

test('full updated file preserves counter and every legacy goal', () => {
  assert.equal((source.match(/var DILIVOX_COUNTER_ID = 110349067;/g) || []).length, 1);
  assert.equal((source.match(/addEventListener\(/g) || []).length, 11);
  assert.ok(!/ym\s*\([^)]*['"]init['"]/.test(source));
  assert.ok(!/window\.ym\s*=/.test(source));
  for (const goal of oldGoals) assert.ok(source.includes(`'${goal}'`), goal);
});

test('new goals are inserted in the existing authoritative handlers', () => {
  assert.match(source, /if \(percent >= 75\) \{\s*sendGoal\('dv_story_read_75'\);\s*sendGoal\('pe_story_progress_75'\);/);
  assert.match(source, /if \(!options\.restore\) \{[\s\S]*?saveChoice\([\s\S]*?sendGoal\('pe_version_selected'\);\s*sendGoal\('pe_story_completed'\);\s*\}/);
  assert.match(source, /'dv_next_story_click',\s*'pe_next_story_clicked'/);
  assert.doesNotMatch(source, /percent >= 98[^\n]*pe_story_completed/);
  for (const goal of ['pe_story_progress_75', 'pe_version_selected', 'pe_story_completed', 'pe_next_story_clicked', 'pe_return_visit']) {
    assert.ok(source.includes(`'${goal}'`), goal);
  }
});

test('return visit fires only once in each later browser session', () => {
  const local = storage();
  assert.deepEqual(returnVisitSession(local), []);
  assert.deepEqual(returnVisitSession(local), [[110349067, 'reachGoal', 'pe_return_visit']]);

  const sameSessionCalls = [];
  let ready;
  const session = storage();
  const document = {
    readyState: 'loading',
    addEventListener(type, callback) { if (type === 'DOMContentLoaded') ready = callback; },
    querySelector() { return null; },
  };
  const context = {
    window: {}, document, location: { pathname: '/other' },
    localStorage: local, sessionStorage: session,
    ym(counter, method, goal) { sameSessionCalls.push([counter, method, goal]); },
  };
  context.window = context;
  vm.runInNewContext(script, context);
  ready();
  vm.runInNewContext(script, context);
  ready();
  assert.equal(sameSessionCalls.filter(call => call[2] === 'pe_return_visit').length, 1);
});

test('file contains no provider, Direct, YAN or network writes', () => {
  assert.ok(!source.includes('fetch('));
  assert.ok(!source.includes('XMLHttpRequest'));
  assert.ok(!source.includes('Campaigns.add'));
  assert.ok(!source.includes('Campaigns.update'));
  assert.ok(!source.includes('Ya.Context.AdvManager.render'));
});
