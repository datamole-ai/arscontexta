---
name: structure
description: Internal pipeline skill — groups claims from source material into structured notes. Invoked by /pipeline as a subagent; do not invoke directly.
version: "1.0"
context: fork
allowed-tools: Read, Write, Grep, Glob, mcp__qmd__query
---

### Vocabulary

All output must use domain-native terms.
Derivation manifest for vocabulary mapping:
!`cat ops/derivation-manifest.md`

### Task Queue

Current task queue:
!`cat ops/queue/queue.json`

---

## THE MISSION (READ THIS OR YOU WILL FAIL)

You are the structuring engine. Raw source material enters. Finished, schema-valid {vocabulary.note_plural} exit — either newly written or enriched in place. Your job spans five phases: identify topic clusters, classify each against the existing graph, materialize the artifact (new note or enrichment to an existing note), queue it for downstream processing, and emit a single handoff block.

### The Core Principle

**Structure is the only producer in the Reduce phase.** No separate create or enrich skill runs after you — the pipeline hands newly materialized artifacts directly to /reflect. Your job is to find the best groupings AND produce the resulting notes with full schema compliance. The default is to group. Split only when keeping claims together actively confuses or misleads.

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

Parse the source file path from arguments. If no argument is provided, report
`ERROR: structure requires source file path` and stop.

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

If MCP is unavailable (e.g. running inside a subagent that does not inherit MCP access), use the CLI:
```bash
qmd vsearch "[cluster scope as sentence]" --collection {vocabulary.notes_collection} -n 5
```
If qmd itself is not installed, stop and tell the user to install it — semantic search is an invariant kernel primitive and duplicate detection cannot safely run on keyword grep alone.

**Enrichment check:** If an existing note covers similar scope, does the source add new claims or detail? If YES, create enrichment task rather than new note.

### 5. Present Findings

Append the grouping structure below to the source task file's `## Outputs` section. No chat output.

Grouping structure:

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

Read the target existing note (the `semantic_neighbor` identified during Classify). Parse:
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

**Update frontmatter:**
- Update `updated` (or equivalent timestamp field) to today's date. If the template has no `updated` field, skip.
- If the note has a `sources` list (or equivalent provenance field), append the new source.
- If the cluster changes the note's scope such that `description` is now misleading, DO NOT auto-revise the description. Flag it in the handoff under "description may need refresh" — leave the description as-is.

**Update footer:**
- Append the new source to the existing `Source:` line as an additional wiki-link if the footer uses the multi-source pattern, OR add a line `Additional source: [[new source]]` if the footer uses the single-source pattern. Match the existing convention.
- Add any new relevant-notes connections discovered while writing, each with a context phrase.

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

**Entity directory routing:** If `entity_directories` appears in the derivation manifest, match the cluster's claim/classification/context against each entity type's description and place the note in `{vocabulary.note_collection}/{entity_type}/`. If no `entity_directories` block exists, place directly in `{vocabulary.note_collection}/`.

**Filename:** the cluster's scope expressed as a prose sentence. Rules:
- Lowercase with spaces
- No filesystem-breaking punctuation: `. * ? + [ ] ( ) { } | \ ^`
- Express the full scope; there is no character limit
- `.md` extension

The prose-as-title test: can you complete this sentence?
> This {vocabulary.note} covers [title]

Before writing, verify no collision:

```bash
find . -name "[proposed filename].md" -type f
```

If a collision is found, refine the title to be more specific. Do NOT append numbers or suffixes — refine the claim to distinguish it.

### M2. Select Template and Fill Frontmatter

**Select template:** Read all templates in `ops/templates/`. For each, examine the `_schema` block (`entity_type`, `granularity`, `required` fields). Select the template whose `_schema` field set best fits the cluster. If only one template exists, use it.

Parse the selected `_schema` block fully:
- `required` — fields that MUST appear in the output
- `optional` — fields that MAY appear when warranted
- `enums` — valid values for enum fields
- `constraints` — field-level rules (`max_length`, `format`, `fixed`)

**Fill prescriptive fields** (always present regardless of template):

- **`description`** (required): ~150 characters, no trailing period, adds information beyond the title. Example of a bad description that restates the title: Title "LLM attention degrades as context fills" → Description "Attention in LLMs gets worse as the context window fills up". Example of a good description that adds mechanism: Same title → "Token-level attention scores drop measurably after 60% context utilization, affecting retrieval accuracy for earlier tokens".
- **`created_at`** (required): today's date in YYYY-MM-DD format.

Identify the parent {vocabulary.topic_map}(s) now — they will be written into the body footer in M3. At least one is required. Scan existing topic maps:

```bash
find {vocabulary.note_collection}/ -name "*.md" -type f | head -50 | while read f; do
  if grep -q "^## Core Ideas" "$f" 2>/dev/null; then
    echo "$(basename "$f" .md)"
  fi
done
```

If no existing topic map matches, note this — the reflect phase will handle topic map creation.

**Fill template-driven fields:** For each field in `_schema.required` not already filled by the prescriptive step, derive a value from the cluster content that satisfies all constraints. Enum fields use ONLY values from `_schema.enums`. Constrained fields respect `max_length`, `format`, `fixed`. There are no optional fields — every field in `_schema.required` must be filled.

The `_schema` block is metadata ABOUT the template; it is NOT included in the output note's frontmatter. Strip it when writing.

### M3. Write Body and Footer

**Heading:** same as the filename, expressed as the prose-as-title claim.

**Body (prescriptive rules):**
- Develop the claim. Do not just assert it. Show WHY, provide context, show the reasoning chain.
- Use connective words: because, therefore, this suggests, however, in contrast, building on.
- Use inline wiki-links as prose where genuine connections exist: "Since [[other note]], the question becomes..." or "This contradicts [[existing claim]] because..."
- Reference the source material's evidence and reasoning — do not invent unsupported claims.
- If the cluster is "open" (needs investigation), acknowledge what remains unresolved.
- If the reasoning is not provided in the source, do not make it up.

For structure notes, body sections each develop one sub-claim within the shared context. Section headings state the claim or argument thread, not a vague topic label.

**Footer** (always present, exact structure):

```markdown
---

Source: [[source filename]]

Relevant Notes:
- [[related note]] — relationship context explaining WHY to follow the link

Topics:
- [[parent-topic-map]]
```

Derive `Source:` from the structure task's source. `Relevant Notes:` includes the semantic neighbor (if classification found one) as the first entry with a context phrase ("extends this by...", "contradicts because...", "provides the evidence base for..."); add other genuine connections discovered while writing. Bare links are not allowed. `Topics:` lists the {vocabulary.topic_map}(s) identified in M2 — at least one entry, used as orientation for readers (the MOC's `## Core Ideas` list remains the canonical membership index).

### M4. Schema Validation (run in order)

See the Shared Helpers appendix for the full 6-check validation procedure. Severity rules:
- **FAIL** — missing required field, invalid enum, constraint violation, empty description, empty Topics footer. FIX INLINE (edit the note) and re-validate. No FAIL-state notes get written.
- **WARN** — broken wiki-link to a note that does not exist yet, missing optional field. Log and continue.

If validation FAILs cannot be resolved after one fix attempt, quarantine the artifact (see Shared Helpers) and continue with the next cluster.

---

## Note Design Reference

### Template

```markdown
---
content_type: [one of the vault's derived content_type enum values, e.g. {DOMAIN:content_type}]
granularity: structure
description: [<=200 chars capturing the scope of grouped claims, no trailing period]
created_at: YYYY-MM-DD
tags: []
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

Structure produces the note and writes the queue entry in the same run. Task files exist only to carry downstream-phase output (reflect → reweave → verify → rethink) — they are created pre-populated with the work already done.

### Per-Artifact Task Files

After materializing each new note OR enrichment, create a task file in `ops/queue/`:

**Filename:**
- New notes: `{source}-NNN.md` where NNN starts from `next_claim_start` in the structure task file.
- Enrichments: `{source}-EEE.md` where EEE starts at 1 and increments per enrichment.

**Structure:**

```markdown
---
claim: "[the scope as a sentence]"
classification: closed | open
granularity: structure
type: note | enrichment
source_task: [source-basename]
semantic_neighbor: "[related note title]" | null
target_path: [full path to the materialized or enriched note]
---

# {Note NNN | Enrichment EEE}: [title or target name]

Source: [[source filename]]

## Structure Notes

Extracted from [source_task]. Scope: [scope description].

Sub-claims:
- [claim A]
- [claim B]

Rationale: [why these belong together, or — for enrichments — why this strengthens the target note]

Semantic neighbor: [if found, explain the relationship]

## Materialize

{For new notes: path to written file, template used, validation result.}
{For enrichments: target path, mode chosen (inline-integrate | append-with-tension | append-new-section), validation result.}

---

## {vocabulary.cmd_reflect}
(to be filled by {vocabulary.cmd_reflect} phase)

## {vocabulary.cmd_reweave}
(to be filled by {vocabulary.cmd_reweave} phase)

## {vocabulary.cmd_verify}
(to be filled by {vocabulary.cmd_verify} phase)
```

### Queue Updates

After creating task files, update `ops/queue/queue.json`:

1. Mark the structure task as `"status": "done"` with completion timestamp.
2. For each materialized artifact (new note OR enrichment), add ONE queue entry:

```json
{
  "id": "note-NNN" | "enrich-EEE",
  "type": "note" | "enrichment",
  "granularity": "structure",
  "status": "pending",
  "target": "[note title or enriched-note title]",
  "target_path": "[full path to the written/modified note]",
  "classification": "closed|open",
  "batch": "[source-basename]",
  "file": "[source-basename]-NNN.md | [source-basename]-EEE.md",
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
- Every task MUST have `"file"` pointing to its uniquely-named task file and `"target_path"` pointing to the materialized note.
- Every task MUST have `"batch"` identifying which source batch it belongs to.

### Handoff Output Format

After materializing all artifacts, creating task files, and updating the queue, output a single handoff block:

```
=== HANDOFF: structure ===
Target: [source file]

Work Done:
- Identified N topic clusters from [source]
- Classified: {written} new, {enriched} enrichment, {skipped} duplicates
- New notes written: {source}-NNN.md through {source}-NNN.md → paths: [list target_paths]
- Enrichments applied: {source}-EEE.md through {source}-EEE.md → targets: [list target note titles with chosen mode]
- Quarantined: [list artifacts + reason, or "none"]
- Descriptions flagged for refresh: [list target notes whose scope drifted, or "none"]

Files Modified:
- {vocabulary.note_collection}/ ({written} new notes + {enriched} modified notes)
- ops/queue/{source}-NNN.md (note task files)
- ops/queue/{source}-EEE.md (enrichment task files)
- ops/queue/queue.json (1 entry per materialized artifact, current_phase: "reflect")
- ops/quarantine/ (any quarantined artifacts with .reason sidecars)
- ops/tensions/ (any tension notes created during append-with-tension enrichments)

Summary: {written: N, enriched: M, quarantined: K}

Learnings:
- [Friction]: [description] | NONE
- [Surprise]: [description] | NONE
- [Methodology]: [description] | NONE
- [Process gap]: [description] | NONE

Queue Updates:
- Mark: {source} done
- Create: {written + enriched} entries (current_phase: "reflect", completed_phases: ["structure"])
=== END HANDOFF ===
```

---

## Template Reference

The single unified note template lives at `ops/templates/note.md`. Every note uses it regardless of `content_type` or `granularity`; structure notes set `granularity: structure` in frontmatter.

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

**When in doubt about grouping: group.** Split only when keeping together would actively confuse or mislead.

**The principle:** find the best groupings that preserve shared context. Default to keeping related claims together.

**Remember:**
- The user chose this skill — respect that intent by grouping generously
- The title describes SCOPE, not a single claim
- `granularity: structure` distinguishes these from atomic notes
- Every section develops a sub-claim — it does not merely state it

---

## Shared Helpers (Reference)

Appendix referenced by both Materialize paths. Do not invoke independently.

### Schema Validation (6 checks, run in order)

| # | Check | Severity | Action on Failure |
|---|-------|----------|-------------------|
| 1 | **Required fields** — every field in `_schema.required` exists in the frontmatter | FAIL | Add missing field, re-validate |
| 2 | **Enum compliance** — every enum field's value is in `_schema.enums.{field}` | FAIL | Correct to valid value, re-validate |
| 3 | **Constraint compliance** — each field satisfies `_schema.constraints` (`max_length`, `format`, `fixed`) | FAIL | Fix violation, re-validate |
| 4 | **Description quality** — adds info beyond the title (not a restatement, not empty) | FAIL | Rewrite description, re-validate |
| 5 | **Topics footer present** — at least one wiki-link in the body-level `Topics:` footer | FAIL | Add topic link, re-validate |
| 6 | **Wiki-link health** — `[[links]]` in body/footer point to files that exist | WARN | Log, continue |

**Severity levels:**
- **FAIL** — missing required field, invalid enum, constraint violation, empty description, empty Topics footer. Fix inline (edit the content in memory) and re-validate. If a FAIL cannot be resolved after one fix attempt, quarantine the artifact.
- **WARN** — broken wiki-link to a note that does not exist yet, missing optional field. Log the warning and continue. Broken links are common during batch creation — sibling notes may not exist yet.

### Quarantine Procedure

When validation FAIL cannot be resolved:

1. Write the proposed artifact to `ops/quarantine/<filename>` (for new notes: same basename as would have been written; for enrichments: `{target-basename}-enrichment-{YYYY-MM-DD-HHMM}.md` carrying the proposed modified content).
2. Write a sidecar `ops/quarantine/<filename>.reason` containing the validation failure summary (which checks failed, what values were produced, what's blocking).
3. Do NOT write to `{vocabulary.note_collection}/` for new notes, and do NOT modify the target note for enrichments.
4. Do NOT emit a queue entry for the quarantined artifact.
5. Continue with the next cluster. Quarantine does not abort the batch.

### Topic Map Scan

Find existing {vocabulary.topic_map}s in the vault:

```bash
find {vocabulary.note_collection}/ -name "*.md" -type f | head -50 | while read f; do
  if grep -q "^## Core Ideas" "$f" 2>/dev/null; then
    echo "$(basename "$f" .md)"
  fi
done
```

If no existing topic map matches the cluster, leave `topics` with a best-available placeholder link and flag it in the handoff — the reflect phase will handle topic map creation.

### Uniqueness Check for Filenames

Before writing a new note:

```bash
find . -name "[proposed filename].md" -type f
```

If a collision is found, refine the title to be more specific. Do NOT append numbers or suffixes.
