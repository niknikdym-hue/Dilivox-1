# TASK 012 — DIRECT PERMISSION READ PROBE

Date: 2026-08-28
Status: CENTRAL BRAIN IMPLEMENTED / CI VERIFIED / LIVE RESULT PENDING
Scope: replace manual Direct Reading/Editing assertion with provider-observed read-only evidence

## Source-of-truth check

At the start of this work:

- public `niknikdym-hue/Dilivox-1` branch `profit-engine`: `c1a0f18746a282956bfd5a139d93b48d1e20d1f0`;
- private `niknikdym-hue/profit-engine-core` branch `main`: `76b1b8670690f102a045243760dfe3d1e58513d5`;
- private-core CI `33182663547`: SUCCESS;
- public open launch-critical issue: `#19` only;
- private core open issues: none;
- no new Codex implementation after the previously accepted Day-12 pre-live scaffold.

Private core remains unchanged and proposal-only.

## Why this change

The prior Day-12 readiness CLI accepted an operator-supplied `--direct-permission` value. That was deliberately fail-closed by default, but it left the permission gate dependent on a manual assertion.

Current Yandex Direct API documentation exposes permission information through the read-only `Clients.get` response:

- `Grants[].Privilege = EDIT_CAMPAIGNS` with `Value = YES|NO`;
- representative roles include `CHIEF`, `DELEGATE`, and `READONLY`.

Therefore the launch gate can determine Reading vs Editing without making a provider mutation.

## Implementation

Implementation chain:

- `1b79bcd941ef01d81c761734407978500634f3a9` — Direct doctor requests `Grants` and `Representatives`, derives `direct.permission=EDITING|READING|UNKNOWN` using GET-only Direct calls;
- `50a06cb4437fbca562ea39bc73af2f78298a3133` — Day-12 readiness consumes provider-observed permission and fails closed on UNKNOWN/READING; an observed READ_ONLY result cannot be overridden by a manual EDITING assertion;
- `756fb0980a6e5038096559cf5eda611ccbf33166` — Day-12 CLI removes the manual permission flag and uses `DIRECT_CLIENTS_GET` as the permission source;
- `9a271f6680e945166deb9992125025c319db9964` — runtime tests for exact read-only permission derivation;
- `438342976a2a60013366aca93e0f43fae3633e31` — readiness tests proving observed permission is authoritative and write authority remains false.

Profit Engine CI run `33209777119`, job `98979872594`: all Python tests, Node tests, JSON validation and diff checks SUCCESS on `438342976a2a60013366aca93e0f43fae3633e31`.

## Safety invariants

- all provider operations in this probe are `get`/read-only;
- no Yandex account permission is changed;
- no Direct campaign/budget mutation is performed;
- no token value is written to Git, issues, logs, or evidence;
- `provider_write_allowed=false` remains hard-coded in Day-12 readiness;
- production writer remains disabled;
- private core remains proposal-only;
- weekly budget increases above +20% still require exact Owner approval;
- no blind retry.

## Acceptance

CENTRAL BRAIN: ACCEPT for read-only permission certification infrastructure.

This is not live launch acceptance. A real live run from the Owner environment must still read the current Direct permission and all three provider doctors must PASS before live candidate selection.

## Remaining external boundary

The repository no longer needs a human to *declare* Reading vs Editing. The next external step is only to execute the read-only Day-12 readiness command in the Owner environment where the existing Keychain credentials are available.

If the observed result is `READING`, the single Owner-only action is to change the relevant Yandex Direct access to Editing. If it is already `EDITING`, no permission change is needed and the system can continue to live candidate selection after the remaining provider checks PASS.
