---
name: verify
description: Internal pipeline skill — runs validate + review quality gate on a note. Invoked by /pipeline as a subagent; do not invoke directly.
context: fork
allowed-tools: Read, Write, Edit, Grep, Glob, Bash
---

## Runtime Configuration

### Vocabulary

All output must use domain-native terms.
Derivation manifest for vocabulary mapping:
!`cat ops/derivation-manifest.md`

### Task Queue

Current task queue:
!`cat ops/queue/queue.json`

### Templates

The templates available are:
!`tree -L 2 ops/templates/`

## Granularity-Aware Verification

After reading the target {vocabulary.note}, check its `granularity` frontmatter field:

- **`structure`**: Scope coherence test (do all sections belong together?), section development test (does each section develop its sub-claim, not just state it?), schema compliance, link health (no broken links, in at least one {vocabulary.topic_map}).
- **`capture`**: Schema compliance, link health. Skip scope coherence test. Add: verbatim integrity check — fenced block present and non-empty, no wikilinks or edits inside the fenced block, all connections in footer sections only.

## EXECUTE NOW

**Target: $ARGUMENTS**

Parse the queue id from arguments (e.g. `note-010`, `enrich-002`). If no argument is provided, end immediately with: report
`ERROR: verify requires queue id`.

Look up the entry in `ops/queue/queue.json`:

```bash
jq --arg id "$QUEUE_ID" '.tasks[] | select(.id == $id)' ops/queue/queue.json
```

From that entry, obtain:
- `id` — this entry's queue id
- `target_path` — the path to the {vocabulary.note} being verified
- `batch` — the batch id
- `granularity` — routes verification depth

All subsequent references to "the {vocabulary.note}" use the `target_path` value from the queue entry.

**START NOW.**

### Step 1: VALIDATE (auto-fixable schema checks)


| Check | Rule | Severity |
|-------|------|----------|
| Frontmatter delimiters | Must start with `---` and close with `---` | FAIL |
| Description trailing period | Description must not end with `.` | WARN |
| Topics footer presence | Topics field must be present and non-empty | FAIL |

### Step 2: REVIEW (light health checks)

Two quick checks only:

**1. Link resolution**
- Scan ALL wiki links in the note — body prose, the `Relevant Notes:` footer, and the `Topics:` footer
- For each `[[link]]`, confirm a matching file exists in the vault
- **Exclude** wiki links inside backtick-wrapped code blocks (single backtick or triple backtick) — these are syntax examples, not real links
- A single dangling link = FAIL with the specific broken link identified

**2. {DOMAIN:topic map} connection**
- The note's Topics footer references at least one valid {DOMAIN:topic map}
- Note appears in at least one {DOMAIN:topic map}'s Core Ideas section (grep for `[[note title]]` in topic map files)
- A note with no {DOMAIN:topic map} mention is orphaned — FAIL

### Step 3: APPLY FIXES

Apply fixes for clear-cut issues:

**Auto-fix (safe to apply):**
- Missing `---` frontmatter delimiters
- Trailing period on description
- Missing Topics footer (if obvious which {DOMAIN:topic map} applies)

## Queue Self-Update

Before emitting the Output Block, mark the entry done in `ops/queue/queue.json` via a single `jq` call. Substitute the queue id (from `$ARGUMENTS`) for `<task-id>`:

```bash
jq --arg id "<task-id>" --arg now "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
   'if any(.tasks[]; .id == $id)
    then (.tasks[] | select(.id == $id)) |= (.completed_phases += ["verify"] | .status = "done" | .current_phase = null | .completed = $now)
    else error("task not found: \($id)")
    end' \
   ops/queue/queue.json > ops/queue/queue.json.tmp \
   && mv ops/queue/queue.json.tmp ops/queue/queue.json
```

If the Bash call fails (non-zero exit), resort to the Read and Write tools to read the original queue.json file and write the updated file back.

## Output Block

After finishing verification (validate + review + any auto-fixes), perform queue self-update (final phase — mark done) and then emit the canonical block below as the final chat message. This is the ONLY chat output — no task file is written.

```
## Verify

**Target:** [[{target note title}]]
**Status:** ok | error: {short message}
**Queue:** marked {id}: verify -> done

### Work
- Validate: [PASS/WARN/FAIL] ({N} checks, {M} warnings, {K} failures)
- Review: [PASS/WARN/FAIL] ({N} checks, {M} issues)

### Learnings
- [Friction]: [description] | NONE
- [Surprise]: [description] | NONE
- [Methodology]: [description] | NONE
- [Process gap]: [description] | NONE
```

On error, set `Status: error: <message>`, `Queue: no change (error)`, and leave `queue.json` unchanged.

---

## critical constraints

**always:**
- report all severity levels clearly (PASS/WARN/FAIL)
- capture observations for friction, surprises, or methodology insights
