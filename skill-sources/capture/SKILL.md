---
name: capture
description: Preserve source material verbatim with structured frontmatter and graph connections. No transformation of content — the source is captured exactly as-is in a fenced block. Triggers on "/capture", "/capture [file]", "capture this", "save this raw".
version: "1.0"
allowed-tools: Read, Write, Grep, Glob
---

## Runtime Configuration (Step 0 — before any processing)

Read these files to configure domain-specific behavior:

1. **`ops/derivation-manifest.md`** — vocabulary mapping
   - Use `vocabulary.note_collection` for the note collection directory
   - If `entity_directories` section exists in manifest, read it for entity-type routing
   - Use `vocabulary.inbox` for the inbox folder name
   - Use `vocabulary.note` / `vocabulary.note_plural` for note type references
   - Use `vocabulary.topic_map` / `vocabulary.topic_maps` for MOC references

2. **`ops/queue/queue.json`** — current task queue

---

## THE MISSION

You are the capture engine. Source material enters. A graph-connected, frontmatter-stamped verbatim copy exits. Your job is to make raw content findable and connected without transforming it.

### The Verbatim Principle

**Content is sacred.** The source material goes into a fenced code block exactly as received. No editing, no reformatting, no summarizing, no restructuring, no "fixing" grammar or formatting. The fenced block is a sealed artifact.

All graph participation happens OUTSIDE the fenced block:
- Frontmatter provides structured metadata
- Title provides discoverability
- Description provides context
- Relevant Notes footer provides connections
- Topics footer provides {vocabulary.topic_map} membership

### When to Use Capture

- Meeting transcripts
- Reference documents where exact wording matters
- Articles or content to preserve as-is
- Source material that may be processed later via /extract or /structure
- Any content where transformation would lose value

Capture is a terminal state — the {vocabulary.note} stays as-is. If claims need extracting later, run /extract on the capture {vocabulary.note} as a source. That produces NEW {vocabulary.note_plural}; the capture itself remains unchanged.

---

## EXECUTE NOW

**Target: $ARGUMENTS**

Parse immediately:
- Source file path: the file to capture (required)
- If target is empty: list files in {DOMAIN:inbox}/ and ask which to capture

### Step 0: Read Vocabulary

Read `ops/derivation-manifest.md` (or fall back to `ops/derivation.md`) for domain vocabulary mapping. All output must use domain-native terms. If neither file exists, use universal terms.

**START NOW.** Capture the source.

---

## Workflow

### 1. Read Source

Read the ENTIRE source file. Understand what it contains — you need this understanding to craft a good title and description, even though you won't transform the content.

### 2. Craft Title (Prose-as-Title — Content Variant)

Write a prose title that summarizes what the captured content contains. This is the main intellectual work of capture. The title works as a noun phrase when linked — "referencing [[title]]" or "as documented in [[title]]" reads naturally — describing what the artifact contains rather than making a claim or defining a scope.

**The content test:** Can you complete this sentence?
> This is a capture of [title]

If it works, the title describes the content. If it doesn't, it's probably a topic label.

Good titles (content descriptions that work as prose when linked):
- "quarterly planning meeting discussing Q3 priorities and hiring timeline"
- "Dr Smith lecture on cognitive load theory and instructional design"
- "customer interview with Jane about onboarding friction points"

Bad titles:
- "meeting notes" (too vague)
- "lecture" (topic label)
- "interview" (says nothing about content)

**Title rules:**
- Lowercase with spaces
- No punctuation that breaks filesystems: . * ? + [ ] ( ) { } | \ ^
- Express the concept fully — there is no character limit
- Each title must be unique across the entire workspace

### 3. Write Description

One sentence (~150 chars) adding context beyond the title. What makes this capture worth keeping? What key topics does it touch?

Bad (restates title):
- Title: "quarterly planning meeting discussing Q3 priorities"
- Description: Meeting about Q3 priorities and planning

Good (adds context):
- Title: "quarterly planning meeting discussing Q3 priorities"
- Description: Key decisions on hiring freeze timeline and product launch date; tension between engineering capacity and marketing commitments

### 4. Identify Connections

Scan the source content for references to existing {vocabulary.note_plural} or topics. Do NOT modify the content — identify connections to add in the footer sections:

- Which existing {vocabulary.note_plural} does this content relate to?
- Which {vocabulary.topic_maps} should reference this capture?
- Are there specific claims in the content that connect to existing {vocabulary.note_plural}?

### 5. Write the {vocabulary.note}

```yaml
---
description: [~150 chars — context beyond the title]
granularity: capture
captured: [YYYY-MM-DD]
source_type: [transcript | article | conversation | document | other]
topics: [array of {vocabulary.topic_map} wiki links]
---
```

```markdown
# [prose-as-title]

` ` `
[VERBATIM CONTENT — exactly as received, no modifications]
` ` `

---

Relevant Notes:
- [[related {vocabulary.note}]] — [why this capture relates]

Topics:
- [[relevant {vocabulary.topic_map}]]
```

(Note: the backticks above should be three consecutive backticks with no spaces — written with spaces here to avoid breaking the markdown nesting)

### 6. Quality Check Before Writing

- Title is specific and descriptive (not a topic label)
- Description adds information beyond the title
- Content inside fenced block is IDENTICAL to source (no edits whatsoever)
- At least one {vocabulary.topic_map} link
- `granularity: capture` in frontmatter
- `captured` date present
- File written to `{vocabulary.note_collection}/[title].md` (single-entity) or `{vocabulary.note_collection}/[entity_dir]/[title].md` (multi-entity, routed by the note's entity_type matching an entity_directories entry)

### 7. Create Queue Entry

Create one queue entry:

```json
{
  "id": "[batch]-cap-001",
  "type": "note",
  "granularity": "capture",
  "status": "pending",
  "target": "[note title]",
  "batch": "[source-name]",
  "created": "[UTC timestamp]",
  "current_phase": "reflect",
  "completed_phases": ["create"]
}
```

No enrichment tasks — capture does not analyze content deeply enough to spot enrichment opportunities.

---

## RALPH HANDOFF Output

After creating the queue entry, always output the RALPH HANDOFF block:

```
=== RALPH HANDOFF: capture ===
Target: [source file]

Work Done:
- Captured [source] as verbatim note
- Created queue entry: [id]

Files Modified:
- {vocabulary.note_collection}/[note title].md
- ops/queue/queue.json

Learnings:
- [Friction]: [description] | NONE
- [Surprise]: [description] | NONE
- [Methodology]: [description] | NONE
- [Process gap]: [description] | NONE

Queue Updates:
- Create: [id] (current_phase: "reflect")
=== END HANDOFF ===
```

---

## THE IMMUTABILITY INVARIANT

**Content inside the fenced block is IMMUTABLE.** This is not a guideline — it is a hard constraint.

- No adding links inside the fenced block
- No reformatting content inside the fenced block
- No correcting typos inside the fenced block
- No "improving" content inside the fenced block
- All connections go in frontmatter and footer sections ONLY

If you catch yourself about to edit the fenced block content, STOP. The fenced block is a sealed artifact. All graph participation happens through frontmatter and footer sections.
