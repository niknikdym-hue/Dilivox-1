# Task 012 — Post-Editing provider read rework

Date: 2026-08-31
Status: ACCEPTED IN CODE / LIVE READ RE-RUN REQUIRED

## Live observation supplied by Owner

The prepared post-Editing read-only flow recorded fresh local Owner UI evidence successfully:

- permission: `EDITING`;
- source: `YANDEX_DIRECT_MANAGING_ACCOUNT_UI`;
- provider write authorized: `false`;
- plaintext target login written: `false`.

The same run then produced:

- Direct: `PROVIDER_ERROR` after `clients.get(operator)` and `direct.operator_identity=PASS`;
- Metrica: `PROVIDER_ERROR` HTTP 400 after `counters.list`, `counter.permission=edit`, and `counter.goals.list`;
- YAN Statistics: `PASS`;
- readiness: `BLOCKED_OWNER_PERMISSION` / Direct permission `UNKNOWN`;
- production writer disabled;
- provider write allowed `false`;
- advertising spend `0`.

No live mutation was sent.

## Root cause rework

### Direct

The failing request was the manager-path `Clients.get(target)` call.

A Yandex Direct Managing Account is distinct from an advertising agency. The public Direct API documentation defines `Client-Login` for `Clients.get` in advertiser-representative / agency-client semantics; it is not the correct proof of a separate Managing Account relationship.

Rework:

- keep exact `Clients.get(operator)` to bind the OAuth token to `reklamadymova`;
- do not call `Clients.get(target)` on the Managing Account path;
- prove exact managed-target data access with read-only `Campaigns.get` carrying the exact private `Client-Login` target;
- if `Units-Used-Login` is returned, require it to equal the exact managed target;
- never infer Editing from provider client grants on the Managing Account path;
- Editing remains bound only to fresh exact Owner UI evidence.

Implementation: `4557d0e47cfc0e7aa3538311a94ad9910dc4b717`.
Manager binding regressions: `9989793513dc5cd256a6bc5c9002bc8c7adaa2cb`.

### Metrica

The generic readiness doctor mixed Metrica availability with a YAN monetization metric probe (`ym:s:yanPartnerPrice`). The live run already proved Management API counter access and goals access before failing on that report probe.

Rework:

- generic Metrica readiness now probes only `ym:s:visits`;
- YAN monetization and campaign-attributed YAN revenue remain exclusively in the Day-12 money preflight, where they are reconciled against exact YAN Statistics control totals.

Implementation: `4557d0e47cfc0e7aa3538311a94ad9910dc4b717`.
Runtime regressions: `7bf42efc8fcd95135957b183d732f979cbfaa7a4`.

## Verification

Integrated Profit Engine CI:

- run `33391500520` / #149;
- HEAD `9989793513dc5cd256a6bc5c9002bc8c7adaa2cb`;
- conclusion: `SUCCESS`.

## Current gate

Run the same local post-Editing read-only flow again from current canonical `profit-engine`.

Expected sequence:

1. fresh Owner Editing evidence;
2. Direct operator identity read;
3. exact managed-target Campaigns read;
4. Metrica counters/goals/basic traffic report read;
5. YAN Statistics read;
6. only if readiness is `READY_FOR_LIVE_CANDIDATE_SELECTION`, exact campaign inventory is printed.

Any failed gate stops the shell before inventory. No provider write authority is granted by this flow.
