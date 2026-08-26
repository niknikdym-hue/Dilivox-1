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

For API-access/debug applications Yandex supplies the verification-code redirect URI; do not invent or commit custom secret callback credentials.

## Secret handling

The OAuth app exposes a ClientID and Client secret.

Rules:

- never commit Client secret;
- do not paste access tokens into GitHub issues/PRs/docs;
- ClientID is kept in private deployment configuration / owner secure storage;
- production Client secret and OAuth tokens go to Yandex Lockbox;
- until Lockbox exists, keep secrets only in the owner's secure local/password-manager storage.

## Direct API access — current next step

After the OAuth app exists:

1. Open Direct API settings under the application-developer/technical identity.
2. If the API settings page is unavailable, note that Yandex currently requires at least one campaign in that developer Direct account before the API settings page becomes available; do not launch spend accidentally just to satisfy this prerequisite.
3. Click `Get API access` / accept the Direct API user agreement if prompted.
4. Open `My requests`.
5. Create one new access request for the Profit Engine ClientID.
6. Provide the current contact email and accurate application description.
7. Submit the request and track its status in `My requests`.
8. Keep operational campaign permissions read-only during M0-M5 even though the `direct:api` OAuth scope itself supports management methods.

Important: provider authorization and our own action policy are separate layers. The Profit Engine Budget Governor and staged rollout remain authoritative regardless of API scope.

## Metrica API

Use the same OAuth application with `metrika:read` for the initial collector.

Required verification:

- list counters available to the technical identity;
- identify the Dilivox counter;
- query normal traffic statistics;
- query YAN monetization metrics/reports available to that counter;
- record IDs only in private/deployment configuration when not intended to be public.

## YAN/RСЯ Statistics API

YAN Statistics API token is obtained from the YAN interface/API action for the YAN-registered account.

Preferred path:

1. under the technical Partner Assistant account, open the RСЯ interface;
2. use the API control and request an OAuth token for the Statistics API;
3. test the statistics tree/report endpoints for the Dilivox resource;
4. if delegated assistant access does not expose the required statistics data, use the minimum necessary statistics token from the owner YAN identity instead;
5. store the resulting token in Lockbox only.

Do not confuse the Statistics API token with the separate in-app block-configuration API token.

## M0 acceptance

- [x] OAuth application `Profit Engine` created under technical identity;
- [x] `direct:api` scope added;
- [x] `metrika:read` scope added;
- [x] ClientID captured privately by owner;
- [x] Client secret captured securely and not committed;
- [ ] Direct API access request submitted;
- [ ] Direct API access request approved as required;
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
