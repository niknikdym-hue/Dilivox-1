(function (w, d) {
  "use strict";
  var COUNTER_ID = 110349067;
  var INSTALL_KEY = "__DILIVOX_CANONICAL_METRICA_V2__";
  var PREFIX = "pe_dilivox_goal_v1:";
  var LEGACY_MAP = Object.freeze({
    dv_story_read_75: "pe_story_progress_75",
    dv_next_story_click: "pe_next_story_clicked"
  });
  if (w[INSTALL_KEY] && w[INSTALL_KEY].installed) {
    w.ProfitEngineMetricaGoals = w[INSTALL_KEY].api;
    return;
  }
  var state = { installed: true, sent: Object.create(null), originalYm: null, api: null };
  w[INSTALL_KEY] = state;
  function killed() { return w.PROFIT_ENGINE_METRICA_GOALS_KILL === true; }
  function dispatch(identifier) {
    if (killed() || state.sent[identifier] || typeof state.originalYm !== "function") return false;
    try {
      state.originalYm.call(w, COUNTER_ID, "reachGoal", identifier);
      state.sent[identifier] = true;
      return true;
    } catch (_) { return false; }
  }
  function installNormalizer() {
    if (typeof w.ym !== "function") return false;
    if (w.ym.__dilivoxCanonicalNormalizer === true) return true;
    state.originalYm = w.ym;
    function normalizedYm(counter, method, identifier) {
      if (counter === COUNTER_ID && method === "reachGoal" && LEGACY_MAP[identifier]) {
        dispatch(LEGACY_MAP[identifier]);
        return;
      }
      return state.originalYm.apply(this, arguments);
    }
    normalizedYm.__dilivoxCanonicalNormalizer = true;
    Object.keys(state.originalYm).forEach(function (key) {
      try { normalizedYm[key] = state.originalYm[key]; } catch (_) {}
    });
    w.ym = normalizedYm;
    return true;
  }
  function safeStorage(storage, method, key, value) {
    try { return method === "get" ? storage.getItem(key) : storage.setItem(key, value); }
    catch (_) { return null; }
  }
  function markReturnVisit() {
    var durableKey = PREFIX + "visitor_seen";
    var sessionKey = PREFIX + "session_seen";
    if (safeStorage(w.sessionStorage, "get", sessionKey)) return;
    var seenBefore = safeStorage(w.localStorage, "get", durableKey);
    safeStorage(w.sessionStorage, "set", sessionKey, "1");
    safeStorage(w.localStorage, "set", durableKey, String(Date.now()));
    if (seenBefore) dispatch("pe_return_visit");
  }
  function wireAuthoritativeChoiceTransition() {
    d.addEventListener("click", function (event) {
      if (killed() || !event.isTrusted) return;
      try {
        var choice = event.target.closest && event.target.closest("[data-dv-choice]");
        if (!choice) return;
        dispatch("pe_version_selected");
        var root = choice.closest && choice.closest('[data-dv-page="story"], main.dv-story, [data-dv-choice-group]');
        var reveal = root && root.querySelector && root.querySelector("[data-dv-final], [data-dv-reveal]");
        var proof = root && root.querySelector && root.querySelector("[data-dv-proof], [data-dv-facts]");
        if (reveal && proof && !reveal.hidden && reveal.getAttribute("aria-hidden") !== "true" &&
            !proof.hidden && proof.getAttribute("aria-hidden") !== "true") dispatch("pe_story_completed");
      } catch (_) {}
    }, false);
  }
  function init() {
    if (killed()) return;
    installNormalizer();
    markReturnVisit();
    wireAuthoritativeChoiceTransition();
  }
  var api = Object.freeze({
    version: "2.0-existing-ux-normalizer", counterId: COUNTER_ID,
    dispatch: dispatch, reach: dispatch, installNormalizer: installNormalizer, legacyMap: LEGACY_MAP,
    killSwitchName: "PROFIT_ENGINE_METRICA_GOALS_KILL"
  });
  state.api = api;
  w.ProfitEngineMetricaGoals = api;
  if (d.readyState === "loading") d.addEventListener("DOMContentLoaded", init, { once: true });
  else setTimeout(init, 0);
})(window, document);
