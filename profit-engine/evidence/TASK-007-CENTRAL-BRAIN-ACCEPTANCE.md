# TASK 007 — CENTRAL BRAIN ACCEPTANCE

Status: ACCEPTED AFTER CENTRAL BRAIN HOTFIX
Updated: 2026-08-27

## Accepted implementation

Codex implementation:
`ffd097881cf1006a54035b7f32da8101e34dd0be`

Central Brain found one launch-critical defect before acceptance: K5 measurements did not uniformly block non-MATCHED reconciliation states. In particular, mature/proven cohort K5 could remain optimizer-consumable with `DRIFT`, `BASIS_BLOCKED`, `SOURCE_MISSING`, or `PENDING` reconciliation.

Central Brain corrections:

- `f6579eac2030084fb7d27fac0b89a99d36371b2f` — added a common reconciliation gate to period/cohort K5 and required `MATCHED` reconciliation for optimizer consumption;
- `e5b21baa1622e77e5d1e9408f799a5843e51f2d4` — added regression coverage for every non-MATCHED reconciliation state and ensured revenue-per-unit diagnostics remain non-consumable while reconciliation is pending.

Accepted Task 007 code state:
`e5b21baa1622e77e5d1e9408f799a5843e51f2d4`

## Permanent CI gate

Central Brain added `.github/workflows/profit-engine-ci.yml` and corrected checkout depth.

Verification descendant:
`7bf092c63c4d04f71eb5d48192395845a110f206`

GitHub Actions `Profit Engine CI` run #2:

- Python: `60/60 PASS`;
- Node: `22/22 PASS`;
- JSON artifacts: `PASS`;
- diff whitespace check: `PASS`.

## Acceptance decision

`TASK_007 = ACCEPTED`

Accepted semantics include:

- explicit attribution grades;
- no date-only attribution;
- Metrica YAN revenue as attribution view;
- YAN Statistics as reconciliation/control total only;
- no double-counting;
- distinct period K5 vs cohort K5;
- original cohort-spend denominator for 1D/7D/30D;
- late-arrival versioning;
- all material reconciliation/attribution/money uncertainty blocks optimizer consumption;
- no real K5 claim from fixtures.

Live provider reads remain `BLOCKED_EXTERNAL_PROVIDER_CREDENTIAL` and continue in parallel.
