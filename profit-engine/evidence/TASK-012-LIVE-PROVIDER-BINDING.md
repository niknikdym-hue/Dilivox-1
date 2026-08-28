# TASK 012 — LIVE PROVIDER BINDING EVIDENCE

Date: 2026-08-28
Status: CENTRAL BRAIN VERIFIED / READ PATH READY
Scope: Dilivox production provider identity + read-only live certification scaffold

## Owner-side live proofs

The Owner executed direct provider calls on the production Mac using OAuth credentials later stored in macOS Keychain.

### YAN Statistics

- `tree.json` returned HTTP 200.
- `get.json` for exact domain `dilivox.ru`, 30-day period, returned `result=ok`.
- Observed 30-day control totals for 2026-07-29..2026-08-28 at the time of certification:
  - partner revenue: 80.77 RUB;
  - ad requests: 1609;
  - ad renders: 1499;
  - visible shows: 1035;
  - fill rate: 93.16345%;
  - CPMV: 78.03 RUB;
  - eCPM: 66.64 RUB;
  - RPM: 50.20 RUB.
- Separate YAN Statistics OAuth is stored under the local Keychain binding referenced by the runtime; no credential value is stored in this repository.

### Yandex Metrica

- Management `counters` request returned HTTP 200.
- Exact Dilivox counter is visible:
  - counter id: `110349067`;
  - site/name: `dilivox.ru`;
  - owner login: `DymovaEI`;
  - counter permission returned by provider: `edit`;
  - status: `Active`.
- This proves live account access to the exact counter. It does not by itself prove any Direct write authority.

### Yandex Direct

- Direct `clients.get` returned HTTP 200.
- Exact client is visible:
  - client id: `100716697`;
  - login: `reklamadymova`;
  - type: `CLIENT`.
- This proves live Direct read access to the intended client identity.
- Direct mutation/Editing authority remains a separate Day-12 gate and is NOT inferred from HTTP 200 read access.

## Runtime integration

Implementation chain:

- `c01e8d73b605d676baea1501fa539ce3c0ce6f73` — exact provider doctor scope:
  - Direct expected-login binding;
  - Metrica exact counter goals-list probe plus monetization report probe;
  - YAN exact `dilivox.ru` 30-day monetary/control-total probe.
- `2a46d6e0554cac6f8218745cf95f2a87df70d9a5` — Dilivox live bootstrap using Keychain references and exact provider identities.
- `ae702db0135000aab171052765f5691e091ef7ae` — provider doctor tests.
- `5cc937257ef54520ef8e8932de27153407f80c4f` — live bootstrap tests.

Profit Engine CI run `33208131487` on exact HEAD `5cc937257ef54520ef8e8932de27153407f80c4f`: SUCCESS.

## Safety invariants retained

- bootstrap writes references/identity bindings only, never token values;
- local private registry remains outside the repository and mode 0600;
- provider doctor is read-only;
- no Direct mutation was executed by this certification;
- production writer remains disabled until the accepted Day-12 launch gates are satisfied;
- >20% weekly budget growth still requires exact explicit Owner approval;
- no blind retry.

## Canonical interpretation

Provider credential/read availability is no longer a launch blocker for YAN Statistics, Metrica, or Direct read access.

The remaining Direct boundary is write authority and the exact one-object guarded production execution path. A successful read must never be interpreted as permission to mutate.

The previously opened Revenue Rescue side issue was folded into Task #19 and closed as a separate workstream. Live monetary diagnostics, Metrica goals and YAN placement signals are inputs to Profit Engine itself, not a second system.
