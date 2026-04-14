---
_schema:
  entity_type: "relationship-note"
  granularity: extract
  required:
    - description
    - granularity
    - topics
  optional:
    - person
    - category
    - last_confirmed
    - follow_up
    - created
  enums:
    granularity:
      - extract
    category:
      - preference
      - pattern
      - important-date
      - interaction
      - care-task
    follow_up:
      - true
      - false
  constraints:
    description:
      max_length: 200
      format: "One sentence adding context beyond the title"
    granularity:
      fixed: extract
    person:
      format: "Name as free text"
    last_confirmed:
      format: "ISO 8601 date"
    topics:
      format: "Array of wiki links, at least one"

description: ""
granularity: extract
topics: []
---

# prose-as-title expressing the relationship insight

Body with details. What was observed, what it means, how to act on it.

---

Topics:
- [[relationships]]
