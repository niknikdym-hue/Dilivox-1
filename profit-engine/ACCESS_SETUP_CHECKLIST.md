# PROFIT ENGINE — TECHNICAL YANDEX ID ACCESS CHECKLIST

Status: ACTIVE SETUP CHECKLIST
Updated: 2026-08-26

Purpose: configure the owner's existing second Yandex ID as the technical operational identity for Profit Engine without exposing the primary owner account.

## A. Identity readiness

- [x] Confirm the second Yandex ID is under the owner's control.
- [x] Technical Yandex ID verification via Gosuslugi completed.
- [ ] Enable strong account security and recovery methods.
- [ ] Record the technical login privately; do not commit it if it is not intended to be public.
- [x] Direct delegation path resolved: use the existing Managing Account relationship rather than a new representative login.

## B. Yandex Metrica — Dilivox

Goal: technical ID can read Dilivox analytics and monetization reports.

Owner actions in the Dilivox counter:

1. Open Metrica -> Dilivox counter -> Settings -> Access.
2. Add the technical Yandex user.
3. Prefer edit access for the technical integration account when required for the intended automation; edit access also provides access to the Monetization report group when YAN monetization is connected to the counter.
4. Verify YAN monetization reports are enabled for the correct Dilivox counter in YAN.

Acceptance:

- [x] technical ID can open the Dilivox counter / access has been granted;
- [ ] technical ID can see Monetization / YAN reports;
- [ ] counter ID is recorded in private deployment configuration / site registry.

## C. YAN / RСЯ — Dilivox site

Goal: technical ID can inspect site/block statistics and, only if needed, edit site/block configuration.

Owner actions:

1. Open YAN -> Advertising on websites -> Sites.
2. Select Dilivox -> Edit -> Accesses.
3. Add the technical Yandex login/email.
4. Accept the Assistant Partner invitation on the technical account if Yandex sends one.
5. Initial preferred role: view/statistics access.
6. Enable site/block editing only when a concrete engineering task requires it.

Acceptance:

- [x] technical ID has been added as Partner Assistant for Dilivox;
- [x] technical ID can see Dilivox site / statistics access is granted;
- [x] technical ID has no unnecessary access to unrelated sites under this grant;
- [x] site/block editing remains disabled.

Note: Partner Statistics API authorization uses an OAuth token for a YAN-registered account. During M0, verify whether the assistant/delegated technical identity can obtain the exact required statistics token for Dilivox. If not, use the minimum-scope statistics token from the owner YAN identity and keep it only in Lockbox; do not store the owner password anywhere.

## D. Yandex Direct — Dilivox

Goal: technical identity can eventually read and control only the required Dilivox campaigns.

Resolved delegation model:

- main Direct account chief representative: owner account;
- technical Direct identity: existing Managing Account `reklamadymova`;
- stale old invitation was revoked by the owner;
- fresh Managing Account invitation was sent with `Reading` access;
- fresh invitation has been accepted by the technical account;
- owner Direct account and its campaign list/statistics are visible from the technical account.

Current rollout requirement:

1. Keep Profit Engine read-only / shadow mode during M0-M5.
2. Restore `Editing` only when M6 guarded autopilot is ready and Budget Governor tests have passed.
3. Register OAuth application/access required by Direct API.
4. Restrict the engine to registered Dilivox account/campaign scopes.

Acceptance:

- [x] fresh Managing Account invitation accepted by the technical identity;
- [x] Managing Account access level is `Reading` during M0-M5;
- [x] technical identity can view owner Direct campaigns and statistics;
- [ ] weekly budget baseline is captured;
- [ ] campaign/account identifiers are mapped to `site_id=dilivox`;
- [x] no automatic Direct writes are enabled yet;
- [ ] future write path is compatible with the Budget Governor.

## E. Budget Governor invariant

Before any write-enabled Direct access goes live:

- [ ] automatic weekly budget increase `<= +20%` is enforced in code;
- [ ] any increase `> +20%` becomes `PENDING_OWNER_APPROVAL`;
- [ ] owner approval is single-purpose and audited;
- [ ] global/site/account/campaign emergency pause works;
- [ ] current weekly budget baseline cannot be silently reset to bypass the +20% rule.

## F. Yandex Cloud identity separation

Do not confuse the technical Yandex ID with Cloud runtime service accounts.

Use:

- human technical Yandex ID: delegated access/OAuth setup for Direct/Metrica/YAN;
- Yandex Cloud service accounts: runtime access to Lockbox, PostgreSQL, Object Storage, Monitoring/Logging;
- Lockbox: production OAuth tokens and secrets.

Runtime code should never contain interactive account passwords.

## Current next action

Technical identity verification is complete and Direct read access is confirmed. Proceed with `OAUTH_API_SETUP.md`: register the `Profit Engine` OAuth application under the technical identity with only `direct:api` and `metrika:read`, then submit the Direct API access request. In parallel, verify Monetization/YAN reports are visible in the Dilivox Metrica counter and obtain the YAN Statistics API token through the RСЯ interface. No token/secret values are committed to GitHub.
