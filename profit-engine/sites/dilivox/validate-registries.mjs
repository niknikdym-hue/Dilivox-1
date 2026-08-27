import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));

export function validateContentRegistry(registry) {
  const ids = new Set();
  const activeUrls = new Set();
  for (const item of registry.items || []) {
    if (!item.content_id || ids.has(item.content_id)) throw new Error("duplicate or missing content_id");
    ids.add(item.content_id);
    if (item.active) {
      if (activeUrls.has(item.canonical_url)) throw new Error("duplicate active canonical_url");
      activeUrls.add(item.canonical_url);
    }
  }
  return {items: ids.size, active_urls: activeUrls.size};
}

export function assertIdentityPreserved(previous, proposed) {
  const bySource = new Map((proposed.items || []).map(item => [item.source.reference, item]));
  for (const oldItem of previous.items || []) {
    const next = bySource.get(oldItem.source.reference);
    if (!next || next.content_id !== oldItem.content_id) throw new Error("assigned content_id changed or disappeared");
  }
  return true;
}

export function validatePlacements(registry, inventory) {
  const active = registry.placements.filter(item => item.active);
  const ids = active.map(item => item.placement_id);
  if (new Set(ids).size !== ids.length) throw new Error("duplicate active placement_id");
  const source = new Set(inventory.ad_block_values);
  const mapped = new Set(ids);
  const missing = [...source].filter(id => !mapped.has(id));
  const unsupported = active.filter(item => !source.has(item.placement_id) && !item.dormant_reason);
  if (missing.length || unsupported.length) throw new Error("placement source coverage failed");
  return {source_values: source.size, active_mappings: active.length};
}

export function validateSourceCoverage(registry, inventory) {
  const bySlug = new Map(registry.items.filter(item => ["story", "comic"].includes(item.content_type)).map(item => [item.current_slug, item]));
  const missing = inventory.story_slugs.filter(slug => !bySlug.has(slug));
  const inactiveDiscoverable = inventory.discoverable_story_slugs.filter(slug => !bySlug.get(slug)?.active);
  if (missing.length || inactiveDiscoverable.length) throw new Error("content source coverage failed");
  return {source_stories: inventory.story_slugs.length, discoverable_active: inventory.discoverable_story_slugs.length};
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const read = name => JSON.parse(fs.readFileSync(path.join(here, name), "utf8"));
  const result = {
    content: validateContentRegistry(read("content-registry.json")),
    source_coverage: validateSourceCoverage(read("content-registry.json"), read("source-hooks-inventory.json")),
    placements: validatePlacements(read("placement-registry.json"), read("source-hooks-inventory.json"))
  };
  process.stdout.write(JSON.stringify(result) + "\n");
}
