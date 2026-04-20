---
name: create
description: Create a note in the correct location with template-driven schema validation. Reads derivation manifest for vocabulary and entity routing, selects the appropriate template, fills frontmatter from _schema blocks, writes the note body, and validates before committing. Used by /pipeline as a subagent skill for the create phase.
version: "1.0"
context: fork
allowed-tools: Read, Write, Edit, Grep, Glob
---

## Runtime Configuration

### Vocabulary

All output must use domain-native terms.
Derivation manifest for vocabulary mapping:
!`cat ops/derivation-manifest.md`

### Configuration

!`cat ops/config.yaml`


### Templates

!`tree -L 3 ops/templates/`

Read the template's `_schema` block. These are used in Step 3.

### Task File

Read **The task file** at the provided path — parse frontmatter (`claim`, `classification`, `granularity`, `source_task`, `semantic_neighbor`) and the content sections (structured notes, sub-claims, rationale).

---

## THE MISSION

You are the note creation engine. A task file enters with a claim and context. A fully-formed, schema-valid, correctly-placed {vocabulary.note} exits. Your job is to transform claims into well-crafted notes with proper placement, complete frontmatter, developed reasoning, and graph connections.

### The Core Principle

**Every note must earn its place in the graph.** Placement must be correct (right directory, right entity type). Frontmatter must comply with the template schema. The body must develop the claim with visible reasoning — not just assert it. The note must connect to the existing knowledge graph through wiki-links and topic membership.

### What You Receive

A task file in `ops/queue/` containing:
- A `claim` — the core proposition or scope this note will develop
- A `classification` — closed (standalone) or open (needs investigation)
- A `granularity` — structure or capture (how the claim was derived)
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

Parse the task file path from arguments. If no path provided, end immediately with: "ERROR: create requires task file path from /pipeline"

**START NOW.**

### Observation Capture (during work, not at end)

When you encounter friction, surprises, methodology insights, process gaps, or contradictions — capture IMMEDIATELY:

| Observation | Action |
|-------------|--------|
| Any observation | Create atomic note in `ops/observations/` with prose-sentence title |
| Tension: content contradicts existing {vocabulary.note} | Create atomic note in `ops/tensions/` with prose-sentence title |

The handoff Learnings section summarizes what you ALREADY logged during processing.

---

## Step 1: Note Placement

Determine where the note file will be written. Three decisions in order.

### 1a. Base Directory

`vocabulary.note_collection`/ is the root directory for all notes.

`vocabulary.note_collection`/ structure:

!`tree -L 3 -d vocabulary.note_collection/`

### 1b. Entity Directory Routing

If the `entity_directories` section exists in the derivation manifest, examine the task file content — claim, classification, and context — to determine which entity-type subdirectory this note belongs in.

**Routing logic:**
- Read each entity type's description and scope from `entity_directories`
- Match the claim content against entity type descriptions
- Place the note in `{vocabulary.note_collection}/{entity_type}/`

If no `entity_directories` section exists in the manifest, place directly in `{vocabulary.note_collection}/`.

### 1c. Filename

The claim from the task file becomes the filename using the prose-as-title pattern.

**Title rules:**
- Lowercase with spaces
- No punctuation that breaks filesystems: `. * ? + [ ] ( ) { } | \ ^`
- Express the claim or scope fully — there is no character limit
- `.md` extension

**The prose-as-title test:** Can you complete this sentence?
> This {vocabulary.note} covers [title]

Good titles:
- "how caching strategies affect API latency under load" (structure — scope)

Bad titles:
- "caching" (topic label)
- "attention and context" (vague, not a scope)

### 1d. Uniqueness Check

Before writing, verify no file with the same name exists anywhere in the workspace:

```bash
find . -name "[proposed filename].md" -type f
```

If a collision is found, adjust the title to be more specific. Do NOT append numbers or suffixes — refine the claim to distinguish it from the existing note.

---

## Step 2: Template Selection and Frontmatter

### 2a. Select Template

Read all templates. For each template, examine the `_schema` block — specifically `entity_type`, `granularity`, `required` fields, and the `notes` description.

**Selection logic:**
- If only one template exists, use it
- If multiple templates exist, select the one that best aligns with the task file's content

Once selected, parse the `_schema` block fully:
- `required` — fields that MUST appear in the output frontmatter
- `optional` — fields that MAY appear when warranted
- `enums` — valid values for enum fields
- `constraints` — field-level rules (max_length, format, fixed values)

### 2b. Fill Frontmatter — Prescriptive Fields

These fields are always present regardless of template:

**`description`** (required):
- ~150 characters, no trailing period
- Must add information beyond the title — not a restatement
- Crafted from the task file's claim and surrounding context

Bad (restates title):
- Title: "LLM attention degrades as context fills"
- Description: Attention in LLMs gets worse as the context window fills up

Good (adds mechanism/scope):
- Title: "LLM attention degrades as context fills"
- Description: Token-level attention scores drop measurably after 60% context utilization, affecting retrieval accuracy for earlier tokens

**`topics`** (required):
- At least one wiki-link to a {vocabulary.topic_map}
- Scan existing {vocabulary.topic_maps} in the vault to find the best match:

```bash
find {vocabulary.note_collection}/ -name "*.md" -type f | head -50 | while read f; do
  if grep -q "^## Core Ideas" "$f" 2>/dev/null; then
    echo "$(basename "$f" .md)"
  fi
done
```

- If no existing {vocabulary.topic_map} matches, note this — the reflect phase will handle {vocabulary.topic_map} creation.

**`created`** (required):
- Today's date in YYYY-MM-DD format

### 2c. Fill Frontmatter — Template-Driven Fields

For each field in `_schema.required` that is not already filled by the prescriptive step:
- Read the field's constraints from `_schema.constraints`
- Read the field's valid values from `_schema.enums` (if it is an enum)
- Produce a value that satisfies all constraints, derived from the task file context

There are no optional fields. Every field in `_schema.required` must be filled. If a value cannot be derived from the task file context, fall back to the field's documented default (e.g. `tags: []`) rather than omitting the field.

**Enum fields:** Use ONLY values listed in `_schema.enums`. Never invent new enum values. If no listed value fits, choose the closest match and flag this in observations.

**Constrained fields:** Respect `_schema.constraints`:
- `max_length` — do not exceed the character limit
- `format` — follow the specified format exactly
- `fixed` — use the fixed value without modification

### 2d. The _schema Block

The `_schema` block is metadata ABOUT the template. It is NOT included in the output note's frontmatter. Strip it when writing the note.

---

## Step 3: Write Note Body and Footer

### 3a. Heading

```markdown
# [prose-as-title]
```

The heading is the same as the filename — the claim expressed as a readable sentence.

### 3b. Body — Prescriptive Rules

**Develop the claim. Do not just assert it.** The body explains WHY, provides context, and shows the reasoning chain. A note that merely restates the title in different words wastes the reader's time.

Writing principles:
- Show reasoning with connective words: because, therefore, this suggests, however, in contrast, building on
- Use inline wiki-links as prose where genuine connections exist: "Since [[other note]], the question becomes..." or "This contradicts [[existing claim]] because..."
- Reference the source material's evidence and reasoning — do not invent unsupported claims
- If the task file's `classification` is "open", acknowledge what remains unresolved
- Be careful with the reasoning. If the reasoning is not provided in the task file, do not make it up.

### 3d. Footer

The footer is always present and follows this exact structure:

```markdown
---

Source: [[source filename]]

Relevant Notes:
- [[related note]] — relationship context explaining WHY to follow the link

Topics:
- [[parent-moc]]
```

**Source:** Wiki-link to the source file. Derive the source name from `source_task` in the task file's frontmatter.

**Relevant Notes:**
- If `semantic_neighbor` exists in the task file (not null), include it as the first relevant note with context explaining the relationship
- Add any other genuine connections discovered while writing the body
- Each link MUST have a context phrase — bare links are not allowed
- Context phrases explain the relationship: "extends this by...", "contradicts because...", "provides the evidence base for..."

**Topics:**
- The {vocabulary.topic_map}(s) identified during frontmatter filling (Step 2b)
- Format as wiki-links: `- [[topic-name]]`

---

## Step 4: Validate Against Template Schema

After writing the note, validate it against the selected template's `_schema` block. Do NOT skip validation — catch drift at creation time, not at the verify phase.

### Validation Checks (run in order)

| # | Check | Severity | Action on Failure |
|---|-------|----------|-------------------|
| 1 | **Required fields** — every field in `_schema.required` exists in the written frontmatter | FAIL | Add missing field, re-validate |
| 2 | **Enum compliance** — every enum field's value is in `_schema.enums.{field}` | FAIL | Correct to valid value, re-validate |
| 3 | **Constraint compliance** — each field satisfies `_schema.constraints` (max_length, format, fixed) | FAIL | Fix constraint violation, re-validate |
| 4 | **Description quality** — adds info beyond the title (not a restatement, not empty) | FAIL | Rewrite description, re-validate |
| 5 | **Topics present** — at least one wiki-link in the topics field | FAIL | Add topic link, re-validate |
| 6 | **Wiki-link health** — `[[links]]` in body/footer point to files that exist | WARN | Log, continue |

### Severity Levels

- **FAIL** — missing required field, invalid enum, constraint violation, empty description, no topics. The skill MUST fix the issue inline (edit the note) and re-validate. No FAIL-state notes get written to the vault.
- **WARN** — broken wiki-link to a note that doesn't exist yet, missing optional field. Log the warning and continue. Broken links are common during batch creation — sibling notes may not exist yet.

### Fix-Before-Commit Protocol

If any FAIL is detected:
1. Edit the note file to fix the issue
2. Re-run the failing check
3. Continue only when all FAIL checks pass

No FAIL-state notes get written to the vault.

---

## Step 5: Update Task File and Handoff

### 5a. Update Task File

Edit the task file to fill the `## Create` section:

```markdown
## Create
Created: {full path to the note file}
Template: {template filename used}
Description: {the description written in frontmatter}
Validated: {PASS | list of WARN items}
```

This gives downstream phases (reflect, reweave, verify) the exact path and context they need.

### 5b. Output HANDOFF Block

After updating the task file, output the handoff block. This is how /pipeline captures your work.

```
=== HANDOFF: create ===
Target: {claim from task file frontmatter}

Work Done:
- Created {vocabulary.note}: {full path to note file}
- Template: {template filename}
- Placed in: {directory path}
- Validation: {PASS or WARN count}

Learnings:
- [Friction]: {description} | NONE
- [Surprise]: {description} | NONE
- [Methodology]: {description} | NONE
- [Process gap]: {description} | NONE
=== END HANDOFF ===
```

---

## Critical Constraints

**Always:**
- Use domain-native vocabulary from the manifest in all output
- Route through entity directories when `entity_directories` exists
- Validate against the template schema after writing
- Fix FAIL-severity issues before proceeding
- Update the task file's `## Create` section
- Output the HANDOFF block as the last action
