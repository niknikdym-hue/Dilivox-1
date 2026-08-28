# Profit Engine read-only provider runtime

Minimal Python 3.12+ diagnostics for Yandex Direct API v5, Yandex Metrica,
and YAN Partner Statistics. The runtime uses only the Python standard library.
It contains no provider write methods and exposes `READ_ONLY = True`.

Run fixture tests:

```bash
python3 -m unittest discover -s profit-engine/runtime/tests -v
```

Run the provider doctor:

```bash
PYTHONPATH=profit-engine/runtime python3 -m profit_engine_runtime.doctor
```

The default private registry path is:

```text
~/.config/profit-engine/sites/dilivox.json
```

Copy the public example from `profit-engine/config/sites/dilivox.example.json`
to that path, replace only private mapping placeholders locally, and restrict it
to mode `0600`. Never put tokens in the registry.

## Secret references

The default ephemeral environment names are:

- `PROFIT_ENGINE_YANDEX_OAUTH_TOKEN`: shared OAuth token carrying
  `direct:api` and `metrika:read` scopes;
- `PROFIT_ENGINE_YAN_STATS_TOKEN`: YAN Statistics API OAuth token.

To avoid shell history, use an interactive hidden read in the current shell, or
store the values in macOS Keychain and set the registry token reference to:

```text
keychain:<service>/<account>
```

The runtime invokes `security find-generic-password -w` directly and never logs
its output. Environment references use `env:<VARIABLE_NAME>`.

Minimum Owner actions when credentials are absent:

1. Authorize the existing Profit Engine OAuth application under the technical
   Yandex identity with `direct:api` and `metrika:read`; securely expose the
   resulting token through the shared token reference.
2. In the YAN interface, use API → “Receive an OAuth token for the Statistics
   API” for an identity that can read Dilivox; securely expose it through the
   YAN statistics token reference. Do not use the Block Configuration API token.

Provider endpoints and authorization shapes follow official Yandex contracts:
Direct uses JSON v5 POST requests whose body method is `get`; Metrica and YAN
Statistics use GET. HTTP POST in the Direct client does not imply a provider
write—the only JSON-RPC method present is `get`.

## Data adapters

`contracts.py` defines provider-neutral relational, raw object, secret, health,
and audit interfaces. `raw_store.py` implements a create-only local raw adapter
whose default root is outside this repository. `data_quality.py` prevents held
or reconciliation-not-ready datasets from being optimizer-consumable.

Run deterministic fixture ingestion without credentials:

```bash
PYTHONPATH=profit-engine/runtime python3 -m profit_engine_runtime.collector_cli all --fixture --raw-root /tmp/profit-engine-fixture-raw
```

The CLI accepts `direct`, `metrica`, `yan`, or `all`. Live mode always runs the
provider doctor first and proceeds only for providers with `PASS`. Raw storage
and integrity verification happen before deterministic normalization.

## Campaign Factory Day-8 dry-run

Build a deterministic credential-free fixture preview (no provider requests or spend):

```bash
PYTHONPATH=profit-engine/runtime python3 -m profit_engine_runtime.campaign_factory_cli valid \
  --registry profit-engine/sites/dilivox/content-registry.json
```

Fixture scenarios are `valid`, `missing-content`, `invalid-tracking`, and
`invalid-capability`. Future provider operations are represented only as inert
data intents with `executable=false`.

## Acquisition Strategy Lab Day-9 public contracts

Build deterministic, credential-free StrategyCell fixtures:

```bash
PYTHONPATH=profit-engine/runtime python3 -m profit_engine_runtime.strategy_lab_cli eligible
PYTHONPATH=profit-engine/runtime python3 -m profit_engine_runtime.strategy_lab_cli private-decision
```

The public lab validates accepted money evidence and creates inert experiment
previews. It never compares strategy outcomes or makes a commercial decision;
sensitive decision requests fail closed with `BLOCKED_PRIVATE_CORE_REQUIRED`.
