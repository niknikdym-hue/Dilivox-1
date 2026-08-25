# PROFIT ENGINE — OAUTH AND API SETUP

Status: ACTIVE M0 GUIDE
Updated: 2026-08-25

## Objective

Create secure API access for the technical Yandex identity without passwords in application code.

## OAuth application

Create the application under the technical Yandex identity used for Profit Engine operations.

Application type: `For API access or debugging`.

Suggested service name: `Profit Engine`.

Current required scopes:

- `direct:api` — Yandex Direct API;
- `metrika:read` — Yandex Metrica statistics/counter read access.

Do not add `metrika:write` during M0 unless a concrete write task requires it.

For API-access/debug applications Yandex supplies the verification-code redirect URI; do not invent or commit custom secret callback credentials.

## Secret handling

The OAuth app will expose a ClientID and Client secret.

Rules:

- never commit Client secret;
- do not paste access tokens into GitHub issues/PRs/docs;
- ClientID may be recorded only in private deployment configuration if desired;
- production Client secret and OAuth tokens go to Yandex Lockbox;
- until Lockbox exists, keep secrets only in the owner's secure local/password-manager storage.

## Direct API access

After the OAuth app exists:

1. Open Direct API settings under the application-developer/technical identity.
2. Accept the Direct API user agreement if prompted.
3. Create a new API access request using the OAuth application's ClientID.
4. Request the appropriate production access after any required test/access stage.
5. Keep operational campaign permissions read-only during M0-M5 even though the `direct:api` OAuth scope itself supports management methods.

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

- [ ] OAuth application `Profit Engine` created under technical identity;
- [ ] `direct:api` scope added;
- [ ] `metrika:read` scope added;
- [ ] ClientID captured privately;
- [ ] Client secret captured securely and not committed;
- [ ] Direct API access request submitted/approved as required;
- [ ] Metrica API can list/read Dilivox counter data;
- [ ] Metrica monetization/YAN data is readable;
- [ ] YAN Statistics API token obtained and Dilivox statistics readable;
- [ ] all tokens/secrets scheduled for migration into Lockbox in M1.

## Next after M0 API access

Provision Yandex Cloud M1 foundation and implement the first read-only collectors:

- Direct collector;
- Metrica collector;
- YAN collector;
- immutable raw snapshot archive;
- canonical site/account mapping for `site_id=dilivox`.
