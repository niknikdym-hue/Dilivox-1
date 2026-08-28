# TASK 012 — DIRECT MANAGER / MANAGED TARGET MISBINDING REWORK

Date: 2026-08-29
Status: CENTRAL BRAIN REWORK / FAIL CLOSED
Scope: Day-12 Direct live-readiness identity and permission certification

## Finding

Fresh source-of-truth review found that the canonical Direct delegation model and the current live bootstrap were inconsistent.

Canonical access setup records:

- owner Direct account is the main advertiser account;
- technical identity `reklamadymova` is a separate Yandex Direct Managing Account;
- that Managing Account was granted `Reading` access to the owner account during the staged rollout.

The previous live bootstrap incorrectly set `client_login_ref` to `reklamadymova`, so the Direct doctor could certify the technical operator's own Direct client identity instead of the distinct managed owner advertiser account.

That made a green read doctor insufficient as exact-target evidence and made the attempted API-derived Reading/Editing inference unsafe for the Managing Account path.

## External contract verification

Current Yandex Direct documentation distinguishes:

- advertiser/agency representative roles and `Clients.get` fields such as `Grants` and `Representatives`;
- a separate Managing Account relationship whose access level is configured as `Administering`, `Editing`, or `Reading` in the Direct interface.

The documented `Clients.get` contract does not state that advertiser `Grants` / `Representatives` expose the access level of a separate Managing Account relationship.

Therefore Central Brain rejects any inference that the technical manager has Editing authority merely because the managed advertiser has `EDIT_CAMPAIGNS=YES` or a `CHIEF`/`DELEGATE` representative.

## Rework implemented

The public runtime now fails closed around that distinction:

1. private Direct config separates `operator_login_ref` from managed `client_login_ref`;
2. configuration rejects operator/target aliasing;
3. live bootstrap requires an explicit managed owner advertiser login and refuses `reklamadymova` as the target;
4. Direct doctor first proves OAuth/operator identity separately, then attempts the managed target read scope;
5. for a configured Managing Account path, the doctor records `direct.permission_source=MANAGER_ACCOUNT_UI_REQUIRED` and `direct.permission=UNKNOWN` even if the managed advertiser reports edit grants;
6. the Owner readiness script requires `PROFIT_ENGINE_DIRECT_TARGET_LOGIN` and cannot silently fall back to the technical manager login;
7. no provider write, Yandex permission change, token value, or budget action is introduced.

## Acceptance boundary

The previous claim that the Managing Account Editing state could be certified from `Clients.get` is REWORKED and superseded.

The safe interpretation is now:

- operator identity PASS != managed advertiser identity PASS;
- managed advertiser read visibility PASS != Managing Account Editing authority;
- Managing Account Reading -> Editing remains an explicit Owner-only Direct UI gate;
- exact managed target identity must be bound privately before further Day-12 live certification;
- until both are satisfied and Central Brain accepts the resulting evidence, candidate selection and production write remain blocked.

## Governance retained

- private core remains proposal-only;
- `provider_write_allowed=false` at readiness;
- production writer remains disabled;
- zero intentional provider mutations were performed;
- weekly budget increases above +20% still require exact Owner approval;
- no secrets are stored in Git/chat/logs.
