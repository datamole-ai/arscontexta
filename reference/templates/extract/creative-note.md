---
_schema:
  entity_type: "creative-note"
  granularity: extract
  required:
    - description
    - granularity
    - topics
  optional:
    - stage
    - medium
    - inspiration
    - created
  enums:
    granularity:
      - extract
    stage:
      - idea
      - draft
      - revision
      - complete
    medium:
      - writing
      - visual
      - music
      - code
  constraints:
    description:
      max_length: 200
      format: "One sentence adding context beyond the title"
    granularity:
      fixed: extract
    inspiration:
      format: "Array of wiki links to reference works"
    topics:
      format: "Array of wiki links, at least one"

description: ""
granularity: extract
topics: []
---

# prose-as-title expressing the creative insight or technique

Body developing the idea. What sparked it, how it could work, what it connects to.

---

Topics:
- [[topic-moc]]
