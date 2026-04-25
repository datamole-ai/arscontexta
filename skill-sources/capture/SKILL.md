---
name: capture
description: Internal pipeline skill — preserves source material verbatim with frontmatter and graph connections. Invoked by /pipeline as a subagent; do not invoke directly.
version: "1.0"
context: fork
allowed-tools: Read, Write, Grep, Glob
---

## Runtime Configuration

### Vocabulary

All output must use domain-native terms.
Derivation manifest for vocabulary mapping:
!`cat ops/derivation-manifest.md`

### Task Queue

Read the current task queue:
!`cat ops/queue/queue.json`

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

---

## EXECUTE NOW

**Target: $ARGUMENTS**

Parse the batch id from arguments (the source basename, e.g. `my-source`). If no argument is provided, end immediately with: report
`ERROR: capture requires batch id`.

Look up the process entry in `ops/queue/queue.json`:

```bash
jq --arg id "$BATCH_ID" '.tasks[] | select(.id == $id and .type == "process")' ops/queue/queue.json
```

From that entry, obtain:
- `id` — the batch id (source basename)
- `source` — the archived source file path
- `granularity` — must equal `capture` (error out otherwise)
- `next_claim_start` — first claim number to use

All subsequent references to "the source" use the `source` value from the queue entry.

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
content_type: [vault content_type value — see the content_type enum in ops/templates/note.md _schema:]
granularity: capture
description: [~150 chars — context beyond the title]
created_at: [YYYY-MM-DD]
tags: [array of free-form strings — may be []]
---
```

```markdown
# [prose-as-title]

(VERBATIM CONTENT — exactly as received, no modifications)

---

Relevant Notes:
- [[related {vocabulary.note}]] — [why this capture relates]

Topics:
- [[relevant {vocabulary.topic_map}]]
```

### 6. Quality Check Before Writing

- Title is specific and descriptive (not a topic label)
- Description adds information beyond the title
- Content inside fenced block is IDENTICAL to source (no edits whatsoever)
- At least one {vocabulary.topic_map} link in the Topics footer
- All five required fields present in frontmatter: `content_type`, `granularity: capture`, `description`, `created_at`, `tags`
- File written to flat `{vocabulary.note_collection}/[title].md` — routing is by `granularity` frontmatter, not by subdirectory

### 7. Create Queue Entry

Create one queue entry:

```json
{
  "id": "note-{NNN}",
  "type": "note",
  "granularity": "capture",
  "status": "pending",
  "target": "[note title]",
  "target_path": "{vocabulary.note_collection}/{note title}.md",
  "batch": "{batch}",
  "created": "[UTC timestamp]",
  "current_phase": "reflect",
  "completed_phases": ["capture"]
}
```

Additionally: set the process task entry's status to "done" and add a "completed" timestamp before writing the file.

No enrichment tasks — capture does not analyze content deeply enough to spot enrichment opportunities.

---

## Output Block

After materializing the note and updating `ops/queue/queue.json` (mark process task done + append the note entry), emit the canonical block below as the final chat message. This is the ONLY chat output — no task file is written.

```
## Capture

**Target:** {batch-id}
**Status:** ok | error: {short message}
**Queue:** marked {batch-id}: process -> done; created 1 note entry (current_phase: reflect)

### Work
- Captured {source} verbatim as [[{note title}]]
- Created queue entry: note-{NNN}

### Files Modified
- {vocabulary.note_collection}/{note title}.md
- ops/queue/queue.json

### Learnings
- [Friction]: {description} | NONE
- [Surprise]: {description} | NONE
- [Methodology]: {description} | NONE
- [Process gap]: {description} | NONE
```

On error, set `Status: error: <message>`, `Queue: no change (error)`, and leave `queue.json` and the target filesystem unchanged.

---

## THE IMMUTABILITY INVARIANT

**Content inside the fenced block is IMMUTABLE.** This is not a guideline — it is a hard constraint.

- No adding links inside the fenced block
- No reformatting content inside the fenced block
- No correcting typos inside the fenced block
- No "improving" content inside the fenced block
- All connections go in frontmatter and footer sections ONLY

If you catch yourself about to edit the fenced block content, STOP. The fenced block is a sealed artifact. All graph participation happens through frontmatter and footer sections.
