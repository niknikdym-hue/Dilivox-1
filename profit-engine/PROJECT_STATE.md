# PROFIT ENGINE — PROJECT STATE

Status: IMPLEMENTATION ACTIVE / DAY 12 — LIVE GUARDED PRODUCTION LAUNCH GATE
Updated: 2026-08-29
Canonical public branch: `profit-engine`
Private core branch: `main`

## Objective

Launch the guarded production loop:

`Yandex Direct -> Dilivox -> behavior -> YAN revenue -> attribution/reconciliation -> private proposal-only core -> ActionProposal -> Budget Governor -> guarded Direct controller -> measured outcome`.

First production site: `site_id=dilivox` / `dilivox.ru`.
Target: `1 RUB Direct spend -> 5 RUB YAN advertising revenue attributable to the acquired Dilivox audience`.
This is a target, not a claimed result.

## Locked governance

- private core emits proposals only and never writes to providers;
- no provider/site mutation before the canonical Day-12 live gates pass;
- automatic weekly budget increase above +20% requires exact explicit Owner approval;
- one autonomous campaign budget mutation per campaign/day at launch;
- exactly one provider object per first launch write;
- no blind retry;
- no secret values in Git/chat/issues/logs;
- chat is not source of truth.

## Current verified repository state

Public: `niknikdym-hue/Dilivox-1`, branch `profit-engine`.

Current Central-Brain implementation chain after the latest safety fix:
- `2520838a4138212c8cbf2a70791955da86fd4d63` — local fail-closed Owner UI permission evidence loader;
- `79e587ad20b7412f006d32cc5aaf04eb5f9102a9` — readiness binds Managing Account permission to Owner UI evidence rather than an impossible provider-derived value;
- `130dd1c49f998813bed8a30650dc6172dc394551` — readiness CLI evidence intake;
- `0295321ee412b28b3095d4c807886aa679e28839` — readiness regressions;
- `141251114b2e9590b9a982c4e4755cee9ed5dc06` — evidence-loader negative tests;
- `ff14bc5204695c320b2173c794a3b9f0ecb9ac53` — canonical evidence for this fix.

CI `33224867707` on `141251114b2e9590b9a982c4e4755cee9ed5dc06`: SUCCESS. The evidence-only commit that follows does not change runtime behavior.

Private core: `niknikdym-hue/profit-engine-core`, `main` = `76b1b8670690f102a045243760dfe3d1e58513d5`.
Private CI `33182663547`: SUCCESS.
Private core remains proposal-only, unchanged by Day 12, with no provider write authority.

Open launch-critical issues:
- public: `#19 — Profit Engine Task 012 — Live guarded production launch`;
- private core: none.

No new Codex implementation exists after the previously accepted Day-12 pre-live scaffold. Current Day-12 safety/reconciliation work was advanced directly by Central Brain.

## Accepted baseline

Tasks 001–010R: ACCEPTED.
- public Day-10 contract: `98c6d3f0c0105c30cfc90a6d5fdf653c2aceb8d6`;
- private accepted contract: `1709925f5b2d29f9c038dde7caca8054b51eea6f`.

Task 011 + 011R: ACCEPTED / DAY 11 COMPLETE.
- Central Brain evidence: `profit-engine/evidence/TASK-011-CENTRAL-BRAIN-ACCEPTANCE.md`;
- final controller: `a494d30b49c8d11687be56cdab870a5d83356e02`;
- CI `33187660342`: GREEN.

Accepted controller invariants include exact proposal/Governor binding, trusted Owner approval >20%, exact target identity, fresh preflight + TOCTOU, kill-switch recheck, current-day cadence, per-target lock, one-object request binding, read-back, no blind retry, immutable-preflight rollback source and production writer disabled by default.

## Day-12 canonical authority

Tracking issue: `#19`.

Authority:
- `profit-engine/DAY12_LIVE_PRODUCTION_LAUNCH_DESIGN.md`;
- `profit-engine/DAY12_PROVIDER_LIVE_CERTIFICATION.md`;
- `profit-engine/DAY12_FIRST_WRITE_ACCEPTANCE_MATRIX.md`;
- `profit-engine/tasks/TASK-012-LIVE-GUARDED-PRODUCTION-LAUNCH.md`.

Accepted pre-live evidence:
- `profit-engine/evidence/TASK-012-PRE-EDITING-READINESS-HARNESS.md`;
- `profit-engine/evidence/TASK-012-CENTRAL-BRAIN-PRELIVE-ACCEPTANCE.md`.

Live read evidence:
- `profit-engine/evidence/TASK-012-LIVE-PROVIDER-BINDING.md`.

Direct permission/identity rework evidence:
- `profit-engine/evidence/TASK-012-DIRECT-PERMISSION-READ-PROBE.md`;
- `profit-engine/evidence/TASK-012-PROVIDER-PERMISSION-FAIL-CLOSED-FIX.md`;
- `profit-engine/evidence/TASK-012-DIRECT-MANAGER-TARGET-MISBINDING-REWORK.md`;
- `profit-engine/evidence/TASK-012-OWNER-UI-PERMISSION-EVIDENCE-GATE.md`.

## Current Direct truth

The owner advertiser account is distinct from the technical Direct Managing Account/operator `reklamadymova`.

The previous bootstrap that treated `reklamadymova` as the managed target is REWORKED and must never be used as launch evidence.

Current runtime rules:
- operator and managed target must be distinct;
- exact managed target login is private and never printed by the bootstrap;
- Direct doctor proves OAuth/operator identity and managed-target read visibility separately;
- advertiser `Clients.get` Grants/Representatives are not used to infer the separate Managing Account `Reading/Editing` relationship;
- manager permission remains fail-closed unless there is fresh explicit Owner UI evidence.

## Owner UI permission evidence gate — VERIFIED / GREEN

Launch-critical finding: after the manager-target REWORK, the doctor correctly returned manager permission `UNKNOWN`, but readiness still required provider-derived `EDITING`. That made the Day-12 transition unreachable even after a real Owner UI permission change.

Fix:
- local Owner evidence lives outside the repository and must be `0600`;
- it binds exact operator, SHA-256 of exact managed target, permission exactly `EDITING`, Direct UI source, explicit Owner confirmation, fresh timezone-aware timestamp and integrity digest;
- missing/stale/future/tampered/mismatched evidence fails closed;
- plaintext managed target is not stored in the evidence;
- Owner evidence is accepted only on the Managing Account UI path;
- provider-derived `READING` outside that path cannot be overridden.

Authority boundary: this evidence is NOT cryptographic authentication and NOT write authorization. It may only let readiness reach `READY_FOR_LIVE_CANDIDATE_SELECTION` after all read doctors PASS. `provider_write_allowed=false`, production writer remains disabled, real provider requests remain 0, advertising spend remains 0.

## Current first incomplete canonical gate

The Managing Account relationship is still canonically recorded as `Reading`; no later accepted evidence shows it changed.

Single next Owner-only action:

`Yandex Direct: for the owner advertiser account managed by reklamadymova, change Managing Account access from Reading to Editing.`

Do not perform any other Direct mutation.

That UI change alone authorizes no provider write.

After explicit Owner confirmation, Central Brain will bind fresh Owner UI evidence to the private exact managed target, run operator/target + Metrica + YAN read-only certification, and only then consider exactly one live candidate.

## First real mutation boundary

Only after accepted Owner Editing evidence, exact managed-target binding, all live doctors PASS, exact Central Brain candidate acceptance and all controller gates:
1. fresh provider preflight;
2. proposal/Governor/Owner approval revalidation;
3. cadence + exact lock;
4. fresh TOCTOU read;
5. runtime kill-switch recheck;
6. exact one-object request from immutable plan;
7. narrow one-shot writer arming;
8. one Direct dispatch;
9. read-back;
10. immutable audit;
11. rollback only if separately guarded/authorized.

Any failed gate => zero dispatches.

## Economic proof boundary

Engineering launch does not prove `K5 >= 5.0`. Economic proof requires reconciled live Direct spend + Metrica-attributed YAN revenue + YAN control totals over mature periods/cohorts.

## Resume protocol

Verify actual public/private HEADs first, then read this file, the four Day-12 authority documents, the four latest Direct/Owner evidence files above, and issue #19. Never infer authority from chat or stale status text.
