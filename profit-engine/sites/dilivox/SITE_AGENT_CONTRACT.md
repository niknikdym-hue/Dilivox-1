# Browser SiteAgent contract v1

`createSiteAgent(window, adapter, options)` is the provider-neutral browser
contract. An adapter supplies only:

- stable `site_id`;
- `resolveContent(document, location)` returning immutable `content_id` and type;
- `placementIds(document)` returning registry-approved placement identities.

The returned read API exposes `site_id`, schema/deployment versions, `enabled`,
`health`, acquisition/session/experiment/placement state, `getContext()`, and
`buildEventContext(extra)`. It never owns page rendering or provider ad code.
Initialization/runtime errors return a frozen safe-no-op agent.

`DILIVOX_ADAPTER` is adapter #1. It resolves the existing `data-dv-story-slug`,
`data-dv-page`, URL path and `data-dv-ad-block` hooks. Choice, reveal and goal
hooks remain untouched and are ready for Day-6 listeners.

Attribution capture is limited to `yclid`, five UTM fields, and explicitly
approved `campaign_id`, `ad_id`, `group_id`, `criterion_id`, `phrase_id`, and
`keyword_id`. Values are Unicode-normalized, control-stripped and length-limited.
No arbitrary query parameters, forms, names, email, phone, fingerprint, or
Metrica ClientID are captured.

New explicit paid landings supersede active acquisition state; organic/internal
navigation preserves it. Session state is first-party and pseudonymous. Optional
return state requires a production privacy review and cannot exceed 30 days.

Experiment hooks validate identities and honor global and per-experiment kill
switches. They implement no allocation, ranking, scoring, winner selection or
commercial policy.
