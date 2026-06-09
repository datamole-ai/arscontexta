# Feature: Schema

## Context File Block

```markdown
## {DOMAIN:Note} Schema — One Schema for Every {DOMAIN:Note}

Every {DOMAIN:note} has the same YAML frontmatter. `ops/schema.yaml` is the single schema contract: five required fields, no custom fields. Schema enforcement is an INVARIANT because without it, frontmatter drifts and queries break. Validation catches errors at creation time.

### The Five Required Fields

```yaml
---
content_type: <enum>          # vault-specific category from setup vocabulary
granularity: structure | capture
description: <string>         # one sentence, <=200 chars, no trailing period
created_at: <YYYY-MM-DD>      # ISO 8601 date
tags: []                      # Obsidian tags property; use a YAML list when populated
---
```

| Field | Reader | Use |
|-------|--------|-----|
| `content_type` | routing + filtering skills | "show me all decisions" |
| `granularity` | /structure, /capture pipelines | selects pipeline behavior |
| `description` | /structure, /capture, progressive disclosure | filter-before-read |
| `created_at` | archive, staleness checks | temporal queries |
| `tags` | Obsidian, users, and agents | conversation-derived attributes and emergent labels |

**There are no optional Ars fields.** If a field is in `ops/schema.yaml.required`, every note has it. If it is not one of the five required fields or an allowed Obsidian default property, it does not belong in frontmatter. Conversation-derived attributes live in `tags`.

### The Escape Hatch

`tags` is the one place ad-hoc structure lives. Use it for:
- Cross-cutting labels ("urgent", "followup", "draft")
- Attributes named during setup that are not one of the fixed fields
- Emergent categories that are useful for filtering

Do not add custom fields during setup. If the user wants to track status, confidence, source, person, region, project, or similar attributes, use tags.

For Obsidian compatibility, write tags without the leading `#`, with no spaces, and with at least one non-numeric character. Use `/` for nested tags, for example:

```yaml
tags:
  - status/draft
  - project/client-portal
```

Use modern Obsidian property names. Do not use deprecated `tag`, `alias`, or `cssclass`; use `tags`, `aliases`, and `cssclasses`.

### Query Patterns

```bash
# Find all {DOMAIN:notes} of a given content_type
rg '^content_type: decision' {DOMAIN:note_collection}/

# Find all structure-granularity notes
rg '^granularity: structure' {DOMAIN:note_collection}/

# Find notes with a given tag
rg '^  - urgent$' {DOMAIN:note_collection}/

# Find stale notes (30+ days old)
rg '^created_at: 2025-' {DOMAIN:note_collection}/

# Count notes by content_type
rg '^content_type:' {DOMAIN:note_collection}/ --no-filename | sort | uniq -c | sort -rn

# Find notes missing description
rg -L '^description:' {DOMAIN:note_collection}/*.md

# Find backlinks to a specific {DOMAIN:note}
rg '\[\[specific-title\]\]' --glob '*.md'
```

### Schema Stability

The schema is intentionally fixed at five fields. Let tags carry new attributes instead of expanding frontmatter.

### Validation

Enforcement is schema-driven: skills that create {DOMAIN:notes} read `ops/schema.yaml` and populate every field declared in `required`.

### The Schema File

`ops/schema.yaml` contains the authoritative schema contract. Skills and hooks read it to check compliance. Every vault's schema contains the same five required fields.
