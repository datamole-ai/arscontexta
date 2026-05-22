# Feature: Schema Contract

## Context File Block

```markdown
## Schema Contract — Five Fields

Your vault has exactly one note schema contract: `ops/schema.yaml`. Every {DOMAIN:note} regardless of content_type or granularity is validated against it.

### What the Schema Defines

- The five required YAML fields (content_type, granularity, description, created_at, tags)
- Field constraints and enum values
- Obsidian compatibility rules for tags and default properties

There are NO optional Ars fields. If one of the five fields is in `ops/schema.yaml.required`, every note has it. The one field that can be empty is `tags`, which is an Obsidian tags property and may be `[]`. User-managed Obsidian default properties such as `aliases` and `cssclasses` may exist when useful, but setup does not derive or require them.

### The Schema-Note Relationship

| Schema says | Note does |
|---------------|-----------|
| `content_type` enum: [<vault values>] | Note uses one of those values |
| `granularity` enum: [structure, capture] | Note uses one of those values |
| `description` max 200 chars | Every note has a description |
| `tags` is an Obsidian tags property | Note uses `[]` or a YAML block list |

The schema defines frontmatter. Skills define the body shape: an H1 prose title, body prose, and a `Topics:` footer.

### Body Conventions by Content Type

The schema does not prescribe body structure per `content_type`. Body conventions (for example, "a decision usually has Context / Decision / Consequences sections") live as lightweight prose guidance in CLAUDE.md, not in the schema. This keeps frontmatter uniform and lets content-type body shapes evolve without schema changes.

### Tags Instead of Extra Fields

When a new attribute recurs across {DOMAIN:notes}, keep it in `tags`. Do not add setup-derived fields to `ops/schema.yaml.required`.

Use Obsidian tag format: omit the leading `#`, avoid spaces, use `/` for nested tags, and include at least one non-numeric character.

### Adding New `content_type` Values

When a new kind of {DOMAIN:note} emerges, extend the `content_type` enum in `ops/schema.yaml`. Do NOT invent enum values inline — formalize them first, then use them.

### Why One Schema

Three reasons:

- **Agent-first.** Agents filter on frontmatter, not directories. One schema + frontmatter fields is simpler than per-type templates + path-based routing.
- **Fixed schema.** Per-type templates accumulated speculative fields. One schema plus tags prevents that drift.
- **Tags absorb variation.** Conversation-derived attributes stay queryable without expanding the schema.
```

## Dependencies
None — the schema contract is foundational.
