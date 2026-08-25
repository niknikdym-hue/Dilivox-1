# PROFIT ENGINE — TECHNICAL YANDEX ID ACCESS CHECKLIST

Status: ACTIVE SETUP CHECKLIST
Updated: 2026-08-25

Purpose: configure the owner's existing second Yandex ID as the technical operational identity for Profit Engine without exposing the primary owner account.

## A. Identity readiness

- [x] Confirm the second Yandex ID is under the owner's control.
- [ ] Enable strong account security and recovery methods.
- [ ] Record the technical login privately; do not commit it if it is not intended to be public.
- [ ] Confirm whether this login has ever been used in Yandex Direct, because representative eligibility may depend on prior Direct usage.

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

- [ ] technical ID can see Dilivox site and block statistics;
- [ ] technical ID has no unnecessary access to unrelated sites;
- [ ] editing remains disabled unless specifically required.

Note: Partner Statistics API authorization uses an OAuth token for a YAN-registered account. During M0, verify whether the assistant/delegated technical identity can obtain the exact required statistics scope for Dilivox. If not, use the minimum-scope statistics token from the owner YAN identity and keep it only in Lockbox; do not store the owner password anywhere.

## D. Yandex Direct — Dilivox

Goal: technical identity can eventually read and control only the required Dilivox campaigns.

Important eligibility check: Yandex Direct representative setup expects a Yandex login that has not already been used to sign in to Direct. If the existing second account was already used in Direct, do not force the representative path; evaluate a Managing Account or another supported delegation model instead.

Initial rollout:

1. First grant/read-map access sufficient to inventory campaigns and current weekly budgets.
2. Keep Profit Engine in read-only / shadow mode during M0-M5.
3. Grant write-capable Direct API access only for M6 guarded autopilot.
4. Register OAuth application/access required by Direct API.
5. Restrict the engine to registered Dilivox account/campaign scopes.

Acceptance:

- [ ] technical identity can view Dilivox campaigns;
- [ ] weekly budget baseline is captured;
- [ ] campaign/account identifiers are mapped to `site_id=dilivox`;
- [ ] no automatic Direct writes are enabled yet;
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

Metrica access is granted. Next configure YAN Partner Assistant access for the Dilivox site with view/statistics permission only. After that, verify Monetization visibility under the technical account and determine the correct Direct delegation path based on whether the technical ID has previously been used in Direct.
