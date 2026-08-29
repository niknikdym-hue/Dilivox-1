# TASK 012 — OWNER UI PERMISSION EVIDENCE GATE

Date: 2026-08-29
Status: CENTRAL BRAIN VERIFIED / SAFE REVERSIBLE FIX
Scope: Day-12 Managing Account `Reading -> Editing` evidence intake only

## Finding

The previous Direct manager-target REWORK correctly stopped inferring Managing Account `Editing` from advertiser `Clients.get` grants/representatives and therefore made the Direct doctor report manager permission as `UNKNOWN`.

However, `day12_readiness.py` still required `direct.permission=EDITING` from the doctor. That combination was impossible to satisfy for the documented Managing Account path: even after the Owner actually changed the Direct UI relationship from `Reading` to `Editing`, readiness would remain permanently blocked.

This was launch-critical because it created an unreachable Day-12 transition.

## Fix

Implementation chain:

- `2520838a4138212c8cbf2a70791955da86fd4d63` — add local fail-closed Owner UI permission evidence loader;
- `79e587ad20b7412f006d32cc5aaf04eb5f9102a9` — readiness accepts fresh validated Owner UI evidence only when the Direct doctor explicitly says `MANAGER_ACCOUNT_UI_REQUIRED`;
- `130dd1c49f998813bed8a30650dc6172dc394551` — readiness CLI loads the local 0600 evidence and reports only status/source, never target login or secret values;
- `0295321ee412b28b3095d4c807886aa679e28839` — readiness regression tests;
- `141251114b2e9590b9a982c4e4755cee9ed5dc06` — evidence-loader negative tests.

Profit Engine CI run `33224867707` on exact HEAD `141251114b2e9590b9a982c4e4755cee9ed5dc06`: SUCCESS.

## Evidence contract

The local evidence file is outside the repository at the runtime approval path and must be mode `0600`.

It is fail-closed and binds:
- schema version;
- exact technical operator login;
- SHA-256 of the distinct exact managed advertiser login (plaintext target is not stored in the evidence);
- permission exactly `EDITING`;
- source exactly `YANDEX_DIRECT_MANAGING_ACCOUNT_UI`;
- explicit Owner confirmation;
- timezone-aware confirmation timestamp;
- integrity digest.

Evidence is rejected when missing, stale (>24h), future-dated beyond bounded clock skew, permission is not `EDITING`, operator/target binding mismatches, fields are added/removed, permissions are broader than 0600, or digest is invalid.

## Authority boundary

This evidence is NOT cryptographic authentication and is NOT provider write authorization.

It may only remove the human Managing Account permission blocker and allow the existing readiness state to reach `READY_FOR_LIVE_CANDIDATE_SELECTION` after all provider read doctors PASS. It never sets `provider_write_allowed=true`; production writer remains disabled; real provider requests and advertising spend remain zero.

Provider-derived `READING` outside the Managing Account UI path cannot be overridden by this evidence.

## Locked governance preserved

- private core remains proposal-only and unchanged;
- no Yandex account permission was changed by this work;
- no provider/site mutation or Direct dispatch occurred;
- no weekly budget increase was attempted;
- >20% weekly budget increase still requires exact Owner approval;
- no secret values or exact managed target login were written to Git/chat/logs;
- no blind retry was added.

## Current gate

The canonical relationship remains recorded as `Reading`; no accepted evidence shows the Owner has changed it yet.

Single Owner-only action remains:

`Yandex Direct: for the owner advertiser account managed by reklamadymova, change Managing Account access from Reading to Editing.`

That UI change alone still authorizes no provider write.
