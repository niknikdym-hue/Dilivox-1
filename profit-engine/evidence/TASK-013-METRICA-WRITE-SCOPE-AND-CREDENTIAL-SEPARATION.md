# TASK 013 — METRICA WRITE SCOPE + CREDENTIAL SEPARATION

Status: ACCEPTED ENGINEERING REWORK / LIVE WRITE CREDENTIAL PENDING
Date: 2026-09-01
Site: `dilivox`
Counter: `110349067`

## Live facts

Owner Mac live goal audit returned:

- goals GET: HTTP 200;
- provider goal count: 22;
- expected Profit Engine goal count: 5;
- all five PE identifiers: `MISSING`;
- duplicate PE identifiers: 0;
- invalid/wrong-type PE identifiers: 0.

Exact missing identifiers:

- `pe_story_progress_75`;
- `pe_version_selected`;
- `pe_story_completed`;
- `pe_next_story_clicked`;
- `pe_return_visit`.

Initial create payload with optional `goal.is_favorite` was rejected HTTP 400. Runtime was reduced to the provider-compatible minimal action-goal shape: `name + type=action + conditions`.

The next bounded create attempt reached the provider with that minimal shape and returned:

`HTTP 403 — Access is denied`

No goal was claimed created and no blind retry was performed.

## Root cause / authority boundary

The read credential is proven sufficient for goal listing, but not accepted for Management API goal creation. Current Yandex Metrica authorization documentation requires `metrika:write` for management writes such as creating/changing tag configuration and goals.

The Profit Engine runtime previously had an architectural coupling: Metrica operations could inherit the Direct OAuth reference even though the private config already exposed a Metrica provider block.

That coupling is REWORKED.

## Accepted credential architecture

Provider credentials are now resolved separately:

- Direct read/control: `SiteConfig.yandex_oauth_token_ref`;
- Metrica read/reporting: `SiteConfig.metrica_oauth_token_ref`;
- Metrica configuration write: `SiteConfig.metrica_write_token_ref`;
- YAN Statistics: `SiteConfig.yan_stats_token_ref`.

Default Metrica write Keychain binding:

- service: `ProfitEngine-MetricaOAuth-Write`;
- account: `profit-engine`.

The working Direct OAuth token/application is not modified to close Metrica goal administration.

P0 uses a separate Yandex OAuth **For API access or debugging** application for Metrica administration, with only:

- `metrika:read`;
- `metrika:write`.

Guided local installer:

`profit-engine/scripts/install-metrica-write-token-mac.sh`

The installer:

1. opens official Yandex OAuth app creation if needed;
2. instructs exact app type/name/scopes locally;
3. accepts Client ID only in a local macOS dialog;
4. opens the OAuth authorization page;
5. accepts the OAuth token only in a hidden local macOS dialog;
6. stores it in Keychain;
7. performs exactly the bounded missing-goal create/read-back flow;
8. prints no token;
9. performs no blind retry.

## Fail-closed behavior

If no Metrica write token exists:

`BLOCKED_METRICA_WRITE_TOKEN_REQUIRED`

with zero goal POSTs.

If the separate write token still receives HTTP 403:

`BLOCKED_METRICA_WRITE_SCOPE`

and execution stops without retry.

The P0 system bootstrap no longer aborts all read-only/site diagnostics merely because the Metrica configuration-write gate is unresolved.

## Regression / CI

Integrated Profit Engine CI on project-state head `75a6dd5dbabe6bbca09544f4e673e1889b7e45de`:

- Python tests: SUCCESS;
- Node tests: SUCCESS;
- JSON validation: SUCCESS;
- whitespace check: SUCCESS.

GitHub Actions run: `33509653171` / run #219.

## Current next gate

Install and live-verify the separate Metrica write credential, then create/read-back only the five missing exact PE goals.

This gate grants no Direct write authority and changes no Direct campaign, bid or budget.
