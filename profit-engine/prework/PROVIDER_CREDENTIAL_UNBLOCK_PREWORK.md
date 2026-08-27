# PROFIT ENGINE — PROVIDER CREDENTIAL UNBLOCK PREWORK

Status: CENTRAL BRAIN PREWORK / NOT YET CANONICAL
Prepared: 2026-08-27

## Objective

Reduce the remaining `BLOCKED_EXTERNAL_PROVIDER_CREDENTIAL` work to the smallest possible Owner interaction, without ever transmitting token values through ChatGPT, GitHub, issues or logs.

Current official provider contracts rechecked 2026-08-27:

- Yandex Direct API uses an OAuth access token issued for the app + specific Direct user; requests use `Authorization: Bearer <token>`.
- Yandex Metrica API uses Yandex OAuth and requires `metrika:read` for read reports/counters; requests use `Authorization: OAuth <token>`.
- YAN Partner Statistics API requires its own Statistics API OAuth token; it is distinct from the Block Configuration / in-app token; requests use `Authorization: OAuth <token>`.

Official references:

- https://yandex.ru/dev/direct/doc/ru/concepts/auth-token
- https://yandex.ru/dev/direct/doc/ru/token
- https://yandex.ru/dev/metrika/ru/intro/authorization
- https://yandex.ru/dev/partner-statistics/doc/ru/concepts/access
- https://yandex.ru/dev/partner-statistics/doc/ru/reference/statistics-get2

## Token A — Direct + Metrica read identity

Use the existing Profit Engine OAuth application under the already designated technical Yandex identity.

The application must retain only the scopes required for this stage:

- `direct:api`;
- `metrika:read`.

One Yandex OAuth token issued to that technical identity/app can be used by the runtime for both providers if it carries both scopes and the account itself has the required delegated access.

Important: Direct token permissions are also bounded by the permissions of the Yandex user for whom the token was issued. Current project policy therefore continues to use the technical delegated identity, not the Owner's primary password.

## Token B — YAN Statistics

Obtain a separate Partner Statistics OAuth token from the YAN interface for an identity authorized to read Dilivox statistics.

Current official UI route documented by Yandex:

`YAN interface -> API icon -> Receive an OAuth token for the Statistics API`.

Do NOT substitute the separate Block Configuration API token.

## Local secret storage before Cloud

Preferred temporary local secret store: macOS Keychain.

Suggested stable service names:

- `ProfitEngine-YandexOAuth-Read`;
- `ProfitEngine-YAN-Statistics`.

The runtime should use keychain references, not literal tokens in config, for example conceptually:

- `keychain:ProfitEngine-YandexOAuth-Read/<technical-account-ref>`;
- `keychain:ProfitEngine-YAN-Statistics/<yan-account-ref>`.

The account-reference label itself must not expose a secret.

Do not use a shell command that embeds the token in command history or logs. Preferred Owner path is a single manual paste into macOS Keychain Access, after which Codex/runtime retrieves it programmatically without printing it.

## Private mapping file

Keep provider IDs outside Git in:

`~/.config/profit-engine/sites/dilivox.json`

Permissions: `0600`.

This file may contain the private mapping identifiers needed to select the correct Direct client/campaign scope, Metrica counter and YAN resource, but it must not contain token values.

## Provider-doctor sequence after secrets exist

1. Resolve Token A from Keychain in memory.
2. Direct doctor:
   - minimal `clients.get`;
   - minimal `campaigns.get`;
   - no write methods.
3. Metrica doctor:
   - counters list;
   - resolve Dilivox counter through private mapping/domain;
   - one bounded monetization report probe.
4. Resolve Token B from Keychain in memory.
5. YAN doctor:
   - `statistics2/tree`;
   - one bounded statistics report.
6. Redact all Authorization values, provider IDs and response details not approved for evidence.
7. Only after doctor `PASS` may live READ_ONLY collectors run.

Any 401/403 remains `BLOCKED_ACCESS`, not an excuse to weaken permissions or expose credentials.

## Minimal Owner interaction target

The Owner should need to do at most:

1. authorize the existing Profit Engine app under the technical Yandex identity if Token A does not yet exist;
2. paste Token A once into the designated Keychain item;
3. obtain the YAN Statistics API token in the Partner interface;
4. paste Token B once into the designated Keychain item;
5. if Codex cannot infer private provider mappings safely, provide/select them through local UI/config — never chat.

Everything after that should be executed by Codex/Profit Engine.

## Production migration

Before Cloud deployment, move runtime token values from local Keychain to Yandex Lockbox using least-privilege service accounts.

Suggested logical names remain provider-specific; the public repository stores secret names/contracts only, never values.

Local Keychain may remain as development fallback but must not become the production credential source of truth.

## Security acceptance

Credential unblock is accepted only when:

- no token value appears in shell history, Git, issue/comment, evidence, screenshots or ChatGPT;
- Direct and Metrica read doctor pass under the intended technical identity;
- YAN Statistics doctor passes with the Statistics-specific token;
- private mappings are `0600` and outside Git;
- no Direct write call is exposed during read certification;
- token rotation/revocation can be performed without changing source code.
