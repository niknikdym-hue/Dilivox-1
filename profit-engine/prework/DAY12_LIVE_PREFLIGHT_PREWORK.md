# PROFIT ENGINE — DAY 12 LIVE PREFLIGHT PREWORK

Status: CENTRAL BRAIN PREWORK / NOT CANONICAL
Updated: 2026-08-28
Branch: `central-brain/day12-live-preflight-prework`
Depends on: Task 011R accepted

## Purpose

Prepare the Day-12 live path without enabling Direct Editing or sending any provider mutation while Task 011R is active.

Target transition after Task 011R acceptance:

`Task 011R accepted -> Owner enables Direct Editing -> live credential/read doctor -> exact target preflight -> one bounded guarded mutation -> read-back -> immutable audit -> launch decision`.

## Hard gates before any write

1. Task 011R accepted by Central Brain.
2. Direct access explicitly changed by Owner from Reading to Editing only after acceptance.
3. Live Direct credential doctor passes with secret-safe local credential loading.
4. Live Metrica and YAN read certification status is known; unresolved money/data-quality state cannot authorize SCALE/TEST.
5. Exact provider target resolves from trusted provider mapping; never infer by name, URL or fuzzy match.
6. Fresh provider preflight snapshot passes integrity, freshness and DQ gates.
7. Current state still matches the accepted controller plan immediately before dispatch.
8. Exact ActionProposal and Governor evidence are current and integrity-valid.
9. If weekly increase >20%, exact trusted OwnerApprovalEvidence is present and current.
10. Kill switches rechecked immediately before dispatch.
11. Mutation cadence proves zero prior autonomous campaign-budget mutations for the same campaign/day when action is a budget update.
12. Exact per-target execution lock is acquired.
13. One request contains exactly one provider object.
14. Exact normalized request payload is derived from the immutable controller plan and bound to provider target and authorized budget/state.
15. Production writer enablement is explicit, narrow, auditable and reversible; no generic always-on write mode.

## First real mutation selection

The first Day-12 mutation must be selected for minimum downside and maximum reversibility.

Preferred order for candidate evaluation:

1. STOP/suspend action already justified by safety/stop-loss evidence;
2. resume only when exact prior state and current guards prove it is intended;
3. bounded budget update only when money evidence is fully accepted and proposed growth is within approved envelope;
4. no create/add/delete/archive/moderation/strategy-migration action for first launch mutation.

Central Brain chooses the actual candidate from live evidence; no fixture or prework document preselects a campaign.

## Live execution contract

The first write must produce an append-only evidence chain including at minimum:

- accepted public/private decision refs;
- ActionProposal digest;
- Governor evidence digest;
- Owner approval digest if required;
- provider target identity;
- fresh preflight digest;
- current-day cadence evidence;
- execution-lock evidence;
- exact normalized request digest;
- dispatch-start record;
- provider response metadata including RequestId/Units when returned;
- read-back record;
- final classification;
- rollback candidate derived from preflight;
- secret-safe redaction proof.

## Uncertain response rule

A timeout or ambiguous response never triggers an immediate retry.

Sequence:

`dispatch once -> read back -> classify applied/unchanged/unexpected -> only then decide whether a separate bounded retry plan is permitted`.

No blind retries and no automatic loops.

## Launch classifications

Recommended Day-12 terminal classifications:

- `GUARDED_PRODUCTION_LAUNCHED` — one real bounded mutation applied and verified by read-back with complete audit evidence;
- `PRODUCTION_WRITE_BLOCKED` — a safety/provider/credential/data-quality gate prevented dispatch; no mutation sent;
- `PRODUCTION_EXECUTION_UNCERTAIN` — dispatch may have occurred but state could not be safely verified; stop for review;
- `PRODUCTION_ROLLBACK_VERIFIED` — bounded rollback separately authorized, applied and verified;
- `PRODUCTION_ROLLBACK_BLOCKED` — rollback unsafe or not authorized; remain held.

## Safety

This prework itself authorizes nothing:

- Direct remains Reading;
- provider requests = 0;
- advertising spend = 0;
- production writer remains disabled;
- no credentials or provider IDs are stored here;
- no private optimizer formulas are exposed.

## Owner action boundary

The Owner will be asked to switch Direct Reading -> Editing only after Task 011R acceptance. Enabling Editing is not equivalent to authorizing a write; every Day-12 write still requires all controller/live gates above.
