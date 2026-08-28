# PROFIT ENGINE — DAY 12 PROVIDER LIVE CERTIFICATION

Status: CANONICAL
Updated: 2026-08-29
Depends on: Task 011/011R accepted

## Purpose

Define the exact live-provider certification gates that must pass after Owner enables Direct Editing and before the first real guarded Direct mutation.

This document authorizes no write by itself.

## Yandex Direct authorization truth

Current Direct API v5 contract:

- application API access must be approved;
- the acting Direct user/client must have access to the intended advertiser data;
- API capabilities are limited by the user's actual Direct permissions;
- read-only Direct access remains read-only through API;
- requests use `Authorization: Bearer <OAuth token>`;
- `Client-Login` is documented for advertiser/agency representative targeting; it must never be assumed to prove a separate Managing Account relationship;
- Direct permission transition Reading -> Editing is an explicit Owner/account gate, not a runtime inference.

### Managing Account boundary

The canonical Dilivox delegation uses a separate Yandex Direct Managing Account as the technical operator. That relationship has its own `Administering` / `Editing` / `Reading` level in the Direct web interface.

The documented Direct API `Clients.get` response exposes advertiser/agency `Grants` and `Representatives`. Those fields describe the advertiser/agency client and its representatives; they do not document the access level of a separate Managing Account relationship.

Therefore:

- the technical Managing Account login and the managed owner advertiser login are distinct identities and must never be aliased in runtime configuration;
- a successful `Clients.get` for the technical operator proves only the OAuth/operator identity;
- a successful read of the managed advertiser/campaign scope proves read visibility only;
- advertiser `Grants` or `Representatives` must not be used to infer that the separate Managing Account has Editing authority;
- Managing Account Reading -> Editing remains an Owner-controlled web-interface gate until Yandex exposes a documented API field that directly represents that relationship;
- if the runtime cannot prove the managed target identity separately from the operator, certification fails closed.

## Yandex Metrica authorization truth

- Yandex OAuth token;
- `metrika:read` supports read/statistics access;
- requests use `Authorization: OAuth <token>`;
- Metrica read authority never grants Direct write authority.

## YAN / Partner Statistics authorization truth

- Statistics API uses its own OAuth token;
- it is distinct from in-app/block-configuration API authorization;
- requests use `Authorization: OAuth <token>`;
- YAN Statistics is measurement/reconciliation authority only.

## Secret boundary

Local development:

- `ProfitEngine-YandexOAuth-Read` Keychain service for approved Yandex OAuth read use where scopes/permissions fit;
- `ProfitEngine-YAN-Statistics` Keychain service for separate YAN Statistics token;
- no token values in Git, issues, chat, screenshots or ordinary logs.

Production target: Yandex Lockbox.

Any future Direct Editing credential remains inside the same secret-safe boundary.

## Live doctor order

After Owner enables Editing:

1. bind the exact technical operator login and a distinct exact managed owner advertiser login in private configuration;
2. load credentials from secret-safe storage without printing values;
3. run Direct READ_ONLY doctor first;
4. prove OAuth operator identity separately from managed advertiser/target identity;
5. prove exact managed advertiser/campaign read visibility;
6. keep Managing Account write authority fail-closed unless accepted Owner-side Editing evidence exists;
7. run Metrica READ_ONLY doctor for exact counter/site;
8. run YAN Statistics READ_ONLY doctor for exact partner/site scope;
9. archive secret-safe certification evidence: status, timestamp, scope refs, provider request IDs where available, redacted error class;
10. do not write merely because all doctors pass.

## Direct response metadata

Secret-safe audit may retain:

- `RequestId`;
- `Units`;
- `Units-Used-Login` where returned.

OAuth/token values may never be retained.

## Budget provider constraints

Current Direct Campaigns.update contract includes provider limits such as maximum campaigns per call and maximum daily-budget changes per campaign/day. Profit Engine launch is stricter:

- exactly one object per write request;
- max one autonomous campaign budget mutation per campaign/day;
- exact weekly-envelope -> provider daily amount/micros mapping;
- incompatible provider strategy/capability blocks execution.

## Live money gate

For SCALE/TEST production actions:

- Direct spend accepted;
- Metrica attribution accepted;
- YAN reconciliation compatible/accepted;
- no DQ hold;
- mature/optimizer-consumable measurement;
- current public/private contract identity;
- no campaign/day-to-cohort semantic substitution.

Safety STOP/HOLD/QUARANTINE follows separate structural rules but still requires exact target/preflight/write-safety gates.

## Official references verified 2026-08-29

- Direct access: `https://yandex.com/dev/direct/doc/en/concepts/access`
- Direct request auth: `https://yandex.com/dev/direct/doc/en/format`
- Direct Clients.get: `https://yandex.com/dev/direct/doc/en/clients/get`
- Direct roles/access: `https://yandex.com/dev/direct/doc/en/objects/roles`
- Direct manager accounts: `https://yandex.com/support/direct/en/campaigns/mcc`
- Direct Campaigns.update: `https://yandex.com/dev/direct/doc/en/campaigns/update`
- Direct headers: `https://yandex.com/dev/direct/doc/en/concepts/headers`
- Metrica auth: `https://yandex.com/dev/metrika/en/intro/authorization`
- YAN Statistics access: `https://yandex.com/dev/partner-statistics/doc/en/concepts/access`

## Safety

Passing provider certification is necessary but not sufficient for a write. Every Day-12 mutation still requires the full accepted controller chain and first-write acceptance matrix.
