---
_schema:
  entity_type: "learning-note"
  granularity: extract
  required:
    - description
    - granularity
    - topics
  optional:
    - domain
    - mastery
    - prerequisites
    - created
  enums:
    granularity:
      - extract
    mastery:
      - new
      - developing
      - solid
      - expert
  constraints:
    description:
      max_length: 200
      format: "One sentence adding context beyond the title"
    granularity:
      fixed: extract
    domain:
      format: "Subject area as free text"
    prerequisites:
      format: "Array of wiki links to prerequisite concepts"
    topics:
      format: "Array of wiki links, at least one"

description: ""
granularity: extract
topics: []
---

# prose-as-title expressing the learning insight

Body developing the insight. What was learned, why it matters, how it connects.

---

Topics:
- [[topic-moc]]
