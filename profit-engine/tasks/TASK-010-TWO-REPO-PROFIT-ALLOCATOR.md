# CODEX TASK 010 — TWO-REPO PROFIT ALLOCATOR + MATERIALIZATION + BUDGET GOVERNOR

Status: READY FOR EXECUTION
Owner: Central Brain
Executor: Codex
Launch day: Day 10

## Repositories

Public:
- `niknikdym-hue/Dilivox-1`
- branch `profit-engine`
- local `~/Documents/New project/Profit Engine/Dilivox-1`

Private:
- `niknikdym-hue/profit-engine-core`
- branch `main`
- canonical local path `~/Documents/New project/Profit Engine/profit-engine-core`

If private clone is absent, clone it normally with existing GitHub auth. Do not request or expose credentials.

## Read first

Public:
1. `profit-engine/PROJECT_STATE.md`
2. `profit-engine/DAY10_PROFIT_ALLOCATOR_AND_GUARDRAILS_DESIGN.md`
3. Task 009 evidence
4. `profit-engine/PRIVATE_CORE_REPOSITORY_BOOTSTRAP.md`

Private:
1. `PROJECT_AUTHORITY.md`
2. `PROJECT_STATE.md`
3. `PUBLIC_CONTRACT_VERSION.md`

## Phase order — mandatory

### Phase A — public contracts/materialization first

Implement in public repo:

1. READ_ONLY Metrica attribution-aware normalized fact using named dimensions and explicit attribution model;
2. deterministic ledger materializer from immutable normalized facts into accepted acquisition/reconciliation/K5 interfaces;
3. `ActionProposal v1` public-safe contract;
4. Budget Governor v1 with the hard +20% weekly Owner rule;
5. generic data-quality/kill-switch/stop-loss structural guards;
6. site experiment action-intent contract;
7. tests/fixtures/evidence.

No proprietary ranking/weights in public code.

Commit/push public Phase A and require GREEN Profit Engine CI.

Then update private `PUBLIC_CONTRACT_VERSION.md` to pin the exact accepted Phase-A public SHA before implementing private decision logic.

### Phase B — private ProfitAllocator

Implement only in `profit-engine-core`:

- private evidence input envelope compatible with the pinned public contract;
- sensitive strategy ranking / winner selection;
- expected contribution/confidence model;
- private stop-loss / scale / reduce / test thresholds;
- allocation proposal logic;
- public-safe ActionProposal output adapter;
- deterministic private decision digest;
- tests and evidence.

Private formulas/weights/thresholds MUST NOT be copied into public repo or public evidence.

Private core has no provider client, transport, OAuth handling or site write path.

## Public ActionProposal requirements

Kinds:
`LEARN`, `TEST`, `SCALE`, `HOLD`, `REDUCE`, `STOP`, `QUARANTINE`.

Every proposal carries:
- version/id/digest/site;
- target refs;
- public evidence package digest;
- measurement/provenance refs;
- proposed weekly budget/current baseline/delta when applicable as Decimal strings;
- guard requirements;
- owner approval requirement;
- private decision digest/reference only;
- audit metadata;
- `requires_budget_governor=true`;
- `provider_write_allowed=false`.

## Budget Governor hard rules

- `<= +20%` weekly increase: may become `GOVERNOR_READY_FOR_DAY11_CONTROLLER` only if ALL evidence/safety guards pass;
- `> +20%`: ALWAYS `PENDING_OWNER_APPROVAL` until explicit Owner approval evidence exists;
- no current budget / malformed Decimal -> blocked;
- DATA_QUALITY_HOLD / non-MATCHED / NOT_COMPUTABLE / immature / non-consumable evidence -> SCALE/TEST blocked;
- global kill switch -> blocked;
- STOP/HOLD/QUARANTINE may pass structural safety if valid;
- governor never calls Direct.

Test boundary exactly at 20.00% vs 20.01%.

## Materialization rules

- no date-only campaign attribution;
- preserve named Metrica dimensions and money provenance;
- unknown/missing attribution dimension -> hold;
- YAN remains reconciliation control total only;
- no Metrica+YAN double-count;
- immutable raw history never rewritten;
- late arrivals create new derived versions;
- cohort K5 requires proven cohort linkage;
- non-MATCHED reconciliation is never consumable.

## Private decision rules

Private core may only rank cells/evidence that the public gates mark eligible/consumable.

Private output may include private score/confidence internally, but public output exposes only proposal/rationale codes and a private decision digest.

Never store production credentials or raw production exports in either repo.

## Forbidden in both repos

- Direct/provider write requests;
- campaign/ad/group/keyword/image mutation;
- budget mutation/spend;
- Tilda publication or production site mutation;
- paid Cloud apply;
- secrets in Git;
- force push;
- merge to public `main`.

## Required tests

At minimum all 15 scenarios in `DAY10_PROFIT_ALLOCATOR_AND_GUARDRAILS_DESIGN.md`, plus all prior public tests and private bootstrap tests.

Public final CI: GREEN.
Private final CI: GREEN.

## Evidence

Public:
`profit-engine/evidence/TASK-010-PUBLIC-MATERIALIZER-GUARDS.md`

Private:
`evidence/TASK-010-PRIVATE-PROFIT-ALLOCATOR.md`

## Final report

Return:
- STATUS
- PUBLIC_BASELINE / PUBLIC_FINAL / PUBLIC_ORIGIN
- PRIVATE_BASELINE / PRIVATE_FINAL / PRIVATE_ORIGIN
- MATERIALIZATION
- ACTION_PROPOSAL
- BUDGET_GOVERNOR
- DATA_QUALITY_STOP_LOSS_GUARDS
- PRIVATE_ALLOCATOR
- PUBLIC_CONTRACT_PIN
- PROVIDER_REQUESTS
- ADVERTISING_SPEND
- PUBLIC_CI
- PRIVATE_CI
- SECRET_SAFETY
- FILES_CHANGED_PUBLIC
- FILES_CHANGED_PRIVATE
- BLOCKERS
- RECOMMENDED_TASK_011

Do not self-accept. Central Brain performs acceptance.
