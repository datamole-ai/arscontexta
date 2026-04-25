---
name: structure
description: Internal pipeline skill — groups claims from source material into structured notes. Invoked by /pipeline as a subagent; do not invoke directly.
version: "1.0"
context: fork
allowed-tools: Read, Write, Grep, Glob, Bash
---

### Vocabulary

All output must use domain-native terms.
Derivation manifest for vocabulary mapping:
!`cat ops/derivation-manifest.md`

### Task Queue

Current task queue:
!`cat ops/queue/queue.json`

### Templates

Available templates:
!`tree -L 2 ops/templates/`

---

## Core Principle

**Structure is the only producer in the Reduce phase.** Your job is to find the best groupings AND produce the resulting notes with full schema compliance. Default to grouping; split only when keeping claims together actively confuses.

---

## EXECUTE NOW

**Target: $ARGUMENTS**

Parse the batch id from arguments (the source basename, e.g. `my-source`). If no argument is provided, report `ERROR: structure requires batch id` and stop.

Look up the process entry in `ops/queue/queue.json`:

```bash
jq --arg id "$BATCH_ID" '.tasks[] | select(.id == $id and .type == "process")' ops/queue/queue.json
```

From that entry, obtain:
- `id` — the batch id (source basename)
- `source` — the archived source file path to process
- `archive_folder` — where the source lives
- `next_claim_start` — first claim number to use
- `granularity` — must equal `structure` (error out otherwise)

All subsequent references to "the source" use the `source` value from the queue entry.

**START NOW.** Reference below explains methodology — use to guide, not as output.

### Observation Capture

When you encounter friction, surprises, methodology insights, process gaps, or contradictions — capture IMMEDIATELY:

| Observation | Action |
|-------------|--------|
| Any observation | Create atomic note in `ops/observations/` with prose-sentence title |
| Tension: content contradicts existing {vocabulary.note} | Create atomic note in `ops/tensions/` with prose-sentence title |

The output Learnings section summarizes what you ALREADY logged during processing.

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

## Source Fidelity

Every sentence in a {vocabulary.note} body must paraphrase a specific line or paragraph of the source. Do not add connective prose, motivation, mechanism explanations, implications, or rationale that is not in the source. If a claim needs background to make sense, either omit it (the source citation suffices) or flag the gap — do not invent the background. When the source is terse, the {vocabulary.note} is proportionally terse; inflation is a fidelity failure, not a thoroughness win.

Neighbor linking is /reflect's job — /structure does not pre-seed wiki-links in the body. At this phase, source-fidelity means: if it is not in the source, it does not enter the body.

---

## Scope Coherence

Three quality checks before saving any structure {vocabulary.note}:

1. **Scope coherence** — Do all sections share evidence, argument, or mechanism from the source? Every section's content must trace to the source.
2. **Source-bounded standalone sense** — Does the {vocabulary.note} cohere using only source-attested claims? If the only way to make it "stand alone" is to add context not in the source, the scope is too narrow — split, or accept the terseness. /reflect will add neighbor links later.
3. **Linkability** — The scope is defined clearly enough for other {vocabulary.note_plural} to link to without ambiguity.

If any check fails, the note needs restructuring — adjust sections or scope, don't reflexively split.

### The Prose-as-Title Pattern

A structure note title is a **sentence** describing the scope of the grouped claims — not a list of topics. When linked into prose, it still reads naturally as a noun phrase ("building on [[title]]", "we explored [[title]]"), but the title itself must parse as a sentence when the completion gate is applied.

**The completion gate:** Can you complete this sentence?
> Since [title], ...

If it parses as a sentence, the title describes a coherent scope. If it reads as a list or trails off incoherently, it is a topic label (too narrow) or a noun bag (too flat) — rewrite before committing.

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
- Must form a sentence after "Since …". A verb or relational preposition (how, why, between, shaped, drives, affects) will typically appear.

---

## Workflow

### 1. Read Source Fully

Read the ENTIRE source. Understand what it contains, what topics it covers, what claims are related.

**Planning the grouping:**
- How many topic clusters do you expect from this source?
- Which clusters share evidence, argument threads, or context?

### 2. Identify Topic Clusters

Group candidates by shared context, evidence, or argument thread. Default to grouping.

**Grouping signals:**
- Claims reference the same study, experiment, or evidence
- Claims form a before/after or cause/effect sequence
- Claims are all consequences of the same underlying mechanism
- Claims provide mutual context — understanding one deepens the other

**Split signals (the exception):**
- A reader would be confused why these claims are together
- The combined note obscures rather than illuminates
- Topics are so unrelated that the title can't honestly describe the scope

### 3. Semantic Search for Existing Notes

For each cluster, check if existing notes already cover the topic:

```bash
qmd query $'vec: [cluster scope as sentence]' --collection {vocabulary.qmd_collection} -n 5
```

**Enrichment check:** If an existing note covers similar scope, does the source add new claims or detail? If YES, create enrichment task rather than new note.

**Classification-only.** Search results drive enrichment-vs-new-note routing. On the new-note path, results do NOT contribute content to the new note's body.

### 4. Proposed Groupings

Keep the grouping analysis in working memory — it becomes the `### Work` section of the Output Block emitted after materialization.

### 5. Write Notes

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

---

## Materialize — Enrichment Path

For every cluster classified as an *enrichment* (an existing note covers the scope and the cluster adds evidence, refinement, or alternative framing), modify the existing note in place. Never create a new note on the enrichment path.

### When a Cluster Is an Enrichment

| Signal | Action |
|--------|--------|
| Source has new sub-claims for an existing structure note | Enrichment: add section or inline-integrate |
| Source has better examples for existing sections | Enrichment: add examples |
| Source has deeper framing or context | Enrichment: strengthen reasoning |
| Source has citations or evidence | Enrichment: add evidence base |
| Source contradicts or reframes existing claim | Enrichment: append alternative framing + create tension note |

**The enrichment default:** When in doubt between "new structure note" and "enrichment to existing note", lean toward enrichment. The existing note already has connections, {vocabulary.topic_map} placement, and integration.

### E1. Load the Target

Read the target existing note (the semantic neighbor identified during Classify). Parse:
- Frontmatter (keep the full YAML for later rewrite)
- Body sections (headings + content)
- Footer (Source, Relevant Notes, Topics)

### E2. Decide Integration Mode

Scan the target note's body for a section whose heading or topic matches the cluster's thrust. Use wiki-link overlap and topic-tag overlap as signals. Three modes:

- **inline-integrate** — a matching section exists AND the cluster adds evidence or refinement that fits that section. Append the cluster's developed content as additional paragraphs under that section heading. Keep the heading intact.
- **append-with-tension** — a matching section exists AND the cluster contradicts or significantly reframes it. Add a new subsection titled `### Alternative framing from {source}` immediately below the matching section. Do NOT alter the prior content. Also create a tension note in `ops/tensions/` per the Observation Capture rules.
- **append-new-section** — no matching section exists. Add a new `## {topic}` section at the end of the body, immediately above the `---` that precedes the footer.

Decide mode before writing. Log the chosen mode for the handoff summary.

### E3. Apply the Modification

Write the new content into the chosen location using the same body rules as the New-note path (develop the claim, use connective words, inline wiki-links where genuine, reference source evidence, do not invent claims).

**Preserve invariants (non-negotiable):**
- NEVER delete existing body content.
- NEVER remove existing wiki-links.
- NEVER alter existing section headings (inline-integrate appends under the heading; it does not rewrite it).
- NEVER strip existing footer entries.

**Update footer:**
- Append the new source to the existing `Source:` line as an additional wiki-link.

### E4. Two-Phase Validation and Write

Enrichment writes are atomic:

1. Compose the full modified note content in memory (frontmatter + body + footer).
2. Run the 6-check schema validation from Shared Helpers on the in-memory content.
3. **On PASS:** overwrite the target note file. Emit a queue entry (see Queue Management) with `type: enrichment`, `current_phase: reflect`, `target_path` set to the modified note's path.
4. **On FAIL:** the target note file is NOT modified. Write the proposed content to `ops/quarantine/{target-basename}-enrichment-{YYYY-MM-DD-HHMM}.md` with a sidecar `.reason` file containing the failure detail. Skip emitting a queue entry for this enrichment. Log in the handoff as quarantined.

---

## Materialize — New-note Path

For every cluster classified as a *new note* (no existing note covers the scope), produce the artifact inline. Four sub-steps, executed per cluster:

### M1. Place the Note

Three decisions in order.

**Base directory:** `{vocabulary.note_collection}/` is the root for all notes.

**Entity directory routing:** Place the note in the appropriate directory in the following structure:
!`tree -L 2 -d {DOMAIN:note_collection}`

**Filename:** Title according to the prose-as-title pattern mentioned in the Philosophy section.

### M2. Select Template and Fill Frontmatter

**Select template:** Select the template whose `_schema` field set best fits the cluster. If only one template exists, use it.

Parse the selected `_schema` block fully:
- `required` — fields that MUST appear in the output
- `enums` — valid values for enum fields
- `constraints` — field-level rules (`max_length`, `format`, `fixed`)

**Fill prescriptive fields.**

Identify the parent {vocabulary.topic_map}(s) now — they will be written into the body footer in M3. At least one is required. Scan existing topic maps:

```bash
grep -rl "^content_type: moc$" {DOMAIN:note_collection}/ --include="*.md" | while read f; do
  echo "$(basename "$f" .md)"
done
```

If no existing topic map matches, note this — the reflect phase will handle topic map creation.

**Fill template-driven fields:** For each field in `_schema.required` not already filled by the prescriptive step, derive a value from the cluster content that satisfies all constraints. Enum fields use ONLY values from `_schema.enums`. Constrained fields respect `max_length`, `format`, `fixed`.

Do not include the `_schema` block in the output note's frontmatter.

### M3. Write Body and Footer

**Heading:** same as the filename, expressed as the prose-as-title claim.

**Body (prescriptive rules):**
- Body is sourced from the input file only. Neighbor notes read during Orient or Semantic Search inform classification, not composition. Do not import their claims, framings, or evidence into this note. If it is not in the source, do not write it.
- Develop the claim. Do not just assert it. Show WHY, provide context. Keep it close to the source material.
- If the reasoning is not provided in the source, do not make it up.
- Reference the source material's evidence and reasoning — do not invent unsupported claims.
- Use connective words: because, therefore, this suggests, however, in contrast, building on.
- Do not include wiki-links in the body. Connection-finding belongs to `/reflect`, which runs semantic search and verifies targets before writing links. Pre-seeding links here produces dangling links and duplicates reflect's work without its verification.

For structure notes, body sections each develop one sub-claim within the shared context. Section headings state the claim or argument thread, not a vague topic label.

**Footer** (always present, exact structure):

```markdown
---

Source: [[source filename]]

Topics:
- [[parent-topic-map]]
```

Derive `Source:` from the structure task's source. `Topics:` lists the {vocabulary.topic_map}(s) identified in M2

### M4. Schema Validation

See the Shared Helpers appendix for the full 7-check validation procedure. Severity rules:
- **FAIL** — missing required field, invalid enum, constraint violation, empty description, empty Topics footer, any wiki-link in the body. FIX INLINE (edit the note) and re-validate. No FAIL-state notes get written.
- **WARN** — broken footer wiki-link (typically a `Topics:` link to a not-yet-existent MOC, which `/reflect` creates), missing optional field. Log and continue.

If validation FAILs cannot be resolved after one fix attempt, quarantine the artifact (see Shared Helpers) and continue with the next cluster.

---

## Queue Management

**Queue mutation sequence (run in order before emitting the Output Block):**

1. Read `ops/queue/queue.json`.
2. Set the process task entry's `status: "done"` and add `completed: "<ISO UTC now>"`.
3. Append one new entry per artifact with the shape shown in "Queue Updates" below.
4. Write the file back.

### Queue Updates

Update `ops/queue/queue.json`:

1. Mark the process queue entry as `"status": "done"` with completion timestamp.
2. For each materialized artifact (new note OR enrichment), add ONE queue entry:

```json
{
  "id": "note-NNN" | "enrich-EEE",
  "type": "note" | "enrichment",
  "granularity": "structure",
  "status": "pending",
  "target": "[note title or enriched-note title]",
  "target_path": "[full path to the written/modified note]",
  "batch": "[source-basename]",
  "created": "[ISO timestamp]",
  "current_phase": "reflect",
  "completed_phases": ["structure"]
}
```

3. For each quarantined artifact, do NOT add a queue entry. Log it in the handoff instead.

**Critical queue rules:**
- ONE entry per artifact (NOT one per phase).
- `current_phase` starts at `"reflect"` for every entry produced by structure — the materialization is already done.
- `completed_phases` starts as `["structure"]` — reflecting that structure has already produced the finished artifact.
- Every task MUST have `"target_path"` pointing to the materialized note.
- Every task MUST have `"batch"` identifying which source batch it belongs to.

### Output Block

After materializing all artifacts and updating `ops/queue/queue.json` (mark process task done + append one pending entry per artifact), emit the canonical block below as the final chat message. This is the ONLY chat output — no task file is written.

```
## Structure

**Target:** {batch-id}
**Status:** ok | error: {short message}
**Queue:** marked {batch-id}: process -> done; created {W} note entries and {E} enrichment entries (current_phase: reflect)

### Work
- Identified {N} topic clusters from {source}
- Classified: {W} new, {E} enrichment, {S} skipped as duplicates
- New notes: [{list of note target_paths}]
- Enrichments: [{list of target note titles with chosen mode}]
- Quarantined: [list artifacts + reason, or "none"]
- Descriptions flagged for refresh: [list target notes, or "none"]

### Learnings
- [Friction]: {description} | NONE
- [Surprise]: {description} | NONE
- [Methodology]: {description} | NONE
- [Process gap]: {description} | NONE
```

On error, set `Status: error: <message>`, `Queue: no change (error)`, fill `### Work` with what got done before the failure, and leave `queue.json` unchanged.

## Shared Helpers (Reference)

Appendix referenced by both Materialize paths. Do not invoke independently.

### Schema Validation (7 checks, run in order)

| # | Check | Severity | Action on Failure |
|---|-------|----------|-------------------|
| 1 | **Required fields** — every field in `_schema.required` exists in the frontmatter | FAIL | Add missing field, re-validate |
| 2 | **Enum compliance** — every enum field's value is in `_schema.enums.{field}` | FAIL | Correct to valid value, re-validate |
| 3 | **Constraint compliance** — each field satisfies `_schema.constraints` (`max_length`, `format`, `fixed`) | FAIL | Fix violation, re-validate |
| 4 | **Description quality** — adds info beyond the title (not a restatement, not empty) | FAIL | Rewrite description, re-validate |
| 5 | **Topics footer present** — at least one wiki-link in the body-level `Topics:` footer | FAIL | Add topic link, re-validate |
| 6 | **Body has no wiki-links** — body (content between the H1 heading and the `---` separator that precedes the footer) contains no `[[...]]` | FAIL | Remove body wiki-links, re-validate |
| 7 | **Footer wiki-link health** — `[[links]]` in the `Source:` and `Topics:` footers resolve to existing files | WARN | Log, continue |

**Severity levels:**
- **FAIL** — missing required field, invalid enum, constraint violation, empty description, empty Topics footer, any wiki-link present in the body. Fix inline (edit the content in memory) and re-validate. If a FAIL cannot be resolved after one fix attempt, quarantine the artifact.
- **WARN** — broken footer wiki-link (most often a `Topics:` link to a not-yet-existent MOC), missing optional field. Log the warning and continue. Topic-map creation happens in `/reflect`; structure flags missing MOCs rather than blocking on them.
