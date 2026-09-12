# TASK 017 — NEXT CONTENT DECISION CORE

Status: READY FOR BOUNDED DEVELOPMENT
Execution package: `AF-2`
Executor: Codex development-only under Central Brain acceptance
Depends on: Task 016 content map
May run before AF-0 live acceptance: YES, offline/deterministic only

## Objective

Build the first production-shaped but offline-testable Adaptive Funnel decision core: one lightweight reader/session state, deterministic candidate generation, a versioned `NextContentDecision` contract, transparent policy v0.1, and guaranteed static fallback.

## Required deliverables

1. `VisitorStateLite` schema/contract.
2. State reducer over allowlisted behavior events.
3. Candidate generator using Task 016 content graph.
4. `NextContentDecision` schema/contract.
5. Bounded action/reason-code vocabulary.
6. Deterministic policy v0.1.
7. Static/editorial control adapter.
8. Global kill-switch contract.
9. `STATIC_EDITORIAL_FALLBACK` path.
10. Offline unit/contract tests and CI gate.

## VisitorStateLite minimum fields

- `session_id`;
- `current_content_id`;
- recent content IDs;
- current cluster/genre family when known;
- series progress when known;
- stories opened/completed this session;
- last decision ID;
- last decision outcome;
- returning-visitor flag where valid;
- traffic-source/acquisition class where available;
- state revision/watermark.

Forbidden in AF-2:
- psychological/personality profile;
- large free-form AI dossier;
- mandatory registered-reader identity;
- email/phone/name;
- opaque model embeddings stored as the only state explanation.

## NextContentDecision minimum fields

- `decision_id`;
- `session_id`;
- `current_content_id`;
- `action_type`;
- `selected_content_id`;
- `candidate_content_ids`;
- `reason_codes`;
- `policy_version`;
- `experiment_id` when applicable;
- `visitor_state_watermark`;
- `created_at`;
- `expires_at` when needed.

## Initial allowed action types

- `CONTINUE_SERIES`;
- `SHOW_SIMILAR_STORY`;
- `SHOW_DIFFERENT_CLUSTER`;
- `SHOW_SHORTER_STORY`;
- `SHOW_HIGH_COMPLETION_STORY`;
- `SHOW_HIGH_RETURN_PATH`;
- `RESTORE_PREVIOUS_SESSION`;
- `STATIC_EDITORIAL_FALLBACK`.

## Initial reason codes

At minimum:
- `SERIES_NEXT_AVAILABLE`;
- `SAME_CLUSTER_MATCH`;
- `RECENTLY_SEEN_EXCLUDED`;
- `HIGH_COMPLETION_PRIOR`;
- `HIGH_RETURN_PRIOR`;
- `SHORT_SESSION_BIAS`;
- `CONTROL_VARIANT`;
- `DATA_UNCERTAIN_FALLBACK`;
- `KILL_SWITCH_FALLBACK`;
- `NO_ELIGIBLE_CANDIDATE_FALLBACK`.

## Policy v0.1 order

1. Validate current state/content/metadata versions.
2. Exclude current, invalid and recently seen items.
3. If kill switch is active -> static fallback.
4. If an explicit next-in-series item is valid -> prefer it.
5. Else prefer same-cluster eligible candidates using only admitted baseline signals.
6. Preserve one bounded exploration candidate where possible.
7. If money/reconciliation evidence is required for a profit-aware reason but is stale/untrusted -> ignore that profit-aware signal.
8. If candidates/evidence are unsafe or empty -> static fallback.

## Determinism / explainability

Given identical:
- state;
- catalog metadata version;
- policy version;
- experiment assignment;
- admitted aggregate signal snapshot;

the decision must be reproducible.

Each decision must explain itself through bounded reason codes; no opaque natural-language AI rationale is required.

## Failure behavior

Adaptive logic must fail safe:
- invalid state -> static fallback;
- unsupported metadata/policy version -> static fallback;
- empty candidate set -> static fallback;
- stale/unreconciled money -> disable profit-aware ranking, not reading;
- internal exception -> static fallback where possible and auditable failure state.

Public reading must not depend on Adaptive Funnel availability.

## Out of scope

- production experiment traffic;
- real-time AI/LLM calls;
- provider writes;
- Tilda publication;
- content generation;
- registered-reader account system;
- direct mutation of `DILIVOX_SYSTEM_V1` behavior beyond a later accepted adapter boundary.

## Acceptance criteria

1. Task 016 metadata is the only content identity source.
2. Every decision validates against the formal schema.
3. Every selected content ID is in the candidate set and canonical registry.
4. Deterministic fixtures reproduce exact decisions/reason codes.
5. Kill switch always forces safe fallback.
6. Invalid/stale state cannot break reading path.
7. Profit-aware signals are ignored when money evidence is not trustworthy.
8. No AI/network/provider dependency exists in the decision core.
9. No browser money truth is accepted.
10. Tests/CI pass offline.

Terminal state:
`ADAPTIVE_AF2_ROUTING_CORE_READY`.
