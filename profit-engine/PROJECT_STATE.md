# PROFIT ENGINE — PROJECT STATE

Status: FOUNDATION / DESIGN LOCK-IN
Updated: 2026-08-25

## Current objective

Build a highly automated multi-site Profit Engine that closes the loop:

`Traffic spend -> real user -> site behavior -> YAN revenue -> attribution -> prediction -> decision -> Direct control`.

First production site: Dilivox (`site_id=dilivox`).

Initial Dilivox target: `YAN_ROAS_30D >= 5.0` where achievable through legal optimization of real traffic, content engagement, recirculation, ad yield, and campaign efficiency.

## Current state

- Canonical project direction created under `profit-engine/`.
- Engine is multi-site by design; Dilivox is adapter/site #1, not hard-coded as the core.
- Recommended production infrastructure: Yandex Cloud.
- External data/control providers: Yandex Direct API, Yandex Metrica API, YAN Partner Statistics API, first-party Dilivox events.
- Recommended data plane: Managed PostgreSQL + Object Storage.
- Recommended secrets plane: Lockbox.
- Recommended runtime: Serverless Containers initially; move to dedicated compute only when load or latency justifies it.
- Owner budget guardrail is LOCKED: weekly budget increases over +20% require explicit owner approval.

## Immediate next milestone: M0 — Measurement and Access Readiness

1. Inventory existing Dilivox Yandex Metrica counter(s), YAN site/resource/block setup, and Direct account/campaign state.
2. Create or designate a dedicated technical Yandex ID for API operations where supported.
3. Configure delegated access with least privilege; do not share the owner's primary password.
4. Register OAuth application(s) and obtain required API access for Direct/Metrica/YAN statistics.
5. Connect YAN monetization reports to the Dilivox Metrica counter.
6. Define first-party Dilivox event taxonomy and deploy instrumentation.
7. Establish baseline metrics by story/page/device/source.
8. Only after data reconciliation passes, enable write-capable Direct automation in shadow mode, then guarded autopilot.

## Core success metrics

- acquisition spend;
- YAN estimated/reconciled revenue;
- `YAN_ROAS_1D`, `YAN_ROAS_7D`, `YAN_ROAS_30D`;
- YAN revenue per acquired user/visit;
- CPMV;
- requests, renders, visible shows;
- stories/pages per acquired user;
- completion rate;
- next-content rate;
- return rate;
- data reconciliation error;
- budget-controller decisions and realized outcome.

## Resume protocol

On any new chat/session:

1. read `profit-engine/README.md`;
2. read this file;
3. read `OWNER_DECISIONS.md`;
4. read `ARCHITECTURE.md`;
5. inspect current repository `main`;
6. continue the first incomplete milestone from this file rather than re-planning from chat memory.

## Safety / honesty invariant

Never fabricate a 5x result. The 5x number is the optimization target. Actual ROAS must come from reconciled data. No campaign is scaled based on insufficient sample size or unreconciled revenue data.
