# PROFIT ENGINE — HARD 12-DAY LAUNCH PLAN

Status: CANONICAL / OWNER-APPROVED EXECUTION SCHEDULE
Start reference: 2026-08-26
Duration: 12 calendar days to guarded-production launch, excluding unavoidable external-provider approval delays.

Important distinction:
- Day 12 target = working guarded-production Profit Engine on Dilivox.
- Stable proof of `K5 >= 5.0` is an economic validation phase using live data and is not fabricated as an engineering deadline.

## Non-negotiable launch result

By the end of Day 12 the closed loop must exist:

`Yandex Direct -> Dilivox -> Metrica/YAN -> reconciled money ledger -> Profit Engine -> guarded Direct/site action -> measured outcome`.

Routine Direct operation must be machine-capable. Dilivox site-side work is mandatory scope.

---

## Day 1 — Canon + local bootstrap + M0 inventory

OWNER:
- only provide an action if a credential/access cannot be obtained without owner authority.

CENTRAL BRAIN:
- verify canonical docs and branch;
- issue/accept Codex local bootstrap task;
- inspect current Dilivox/Profit Engine repository structure;
- reconcile known access state with repository state;
- define exact M0 evidence gaps.

CODEX:
- create/verify local working folder as a clone of `niknikdym-hue/Dilivox-1`;
- checkout `profit-engine`;
- verify clean sync and toolchain;
- inventory current site implementation, tracking hooks, configs and scripts without exposing secrets.

Deliverables:
- local clone path recorded privately in execution evidence;
- current branch/HEAD evidence;
- M0 inventory report;
- no secret values committed.

Gate D1: repository can be worked locally and all remaining M0 unknowns are explicit.

## Day 2 — Provider read access certification

CENTRAL BRAIN:
- direct the read-access verification sequence;
- accept/reject provider evidence.

CODEX:
- implement minimal diagnostic clients/scripts for Direct, Metrica and YAN statistics where credentials are available;
- map provider IDs to `site_id=dilivox`;
- record weekly Direct budget baseline;
- verify Metrica monetization visibility;
- verify YAN statistics readability.

OWNER:
- only intervene for required provider UI permissions/token issuance.

Gate D2:
- Direct read succeeds;
- Metrica read succeeds;
- YAN statistics read succeeds or is isolated as the sole external blocker;
- identifiers mapped without secrets in GitHub.

## Day 3 — Cloud/data foundation

CENTRAL BRAIN:
- choose only minimal production components required for launch;
- enforce portability and least privilege.

CODEX:
- infrastructure-as-code for Yandex Cloud foundation where credentials allow;
- PostgreSQL schema foundation;
- immutable raw snapshot storage contract;
- Lockbox secret-name contract;
- logging/health checks.

Gate D3:
- runtime can read allowed secret, connect DB, write test raw snapshot and emit logs without broad admin access.

## Day 4 — Read-only ingestion

CODEX:
- Direct collector;
- Metrica collector;
- YAN statistics collector;
- idempotency/retry/freshness/error handling;
- normalized provider-neutral schema with `site_id`.

CENTRAL BRAIN:
- inspect sample raw/normalized outputs and source fidelity.

Gate D4:
- repeatable ingestion from all available providers;
- raw data can reproduce normalized daily facts.

## Day 5 — Dilivox identity and attribution layer

CODEX:
- stable content/story/page IDs;
- `DilivoxSiteAgent` first contract implementation;
- Direct/UTM acquisition preservation;
- experiment ID hooks;
- provider-neutral monetization placement registry foundation.

CENTRAL BRAIN:
- verify no Dilivox-only leakage into shared core.

Gate D5:
- paid acquisition can be associated with stable Dilivox content identity through internal navigation.

## Day 6 — Dilivox first-party events + site safety

CODEX:
- event taxonomy from `DILIVOX_SITE_INTEGRATION.md`;
- mobile/desktop event validation;
- JS/performance error instrumentation;
- experiment exposure hooks;
- kill-switch/fallback foundation.

CENTRAL BRAIN:
- validate event correctness and absence of unnecessary personal data.

Gate D6:
- event counts internally consistent;
- failures do not break normal Dilivox operation;
- site can fail safe if control plane is unavailable.

## Day 7 — Money ledger and reconciliation

CODEX:
- join Direct spend to paid cohorts;
- ingest/associate Metrica YAN monetization;
- reconcile provider YAN statistics;
- calculate `K5_1D`, `K5_7D`, `K5_30D` / observed-vs-estimated states;
- calculate revenue/visit and revenue/acquired-user;
- implement `DATA_QUALITY_HOLD`.

CENTRAL BRAIN:
- inspect economics, discrepancies and actual baseline distance to 5:1.

Gate D7:
- the system can answer with evidence: `what did we spend and what YAN revenue did the acquired cohort produce?`.

## Day 8 — Campaign Factory + Creative Factory foundation

CODEX:
- provider-neutral campaign specification model;
- Yandex Direct adapter supporting create/update lifecycle for supported campaign entities;
- campaign/group/ad/keyword-or-autotargeting construction where applicable;
- image upload/attachment pipeline through supported Direct API;
- tracking parameter generation;
- creative asset registry/versioning;
- automated quality/policy validation hooks;
- dry-run/preview plan output before provider writes.

CENTRAL BRAIN:
- define generation templates, money-oriented experiment structure and acceptance rules;
- accept API lifecycle in non-spending test/dry-run mode.

Gate D8:
- machine can generate a complete valid Direct campaign plan and map every entity to an audit/version record.

## Day 9 — AcquisitionStrategyLab + proxy-value model

CODEX:
- strategy abstraction for CPC, conversion-optimized click payment, pay-for-conversion, value/DRR and Maximum Profit where supported/eligible;
- proxy conversion scoring pipeline;
- segment/cell schema;
- experiment definitions and bounded learning budgets.

CENTRAL BRAIN:
- derive candidate proxy goals from actual Dilivox revenue correlations;
- reject goals that optimize easily but do not predict money.

Gate D9:
- system can compare strategy cells using K5/expected contribution rather than provider vanity metrics.

## Day 10 — ProfitAllocator + stop-loss + site experiment engine

CODEX:
- portfolio allocator across campaign/segment/strategy cells;
- rule engine for LEARN/TEST/SCALE/HOLD/REDUCE/STOP/QUARANTINE;
- stop-loss conditions;
- experiment traffic allocation and control groups;
- Dilivox recirculation experiment hooks;
- monetization/site experiment evaluator;
- auto-pause on significant downside.

CENTRAL BRAIN:
- set conservative launch thresholds from observed data;
- validate portfolio-level logic rather than forcing every cell to equal 5:1.

Gate D10:
- optimizer can replay historical/current data and generate explainable bounded actions with no provider writes.

## Day 11 — Budget Governor + guarded Direct Controller

CODEX:
- write-capable Direct controller behind Budget Governor;
- exact +20% weekly growth invariant;
- owner-approval object for >20%;
- global/site/account/campaign emergency stops;
- audit record for every write;
- idempotency and uncertain-response protection;
- rollback/recovery procedure.

CENTRAL BRAIN:
- adversarially test attempts to bypass budget policy;
- only accept write-enable if every financial guard passes.

OWNER:
- upgrade Direct permission from Reading to Editing only when Central Brain declares the gate ready.

Gate D11:
- no optimizer/provider path can increase weekly budget >20% without explicit Owner approval;
- stop/resume and rollback are tested.

## Day 12 — End-to-end guarded-production launch

CENTRAL BRAIN:
- select minimal real launch scope and test budget;
- inspect all data, compliance and safety gates;
- authorize first bounded machine-operated campaign/experiment only if ready;
- verify full money loop after launch;
- record launch state and next optimization task.

CODEX:
- deploy accepted release;
- run end-to-end smoke/evidence suite;
- fix launch-blocking engineering defects;
- publish exact commit/deployment evidence.

OWNER:
- only provide explicit budget/permission approval if required by current state.

Gate D12 = `GUARDED_PRODUCTION_LAUNCHED` when:
- providers are connected;
- Dilivox instrumentation is live;
- money ledger/reconciliation works;
- Campaign Factory exists;
- optimizer and strategy lab exist;
- Budget Governor is enforced;
- Direct writes are guarded/auditable;
- site experiments have kill switches;
- at least one bounded real closed-loop action can be executed and measured.

---

# Post-launch economic proof phase

Expected observation/optimization period: approximately 14–30 days of live evidence depending on traffic volume and conversion/revenue delay.

Objective:
- discover repeatable segments/strategy/site combinations at or above K5 target;
- stop structurally losing cells;
- improve Dilivox revenue per acquired user;
- validate return-value contribution;
- scale winners under Budget Governor;
- introduce additional monetization providers later without rewriting the core.

No calendar date may be used to fabricate `K5 >= 5.0`; only reconciled money can prove it.

# Schedule enforcement

- Central Brain owns this schedule.
- Every accepted task immediately advances to the next unfinished item.
- External provider waiting time is recorded as `BLOCKED_EXTERNAL_PROVIDER`, while parallel engineering work continues wherever possible.
- Owner is not asked to perform engineering or advertising routine.
