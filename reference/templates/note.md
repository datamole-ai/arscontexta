---
_schema:
  applies_to: "{vocabulary.note_collection}/**/*.md"
  required:
    - title
    - content_type
    - granularity
    - description
    - created_at
    - tags
  enums:
    granularity:
      - extract
      - structure
      - capture
    content_type:
      # Vault-specific. Populated during setup from the user's domain.
      # Examples: spec, decision, lesson, reflection, observation.
  constraints:
    title:
      format: "Prose-as-title. Specific enough for search and linking."
    content_type:
      format: "One of the enum values derived during setup."
    granularity:
      format: "One of extract | structure | capture."
    description:
      max_length: 200
      format: "One sentence adding context beyond the title. No trailing period."
    created_at:
      format: "ISO 8601 date (YYYY-MM-DD)."
    tags:
      format: "Array of free-form strings. May be []. Escape hatch for emergent attributes — not a substitute for fields that would pass Filter A."
  notes: >
    This is the single canonical template for every note in every vault.
    Setup derives the content_type enum from the user's domain and MAY add
    extra fields that pass Filter A (day-one reader + use). No optional
    fields exist; if a field is in the template, it is required.

title: ""
content_type: ""
granularity: extract
description: ""
created_at: YYYY-MM-DD
tags: []
---

# prose-as-title expressing what this note is about

Body text. No prescribed sections. Content-type body conventions (for example,
a "decision" typically has Context / Decision / Consequences) live as
lightweight prose guidance in the vault's CLAUDE.md, not as template
scaffolding.

Use inline wiki-links as prose: "Since [[other note]], the question becomes..."

---

Topics:
- [[parent-moc]]
