---
name: seed
description: Add a source file to the processing queue. Checks for duplicates, creates archive folder, moves source from inbox, creates process task, and updates queue. Triggers on "/seed", "/seed [file]", "queue this for processing".
version: "1.0"
context: fork
allowed-tools: Read, Write, Edit, Grep, Glob, Bash
---

## EXECUTE NOW

The target MUST be a file path. If no target provided, end immediately with: `ERROR: seed requires file path`.

The granularity flag MUST be `--structure` or `--capture`. If absent, end immediately with: `ERROR: seed requires granularity flag`.

### Vocabulary

All output must use domain-native terms.
Derivation manifest for vocabulary mapping:
!`cat ops/derivation-manifest.md`

### Step 1: Run validate

```bash
bash .claude/skills/seed/scripts/seed-validate.sh "$FILE" "$GRAN_FLAG"
```

Read the key=value lines from stdout. The script computes `source_basename`, `archive_dir`, `next_claim_start`, `line_count`, `content_format`, and one or more `filename_match=` entries (`NONE` if no match).

### Step 2: Duplicate handling (LLM judgment)

If every `filename_match` line equals `NONE`, skip to Step 3.

Otherwise:
1. Run a content-similarity query:
   ```bash
   qmd query "$(head -100 "$FILE")" --collection {vocabulary.qmd_collection} -n 5
   ```
2. Read the matched files and decide:
   - **Exact duplicate** — abort with `WARN: Source is an exact duplicate of an existing {DOMAIN:note_plural} and was not seeded.`
   - **Near duplicate** — note this in the report from Step 3 (suggest enrichment task) and proceed to commit.
   - **Not a real duplicate** (different topic, coincidental name match) — proceed to commit.

### Step 3: Commit the seed

```bash
bash .claude/skills/seed/scripts/seed-commit.sh "$FILE" "$GRAN_FLAG" "$archive_dir" "$next_claim_start"
```

Print the commit script's report block verbatim. If you flagged a near-duplicate in Step 2, append a one-line note: `Note: near-duplicate of <path> — consider enrichment task.`

If either script exits nonzero, emit `ERROR: <script-name> failed (exit <code>)` and stop. Do not attempt recovery.

## Step 4: Report

```
--=={ seed }==--

Seeded: {SOURCE_BASENAME}
Source: {original path} -> {FINAL_SOURCE}
Archive folder: {ARCHIVE_DIR}
Archived copy: {DOMAIN:archive}/{DATE}-{SOURCE_BASENAME}.md
Size: {line count} lines
Content type: {detected type}

Claims will start at: {NEXT_CLAIM_START}
Claim files will be: {SOURCE_BASENAME}-{NNN}.md (unique across vault)
Queue: updated with process task (granularity: {GRANULARITY_FLAG})
```

---

## Naming Convention

The source basename is reused for human readability:
- Claim files: `{source-basename}-{NNN}.md`
- Archive folder: `{date}-{source-basename}/`

Claim numbers (NNN) are globally unique across all batches, ensuring every filename is unique vault-wide. This is required because wiki links resolve by filename, not path.

---

## Edge Cases

**Large source (2500+ lines):** Note in output: "Large source ({N} lines) -- processing skill will chunk automatically."

---

## Critical Constraints

**always:**
- Create the archive folder even for living docs
- Use the archived path (not original) in the queue entry for {DOMAIN:inbox} sources
- Report next steps clearly so the orchestrator knows what to do next
- Compute next_claim_start from both queue AND archive (not just one)
