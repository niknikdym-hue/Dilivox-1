# CODEX TASK 009 — ACQUISITION STRATEGY LAB / PUBLIC-SAFE CONTRACTS

Status: READY FOR EXECUTION
Owner: Central Brain
Executor: Codex
Repository: `niknikdym-hue/Dilivox-1`
Canonical branch: `profit-engine`
Launch day: Day 9

## READ FIRST — MANDATORY

1. `profit-engine/PROJECT_HANDOFF.md`
2. `profit-engine/OWNER_DECISIONS.md`
3. `profit-engine/PROJECT_STATE.md`
4. `profit-engine/HARD_12_DAY_LAUNCH_PLAN.md`
5. `profit-engine/DAY9_ACQUISITION_STRATEGY_LAB_DESIGN.md`
6. `profit-engine/ACQUISITION_STRATEGY_LAB.md`
7. `profit-engine/PRIVATE_CORE_BOUNDARY.md`
8. `profit-engine/PRIVATE_CORE_REPOSITORY_BOOTSTRAP.md`
9. Task 007 Central Brain acceptance evidence
10. Task 008 evidence

## BASELINE / SYNC

Task 008 accepted by Central Brain at final Codex HEAD:

`6cdfe596a2417655d844b626bfefac8c636e868f`

Central Brain advanced `origin/profit-engine` after acceptance with Day-9 canon. Therefore:

- `git fetch origin` first;
- safe fast-forward only;
- use current `origin/profit-engine` as actual baseline;
- no force push;
- do not overwrite Central Brain commits.

Canonical local workspace:

`~/Documents/New project/Profit Engine/Dilivox-1`

Separate site/Tilda workspace remains READ_ONLY:

`~/Documents/New project/Dilivox`

## OBJECTIVE

Implement a public-safe AcquisitionStrategyLab foundation that answers:

`which strategy cells have sufficient accepted money evidence to enter a bounded experiment preview, which are held and why, and what versioned evidence package can be sent to the future private decision core?`

Task 009 MUST NOT answer which strategy wins in public code.

## CRITICAL PRIVATE-CORE GATE

The private repository `niknikdym-hue/profit-engine-core` is not currently visible to the connected GitHub integration at task issue time.

Therefore public Task 009 must:

- implement public-safe evidence/experiment contracts;
- return `BLOCKED_PRIVATE_CORE_REQUIRED` for ranking, learned scoring, winner selection or allocation requests;
- contain no proprietary weights/thresholds/ranking logic.

Do NOT wait for private-core creation to complete the public-safe Task 009 engineering.

## REQUIRED IMPLEMENTATION

### A. STRATEGY CELL MODEL

Implement immutable/deterministic `StrategyCell` v1 with at least:

- `cell_version`;
- `site_id`;
- `cell_key`;
- Campaign Factory preview/spec digest ref;
- strategy kind;
- landing content ID;
- public-safe dimensions (optional device/geo/schedule/audience-query class);
- measurement kind;
- measurement/evidence refs;
- attribution grade;
- reconciliation state;
- money/source state;
- cohort linkage flag;
- maturity/late-arrival state;
- proxy goal ref/state when applicable;
- eligibility result;
- hold reasons;
- deterministic digest.

No private provider IDs/mappings/secrets in fixtures.

### B. STRATEGY KINDS

Validate public-safe requests for:

- `cpc`;
- `conversion_click`;
- `pay_for_conversion`;
- `value_crr`;
- `maximum_profit`;
- future versioned provider-native kinds via capability metadata.

Use the accepted Day-8 capability model where practical rather than inventing an unrelated duplicate.

Task 009 validates eligibility only and does not choose the commercial winner.

### C. MONEY EVIDENCE GATE

Consume accepted generic money-measurement structures from Task 007.

Requirements:

- `optimizer_consumable=false` -> cell held;
- non-MATCHED reconciliation -> cell held;
- NOT_COMPUTABLE -> cell held;
- immature/late-arrival-open cohort -> cell held;
- missing provenance -> cell held;
- incompatible measurement kind -> cell held;
- C-grade Metrica-only evidence must not become proven acquisition-cohort evidence;
- E/UNJOINABLE cannot enter autonomous experiment evidence;
- A/B and valid D may be eligible only if measurement itself passes all accepted money gates.

Do not recompute or upgrade evidence quality in Strategy Lab.

### D. PROXY SIGNAL CONTRACT

Model explicit states:

- `PROXY_UNPROVEN`;
- `PROXY_EVIDENCE_PENDING`;
- `PROXY_MONEY_ASSOCIATION_SUPPORTED`;
- `PROXY_REJECTED`.

A proxy may reference supporting evidence but Task 009 must not invent a monetary value/weight.

Unproven/pending/rejected proxy cannot unlock a held strategy cell.

### E. EXPERIMENT PREVIEW

Implement deterministic `ExperimentPreview` v1 with:

- experiment key/version;
- one explicit control cell;
- one or more treatment cells;
- hypothesis label;
- primary measurement kind;
- observation window;
- late-arrival/maturity requirement;
- generic evidence prerequisites;
- campaign preview refs;
- budget proposal refs;
- guardrail refs;
- explicit holdout/control;
- prerequisite errors/holds;
- preview digest;
- `provider_write_allowed=false`;
- `provider_requests=0`;
- `advertising_spend=0`.

The preview must not launch an experiment.

### F. PUBLIC DECISION BOUNDARY

Implement a versioned public evidence package for the future private core.

It may contain:

- cell refs/digests;
- accepted measurement refs/states;
- experiment preview ref/digest;
- generic capability/safety state;
- no secrets/private mappings.

Any public API request to:

- rank cells;
- select winner;
- choose scale candidate;
- allocate budget;
- apply learned weight;

must fail closed / return:

`BLOCKED_PRIVATE_CORE_REQUIRED`.

No hidden ranking by list order, max K5, sorting, score, weighted sum or similar.

### G. RESULT STATES

Use only public-safe states equivalent to:

- `CELL_ELIGIBLE_FOR_EXPERIMENT_PREVIEW`;
- `CELL_HELD_DATA_QUALITY`;
- `CELL_HELD_ATTRIBUTION`;
- `CELL_HELD_MATURITY`;
- `CELL_BLOCKED_MONEY_EVIDENCE`;
- `CELL_BLOCKED_PROVIDER_CAPABILITY`;
- `EXPERIMENT_PREVIEW_VALID`;
- `EXPERIMENT_PREVIEW_INVALID`;
- `BLOCKED_PRIVATE_CORE_REQUIRED`.

There must be no `WINNER`, `SCALE_SELECTED`, `ALLOCATED`, `EXECUTED`, `LAUNCHED` public state.

### H. CLI / FIXTURES

Provide deterministic fixture/CLI scenarios that prove at minimum:

1. A-grade reconciled mature cohort K5 -> eligible cell;
2. B-grade reconciled mature cohort K5 -> eligible cell;
3. C-grade period evidence can remain diagnostic but cannot become proven cohort evidence;
4. E-grade -> held;
5. UNJOINABLE -> held;
6. PENDING reconciliation -> held;
7. DRIFT -> held;
8. BASIS_BLOCKED -> held;
9. SOURCE_MISSING -> held;
10. immature/late-arrival cohort -> held;
11. upstream `optimizer_consumable=false` -> held;
12. missing provenance -> held;
13. unsupported strategy -> provider-capability block;
14. unproven proxy cannot unlock cell;
15. supported proxy can be referenced without money weight;
16. control+treatment experiment preview valid with eligible cells;
17. held treatment -> experiment preview invalid;
18. identical semantic input -> deterministic digests;
19. sensitive ranking/winner/allocate request -> `BLOCKED_PRIVATE_CORE_REQUIRED`;
20. `provider_requests=0`, `advertising_spend=0`, `provider_write_allowed=false`;
21. all previous Python/Node tests remain green.

### I. CI / SAFETY SCANS

Final origin HEAD must have GREEN `Profit Engine CI`.

Also perform/report:

- `git diff --check`;
- secret/private-data scan;
- provider-write reachability scan;
- ranking/winner-selection/proprietary logic scan;
- ensure no public test/fixture contains real provider IDs/mappings or production data.

## FORBIDDEN

- Direct writes;
- provider add/update/delete/suspend/resume/moderation;
- campaign/group/ad/keyword/image mutation;
- budget mutation;
- advertising spend;
- Tilda production publication;
- production Dilivox mutation;
- YAN code mutation;
- paid Cloud apply;
- secrets/private mappings/raw production exports in Git;
- proprietary scoring/ranking/winner selection/learned thresholds in public repo;
- force push;
- merge to `main`.

## LIVE CREDENTIAL STATUS

Provider OAuth certification remains an external blocker. Task 009 is fixture/source-contract capable and must not idle on credentials.

## EVIDENCE

Create:

`profit-engine/evidence/TASK-009-ACQUISITION-STRATEGY-LAB.md`

Evidence must include:

- baseline/final/origin SHAs;
- StrategyCell contract summary;
- eligibility/hold matrix;
- strategy capability results;
- proxy-state behavior;
- ExperimentPreview result;
- private decision boundary proof;
- explicit proof that no ranking/winner path exists;
- provider requests/spend/write state;
- tests/checks/CI run;
- files changed;
- blockers;
- recommended Task 010 boundary.

## FINAL REPORT FORMAT

Return:

- `STATUS: COMPLETE | PARTIAL | BLOCKED`
- `BASELINE_HEAD:`
- `FINAL_HEAD:`
- `ORIGIN_PROFIT_ENGINE:`
- `WORKTREE:`
- `STRATEGY_CELL_MODEL:`
- `MONEY_EVIDENCE_GATE:`
- `STRATEGY_CAPABILITY:`
- `PROXY_CONTRACT:`
- `EXPERIMENT_PREVIEW:`
- `PRIVATE_CORE_GATE:`
- `PROVIDER_REQUESTS:`
- `ADVERTISING_SPEND:`
- `PROVIDER_WRITE_ALLOWED:`
- `SECRET_SAFETY:`
- `FILES_CHANGED:`
- `COMMIT_SHA:`
- `TESTS/CHECKS:`
- `BLOCKERS:`
- `RECOMMENDED_TASK_010:`

Do not self-accept. Central Brain will inspect origin/evidence/CI and immediately advance the launch plan.
