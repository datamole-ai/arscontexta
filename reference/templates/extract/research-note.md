---
_schema:
  entity_type: "research-note"
  granularity: extract
  required:
    - description
    - granularity
    - topics
  optional:
    - methodology
    - source
    - classification
    - created
  enums:
    granularity:
      - extract
    methodology:
      - Zettelkasten
      - Evergreen
      - Cornell
      - Memory Arts
      - Network Science
      - Cognitive Science
      - Original
    classification:
      - claim
      - methodology
      - tension
  constraints:
    description:
      max_length: 200
      format: "One sentence adding context beyond the title"
    granularity:
      fixed: extract
    source:
      format: "Wiki link to source file"
    topics:
      format: "Array of wiki links, at least one"

description: ""
granularity: extract
topics: []
---

# prose-as-title expressing the research claim

Body developing the claim with visible reasoning.

---

Relevant Notes:
- [[related note]] — relationship context

Topics:
- [[topic-moc]]
