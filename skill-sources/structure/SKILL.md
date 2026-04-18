---
name: structure
description: Group claims from source material into structured notes, defaulting to generous grouping. Each note covers one coherent topic with multiple related claims organized in sections. Triggers on "/structure", "/structure [file]", "group these", "structure this".
version: "1.0"
context: fork
allowed-tools: Read, Write, Grep, Glob, mcp__qmd__query
---

## Runtime Configuration (Step 0 — before any processing)

Read these files to configure domain-specific behavior:

1. **`ops/derivation-manifest.md`** — vocabulary mapping, extraction categories, platform hints
   - Use `vocabulary.note_collection` for the note collection directory
   - If `entity_directories` section exists in manifest, read it for entity-type routing
   - Use `vocabulary.inbox` for the inbox folder name
   - Use `vocabulary.note` for the note type name in output
   - Use `vocabulary.note_plural` for the plural form
   - Use `vocabulary.reduce` for the process verb in output
   - Use `vocabulary.cmd_reflect` for the next-phase command name
   - Use `vocabulary.cmd_reweave` for the backward-pass command name
   - Use `vocabulary.cmd_verify` for the verification command name
   - Use `vocabulary.topic_map` for MOC/topic map references
   - Use `vocabulary.topic_maps` for plural form

2. **`ops/queue/queue.json`** — current task queue

If these files don't exist (pre-init invocation or standalone use), use universal defaults:
- note collection: `notes/`
- inbox folder: `inbox/`

---

## THE MISSION (READ THIS OR YOU WILL FAIL)

You are the structuring engine. Raw source material enters. Structured, multi-claim {vocabulary.note_plural} exit. Your job is to identify coherent topic clusters and group related claims that share context, evidence, or argument threads.

### The Core Principle

**You are here because the user chose structured grouping.** Your job is to find the best groupings — clusters of claims that share context, evidence, or argument threads. The default is to group. Split only when keeping claims together actively confuses or misleads.

### The Grouping Principle

**For every source, COMPREHENSIVE STRUCTURING is the default.** This means:

1. **Identify ALL topic clusters** — groups of claims that share context, evidence, or argument threads.
2. **Keep related claims together** — claims that share evidence base, form a sequential argument, need each other for context, or address the same question from different angles.
3. **Split unrelated topics** — when claims are genuinely independent (different evidence, different questions, no shared context), they become separate structure notes.

### The Grouping Question (ask for EVERY cluster)

**"Would keeping these claims together confuse or mislead the reader?"**

If NO -> keep together in one structure note (this is the default)
If YES -> split into separate structure notes

### Grouping Signals (the default)

- They share the same evidence base
- They form a sequential argument (A leads to B leads to C)
- They provide mutual context (understanding one deepens the other)
- They address the same question from different angles
- They come from the same analytical framework applied to the same subject

### Split Only When Grouping Hurts

- Sections would actively confuse if someone linked to the whole note
- Topics are so unrelated that a reader would wonder why they're together
- The combined note obscures rather than illuminates each claim

---

## EXECUTE NOW

**Target: $ARGUMENTS**

Parse immediately:
- If target contains a file path: group claims from that file into structure notes
- If target is empty: scan {vocabulary.inbox}/ for unprocessed items, pick one
- If target is "inbox" or "all": process all inbox items sequentially

**Execute these steps:**

1. Read the source file fully — understand what it contains, what topics it covers
2. **Source size check:** If source exceeds 2500 lines, STOP. Plan chunks of 350-1200 lines. Process each chunk with fresh context. See "Large Source Handling" section below.
3. Identify topic clusters — groups of related claims
4. For each cluster:
   - Tier 1 (preferred): use `mcp__qmd__query` with query "[cluster scope as sentence]", collection="{vocabulary.notes_collection}", limit=5
   - Tier 2 (CLI fallback): `qmd vsearch "[cluster scope as sentence]" --collection {vocabulary.notes_collection} -n 5`
   - Tier 3 fallback if qmd is unavailable: use keyword grep duplicate checks
   - If existing note covers same scope: evaluate for enrichment or merge
5. If task file path is in context (pipeline): append the grouping summary (proposed titles, cluster membership, enrichments) to the source task file's `## Outputs` section, no chat output. If no task file path is in context (standalone): print the grouping report as chat output (see "Present Findings" below). Per-note rationale is captured in step 7 when per-note task files are created.
6. If no task file path is in context (standalone invocation): wait for user approval before writing files. When invoked from /pipeline, skip and proceed.
7. Create per-note task files, update queue, output HANDOFF block

**START NOW.** Reference below explains methodology — use to guide, not as output.

### Observation Capture (during work, not at end)

When you encounter friction, surprises, methodology insights, process gaps, or contradictions — capture IMMEDIATELY:

| Observation | Action |
|-------------|--------|
| Any observation | Create atomic note in `ops/observations/` with prose-sentence title |
| Tension: content contradicts existing {vocabulary.note} | Create atomic note in `ops/tensions/` with prose-sentence title |

The handoff Learnings section summarizes what you ALREADY logged during processing.

---

# Structure

Group related claims from source material into structured {vocabulary.note_plural} in {vocabulary.note_collection}/.

## Philosophy

**Group generously. Split only when grouping actively hurts.**

The user chose /structure. That decision carries intent — they want related claims organized together, preserving shared context. Your job is to find the best groupings, not to question whether grouping is appropriate.

You receive raw content and identify clusters of related claims that share context, evidence, or argument threads. The mission is building **structured, multi-claim notes** — each covering a coherent topic with internal organization.

**THE GROUPING QUESTION:**

- BASIC thinking: "Are these claims on the same topic?"
- BETTER thinking: "Do these claims share evidence or build on each other?"
- BEST thinking: **"Would keeping these together confuse or mislead a reader?"**

If NO -> group them (this is the default)
If YES -> split into separate structure notes

---

## The Selectivity Gate (for OFF-TOPIC content filtering)

**CRITICAL:** This gate exists to filter OUT content that does not serve {vocabulary.domain}. It applies ONLY to content from GENERAL (off-topic) sources. Domain-relevant content skips this gate entirely.

For content from general sources, verify these quality criteria:

### 1. Coherent (required)

All sections genuinely relate. A reader would expect these claims together.

Fail: a mix of unrelated observations stapled into one file
Pass: a set of claims that build a shared argument or explore the same question

### 2. Standalone (required)

The grouped note is understandable without source context. Someone reading this {vocabulary.note} cold can grasp what it covers without needing to know where it came from.

Fail: "the author's third and fourth points about methodology"
Pass: "trade-offs between caching strategies and API latency under load"

### 3. Novel Scope (required)

The scope isn't already covered by existing notes. Semantic search AND existing {vocabulary.note_plural} scan both clear.

Fail: semantically equivalent scope to an existing structure note
Pass: genuinely new topic cluster not yet organized

### 4. Connected (soft signal, not a hard gate)

Consider whether the cluster relates to existing thinking in the vault. Unconnected clusters may indicate a new frontier worth exploring rather than content to filter out.

Signal: extends, contradicts, or deepens existing {vocabulary.note_plural}
No signal: flag for the user's attention, but do not auto-reject

**If coherence, standalone, or novel scope fails: do not structure.**

---

## Scope Coherence

Three quality checks before saving any structure {vocabulary.note}:

1. **Scope coherence** — Do all sections genuinely relate? Would a reader expect these claims together?
2. **Standalone sense** — Does the note make sense without reading three other notes first?
3. **Linkability** — Would linking to this note bring useful context to the reader?

If any check fails, the note needs restructuring — adjust sections or scope, don't reflexively split.

### The Prose-as-Title Pattern (Scope Variant)

Structure note titles capture the SCOPE of the grouped claims. They work as noun phrases when linked — "building on [[title]]" or "we explored [[title]]" reads naturally — describing territory rather than a single proposition.

**The scope test:** Can you complete this sentence?
> This note covers [title]

If it works, the title describes a coherent scope. If it doesn't, it's probably a topic label.

Good titles (scope descriptions that work as prose when linked):
- "how caching strategies affect API latency under load"
- "trade-offs between consistency and availability in distributed systems"
- "morning routine patterns and their relationship to anxiety management"

Bad titles:
- "caching reduces API latency by 40%" (single claim, not scope)
- "caching" (topic label, not scope description)
- "various thoughts about systems" (too vague)

**Title rules:**
- Lowercase with spaces
- No punctuation that breaks filesystems: . * ? + [ ] ( ) { } | \ ^
- Express the scope fully — there is no character limit
- Each title must be unique across the entire workspace

---

## Workflow

### 1. Orient

Before reading the source, understand what already exists:

```bash
# Get descriptions from existing notes
for f in $(find {vocabulary.note_collection}/ -name "*.md" -type f); do
  echo "=== $(basename "$f" .md) ===" && rg "^description:" "$f" -A 0
done
```

Scan descriptions to understand current {vocabulary.note_plural}. This prevents duplicate structuring and helps identify enrichment opportunities.

### 2. Read Source Fully

Read the ENTIRE source. Understand what it contains, what topics it covers, what claims are related.

**Planning the grouping:**
- How many topic clusters do you expect from this source?
- Which clusters share evidence, argument threads, or context?
- Is this domain-relevant (comprehensive structuring) or general (gate applies)?

### 3. Identify Topic Clusters

Group candidates by shared context, evidence, or argument thread. Default to grouping — split only when keeping together would confuse.

**Grouping signals:**
- Claims reference the same study, experiment, or evidence
- Claims form a before/after or cause/effect sequence
- Claims answer the same question from different angles
- Claims are all consequences of the same underlying mechanism
- Claims provide mutual context — understanding one deepens the other

**Split signals (the exception):**
- A reader would be confused why these claims are together
- The combined note obscures rather than illuminates
- Topics are so unrelated that the title can't honestly describe the scope

### 4. Semantic Search for Existing Notes

For each cluster, check if existing notes already cover the topic:

```
mcp__qmd__query  query="[cluster scope as sentence]"  collection="{vocabulary.notes_collection}"  limit=5
```

If MCP is unavailable, run:
```bash
qmd vsearch "[cluster scope as sentence]" --collection {vocabulary.notes_collection} -n 5
```
If qmd CLI is unavailable, fall back to keyword grep duplicate checks.

**Enrichment check:** If an existing note covers similar scope, does the source add new claims or detail? If YES, create enrichment task rather than new note.

### 5. Present Findings

**Mode-dependent output.** When invoked from `/pipeline` (task file path in context): append the grouping structure below to the source task file's `## Outputs` section — no chat output. When invoked standalone (no task file path): print the grouping structure below as chat output and wait for user approval before proceeding to step 6.

Grouping structure (same format for both modes):

```
## Proposed Structure Notes

### 1. [proposed title]
Sub-claims:
- [claim A]
- [claim B]
- [claim C]
Rationale: [why these belong together]

### 2. [proposed title]
...

### Enrichments
- [[existing note]] — [what new detail to add]
```

Standalone invocation only: wait for user approval before writing. When invoked from `/pipeline`, skip approval and proceed — per-note task files get written without interruption.

### 6. Write Notes

For each approved cluster, write a structure note.

---

## Large Source Handling

**For sources exceeding 2500 lines: chunk processing is MANDATORY.**

Context degrades as it fills. A single-pass review of a 3000-line source will miss clustering opportunities in later sections. Chunking ensures each section gets fresh attention.

### Chunking Strategy

| Source Size | Chunk Count | Chunk Size | Rationale |
|-------------|------------|------------|-----------|
| 2500-4000 lines | 3-4 chunks | 700-1200 lines | Standard chunking |
| 4000-6000 lines | 4-5 chunks | 800-1200 lines | Balanced attention |
| 6000+ lines | 5+ chunks | 1000-1500 lines | Prevent context overflow |

**Chunk boundaries:** Split at natural section breaks (headings, topic transitions). Never split mid-paragraph or mid-argument. A chunk should be a coherent unit of content.

**Cross-chunk coordination:** When processing in chunks, maintain a running list of identified clusters across chunks. Later chunks may ADD to earlier clusters — check before creating separate notes.

### Chunking Strategy

Fresh context per chunk (spawn subagent per chunk). Maximum quality.

---

## Enrichment Detection

When source content adds value to an EXISTING {vocabulary.note} rather than creating a new note, create an enrichment task instead.

### When to Create Enrichment Tasks

| Signal | Action |
|--------|--------|
| Source has new sub-claims for an existing structure note | Enrichment: add sections |
| Source has better examples for existing sections | Enrichment: add examples |
| Source has deeper framing or context | Enrichment: strengthen reasoning |
| Source has citations or evidence | Enrichment: add evidence base |

**The enrichment default:** When in doubt between "new structure note" and "enrichment to existing note", lean toward enrichment. The existing note already has connections, {vocabulary.topic_map} placement, and integration.

---

## Note Design Reference

### Template

```markdown
---
description: [~150 chars capturing the scope of grouped claims]
granularity: structure
type: [insight | pattern | preference | fact | decision | question]
claims:
  - "first sub-claim as prose"
  - "second sub-claim as prose"
created: YYYY-MM-DD
[domain-specific fields]
---

# [prose-as-title capturing topic scope]

## [First claim or argument thread]

[Body developing the first claim within shared context]

## [Second claim or argument thread]

[Body developing the second claim]

---

Source: [[source filename]]

Relevant Notes:
- [[related claim]] — [why it relates: extends, contradicts, builds on]

Topics:
- [[relevant {vocabulary.topic_map}]]
```

### Titles

See "The Prose-as-Title Pattern (Scope Variant)" above for full guidance. The scope test: "someone linking to this note would expect to find [sections you wrote]"

### Description

One field. ~150 characters. Must capture the SCOPE of the grouped claims — what questions the note addresses, what territory it covers.

Bad (too narrow): "caching reduces API latency by 40%"
Good (captures scope): "how cache hit rate, eviction strategy, and invalidation timing interact to determine API latency under varying load conditions"

### Sections

Each section develops one sub-claim within the shared context. Sections should:
- Have headings that state the claim or argument thread
- Develop the claim with reasoning, not just assertion
- Reference the shared evidence or context when relevant
- Cross-link to related {vocabulary.note_plural} where they extend or contradict

### Footer

```markdown
---

Source: [[source filename]]

Relevant Notes:
- [[related note]] — extends this by adding the temporal dimension

Topics:
- [[relevant {vocabulary.topic_map}]]
```

The relationship context explains WHY to follow the link:
- Bad: "-- related"
- Good: "-- contradicts by arguing for explicit structure"
- Good: "-- provides the foundation this challenges"

---

## Quality Gates

- Scope coherence: all sections in one note genuinely relate
- Title captures scope (not single claim, not vague topic label)
- Description adds info beyond title
- Each section develops its sub-claim, not just states it
- At least one {vocabulary.topic_map} link
- `granularity: structure` in frontmatter

### Red Flags: Over-splitting (primary concern)

- Creating single-section "structure" notes — if there's only one section, the scope is too narrow
- Splitting clusters because they could theoretically stand alone — that's not the question; the question is whether grouping hurts
- Refusing to group claims that share the same evidence base
- Redirecting content to other skills — the user chose /structure

### Red Flags: Under-grouping

- Grouping claims that have nothing in common beyond being in the same source
- Creating notes where sections confuse rather than illuminate
- Title that can't honestly predict what sections the reader will find

### Calibration Check (REQUIRED Before Finishing)

**STOP before outputting results.** Count your outputs by category:

```
structure notes proposed: ?
enrichment tasks: ?
truly skipped: ?
TOTAL: ?
```

---

## Queue Management

This skill always handles queue management for orchestrated execution.

### Per-Note Task Files

After structuring, for EACH approved note, create a task file in `ops/queue/`:

**Filename:** `{source}-NNN.md` where:
- {source} is the source basename (from the structure task)
- NNN is the note number, starting from `next_claim_start` in the structure task file

**Structure:**

```markdown
---
claim: "[the scope as a sentence]"
classification: closed | open
granularity: structure
source_task: [source-basename]
semantic_neighbor: "[related note title]" | null
---

# Note NNN: [note title]

Source: [[source filename]]

## Structure Notes

Extracted from [source_task]. Scope: [scope description].

Sub-claims:
- [claim A]
- [claim B]

Rationale: [why these belong together]

Semantic neighbor: [if found, explain why DISTINCT not DUPLICATE]

---

## Create
(to be filled by create phase)

## {vocabulary.cmd_reflect}
(to be filled by {vocabulary.cmd_reflect} phase)

## {vocabulary.cmd_reweave}
(to be filled by {vocabulary.cmd_reweave} phase)

## {vocabulary.cmd_verify}
(to be filled by {vocabulary.cmd_verify} phase)
```

### Queue Updates

After creating task files, update `ops/queue/queue.json`:

1. Mark the structure task as `"status": "done"` with completion timestamp
2. For EACH note, add ONE queue entry:

```json
{
  "id": "note-NNN",
  "type": "note",
  "granularity": "structure",
  "status": "pending",
  "target": "[note title]",
  "classification": "closed|open",
  "batch": "[source-basename]",
  "file": "[source-basename]-NNN.md",
  "created": "[ISO timestamp]",
  "current_phase": "create",
  "completed_phases": []
}
```

3. For EACH enrichment, add ONE queue entry:

```json
{
  "id": "enrich-EEE",
  "type": "enrichment",
  "status": "pending",
  "target": "[existing note title]",
  "source_detail": "[what to add]",
  "batch": "[source-basename]",
  "file": "[source-basename]-EEE.md",
  "created": "[ISO timestamp]",
  "current_phase": "enrich",
  "completed_phases": []
}
```

**Critical queue rules:**
- ONE entry per note (NOT one per phase) — phase progression is tracked via `current_phase` and `completed_phases`
- `type` is `"note"` with `"granularity": "structure"` — these are the task's single queue entries
- Every task MUST have `"file"` pointing to its uniquely-named task file
- Every task MUST have `"batch"` identifying which source batch it belongs to
- `current_phase` starts at `"create"` for notes, `"enrich"` for enrichments

### Handoff Output Format

After creating files and updating queue, output:

```
=== HANDOFF: structure ===
Target: [source file]

Work Done:
- Identified N topic clusters from [source]
- Created note files: {source}-NNN.md through {source}-NNN.md
- Created M enrichment files: {source}-EEE.md through {source}-EEE.md (if any)
- Duplicates skipped: [list or "none"]
- Semantic neighbors flagged for cross-linking: [list or "none"]

Files Modified:
- ops/queue/{source}-NNN.md (note files)
- ops/queue/{source}-EEE.md (enrichment files, if any)
- ops/queue/queue.json (N note tasks + M enrichment tasks, 1 entry each)

Learnings:
- [Friction]: [description] | NONE
- [Surprise]: [description] | NONE
- [Methodology]: [description] | NONE
- [Process gap]: [description] | NONE

Queue Updates:
- Mark: {source} done
- Create: note-NNN entries (1 per note, current_phase: "create")
- Create: enrich-EEE entries (1 per enrichment, current_phase: "enrich", if any)
=== END HANDOFF ===
```

---

## Template Reference

Note templates live in `ops/templates/structure/`.

---

## Downstream Routing

After structuring completes, the created {vocabulary.note_plural} proceed through the pipeline:

| State | Next Step | Why |
|-------|-----------|-----|
| {vocabulary.note} just created | /{vocabulary.cmd_reflect} | New {vocabulary.note_plural} need connections |
| After connecting | /{vocabulary.cmd_reweave} | Old {vocabulary.note_plural} need updating |
| Quality check | /{vocabulary.cmd_verify} | Combined verification gate |

---

## Critical

Never auto-structure when invoked standalone. Always present findings and wait for user approval before writing files. When invoked from `/pipeline` (task file path in context), the approval gate is skipped — per-note rationale and grouping summary are written to the task file instead; batch-level review happens at archive time.

**When in doubt about grouping: group.** The user chose /structure. Split only when keeping together would actively confuse or mislead.

**The principle:** find the best groupings that preserve shared context. Default to keeping related claims together.

**Remember:**
- The user chose this skill — respect that intent by grouping generously
- The title describes SCOPE, not a single claim
- `granularity: structure` distinguishes these from atomic notes
- Every section develops a sub-claim — it does not merely state it
