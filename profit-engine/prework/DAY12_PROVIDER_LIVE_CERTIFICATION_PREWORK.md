# PROFIT ENGINE — DAY 12 PROVIDER LIVE CERTIFICATION PREWORK

Status: CENTRAL BRAIN PREWORK / NOT CANONICAL
Updated: 2026-08-28
Branch: `central-brain/day12-live-preflight-prework`
Depends on: Task 011R accepted

## Purpose

Define the exact live-provider gates that must pass after Task 011R acceptance and before the first real guarded Direct mutation.

This document does not authorize Direct Editing, credential creation, provider writes, advertising spend or production execution.

## Provider authorization truth

### Yandex Direct

Current Direct API v5 authorization contract:

- API application access must be approved;
- the acting Yandex Direct user must have access to the advertiser/client data;
- API capabilities are limited by that user's actual Direct permissions;
- a client/representative with read-only access remains read-only through the API;
- Direct requests use `Authorization: Bearer <OAuth token>`;
- `Client-Login` is used when required for agency-client access;
- production credentials never belong in Git, ChatGPT, issue bodies, screenshots or ordinary logs.

Therefore changing Direct from Reading to Editing is an explicit Owner account-permission gate, not something the runtime can infer or bypass.

### Yandex Metrica

Current Metrica API authorization contract:

- Yandex OAuth token;
- `metrika:read` is sufficient for statistics/read-only access;
- request header uses `Authorization: OAuth <token>`;
- the token is read-only measurement authority and never grants Direct write authority.

### YAN / Partner Statistics

Current Yandex Partner Statistics API contract:

- Statistics API uses its own OAuth token;
- it is distinct from the in-app/block-configuration API token;
- token is obtainable from the YAN interface API control / Statistics API flow;
- requests use `Authorization: OAuth <token>`;
- this token is measurement/reconciliation authority only and never Direct write authority.

## Local secret boundary

Temporary local-development secret storage remains:

- macOS Keychain service `ProfitEngine-YandexOAuth-Read` for the approved Yandex OAuth token used for Direct/Metrica reads where scopes/permissions permit;
- macOS Keychain service `ProfitEngine-YAN-Statistics` for the separate YAN Statistics API token;
- site/provider mapping file under `~/.config/profit-engine/` contains references/config only and no token values;
- later production secret storage moves to Yandex Lockbox.

A future Direct Editing credential must remain in the same secret-safe boundary. No token value is committed to either public or private Git repository.

## Live doctor sequence

After Task 011R acceptance only:

1. Owner changes the relevant Direct access from Reading to Editing.
2. Re-confirm the acting login/client relationship and exact advertiser identity.
3. Load credentials from Keychain without printing values.
4. Run Direct READ_ONLY doctor first.
5. Confirm the OAuth token resolves to the intended Direct account/user and can read the exact registered target IDs.
6. Run Metrica READ_ONLY doctor with exact counter/site scope.
7. Run YAN Statistics READ_ONLY doctor with exact partner/site scope.
8. Archive secret-safe doctor evidence: success/failure state, provider request IDs where available, scope identity refs, timestamps and redacted error class.
9. No write may occur merely because credential doctors pass.

## Direct live preflight requirements

Before a first mutation, perform a fresh read of the exact provider entity and bind:

- provider entity ID;
- advertiser/client identity ref;
- campaign/ad state and status;
- strategy subtype;
- current daily budget when applicable;
- currency/budget semantics;
- request/source provenance;
- Direct `RequestId` and `Units` response metadata when available;
- freshness deadline;
- deterministic preflight digest.

No campaign-name, URL, date or fuzzy target resolution.

## Direct response metadata

Current Direct API returns response metadata including:

- `RequestId` — unique provider request identifier;
- `Units` — request points spent / available / daily limit;
- `Units-Used-Login` where applicable.

These values may be retained in secret-safe audit evidence. OAuth/token values may not.

## Budget-write provider constraints

Current `Campaigns.update` provider contract includes:

- up to 10 campaigns per method call;
- at most 3 daily-budget changes per campaign per day;
- DailyBudget update availability depends on compatible campaign strategy/provider semantics.

Profit Engine launch policy is intentionally stricter:

- one provider object per write request;
- maximum one autonomous campaign budget mutation per campaign/day;
- no budget write unless the accepted ProviderBudgetPlan exactly binds weekly envelope -> provider daily amount -> provider integer/micros representation;
- provider capability/strategy incompatibility blocks execution.

## Live money gate

A Direct write credential does not prove economics.

Before any SCALE/TEST production action:

- Direct spend evidence must be accepted;
- Metrica attribution evidence must be accepted;
- YAN control/reconciliation state must be known;
- held/unreconciled/non-consumable money cannot authorize SCALE/TEST;
- campaign/day revenue cannot masquerade as cohort K5;
- private decision must reference accepted public evidence and current public contract.

Safety STOP/HOLD/QUARANTINE actions may be evaluated under their separate structural safety rules.

## First real mutation selection

Central Brain selects the first production mutation only from current live evidence after all doctors/preflight pass.

Preferred first-action priority:

1. reversible STOP/suspend justified by safety or stop-loss evidence;
2. bounded resume only when exact prior/current state proves it is intended;
3. bounded campaign budget update only with accepted money evidence and approved envelope;
4. never create/add/delete/archive/moderate/strategy-migrate as the first launch write.

## First-write execution envelope

The first real write is exactly one provider object and one guarded action.

Immediately before dispatch:

- revalidate ActionProposal/Governor binding;
- revalidate trusted Owner approval if >20%;
- revalidate current-day mutation cadence;
- acquire exact per-target execution lock;
- perform fresh pre-dispatch snapshot and TOCTOU comparison;
- recheck all applicable kill switches;
- derive normalized request from immutable ControllerPlan;
- confirm production writer enablement is explicit for this bounded execution only.

Any failed gate => zero dispatches.

## Response/read-back rule

After dispatch:

- record dispatch start before send;
- capture HTTP/provider result and `RequestId`/`Units` when returned;
- evaluate per-object provider result, not HTTP status alone;
- perform READ_ONLY read-back;
- compare read-back with plan-derived expected state;
- no blind retry after timeout or ambiguous response;
- classify applied / unchanged / unexpected before any future retry decision.

## Day-12 launch decision states

- `GUARDED_PRODUCTION_LAUNCHED` — exactly one bounded real mutation applied and read-back verified with complete audit chain;
- `PRODUCTION_WRITE_BLOCKED` — a gate prevented dispatch; zero provider writes;
- `PRODUCTION_EXECUTION_UNCERTAIN` — possible dispatch but safe verification failed; stop;
- `PRODUCTION_ROLLBACK_VERIFIED` — separately authorized rollback applied and verified;
- `PRODUCTION_ROLLBACK_BLOCKED` — rollback unsafe/not authorized.

## Official references verified 2026-08-28

- Yandex Direct API access/authorization: `https://yandex.com/dev/direct/doc/en/concepts/access`
- Yandex Direct request authorization: `https://yandex.com/dev/direct/doc/en/format`
- Yandex Direct Campaigns.update: `https://yandex.com/dev/direct/doc/en/campaigns/update`
- Yandex Direct HTTP headers: `https://yandex.com/dev/direct/doc/en/concepts/headers`
- Yandex Metrica authorization: `https://yandex.com/dev/metrika/en/intro/authorization`
- YAN Statistics API access: `https://yandex.com/dev/partner-statistics/doc/en/concepts/access`

## Safety

Until Task 011R acceptance and explicit later Owner action:

- Direct remains Reading;
- no write credential is requested or exercised;
- provider writes = 0;
- advertising spend = 0;
- production writer disabled;
- this branch remains PREWORK and is not canonical launch authority.