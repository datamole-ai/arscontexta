---
_schema:
  entity_type: "life-note"
  granularity: extract
  required:
    - description
    - granularity
    - topics
  optional:
    - area
    - priority
    - deadline
    - created
  enums:
    granularity:
      - extract
    area:
      - health
      - finance
      - home
      - social
      - career
    priority:
      - low
      - medium
      - high
      - urgent
  constraints:
    description:
      max_length: 200
      format: "One sentence adding context beyond the title"
    granularity:
      fixed: extract
    deadline:
      format: "ISO 8601 date"
    topics:
      format: "Array of wiki links, at least one"

description: ""
granularity: extract
topics: []
---

# prose-as-title expressing the life management insight or decision

Body with details. What was decided, why, what follows.

---

Topics:
- [[topic-moc]]
