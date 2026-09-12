# DILIVOX bounded development requests

This directory contains explicit, auditable requests for the development executor.

A JSON request is executable only when a single owner-controlled commit changes exactly one file in this directory and the request contains:

- `request_id`;
- `created_at` (ISO-8601);
- `task_id`;
- `task_file`;
- exact `base_sha`, which must equal the request commit parent;
- `task_budget_usd`;
- `execute: true`;
- bounded `allowed_paths` (maximum 12 entries);
- allowlisted `check_profiles`;
- `task_descriptor` used by the quality-first router.

The request does not grant merge, deploy, Tilda publication, production/provider mutation, or autonomous commercial authority.

Routing follows `DEVELOPMENT_FINOPS_POLICY.md`: use the least expensive route confidently sufficient for the quality floor. A free route is not mandatory when it would reduce quality or delay work.

Astra remains explicit Owner opt-in. Normal paid development inside the accepted DILIVOX development envelope may use Luna/Terra/Sol according to task capability requirements.
