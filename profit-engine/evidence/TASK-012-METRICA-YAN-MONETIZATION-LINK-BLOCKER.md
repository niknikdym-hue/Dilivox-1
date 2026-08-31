# Task 012 — Metrica ↔ YAN monetization link blocker

Date: 2026-08-31
Status: OWNER CONFIGURATION REQUIRED / PROVIDER WRITES BLOCKED

## Live evidence

After Day-12 live provider readiness passed for all three providers and exact Direct campaign inventory was retrieved, the bounded Dilivox money preflight was run for the first exact candidate (`712203524`) over `2026-08-01..2026-08-30`.

The Direct spend read completed and the flow then failed at the Metrica YAN-attributed revenue read with HTTP 400.

A dedicated six-request read-only compatibility probe was then run against exact Metrica counter `110349067`.

Observed results:

- ordinary Direct campaign dimension + `ym:s:visits`: `PASS`, HTTP 200, 50 rows, `sampled=false`;
- every probe containing `ym:s:yanPartnerPrice` failed HTTP 400;
- provider message was exact and consistent across all YAN probes: `partner is not enabled for 110349067`;
- provider write requests: `0`;
- provider write allowed: `false`.

This proves the current blocker is not OAuth, counter access, Direct campaign attribution, campaign identity, or the Direct/YAN candidate IDs. The Metrica counter is not enabled as a YAN monetization tag for the Dilivox YAN site.

## Official provider configuration required

Yandex documentation requires YAN publishers to enable monetization reports from the YAN site/resource settings:

1. open the Dilivox site/resource in Yandex Advertising Network;
2. edit the site/resource;
3. on General, enable **Show YAN reports in Yandex Metrica** / **Показывать отчеты по РСЯ в Метрике**;
4. bind Metrica tag `110349067`;
5. save.

Provider documentation states that Monetization-group data can begin appearing in Metrica within 24 hours after the tag is enabled in YAN.

References checked on 2026-08-31:
- https://yandex.ru/support/partner/ru/statistics/metrika-visitors-statistics
- https://www.yandex.ru/support/metrica/ru/reports/monetization
- https://yandex.com/support/metrica/en/reports/partner

## Runtime hardening after live finding

The compatibility probe now classifies the exact provider response `partner is not enabled` as:

`metrica_yan_monetization_link=NOT_ENABLED`

and emits a concrete Owner action instead of leaving the result as an undifferentiated HTTP 400.

The bounded money runner now executes this link gate first and exits fail-closed with:

`BLOCKED_METRICA_YAN_NOT_ENABLED`

before any Direct/YAN money attribution probe if the link is still missing.

No campaign mutation, budget mutation, or provider write is authorized by this gate.

## Current launch gate

Owner action only:

**In the YAN settings for the Dilivox site/resource, enable “Show YAN reports in Yandex Metrica” and bind counter `110349067`.**

After Owner confirms the setting was saved, Central Brain will re-run the read-only compatibility gate. Because Yandex says data can take up to 24 hours to appear, a temporary `NOT_ENABLED`/not-yet-populated result after the UI change must remain fail-closed and must not be treated as configuration failure or write authority.

Only after Metrica YAN monetization becomes readable will the two exact Dilivox candidate money preflights resume.
