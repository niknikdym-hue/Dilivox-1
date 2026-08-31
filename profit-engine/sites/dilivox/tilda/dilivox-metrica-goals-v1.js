(function (w, d) {
  "use strict";

  var COUNTER_ID = 110349067;
  var PREFIX = "pe_dilivox_goal_v1:";
  var sent = Object.create(null);

  function killed() {
    return w.PROFIT_ENGINE_METRICA_GOALS_KILL === true;
  }

  function reach(identifier) {
    if (killed() || sent[identifier]) return false;
    if (typeof w.ym !== "function") return false;
    try {
      w.ym(COUNTER_ID, "reachGoal", identifier);
      sent[identifier] = true;
      return true;
    } catch (_) {
      return false;
    }
  }

  function safeStorage(storage, method, key, value) {
    try {
      return method === "get" ? storage.getItem(key) : storage.setItem(key, value);
    } catch (_) {
      return null;
    }
  }

  function markReturnVisit() {
    if (killed()) return;
    var durableKey = PREFIX + "visitor_seen";
    var sessionKey = PREFIX + "session_seen";
    var inSession = safeStorage(w.sessionStorage, "get", sessionKey);
    if (inSession) return;
    var seenBefore = safeStorage(w.localStorage, "get", durableKey);
    safeStorage(w.sessionStorage, "set", sessionKey, "1");
    safeStorage(w.localStorage, "set", durableKey, String(Date.now()));
    if (seenBefore) reach("pe_return_visit");
  }

  function storyProgress75() {
    var text = d.querySelector("[data-dv-story-text]");
    if (!text) return;
    function check() {
      try {
        var rect = text.getBoundingClientRect();
        var vh = w.innerHeight || d.documentElement.clientHeight || 0;
        var ratio = Math.max(0, Math.min(1, (vh - rect.top) / Math.max(rect.height, 1)));
        if (ratio >= 0.75) reach("pe_story_progress_75");
      } catch (_) {}
    }
    w.addEventListener("scroll", check, { passive: true });
    w.addEventListener("resize", check, { passive: true });
    check();
  }

  function wireClicks() {
    d.addEventListener("click", function (event) {
      if (killed() || !event.isTrusted) return;
      try {
        var choice = event.target.closest && event.target.closest("[data-dv-choice]");
        if (choice) reach("pe_version_selected");
        var nav = event.target.closest && event.target.closest('[data-dv-goal="next-story"]');
        if (nav) reach("pe_next_story_clicked");
      } catch (_) {}
    }, true);
  }

  function wireCompletion() {
    var reveals = d.querySelectorAll("[data-dv-reveal]");
    if (!reveals.length || typeof w.IntersectionObserver !== "function") return;
    var observer = new w.IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.intersectionRatio < 0.5) return;
        var node = entry.target;
        var open = !node.hidden && node.getAttribute("aria-hidden") !== "true";
        if (open) reach("pe_story_completed");
      });
    }, { threshold: [0.5] });
    reveals.forEach(function (node) { observer.observe(node); });
  }

  function init() {
    if (killed()) return;
    markReturnVisit();
    storyProgress75();
    wireClicks();
    wireCompletion();
  }

  if (d.readyState === "loading") d.addEventListener("DOMContentLoaded", init, { once: true });
  else setTimeout(init, 0);

  w.ProfitEngineMetricaGoals = Object.freeze({
    version: "1.0",
    counterId: COUNTER_ID,
    reach: reach,
    killSwitchName: "PROFIT_ENGINE_METRICA_GOALS_KILL"
  });
})(window, document);
