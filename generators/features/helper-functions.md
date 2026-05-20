# Feature: Helper Functions

## Context File Block

```markdown
## Helper Functions — Essential Graph Infrastructure

Your vault ships with direct command surfaces for safe graph maintenance. These are not afterthoughts — they are essential infrastructure.

### Safe Rename

Never rename a {DOMAIN:note} manually. Manual renames break every wiki link that references the old title, silently degrading the graph. Use Obsidian CLI rename/move operations so Obsidian owns graph-note path semantics:

```bash
obsidian rename "{DOMAIN:note_collection}/old title.md" "new title"
obsidian move "{DOMAIN:note_collection}/old title.md" "{DOMAIN:note_collection}/new title.md"
```

This is the only safe way to rename graph notes. Wiki links resolve by filename — when a filename changes, every `[[old title]]` in the vault becomes a dangling link unless updated.

### Graph Maintenance Utilities

Use Obsidian CLI for vault-native graph facts:

**Orphan detection** — Find {DOMAIN:notes} with no incoming links. Orphaned {DOMAIN:notes} are invisible to traversal — they exist but nobody can reach them:
```bash
obsidian orphans
```
Every orphan is either a gap (needs connections) or stale (needs archiving). Neither is acceptable as a permanent state.

**Dangling link detection** — Find wiki links that point to non-existent {DOMAIN:notes}:
```bash
obsidian unresolved
```
Dangling links are demand signals — they tell you what {DOMAIN:notes} should exist but do not. Either create the missing {DOMAIN:note} or fix the link.

**Backlink count** — Count incoming links to a specific {DOMAIN:note}:
```bash
obsidian backlinks "note title"
```
High backlink counts identify hub {DOMAIN:notes} — central concepts that many other {DOMAIN:notes} reference. Low counts on important {DOMAIN:notes} suggest connection-finding opportunities.

**Link and property inspection** — Inspect vault-native graph facts:
```bash
obsidian links
obsidian properties
obsidian tags
```

**Schema validation** — Validate all {DOMAIN:notes} against their template schemas:
```bash
uv run arscontexta-vault validate --all
```
Checks required fields, enum values, and deterministic constraints. Emits JSON.

- **Health diagnostics** — Run condition-based invariant checks and surface violations as a ranked report via /health. This is idempotent — safe to run any number of times. It only reads state, never modifies your {DOMAIN:notes} or graph.

### Domain-Specific Helpers

As your vault grows, you may add domain-specific snippets or scripts for repeated inspection tasks. Document their usage here. Common extensions include:

- Export scripts for sharing subsets of the graph
- Import scripts for bulk ingestion from external sources
- Report generators for domain-specific analytics
- Migration scripts for schema evolution across existing {DOMAIN:notes}

The pattern: if you find yourself running the same sequence of commands repeatedly, extract it into a script. Scripts encode methodology the same way skills do — they make repeatable operations reliable and consistent.

### When to Use Helpers vs Skills

Helpers are lightweight, stateless operations — they inspect or modify the graph without pipeline state. Skills are workflows with quality gates and lean handoff protocols. Use helpers for quick checks and mechanical operations. Use skills for knowledge work that requires judgment and quality verification.
```

## Dependencies
Requires Obsidian CLI, qmd for semantic discovery, and the vault-local Python runtime for deterministic validation.
