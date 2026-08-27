# Data foundation

`migrations/` contains ordered PostgreSQL migrations. `raw-snapshot-envelope.schema.json`
is the public immutable-object envelope contract. No production payload belongs
in this repository.

The local adapter writes under `~/.local/share/profit-engine/raw` by default.
Override that location only with `PROFIT_ENGINE_LOCAL_RAW_ROOT`; keep the target
outside Git. The future Object Storage adapter must preserve the same logical key,
hash verification, create-only semantics, and conflict behavior.
