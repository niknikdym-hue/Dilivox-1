# TASK 012 — PROVIDER PERMISSION FAIL-CLOSED FIX

Date: 2026-08-29
Status: CENTRAL BRAIN FIX / CI VERIFIED
Scope: Day-12 readiness permission authority boundary

## Finding

The Owner-facing Day-12 CLI had already removed the manual Direct permission flag, and the canonical project state required provider-observed Direct permission with `UNKNOWN => fail closed`.

However, the internal `build_day12_launch_readiness()` API still accepted an optional `direct_permission` argument. When the Direct doctor produced no observable permission, a caller could supply `EDITING` and advance readiness to candidate selection if the remaining diagnostics passed.

That path contradicted the canonical authority model even though the current CLI did not expose it.

## Fix

Implementation:

- `4dd17793283961fe1df99a9cc1ea60e1affc09e9` — remove the manual Direct permission input from the readiness API; readiness now derives permission only from Direct doctor checks and increments the readiness contract to v1.2.
- `2c94fe7575f954c18591ed89a4e4e702e035d410` — update readiness tests so `READING`, `EDITING`, and `UNKNOWN` are provider-observed; add a regression test proving manual override is no longer accepted.
- `b66050fc8dc7b5b42e8b19ebbb2f8043b5869b37` — update Day-12 launch-gate tests so candidate-selection fixtures require provider-observed `direct.permission=EDITING`.

## Verified safety properties

- `UNKNOWN` cannot be promoted by caller assertion;
- `READING` remains blocked;
- only provider-observed `EDITING` can satisfy the permission stage;
- all provider doctors must still PASS before readiness can reach `READY_FOR_LIVE_CANDIDATE_SELECTION`;
- readiness still sets `provider_write_allowed=false`;
- production writer remains disabled;
- real provider requests and advertising spend remain zero in this readiness layer;
- no provider/site mutation was performed;
- private core was not changed and remains proposal-only;
- no secret values were added to repository data.

CI run `33218249298` on `b66050fc8dc7b5b42e8b19ebbb2f8043b5869b37` completed all Python tests, Node tests, JSON validation, and diff whitespace checks successfully.

## Canonical interpretation

Provider-observed Direct permission is now an enforced API invariant rather than only a CLI convention. The next live step remains the read-only Owner-environment readiness command using existing Keychain credentials. No Yandex permission change should be made unless that command reports provider-observed `READING`.
