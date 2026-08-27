# Dilivox SiteAgent — unpublished Task 005 artifact

Canonical artifact: `dilivox-site-agent-task005.js`.

It is self-contained, dependency-free, non-blocking and does not dispatch network
events. It only reads existing T123 hooks and first-party URL/storage state. It
does not call or modify `Ya.Context`, YAN containers, story content, choices, or
reveal behavior.

Future controlled installation (not performed in Task 005): place the script in
one global Tilda T123/HEAD block after the existing global Dilivox utilities and
before future Day-6 event wiring. Load it once. Validate on an unpublished copy
before any production publication.

Rollback: set `window.__PROFIT_ENGINE_SITE_AGENT_DISABLED__ = true` before the
artifact loads, or remove the single artifact block and republish through an
authorized deployment task. Existing content and YAN behavior remain independent.

Durable return identity is disabled by default. Enabling it requires both
`enableReturnId: true` and `privacyReviewApproved: true`; that approval is a
production privacy-review gate, not granted by this artifact. Attribution and
return TTLs are capped at 30 days. Metrica ClientID and fingerprinting are never
used.
