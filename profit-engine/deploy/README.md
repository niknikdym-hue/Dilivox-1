# Portable service boundaries

Initial independent read-only services are `collector-direct`,
`collector-metrica`, and `collector-yan`. Later boundaries are `event-api` and
`reconciliation-worker`. Every service uses the provider-neutral relational,
raw object, secret, health, and audit contracts. Provider SDKs, Lockbox, Object
Storage, and Managed PostgreSQL remain adapter details. Kubernetes is not
required.

Task 003 does not apply Cloud resources. Deployment remains
`BLOCKED_OWNER_CLOUD_ACCESS` until the Owner separately authorizes the account,
folder, service identities, and any paid resources.
