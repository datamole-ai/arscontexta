---
name: verify
description: Internal pipeline skill — runs validate + review quality gate across all notes in a batch in one pass, with shared vault-scope checks. Invoked by /pipeline as a subagent; do not invoke directly.
context: fork
model: sonnet
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

Parse the batch id from arguments (e.g. `my-source` — the source basename). If no argument is provided, end immediately with: report `ERROR: verify requires batch id`.

### Step 1: Structural pass

```bash
bash .claude/skills/{DOMAIN:verify}/scripts/verify-batch.sh "$BATCH_ID"
```

The script:
- Discovers the work-list (pending entries with `current_phase=verify` for this batch).
- Runs vault-scope link health and orphan checks across the batch.
- Runs per-note structural checks (frontmatter delimiters, trailing-period description, Topics footer presence, capture verbatim integrity).
- Emits the partial `## Verify` block with each per-note line ending in `Review: TBD`.
- Appends a `### Machine output` JSON object with the deterministic findings:
  ```json
  {"batch":"<id>","worklist":N,"link_health":{"status":"PASS|FAIL","scanned":K,"broken":[{"id","target"}]},"orphan_check":{"status":"PASS|FAIL","count":O,"ids":[{"id","target_path"}]},"per_note":[{"id","path","granularity","validate":"PASS|WARN|FAIL","issues":[],"review":"TBD"}]}
  ```
  Use this JSON as the source of truth for the deterministic verdicts — the human-readable lines above it are for audit, not for re-parsing.

If the work-list is empty, the script exits 0 with an explicit "no entries" line and `link_health.status: SKIP`. Print its output and stop — there is nothing to do.

### Step 2: Semantic per-note checks (LLM judgment)

For each work-list note with `granularity == "structure"`, perform the semantic checks listed in **## Granularity-Aware Verification** above:
- **Scope coherence** — do all sections of the {vocabulary.note} belong to one claim?
- **Section development** — does each section develop its sub-claim, not just state it?

For each note, replace its `Review: TBD` substring with `Review: PASS | WARN ({issue}) | FAIL ({issue})`.

### Step 3: Auto-fixes

Apply auto-fixes only where judgment is required (the script does not):
- A missing Topics footer where the correct {vocabulary.topic_map} is obvious from the note's content — add it.
- Other fixes from the structural pass (missing `---`, trailing period) are already deterministic; the script reports them and the LLM applies them inline if it has the file open.

Record each fix in the Output Block's `### Auto-fixes applied` section.

### Step 4: Mark queue done

Once every successful entry has a `Review:` verdict, build a JSON array of completed ids and call:

```bash
bash .claude/skills/{DOMAIN:verify}/scripts/verify-complete.sh "$BATCH_ID" "$COMPLETED_IDS_JSON"
```

Append the script's confirmation line to the Output Block's `**Queue:**` field.

If either script exits nonzero, emit `ERROR: <script-name> failed (exit <code>)` and stop. Do not attempt recovery.

## Output Contract

After finishing all steps for every note in the work list (or after a system-level error), perform queue self-update (mark every successfully verified entry done) and then emit a single fenced JSON block as the final chat message. The verify-batch.sh `### Machine output` block is the input; the verify skill's chat JSON is the output. No prose, no headings, no progress narration.

```json
{
  "skill": "verify",
  "status": "ok",
  "batch": "<batch-id>",
  "queue": "marked <N> entries: verify -> done",
  "vault_scope": {
    "link_health": {"status": "PASS|FAIL", "scanned": <K>, "broken": [{"id": "<queue-id>", "target": "<title>"}]},
    "orphan_check": {"status": "PASS|FAIL", "count": <O>, "ids": [{"id": "<queue-id>", "target_path": "<path>"}]}
  },
  "per_note": [
    {"id": "<queue-id>", "title": "<note title>", "validate": "PASS|WARN|FAIL", "review": "PASS|WARN|FAIL", "issues": ["<short>", "..."]}
  ],
  "auto_fixes": [{"note": "<title>", "fix": "<short description>"}],
  "warnings": [],
  "learnings": [
    {"category": "Friction|Surprise|Methodology|Process gap", "description": "<short>"}
  ]
}
```

Token cap: ~500. Successful PASS notes carry empty `issues`; only failing/warning notes carry detail. The orchestrator reads `status`, `queue`, vault-scope verdicts, per-note review failures, and `learnings`.

On error: `"status": "error"`, `"error": "<short>"`, populate `per_note` with what completed before the failure, and leave `queue.json` unchanged.

---

## critical constraints

**always:**
- report all severity levels clearly (PASS/WARN/FAIL)
- capture observations for friction, surprises, or methodology insights
