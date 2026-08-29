# TASK 012 — PRODUCTION WRITER READY

Date: 2026-08-29
Status: CENTRAL BRAIN VERIFIED / CODE READY / NO LIVE MUTATION YET

## Scope

This evidence records the missing Day-12 executable Direct path prepared before the Owner Editing gate. No provider mutation was performed while producing this evidence.

## Implementation

- `0f1a1803ac4da6f1c630c598d596a236594cd86e` / `f3bdae1a0790a955b1d6c4142e013bf38b179ff3` — fail-closed production writer and single-attempt mutation transport;
- `6d65812cb2c1ae9fa43c1874ce5780dd12c4b080` — writer regression tests;
- `c6a8031c5976d9015ac7e4cc9577073f676f910b` + `36b7799dc8f082053ce0c515347aab362fd64ac1` — Direct runtime/live bootstrap aligned to canonical JSON v501 endpoint;
- `1ba2a36320e2de4de88d28493bc7d5fe46c7c874` — first-write acceptance narrowed to current reversible Direct methods;
- `5c3c07e577c682f99add9ea1e09804a0b6fbd6f0` — guarded production execution harness;
- `7b8fc3204a770f049fd29952e513a1cb3c7a14a6` — guarded execution regression tests;
- `cbd537ea978e1781098bca56442e91f4c7cf56fe` + `c582a2475d64e831e6decd9b47a242e6e9727f91` — outcome audit validation moved after `EXECUTION_LOCK_RELEASED`, with regression proof that the reported audit validity covers the complete terminal chain.

Profit Engine CI:
- `33264804958` on `7b8fc3204a770f049fd29952e513a1cb3c7a14a6`: SUCCESS;
- `33264960239` on `c582a2475d64e831e6decd9b47a242e6e9727f91`: SUCCESS.

## First-live writer contract

Allowed live mutation methods are deliberately limited to:
- `campaign.suspend`;
- `campaign.resume`;
- `ad.suspend`;
- `ad.resume`.

The production writer:
- is disabled by default;
- requires an integrity-valid, non-expired one-shot arm;
- requires Day-12 readiness with Direct Editing;
- binds exact readiness/candidate/ControllerPlan/target/method digests;
- allows exactly one dispatch attempt;
- uses exactly one Direct object ID;
- uses JSON v501 service endpoints;
- never automatically retries a mutation, including timeout/429/5xx paths;
- performs fresh preflight + target lock + TOCTOU + runtime kill-switch checks;
- immediately performs exact read-back after the dispatch attempt;
- releases the target lock before final audit validity is reported;
- classifies only `GUARDED_PRODUCTION_LAUNCHED`, `PRODUCTION_WRITE_BLOCKED`, or `PRODUCTION_EXECUTION_UNCERTAIN` in this first-write executor.

## Current Direct API compatibility decision

Legacy `campaign.update_budget` is NOT enabled in the production writer.

Current Direct documentation states that campaign `DailyBudget` stops working and strategy-aware weekly control uses `WeeklySpendLimit`. The Day-11 DailyBudget mapping remains synthetic safety evidence only and cannot be dispatched live.

Budget automation is therefore fail-closed until a separate strategy-aware `WeeklySpendLimit` implementation and Central Brain acceptance are complete. This does not block the Day-12 engineering launch because the first write is intentionally allowed to be the lowest-downside reversible suspend/resume action selected from accepted live evidence.

## Safety result

- real Direct mutation requests during this work: 0;
- advertising spend caused by this work: 0;
- Yandex permission changes caused by this work: 0;
- production writer default: disabled;
- private core: unchanged / proposal-only;
- >20% weekly budget increase rule: unchanged;
- no blind retry: preserved.

## Remaining gate

The owner advertiser is managed by technical Managing Account `reklamadymova`. Canonical accepted evidence still records that relationship as Reading.

Before any real mutation:
1. Owner changes the exact Managing Account relationship Reading -> Editing;
2. fresh Owner UI evidence is bound to the private exact managed target;
3. Direct/Metrica/YAN read certification passes;
4. Central Brain selects exactly one reversible live candidate;
5. all controller and production-writer gates pass.

Until then: `PRODUCTION_WRITE_BLOCKED`.
