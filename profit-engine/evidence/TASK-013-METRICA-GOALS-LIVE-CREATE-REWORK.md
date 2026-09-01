# TASK 013 — METRICA GOALS LIVE CREATE REWORK

Status: REWORKED / LIVE RETRY REQUIRED
Date: 2026-09-01
Site: `dilivox`
Counter: `110349067`

## Live audit result

Owner Mac P0 bootstrap successfully reached the live Metrica goals audit.

Observed provider state:

- management GET: HTTP 200;
- provider goal count: 22;
- canonical expected goals: 5;
- duplicates: 0;
- wrong-type canonical identifiers: 0;
- all five canonical Profit Engine goals were `MISSING` at audit time:
  - `pe_story_progress_75`;
  - `pe_version_selected`;
  - `pe_story_completed`;
  - `pe_next_story_clicked`;
  - `pe_return_visit`.

Therefore the live goal configuration state was correctly classified `REWORK_REQUIRED` before any successful goal creation was proven.

## Failed create attempt

After explicit Owner choice to create only missing goals, the first Metrica POST returned HTTP 400 with provider message:

`Could not read JSON, error in line 1, column 138, path: goal.is_favorite`

No successful goal creation/read-back was established from that attempt.

The failure is not OAuth/counter access: the immediately preceding goals audit returned HTTP 200.

## Root cause / correction

The create runtime had included optional field:

`goal.is_favorite=false`

The live endpoint rejected that member for this request despite the published OpenAPI documentation describing `is_favorite` on goal objects.

Launch runtime now uses a deliberately minimal create payload containing only:

- `name`;
- `type=action`;
- exact `conditions` with the canonical event identifier.

Optional `is_favorite`, `id`, `status`, and `default_price` are omitted unless a future live compatibility proof requires/accepts them.

`Content-Type` is explicit UTF-8 JSON.

Regression tests assert the exact minimal payload and forbid `is_favorite` from reappearing.

## Control panel correction

The Owner requested a Russian operator interface.

The primary local panel surface is now Russian, including system state, campaign state, Metrica goal state, manual Search P0 labels, and locked-write messaging. Technical state codes remain available as secondary diagnostics only.

The installer also now restarts only the existing `profit_engine_runtime.control_panel` process after a runtime upgrade so an in-memory older UI cannot survive a code update.

## Safety

- Direct provider writes: 0;
- campaign/budget/bid mutations: 0;
- failed Metrica request was configuration-only and received HTTP 400;
- no blind retry was made inside the failed run;
- next create attempt remains explicit missing-only + read-back.

## Next gate

Rerun the P0 bootstrap from current `profit-engine`.

Expected path:

1. local runtime mirror updates without full re-clone;
2. Russian panel restarts on fresh code;
3. goals audit again identifies only actually missing canonical goals;
4. Owner explicitly approves `Создать отсутствующие`;
5. minimal payload creates only missing goals;
6. live read-back must reach `PASS` before Task 013 goal configuration is accepted;
7. bootstrap then continues to YAN→Metrica money readiness, live-site instrumentation probe, and Tilda package preparation.
