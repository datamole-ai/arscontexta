# Feature: Schema

## Context File Block

```markdown
## {DOMAIN:Note} Schema — One Schema for Every {DOMAIN:Note}

Every {DOMAIN:note} has the same YAML frontmatter. One schema, six required fields, no optional fields. Schema enforcement is an INVARIANT because without it, frontmatter drifts and queries break. Validation catches errors at creation time.

### The Six Required Fields

```yaml
---
title: <string>               # prose-as-title, unique identifier
content_type: <enum>          # vault-specific category (derived during setup)
granularity: structure | capture
description: <string>         # one sentence, <=200 chars, no trailing period
created_at: <YYYY-MM-DD>      # ISO 8601 date
tags: [<free-form strings>]   # may be empty []
---
```

| Field | Reader | Use |
|-------|--------|-----|
| `title` | every skill | wiki-link target, search, display |
| `content_type` | routing + filtering skills | "show me all decisions" |
| `granularity` | /structure, /capture pipelines | selects pipeline behavior |
| `description` | /{DOMAIN:verify}, progressive disclosure | filter-before-read |
| `created_at` | archive, staleness checks | temporal queries |
| `tags` | users and agents alike | emergent attributes that have not been formalized |

**There are no optional fields.** If a field is in the template, it is required. If it is not required, it does not belong in the template. Emergent attributes live in `tags` until they earn promotion to a field.

### The Escape Hatch

`tags` is the one place ad-hoc structure lives. Use it for:
- Cross-cutting labels ("urgent", "followup", "draft")
- Emergent categories that have not yet been promoted to a field
- Anything that does not have a concrete day-one reader

Do NOT use `tags` as a substitute for fields that clearly belong in the schema. The rule: if a reader wants to filter on X from day one, X should be a field, not a tag.

### Query Patterns

```bash
# Find all {DOMAIN:notes} of a given content_type
rg '^content_type: decision' {DOMAIN:note_collection}/

# Find all structure-granularity notes
rg '^granularity: structure' {DOMAIN:note_collection}/

# Find notes with a given tag
rg '^tags:.*\burgent\b' {DOMAIN:note_collection}/

# Find stale notes (30+ days old)
rg '^created_at: 2025-' {DOMAIN:note_collection}/

# Count notes by content_type
rg '^content_type:' {DOMAIN:note_collection}/ --no-filename | sort | uniq -c | sort -rn

# Find notes missing description
rg -L '^description:' {DOMAIN:note_collection}/*.md

# Find backlinks to a specific {DOMAIN:note}
rg '\[\[specific-title\]\]' --glob '*.md'
```

### Schema Evolution

The schema evolves through observation, not decree. When a tag recurs across enough {DOMAIN:notes} that a skill would benefit from reading it as a first-class field, promote it by editing the `_schema.required:` list in `ops/templates/note.md` directly, then add a matching entry in the Schema Decisions section of `ops/derivation.md` naming its reader, use, and day-one rationale. Dead fields can be demoted back to `tags` or removed entirely.

### Validation

Enforcement is template-driven: skills that create {DOMAIN:notes} copy `ops/templates/note.md` and populate every required field declared in its `_schema:` block.

### The `_schema` Block

`ops/templates/note.md` contains the authoritative `_schema` block. Skills and hooks read it to check compliance. Every vault's `_schema` block contains the same six required fields plus whatever survived Filter A during setup.
