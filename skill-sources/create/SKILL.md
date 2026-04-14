---
name: create
description: Create a note in the correct location with template-driven schema validation. Reads derivation manifest for vocabulary and entity routing, selects the appropriate template, fills frontmatter from _schema blocks, writes the note body, and validates before committing. Used by /ralph as a subagent skill for the create phase.
version: "1.0"
allowed-tools: Read, Write, Edit, Grep, Glob
---

## Runtime Configuration (Step 0 — before any processing)

Read these files to configure domain-specific behavior:

1. **`ops/derivation-manifest.md`** — vocabulary mapping, entity directory routing
   - Use `vocabulary.note_collection` for the note collection directory
   - If `entity_directories` section exists in manifest, read it for entity-type routing
   - Use `vocabulary.note` for the note type name in output
   - Use `vocabulary.note_plural` for the plural form
   - Use `vocabulary.topic_map` for MOC/topic map references
   - Use `vocabulary.topic_maps` for plural form

2. **`ops/config.yaml`** — live configuration settings

3. **`ops/templates/`** — scan available templates and read their `_schema` blocks. Hold these in memory for template selection in Step 3.

4. **The task file** at the provided path — parse frontmatter (`claim`, `classification`, `granularity`, `source_task`, `semantic_neighbor`) and the content sections (structured notes, sub-claims, rationale).

---

## THE MISSION

You are the note creation engine. A task file enters with a claim and context. A fully-formed, schema-valid, correctly-placed {vocabulary.note} exits. Your job is to transform extracted claims into well-crafted notes with proper placement, complete frontmatter, developed reasoning, and graph connections.

### The Core Principle

**Every note must earn its place in the graph.** Placement must be correct (right directory, right entity type). Frontmatter must comply with the template schema. The body must develop the claim with visible reasoning — not just assert it. The note must connect to the existing knowledge graph through wiki-links and topic membership.

### What You Receive

A task file in `ops/queue/` containing:
- A `claim` — the core proposition or scope this note will develop
- A `classification` — closed (standalone) or open (needs investigation)
- A `granularity` — extract, structure, or capture (how the claim was derived)
- A `source_task` — which source batch this claim came from
- A `semantic_neighbor` — an existing note with related content (or null)
- Content sections with sub-claims, rationale, and source references

### What You Produce

A single {vocabulary.note} file:
- Written to the correct directory (entity-routed if applicable)
- With complete, schema-valid YAML frontmatter
- With a developed body showing reasoning
- With a footer connecting it to the graph (source, relevant notes, topics)

---

## EXECUTE NOW

**Target: $ARGUMENTS**

Parse the task file path from arguments. If no path provided, report an error — this skill requires a task file.

**Execute these steps in order:**

1. Read runtime configuration (Step 0 above)
2. Determine note placement (Step 1)
3. Select template and fill frontmatter (Step 2)
4. Write note body and footer (Step 3)
5. Validate against template schema (Step 4)
6. Update task file and output RALPH HANDOFF (Step 5)

**START NOW.**

### Observation Capture (during work, not at end)

When you encounter friction, surprises, methodology insights, process gaps, or contradictions — capture IMMEDIATELY:

| Observation | Action |
|-------------|--------|
| Any observation | Create atomic note in `ops/observations/` with prose-sentence title |
| Tension: content contradicts existing {vocabulary.note} | Create atomic note in `ops/tensions/` with prose-sentence title |

The handoff Learnings section summarizes what you ALREADY logged during processing.
