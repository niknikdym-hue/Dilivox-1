# DILIVOX — EKSAMIO PATTERN ADOPTION FOR ADAPTIVE FUNNEL

Status: OWNER-APPROVED IMPLEMENTATION CONSTRAINT
Date: 2026-09-11
Repository: `niknikdym-hue/Dilivox-1`
Branch: `profit-engine`
Authority: `profit-engine/PROFIT_ENGINE_AUTHORITY.md`
Applies to: Adaptive Funnel W0-W2 and later extensions unless superseded by an explicit Owner decision.

## 1. PURPOSE

DILIVOX may reuse implementation ideas proven useful in Eksamio, but must not copy Eksamio's product complexity.

The adoption rule is:

> Borrow the minimum mechanism that improves measurement, routing, auditability or resilience; do not import educational SaaS infrastructure that has no demonstrated profit role for DILIVOX.

This document records exactly what is approved to borrow and what is explicitly excluded.

## 2. OWNER-APPROVED PATTERNS TO ADOPT

### E-001 — Event Truth / observation before inference — APPROVED

Record a small append-only first-party event stream for facts that the site actually observed. Do not write conclusions such as “this reader is valuable” as if they were raw facts.

Minimum event envelope for the first implementation:
- `event_id`;
- `session_id`;
- `content_id`;
- `content_version` where available;
- `event_type`;
- `decision_id` where the event follows an adaptive decision;
- `experiment_id` where applicable;
- `traffic_source` / acquisition join reference where permitted;
- `occurred_at_client`;
- `received_at_server` or trusted collector timestamp.

Initial event vocabulary should remain small. The required first set is:
- `STORY_OPEN`;
- `STORY_PROGRESS_75` where reliable;
- `STORY_COMPLETE`;
- `RECOMMENDATION_SHOWN`;
- `RECOMMENDATION_CLICKED`;
- `NEXT_STORY_OPEN`;
- `RETURN_VISIT`;
- `SERIES_CONTINUE`.

Do not create a large analytics ontology before the first economic baseline.

### E-002 — Browser signals are not money truth — APPROVED

Client/browser code may report behavioral signals only.

Browser code must not authoritatively declare:
- YAN/RSYA revenue;
- Direct spend;
- K5;
- profit;
- provider reconciliation status;
- any server/provider accounting fact.

Money truth must come from admitted provider/server sources and be joined by Profit Engine.

The browser bridge should use an allowlist of event names and an allowlist of safe parameter keys. Unknown fields must be dropped rather than forwarded blindly.

### E-003 — VisitorStateLite, one lightweight state owner — APPROVED

DILIVOX must not create several competing reader profiles across browser code, Metrika and backend services.

The first adaptive state is intentionally small:
- `session_id`;
- current story/content id;
- recently seen story ids;
- current cluster/genre family when known;
- series progress when known;
- stories opened/completed in current session;
- last `decision_id`;
- last decision outcome;
- returning-visitor flag where legally/technically valid;
- traffic-source class / acquisition reference where available.

No psychological profile, personality inference or large AI-generated reader dossier is allowed in W0-W2.

Persist only what is needed to prove routing value. Long-term individual persistence is not mandatory for the first funnel.

### E-004 — Formal NextContentDecision contract — APPROVED

The next-content choice must be a versioned, inspectable decision object, not an opaque AI sentence.

Minimum contract:
- `decision_id`;
- `session_id`;
- `current_content_id`;
- `action_type`;
- `selected_content_id`;
- `candidate_content_ids`;
- `reason_codes`;
- `policy_version`;
- `experiment_id` where applicable;
- `visitor_state_watermark` or equivalent state revision;
- `created_at`;
- `expires_at` when needed.

Initial allowed action types:
- `CONTINUE_SERIES`;
- `SHOW_SIMILAR_STORY`;
- `SHOW_DIFFERENT_CLUSTER`;
- `SHOW_SHORTER_STORY`;
- `SHOW_HIGH_COMPLETION_STORY`;
- `SHOW_HIGH_RETURN_PATH`;
- `RESTORE_PREVIOUS_SESSION`;
- `STATIC_EDITORIAL_FALLBACK`.

Reason codes must be machine-readable and small, for example:
- `SERIES_NEXT_AVAILABLE`;
- `SAME_CLUSTER_MATCH`;
- `RECENTLY_SEEN_EXCLUDED`;
- `HIGH_COMPLETION_PRIOR`;
- `HIGH_RETURN_PRIOR`;
- `SHORT_SESSION_BIAS`;
- `CONTROL_VARIANT`;
- `DATA_UNCERTAIN_FALLBACK`.

The first production policy is rule/statistical, not LLM-dependent.

### E-005 — Decision outcome loop — APPROVED

Every adaptive decision must be evaluable separately from the raw reading event stream.

Minimum outcome vocabulary:
- `SHOWN`;
- `CLICKED`;
- `OPENED`;
- `COMPLETED`;
- `ABANDONED`.

Where attribution is valid, the decision may later be joined to:
- subsequent stories/session;
- return visit;
- attributable monetization value;
- incremental ARPU versus control;
- Feature ROI.

An adaptive route is not considered successful merely because it was clicked. Economic evidence remains the final scale criterion.

### E-006 — Fail-closed routing with static fallback — APPROVED

Adaptive routing must never become a single point of failure for reading.

If any of the following is true:
- routing service unavailable;
- state invalid/stale;
- candidate set empty;
- policy version unsupported;
- money/reconciliation data not trustworthy;
- experiment configuration invalid;

then the site must fall back to a normal editorial/static recommendation path.

The reader should still be able to continue using DILIVOX.

Profit-aware routing must be disabled when monetary truth is stale or materially unreconciled. Safe editorial routing may continue.

A global kill switch for Adaptive Funnel is mandatory before production experiments.

### E-007 — Minimal Owner Console pattern — APPROVED

Borrow Eksamio's principle of a compact, read-only first owner screen rather than a large BI dashboard.

First DILIVOX owner screen should prioritize no more than the following headline measures:
1. Direct spend;
2. YAN/RSYA attributable revenue;
3. K5;
4. YAN ARPU/RPV per acquired visitor;
5. stories per session;
6. next-story continuation rate.

Below the headline layer:
- one reader funnel: `visit -> meaningful read -> completion -> next story -> return`;
- one compact table by genre/cluster/series and traffic source;
- one recent trend view;
- maximum three high-priority alerts.

Useful initial alerts:
- money sources do not reconcile / data stale;
- paid traffic is below economic guardrail;
- a new routing variant reduces ARPU/value versus control.

The console starts read-only. It must not become a second control plane until there is a demonstrated need.

## 3. EXPLICITLY NOT ADOPTED FROM EKSAMIO

The following Eksamio mechanisms are not justified for the first DILIVOX Adaptive Funnel and must not be imported merely because code/patterns already exist there:
- PEIS learner model;
- registered learner identity architecture;
- mandatory login/registration for reading;
- PostgreSQL per-reader canonical educational history as a launch prerequisite;
- Tutor lifecycle;
- voice STT/TTS;
- educational mastery/evidence semantics;
- entitlement/payment runtime;
- large semantic authority machinery;
- multiple live AI providers with automatic failover;
- SSE/WebSocket/realtime agent infrastructure;
- heavyweight individual profile/history APIs;
- AI personality/psychological reader profiling;
- a second owner/task database duplicating GitHub or Profit Engine truth.

Any later proposal to add one of these classes must pass the normal profit/necessity gates rather than inherit approval from Eksamio.

## 4. W0-W2 IMPLEMENTATION MAPPING

### W0 — Measurement truth on the current 50 stories

Goal: create trustworthy baseline facts before adaptive logic.

Implement/verify:
- event allowlist and parameter allowlist;
- `STORY_OPEN`, `STORY_PROGRESS_75`, `STORY_COMPLETE`, recommendation and next-story events;
- stable content ids from the existing content registry;
- session/experiment identity without building a registered-user system;
- provider-side money truth remains separate from browser signals;
- reconciliation status blocks profit-aware conclusions when stale/conflicted.

Exit criteria:
- event flow verified on real DILIVOX pages;
- no duplicate/obviously inflated key events;
- behavior can be joined to story/cluster and traffic source;
- YAN revenue and Direct spend remain provider-sourced;
- baseline can report completion, continuation, stories/session, returns, ARPU/RPV and K5 without inventing missing data.

### W1 — Static control + NextContentDecision contract

Goal: make routing measurable before making it “smart”.

Implement:
- `VisitorStateLite`;
- candidate generator over the current content registry;
- `NextContentDecision` schema;
- simple static/editorial control route;
- rule-based treatment route;
- decision outcome events;
- policy versioning;
- global kill switch;
- automatic static fallback.

The first rules should be cheap and transparent, for example:
1. exclude recently seen content;
2. prefer explicit next item in a series;
3. otherwise prefer same-cluster high-completion candidates;
4. keep a bounded exploration candidate;
5. fall back to editorial/static list if evidence is weak.

No real-time LLM is permitted in W1.

Exit criteria:
- every recommendation can be traced to `decision_id` + reason code + policy version;
- a failed adaptive service cannot break reading;
- control and treatment are distinguishable;
- the outcome of each recommendation is measurable.

### W2 — Profit-linked rule-based funnel experiment

Goal: prove whether the adaptive layer creates money, not merely clicks.

Implement:
- stable control/treatment assignment;
- join decision outcomes to aggregate/reconciled monetization windows where valid;
- compare next-story rate, stories/session, return and ARPU/RPV;
- calculate incremental revenue and full feature cost;
- calculate `FEATURE_ROI`;
- stop/hold/scale recommendation for the feature.

Scale gate remains:

`FEATURE_ROI >= 3.0`

Engagement lift without economic lift is insufficient.

AI remains OFF in the default W2 path.

## 5. DEVELOPMENT TOOLING BOUNDARY

Codex/OpenAI API may be used to develop, test and review these components under `CODEX_DEVELOPMENT_ONLY_POLICY.md`.

Codex is not part of visitor routing, monetization decisions or production DILIVOX runtime.

## 6. CANONICAL FIRST ADAPTIVE LOOP

The approved lightweight architecture is:

`DILIVOX page`
`-> allowlisted behavior event`
`-> VisitorStateLite`
`-> candidate generator`
`-> NextContentDecision`
`-> transparent rule policy`
`-> next-story UI`
`-> outcome event`
`-> Metrika/YAN/Direct accounting join`
`-> Profit Engine`
`-> KEEP / HOLD / KILL / SCALE recommendation`

Fallback:

`adaptive unavailable or data unsafe -> STATIC_EDITORIAL_FALLBACK`

AI is not required for this loop.

## 7. ACCEPTANCE PRINCIPLE

The Eksamio-derived patterns are approved because they reduce ambiguity and failure risk without materially increasing variable production cost.

They do not weaken any existing DILIVOX rule:
- K5 target remains;
- Feature Profit Gate remains;
- content scale gates remain;
- compliance constraints remain;
- provider reconciliation remains mandatory for money truth;
- AI remains optional and separately profit-gated.

This file must be read together with `PROFIT_ENGINE_AUTHORITY.md` and `ADAPTIVE_FUNNEL_IMPLEMENTATION_PLAN.md` before implementing Adaptive Funnel W0-W2.