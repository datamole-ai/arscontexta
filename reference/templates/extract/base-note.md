---
_schema:
  entity_type: "extract-note"
  granularity: extract
  required:
    - description
    - granularity
    - topics
  optional:
    - type
    - status
    - created
  enums:
    granularity:
      - extract
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
      format: "One sentence adding context beyond the title"
    granularity:
      fixed: extract
    topics:
      format: "Array of wiki links, at least one"

description: ""
granularity: extract
topics: []
---

# prose-as-title expressing the insight as a complete proposition

Body text developing the insight. Show reasoning with connective words: because, therefore, this suggests, however.

Use inline wiki-links as prose: "Since [[other note]], the question becomes..."

---

Topics:
- [[parent-moc]]
