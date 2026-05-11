---
name: verify
description: Internal pipeline skill — runs deterministic structural checks across all notes in a batch. Invoked by /pipeline as a subagent; do not invoke directly.
context: fork
model: sonnet
allowed-tools: Read, Write, Edit, Grep, Glob, Bash
---

## Runtime Configuration

### Vocabulary

All output must use domain-native terms.
Derivation manifest for vocabulary mapping:
!`cat ops/derivation-manifest.md`

## EXECUTE NOW

**Target: $ARGUMENTS**

Parse the batch id from arguments (e.g. `my-source` — the source basename). If no argument is provided, end immediately with: report `ERROR: verify requires batch id`.

### Step 1: Structural pass

```bash
bash .claude/skills/verify/scripts/verify-batch.sh "$BATCH_ID"
```

The script:
- Discovers the work-list from `ops/queue/queue.json`: pending entries with `current_phase=verify` for this batch.
- Checks every target file exists.
- Checks frontmatter opens on line 1 with `---` and has a closing `---`.
- Checks frontmatter contains `description:` and `tags:`.
- Resolves ordinary wiki links against the configured note collection by normalized filename.
- Rejects alias wiki links such as `[[Target|alias]]`.
- Ignores `[[source:*]]` links because they are pipeline traceability handles, not note links.
- Appends a `### Machine output` JSON object with the deterministic findings:
  ```json
  {
    "batch": "<id>",
    "worklist": 0,
    "checks": {
      "frontmatter": {
        "status": "PASS|FAIL|SKIP",
        "issues": [{"id": "<queue-id>", "path": "<path>", "issue": "<short>"}]
      },
      "wiki_links": {
        "status": "PASS|FAIL|SKIP",
        "scanned": 0,
        "broken": [{"id": "<queue-id>", "path": "<path>", "target": "<link target>"}],
        "aliases": [{"id": "<queue-id>", "path": "<path>", "target": "<raw alias target>"}]
      }
    },
    "per_note": [
      {"id": "<queue-id>", "path": "<path>", "validate": "PASS|FAIL", "issues": ["<short>", "..."]}
    ]
  }
  ```
  Use this JSON as the source of truth for deterministic verdicts. The human-readable lines above it are for audit, not for re-parsing.

If the work-list is empty, the script exits 0 with an explicit "no entries" line and `checks.*.status: SKIP`. Print its output and stop — there is nothing to do.

### Step 2: Mark queue done

Build a JSON array of ids whose `per_note[].validate` is `"PASS"` and call:

```bash
bash .claude/skills/verify/scripts/verify-complete.sh "$BATCH_ID" "$COMPLETED_IDS_JSON"
```

Use the script's confirmation line to populate the Output Contract's `queue` field.

If either script exits nonzero, emit `ERROR: <script-name> failed (exit <code>)` and stop. Do not attempt recovery.

## Output Contract

After finishing the structural pass and queue self-update, emit a single fenced JSON block as the final chat message. The verify-batch.sh `### Machine output` block is the input; the verify skill's chat JSON is the output. No prose, no headings, no progress narration.

```json
{
  "skill": "verify",
  "status": "ok",
  "batch": "<batch-id>",
  "queue": "marked <N> entries: verify -> done",
  "checks": {
    "frontmatter": {
      "status": "PASS|FAIL|SKIP",
      "issues": [{"id": "<queue-id>", "path": "<path>", "issue": "<short>"}]
    },
    "wiki_links": {
      "status": "PASS|FAIL|SKIP",
      "scanned": 0,
      "broken": [{"id": "<queue-id>", "path": "<path>", "target": "<link target>"}],
      "aliases": [{"id": "<queue-id>", "path": "<path>", "target": "<raw alias target>"}]
    }
  },
  "per_note": [
    {"id": "<queue-id>", "path": "<path>", "validate": "PASS|FAIL", "issues": ["<short>", "..."]}
  ],
  "learnings": [
    {"category": "Friction|Surprise|Methodology|Process gap", "description": "<short>"}
  ]
}
```

Token cap: ~500. Successful PASS notes carry empty `issues`; only failing notes carry detail. The orchestrator reads `status`, `queue`, `checks`, `per_note`, and `learnings`.

On error: `"status": "error"`, `"error": "<short>"`, populate `per_note` with what completed before the failure, and leave `queue.json` unchanged.

---

## critical constraints

**always:**
- report PASS/FAIL/SKIP clearly
- capture observations for friction, surprises, or methodology insights
