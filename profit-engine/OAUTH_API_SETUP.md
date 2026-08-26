# PROFIT ENGINE — OAUTH AND API SETUP

Status: ACTIVE M0 GUIDE
Updated: 2026-08-26

## Objective

Create secure API access for the technical Yandex identity without passwords in application code.

## OAuth application

Application created under the technical Yandex identity used for Profit Engine operations.

Application type: `For API access or debugging`.

Service name: `Profit Engine`.

Configured scopes:

- `direct:api` — Yandex Direct API;
- `metrika:read` — Yandex Metrica statistics/counter read access.

Do not add `metrika:write` during M0 unless a concrete write task requires it.

## Secret handling

The OAuth app exposes a ClientID and Client secret.

Rules:

- never commit Client secret;
- do not paste access tokens into GitHub issues/PRs/docs/chat;
- ClientID is kept in private deployment configuration / owner secure storage;
- production Client secret and OAuth tokens go to Yandex Lockbox;
- until Lockbox exists, keep secrets only in the owner's secure local/password-manager storage.

## Direct API access — current confirmed UI path

Observed in the current Russian Direct UI for the technical account on 2026-08-26:

- `My requests -> New request` opens the Full Access certification form;
- the separate `Sandbox` tab exists, but attempting to initialize it returns `Создание песочницы более не доступно`;
- therefore a new Sandbox cannot be created for this technical account through the current interface.

Current Russian Direct API documentation also describes the production path as OAuth application -> API access request -> approval -> OAuth token -> API calls.

### D0 — Full Access application now

Proceed with the Full Access certification request for the `Profit Engine` OAuth ClientID.

The application is an internal system for the owner's own advertising accounts/sites. The request must describe the intended real architecture truthfully; it must not claim that unimplemented UI or automation is already deployed.

Current intended Direct API scope/functions:

1. read campaign/account structure and current settings;
2. obtain campaign/ad/group statistics and reports;
3. synchronize Direct spend/traffic data with internal Profit Engine data;
4. later, after guarded rollout, manage campaigns/ads/budgets through the Direct API;
5. later, apply bounded optimization decisions from Profit Engine;
6. never bypass the Budget Governor or owner approval policy.

### D1 — Read-only implementation first

Even after Full Access approval, real campaign rollout remains staged:

1. implement read-only Direct collector;
2. verify campaign/account mapping for `site_id=dilivox`;
3. collect spend and statistics;
4. build immutable raw snapshots and audit logs;
5. reconcile with Metrica/YAN data;
6. run optimizer in shadow mode during M0-M5.

### D2 — Guarded write control later

Write-capable Direct automation is enabled only at M6 after:

- Budget Governor implementation/tests;
- emergency-stop implementation/tests;
- owner-approval workflow implementation/tests;
- data-quality gates pass;
- Direct managing account permission is intentionally upgraded from `Reading` to `Editing`.

Hard owner invariant:

- automatic weekly budget increase `<= +20%` may be applied only when all other guards pass;
- any requested weekly budget increase `> +20%` MUST remain blocked as `PENDING_OWNER_APPROVAL` until explicit owner approval.

## Metrica API

Use the same OAuth application with `metrika:read` for the initial collector.

Required verification:

- list counters available to the technical identity;
- identify the Dilivox counter;
- query normal traffic statistics;
- query YAN monetization metrics/reports available to that counter;
- record IDs only in private/deployment configuration when not intended to be public.

## YAN/RСЯ Statistics API

YAN Statistics API token is obtained through the YAN interface/API flow for the YAN-registered account.

Preferred path:

1. under the technical Partner Assistant account, open the RСЯ interface;
2. obtain the Statistics API token if delegated access supports the required Dilivox data;
3. test the statistics tree/report endpoints for the Dilivox resource;
4. if delegated assistant access does not expose required statistics data, use the minimum necessary statistics token from the owner YAN identity instead;
5. store the resulting token in Lockbox only.

Do not confuse the Statistics API token with the separate in-app block-configuration API token.

## M0 acceptance

- [x] OAuth application `Profit Engine` created under technical identity;
- [x] `direct:api` scope added;
- [x] `metrika:read` scope added;
- [x] ClientID captured privately by owner;
- [x] Client secret captured securely and not committed;
- [x] Direct Sandbox path checked; current UI reports new Sandbox creation is no longer available;
- [ ] Direct Full Access certification request submitted;
- [ ] Direct Full Access request approved;
- [ ] Direct API read request succeeds for the authorized real account;
- [ ] Metrica API can list/read Dilivox counter data;
- [ ] Metrica monetization/YAN data is readable;
- [ ] YAN Statistics API token obtained and Dilivox statistics readable;
- [ ] all tokens/secrets migrated into Lockbox in M1.

## Next actions

1. Prepare and submit the truthful Full Access certification package, including a technical specification file.
2. In parallel, begin M1 Yandex Cloud foundation and the real read-only Metrica/YAN collectors.
3. After Direct approval, implement Direct read-only collector against the real account.
4. Do not enable Direct write automation before M6 guarded-autopilot gates pass.
