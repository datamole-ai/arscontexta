---
name: verify
description: Internal pipeline skill — runs recite + validate + review quality gate on a note. Invoked by /pipeline as a subagent; do not invoke directly.
context: fork
allowed-tools: Read, Write, Edit, Grep, Glob, mcp__qmd__query
---

## Runtime Configuration

### Vocabulary

All output must use domain-native terms.
Derivation manifest for vocabulary mapping:
!`cat ops/derivation-manifest.md`

### Templates

The templates available are:
!`tree -L 2 ops/templates/`

## Granularity-Aware Verification

After reading the target {vocabulary.note}, check its `granularity` frontmatter field:

- **`structure`**: Scope coherence test (do all sections belong together?), section development test (does each section develop its sub-claim, not just state it?), description cold-read test, schema compliance, link health (no broken links, in at least one {vocabulary.topic_map}).
- **`capture`**: Description cold-read test, schema compliance, link health. Skip scope coherence test. Add: verbatim integrity check — fenced block present and non-empty, no wikilinks or edits inside the fenced block, all connections in footer sections only.

## EXECUTE NOW

**Target: $ARGUMENTS**

Parse the {vocabulary.note} path from arguments. If no argument is provided, end immediately with: report
`ERROR: verify requires {vocabulary.note} path`.

**START NOW.**

### Step 1: RECITE (cold-read prediction test)

**CRITICAL: Do NOT read the full note yet. Only read frontmatter.**

This step tests whether the title + description alone enable an agent to predict the note's content. The cold-read constraint is the entire point — reading the note first contaminates the prediction.

**1. Read ONLY title + description**

Use Read with a line limit to get just the first few lines of frontmatter. Extract:
- Title (the filename without .md)
- Description (the description field)

Do NOT scroll past the frontmatter closing `---`.

**2. Form prediction**

Before reading further, write out what you expect:
- Core argument: what claim does this note make?
- Mechanism: what reasoning or evidence does it use?
- Scope: what boundaries does the argument have?
- Likely connections: what other notes would it reference?

Write this prediction explicitly in your output. It must be specific enough to be wrong.

**3. Read full note content**

NOW read the complete note. Compare against your prediction.

**4. Score prediction accuracy (1-5)**

| Score | Meaning | Threshold |
|-------|---------|-----------|
| **5** | Perfect — description fully captured the argument | Pass |
| **4** | Strong — minor details missed, core predicted | Pass |
| **3** | Adequate — general area right, missed key aspects | Pass (minimum) |
| **2** | Weak — significant mismatch between prediction and content | FAIL |
| **1** | Failed — note argued something different than expected | FAIL |

**Passing threshold: 3 or above.**

**5. Run semantic retrieval test**

Test whether the description enables semantic retrieval:

- `mcp__qmd__query` with query = "[the note's description text]", collection = "{vocabulary.notes_collection}", limit = 10

Check where the note appears in results:
- Top 3: description works well for semantic retrieval
- Position 4-10: adequate but could improve
- Not in top 10: flag — description may not convey the note's meaning

**Why vector_search specifically:** Agents find notes via semantic search during reflect and reweave. Testing with keyword search tests the wrong retrieval method. Full hybrid search with LLM reranking compensates for weak descriptions — too lenient. vector_search tests real semantic findability without hiding bad descriptions behind reranking.

**6. Draft improved description if needed**

If prediction score < 3:
- Diagnose the failure: too vague? missing mechanism? wrong emphasis? restates title?
- Draft an improved description that would score higher
- If you have Edit tool access: apply the improvement

**7. Combined scoring**

| Prediction Score | Retrieval Rank | Suggested Action |
|------------------|----------------|------------------|
| 3-5 | top 10 | PASS — no changes needed |
| < 3 | not in top 10 | FAIL — description may need improvement |

### Step 2: VALIDATE (schema check)

Determine which template applies from frontmatter fields only (no filename inference). Each template's `_schema` declares an `entity_type` and a unique set of required/optional fields.

**Template matching strategy:**

1. Match the template whose `_schema` field set best fits the note's frontmatter — the template whose required and optional fields are present in the note
2. If multiple templates match, prefer the one with the most specific field overlap (e.g., a note with `classification` and `methodology` matches `research-note` over `generic-note`)
3. If no template matches, FAIL: "No template found for this note type"

Read the matched template's `_schema` block.

**Required fields (FAIL if missing):**

Check every field listed in `_schema.required`. Each missing required field is a FAIL.

**Description constraints (WARN if violated):**

| Constraint | Check | Severity |
|------------|-------|----------|
| Length | Must be under `_schema.constraints.description.max_length` (default 200) characters | WARN |
| Format | Single sentence, no trailing period | WARN |
| Content | MUST add NEW information beyond title | WARN |
| Semantic value | Should capture mechanism, not just topic | WARN |

**How to check "adds new info":** Read the title, read the description. If the description says the same thing in different words, it fails this check. A good description adds: mechanism (how/why), scope (boundaries), implication (what follows), or context (where it applies).

**YAML validity (FAIL if broken):**

| Check | Rule | Severity |
|-------|------|----------|
| Frontmatter delimiters | Must start with `---` and close with `---` | FAIL |
| Valid YAML | Must parse without errors | FAIL |
| No duplicate keys | Each YAML key appears only once | FAIL |
| No unknown fields | Fields not in `_schema.required` | WARN |

**Enum validation (WARN if invalid):**

For each field in the note's frontmatter that has a corresponding entry in `_schema.enums`, check the note's value against the allowed list. Each invalid enum value produces a WARN that reports the invalid value and lists the valid options.

**Constraint validation (WARN if violated):**

For each field in the note's frontmatter that has a corresponding entry in `_schema.constraints`, check format and value constraints. Report violations with the specific constraint that was violated and the expected format.

**Relevant notes format (WARN if incorrect):**

| Constraint | Check | Severity |
|------------|-------|----------|
| Format | Array with context: `["[[note]] -- relationship"]` | WARN |
| Relationship type | Should use standard types: extends, foundation, contradicts, enables, example | INFO |
| Links exist | Each referenced note must exist as a file | WARN |

**Topics format (FAIL if invalid):**

| Constraint | Check | Severity |
|------------|-------|----------|
| Format | Array of wiki links: `["[[topic]]"]` | FAIL |
| Links exist | Each {DOMAIN:topic map} must exist as a file | WARN |

**Composability (WARN if fails):**

| Check | Rule | Severity |
|-------|------|----------|
| Title test | Can you complete "This note argues that [title]"? | WARN |
| Specificity | Is the claim specific enough to disagree with? | WARN |

### Step 3: REVIEW (per-note health checks)

Run these 5 checks on the note:

**1. YAML frontmatter integrity**
- File starts with `---`, has closing `---`
- YAML parses without errors
- No duplicate keys

**2. Description quality (independent of recite)**
- Description is present and non-empty
- Description adds information beyond the title
- Description is not just the title rephrased

**3. {DOMAIN:topic map} connection**
- Note appears in at least one {DOMAIN:topic map}'s Core Ideas section
- How to check: grep for `[[note title]]` in files that serve as {DOMAIN:topic map}s
- The note's Topics footer references a valid {DOMAIN:topic map}
- A note with no {DOMAIN:topic map} mention is orphaned — FAIL

**4. Wiki link density**
- Count outgoing wiki links in the note body (not just frontmatter)
- Expected minimum: 2 outgoing links
- If < 2: flag as sparse — the note is not participating in the graph
- Sparse notes should be routed to /reflect for connection finding

**5. Link resolution**
- Scan ALL wiki links in the note — body, frontmatter `relevant_notes`, and Topics
- For each `[[link]]`, confirm a matching file exists in the vault
- **Exclude** wiki links inside backtick-wrapped code blocks (single backtick or triple backtick) — these are syntax examples, not real links
- A single dangling link = FAIL with the specific broken link identified

**Health analysis checks:**

**6. Orphan risk assessment**
- Count incoming links: grep for `[[note title]]` across all .md files
- If 0 incoming links: AT RISK — note exists but nothing references it
- If 1 incoming link: LOW RISK — single point of connection
- If 2+ incoming links: OK

**7. Content staleness detection**
- Read the note's content and assess whether claims still seem current
- Check if referenced concepts/tools/approaches have changed
- Flag anything that reads as potentially outdated

**8. Bundling analysis**
- Does the note make multiple distinct claims that could be separate notes?
- Check: could you link to part of this note without dragging unrelated context?
- If yes: flag for potential splitting

### Step 4: APPLY FIXES

Apply fixes for clear-cut issues:

**Auto-fix (safe to apply):**
- Improved description if recite score < 3
- Missing `---` frontmatter delimiters
- Trailing period on description
- Missing Topics footer (if obvious which {DOMAIN:topic map} applies)

### Step 5: Compile Results

Combine all checks and resuslts into the HANDOFF output.

## HANDOFF Output

Always output this structured format at the END of the session:

```
=== HANDOFF: verify ===
Target: [[note name]]

Work Done:
- Recite: prediction N/5, retrieval #N, [pass/fail]
- Validate: [PASS/WARN/FAIL] (N checks, M warnings, K failures)
- Review: [PASS/WARN/FAIL] (N checks, M issues)
- Description improved: [yes/no]

Files Modified:
- {DOMAIN:note_collection}/[note].md (description improved, if applicable)
- [task file path] (Verify section updated, if applicable)

Learnings:
- [Friction]: [description] | NONE
- [Surprise]: [description] | NONE
- [Methodology]: [description] | NONE
- [Process gap]: [description] | NONE

Queue Updates:
- Mark: verify done for this task
=== END HANDOFF ===
```

---

## critical constraints

**always:**
- be honest about prediction accuracy (inflated scores defeat the purpose)
- suggest specific improved descriptions for score < 3
- report all severity levels clearly (PASS/WARN/FAIL)
- capture observations for friction, surprises, or methodology insights
