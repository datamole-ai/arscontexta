---
_schema:
  entity_type: "capture-note"
  granularity: capture
  required:
    - description
    - granularity
    - topics
    - captured
  optional:
    - source_type
    - source_url
  enums:
    granularity:
      - capture
    source_type:
      - transcript
      - article
      - conversation
      - document
      - other
  constraints:
    description:
      max_length: 200
      format: "One sentence summarizing what is captured"
    granularity:
      fixed: capture
    captured:
      format: "ISO 8601 date"
    topics:
      format: "Array of wiki links, at least one"
  notes: >
    Capture notes preserve source material verbatim. The title summarizes
    what is inside. The fenced block is untouched — no transformation,
    no restructuring, no summarization. Wikilinks and topic membership
    connect the capture to the graph. All connections live outside the
    fenced block in the footer sections.

description: ""
granularity: capture
captured: YYYY-MM-DD
topics: []
---

# prose-as-title summarizing what the captured content contains

```
Verbatim content here — preserved exactly as received.
No transformation, no restructuring, no edits.
```

---

Relevant Notes:
- [[related note]] — why this capture relates

Topics:
- [[parent-moc]]
