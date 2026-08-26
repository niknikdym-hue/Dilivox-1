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

## Direct API access — current UI path

The current Russian Direct UI for this account exposes:

- `My requests -> New request` as the Full Access certification form;
- a separate `Sandbox` tab with `Start using Sandbox`.

Therefore the project follows the current UI rather than assuming a visible `Test access` item exists in the New request menu.

### D0 — Enable Sandbox first

1. Open Direct API settings under the technical identity.
2. Open the `Sandbox` tab.
3. Click `Start using Sandbox`.
4. If the UI asks to associate/select an OAuth application, use `Profit Engine`.
5. Obtain an OAuth token for the technical developer/test identity when required.
6. Use only the Sandbox API endpoint during this stage.

Sandbox is isolated from live Direct data. Test campaigns/ads are not actually served and simulated funds do not affect real campaigns.

### D1 — Build and validate against Sandbox

Implement and test:

1. Direct campaign/statistics read client;
2. campaign-control methods against toy campaigns only;
3. API error handling and retry policy;
4. idempotency and action audit log;
5. Budget Governor;
6. hard owner invariant: automatic weekly budget increase > +20% is impossible without explicit owner approval;
7. emergency-stop and DATA_QUALITY_HOLD behavior.

The Sandbox JSON endpoint follows the `api-sandbox.direct.yandex.com/json/v5/...` pattern.

### D2 — Full access later

`My requests -> New request` currently opens the Full Access certification form. Do not submit it prematurely.

Submit Full Access only after the application actually exists and we can truthfully provide:

- implemented function list;
- technical architecture/interaction scheme;
- programming language and library versions;
- application screenshots/specification;
- example Direct login(s) where the application is actually used;
- real description of new user capabilities;
- API services/methods, call order/frequency, error handling and API-limit handling.

Full access is required for real Direct campaign API data/control.

M0-M5 policy remains read-only/shadow for real campaigns. M6 enables guarded write control only after Budget Governor tests pass and Direct access is upgraded appropriately.

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
- [ ] Direct Sandbox enabled for the technical developer identity;
- [ ] Direct Sandbox API request succeeds;
- [ ] Metrica API can list/read Dilivox counter data;
- [ ] Metrica monetization/YAN data is readable;
- [ ] YAN Statistics API token obtained and Dilivox statistics readable;
- [ ] all tokens/secrets migrated into Lockbox in M1.

## Next after Sandbox enablement

Proceed in parallel rather than waiting for Full Access certification:

- begin M1 Yandex Cloud foundation;
- implement Direct connector/controller against Sandbox;
- implement real read-only Metrica collector;
- implement real read-only YAN collector;
- create immutable raw snapshot archive;
- create canonical site/account mapping for `site_id=dilivox`.

When those pieces are demonstrably working, prepare and submit the Full Access certification package with real screenshots/specification rather than placeholders.
