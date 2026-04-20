# Feature: Templates

## Context File Block

```markdown
## Templates — One Template, Six Fields

Your vault has exactly one template: `ops/templates/note.md`. Every {DOMAIN:note} regardless of content_type or granularity starts from it.

### What the Template Defines

- The five required YAML fields (content_type, granularity, description, created_at, tags)
- Any Filter-A survivor fields approved during setup (see the `_schema.required:` list in `ops/templates/note.md` for the exact list)
- A `_schema` block that documents field constraints and enum values
- A minimal body structure (H1 for prose-as-title, body prose, `Topics:` footer)

There are NO optional fields. If a field is in the template, every note has it. The one field that can be empty is `tags`, which is an array and may be `[]`.

### The Template-Note Relationship

| Template says | Note does |
|---------------|-----------|
| `content_type` enum: [<vault values>] | Note uses one of those values |
| `granularity` enum: [structure, capture] | Note uses one of those values |
| `description` max 200 chars | Every note has a description |
| Body has an H1 | Note leads with a prose-as-title H1 |
| Footer has Topics | Note links to its {DOMAIN:topic map}s |

Templates define the shape; notes provide the substance. The template is not content.

### Body Conventions by Content Type

The template does not prescribe body structure per `content_type`. Body conventions (for example, "a decision usually has Context / Decision / Consequences sections") live as lightweight prose guidance in CLAUDE.md — not as template scaffolding. This keeps the template uniform and lets content-type body shapes evolve without schema changes.

### Evolving the Schema

The schema evolves through observation:

1. **Observe** a tag or prose pattern recurring across {DOMAIN:notes}.
2. **Validate** that at least one day-one reader would genuinely use it as a first-class field.
3. **Promote** by editing `ops/templates/note.md` directly — add the field to `_schema.required:` and record the reader/use/day-one rationale in the Schema Decisions section of `ops/derivation.md`. Same Filter A bar used at setup.
4. **Backfill** existing notes if the new field has meaningful values for them.

The reverse also works: if a field is never queried, demote it back to `tags` or remove it.

### Adding New `content_type` Values

When a new kind of {DOMAIN:note} emerges, extend the `content_type` enum in the `_schema:` block of `ops/templates/note.md`. Do NOT invent enum values inline — formalize them first, then use them.

### Why One Template

Three reasons:

- **Agent-first.** Agents filter on frontmatter, not directories. One template + frontmatter fields is simpler than per-type templates + path-based routing.
- **Justify-or-drop.** Per-type templates accumulated speculative fields. One schema with strict Filter A at setup prevents that drift.
- **Deferrals are visible.** What did not make it into the schema is recorded in the "Deferred Candidates" section of `ops/derivation.md` — the alternative was invisible accretion.
```

## Dependencies
None — templates are foundational.
