# Task 013 — Metrica goals + read model live PASS

Date: 2026-09-01
Site: `dilivox.ru`
Counter: `110349067`
Status: `LIVE_PROVIDER_VERIFIED`

## Owner-run bounded evidence

The separate Yandex OAuth application `Profit Engine — Metrica Admin` was created for Metrica administration with `metrika:read` + `metrika:write`. The working Direct OAuth application was not modified.

The local installer stored the Metrica-write credential in the dedicated Keychain boundary and performed missing-only goal creation followed by read-back.

Final goal read-back:

- provider goal count: `27`;
- canonical Profit Engine goals missing: `0`;
- invalid canonical identifiers: `0`;
- duplicate canonical identifiers: `0`;
- HTTP status: `200`;
- audit state: `PASS`;
- apply state: `APPLIED_AND_VERIFIED`;
- terminal marker: `METRICA_WRITE_SCOPE_VERIFIED`.

Canonical goals verified:

1. `pe_story_progress_75`;
2. `pe_version_selected`;
3. `pe_story_completed`;
4. `pe_next_story_clicked`;
5. `pe_return_visit`.

All remain proxy goals with `native_bidding_eligible=false` until revenue validation.

## P0 bootstrap after goal closure

The subsequent canonical bootstrap resolved:

- `state=READ_MODEL_READY`;
- `writer_state=LOCKED`;
- `provider_write_allowed=False`;
- `metrica_goals_write_state=NOT_NEEDED`;
- `site_instrumentation_live=false`;
- `site_probe_exit_code=2`;
- `direct_provider_write_requests=0`;
- `direct_writer_authorized=false`.

By runtime definition, `READ_MODEL_READY` is reachable only after:

- YAN→Metrica monetization probe is readable (`yan_total_by_date = PASS`);
- Metrica goals state is `PASS`;
- both exact Dilivox campaigns are present;
- money preflight completed without runtime `ERROR`.

This closes the old Metrica goal-write blocker and the old YAN→Metrica propagation blocker.

## Remaining production blockers

1. Site instrumentation is not yet published on production Tilda. The prepared package is local at `~/.config/profit-engine/tilda/dilivox-profit-engine-head-v1.html` and must be published site-wide, then live-probed.
2. Exact money outcomes for the two Dilivox campaign candidates must be reviewed before selecting any reversible Direct smoke.
3. Direct writer remains locked; this evidence grants no mutation authority.

## Safety

- Direct provider writes during bootstrap: `0`.
- No Direct writer authorization was granted.
- No secrets are stored in this evidence.
- No blind retry occurred.
