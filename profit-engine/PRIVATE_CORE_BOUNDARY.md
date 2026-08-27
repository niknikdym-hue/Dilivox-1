# Profit Engine public/private core boundary

This repository is public. It may contain provider-neutral interfaces, generic
schemas and safety invariants, redaction utilities, site-adapter contracts,
placeholder-only configuration, and generic storage, health, and audit
abstractions.

The following material MUST NOT be implemented or stored here:

- proprietary scoring formulas, weights, and profit-pool ranking logic;
- budget allocation heuristics beyond generic public safety invariants;
- optimizer thresholds learned from Owner economics;
- commercially revealing creative ranking or generation decisions;
- confidential provider/account mappings and future private multi-site config;
- credentials, production datasets, raw exports, or private provider IDs.

Provider collectors may normalize facts into the public schemas, but they must
not embed commercial optimization policy. Public code can expose a decision or
approval interface; the implementation that selects commercially sensitive
actions belongs in the future private core.

No private repository is asserted to exist. The mandatory migration gate is:

`PRIVATE_CORE_REPOSITORY_REQUIRED_BEFORE_SENSITIVE_OPTIMIZER_IMPLEMENTATION`

Until that gate is satisfied, held or not-ready data cannot be consumed by an
optimizer and only read-only provider collection is permitted.
