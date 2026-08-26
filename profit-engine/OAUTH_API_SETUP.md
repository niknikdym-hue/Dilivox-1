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

## Direct API access — staged rule

Use Yandex's staged access model.

### D0 — Test access first

During development, request `Test access` / trial access for the Profit Engine OAuth application.

Test access works only with the Direct API Sandbox and is sufficient to implement and debug the client without touching real campaigns or spending real money.

Do NOT submit the full-access certification form while the Profit Engine implementation, screenshots, and technical specification do not yet exist.

If the UI shows a long form requiring company data, programming language, example Direct logins, application functions, interaction scheme, and mandatory specification/screenshots, treat that as the FULL ACCESS certification form and return to the request list.

Create/select `Test access` instead.

### D1 — Build and validate in Sandbox

After test access approval:

1. obtain an OAuth token for the technical developer/test identity;
2. use the Direct Sandbox;
3. implement read/write API calls against Sandbox only;
4. build Direct connector/controller tests;
5. validate error handling, idempotency, and audit logging;
6. implement and test Budget Governor before any real write-capable access.

### D2 — Full access later

Convert the same application/request to Full access only after the application actually exists and we can truthfully provide:

- implemented function list;
- technical architecture/scheme;
- programming language and library versions;
- application screenshots/specification;
- example Direct login(s) where the application is actually used;
- real description of new user capabilities.

Full access is required for real Direct campaign data/control.

M0-M5 policy remains read-only/shadow for real campaigns. M6 enables guarded write control only after Budget Governor tests pass.

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
- [ ] Direct API TEST access request submitted/approved;
- [ ] Direct Sandbox request succeeds;
- [ ] Metrica API can list/read Dilivox counter data;
- [ ] Metrica monetization/YAN data is readable;
- [ ] YAN Statistics API token obtained and Dilivox statistics readable;
- [ ] all tokens/secrets migrated into Lockbox in M1.

## Next after M0 API access

Provision Yandex Cloud M1 foundation and implement the first read-only collectors:

- Direct collector;
- Metrica collector;
- YAN collector;
- immutable raw snapshot archive;
- canonical site/account mapping for `site_id=dilivox`.
