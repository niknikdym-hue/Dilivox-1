# Task 012 — Live readiness + exact Dilivox campaign inventory PASS

Date: 2026-08-31
Status: ACCEPTED LIVE READ EVIDENCE / MONEY PREFLIGHT NEXT

## Owner-executed canonical read-only flow

The Owner ran the current canonical post-Editing flow from `profit-engine` using local macOS Keychain credentials and the exact private managed advertiser target.

Fresh Owner UI evidence:
- permission: `EDITING`;
- source: `YANDEX_DIRECT_MANAGING_ACCOUNT_UI`;
- evidence status: `RECORDED` / `VALID`;
- provider write authorized: `false`;
- plaintext target login written: `false`.

## Provider readiness

All three live provider reads passed:

- Direct: `PASS`;
  - `clients.get(operator)`;
  - `direct.operator_identity=PASS`;
  - `direct.permission_source=MANAGER_ACCOUNT_UI_REQUIRED`;
  - `campaigns.get(target,limit=1)`;
  - `direct.target_units_login=PASS`;
  - HTTP 200;
  - Direct units snapshot: `11/119989/120000`.
- Metrica: `PASS`;
  - `counters.list`;
  - `counter.permission=edit`;
  - `counter.goals.list`;
  - `traffic.report_probe`;
  - HTTP 200.
- YAN Statistics: `PASS`;
  - `statistics.tree`;
  - `statistics.report(domain,30days,money)`;
  - HTTP 200.

Readiness result:
- state: `READY_FOR_LIVE_CANDIDATE_SELECTION`;
- Direct permission: `EDITING`;
- permission source: `OWNER_UI_EVIDENCE`;
- reasons: none;
- readiness digest: `e0a722f92645046f49eaf033385b682f21baa2d478aae767a9a3b8c108942c3f`;
- production writer enabled: `false`;
- provider write allowed: `false`;
- real provider mutation requests: `0`;
- advertising spend caused by the readiness flow: `0`.

## Exact campaign inventory

Read-only inventory completed successfully:
- total campaigns: `46`;
- page count: `1`;
- inventory digest: `b3a1cdf9aa48493445ef73779e44e43c785f3ec905c45751caa6c0da20174c1f`;
- candidate selected by runtime: `false`;
- provider write allowed: `false`;
- credential values printed: `false`;
- Direct units snapshot: `56/119933/120000`.

Exactly two campaigns are accepted as Dilivox first-smoke commercial candidates by Central Brain naming/scope review:

1. campaign `712203524` — name `Dilivox` — state `SUSPENDED` — status `ACCEPTED` — type `UNIFIED_CAMPAIGN`;
2. campaign `712791195` — name `dilivox.ru` — state `ACTIVE` (`ON`) — status `ACCEPTED` — type `UNIFIED_CAMPAIGN`.

All other active campaigns in the inventory belong to other products/sites and are excluded from the first Dilivox production smoke.

## Central Brain decision

Do not choose between `campaign.resume` on `712203524` and `campaign.suspend` on `712791195` from state/name alone.

Next mandatory gate is read-only Day-12 money preflight for both exact Dilivox campaign IDs over the same completed date window. Candidate selection must use the resulting spend / attributed YAN revenue / YAN control evidence and choose the lowest-downside reversible action.

No live Direct mutation has been sent.
