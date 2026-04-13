---
_schema:
  entity_type: "structure-note"
  granularity: structure
  required:
    - description
    - granularity
    - topics
  optional:
    - type
    - status
    - created
    - claims
  enums:
    granularity:
      - structure
    type:
      - insight
      - pattern
      - preference
      - fact
      - decision
      - question
    status:
      - preliminary
      - active
      - archived
  constraints:
    description:
      max_length: 200
      format: "One sentence capturing the scope of the grouped claims"
    granularity:
      fixed: structure
    claims:
      format: "Array of prose sub-claims covered in this note"
    topics:
      format: "Array of wiki links, at least one"
  notes: >
    Structure notes group related claims that share context. The title
    captures scope, not a single proposition. Sections organize the
    sub-claims. Use when claims lose meaning if separated — when they
    share evidence base, form a sequential argument, need each other
    for context, or address the same question from different angles.

description: ""
granularity: structure
topics: []
---

# prose-as-title capturing the scope of grouped claims

## First claim or argument thread

Body developing the first claim within the shared context.

## Second claim or argument thread

Body developing the second claim. Sections share context, which is why they belong in one note.

---

Source: [[source filename]]

Relevant Notes:
- [[related note]] — relationship context

Topics:
- [[parent-moc]]
