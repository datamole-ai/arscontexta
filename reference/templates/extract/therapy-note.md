---
_schema:
  entity_type: "therapy-note"
  granularity: extract
  required:
    - description
    - granularity
    - topics
  optional:
    - category
    - confidence
    - frequency
    - created
  enums:
    granularity:
      - extract
    category:
      - pattern
      - trigger
      - coping-strategy
      - insight
      - growth-goal
    confidence:
      - observed
      - hypothesized
      - verified
    frequency:
      - once
      - occasional
      - regular
      - constant
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

# prose-as-title expressing the reflection or pattern

Body exploring the pattern. When it happens, what triggers it, what helps.

---

Topics:
- [[topic-moc]]
