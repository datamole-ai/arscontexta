---
name: process
description: End-to-end source processing -- seed, structure/capture, connect, verify, and commit. Triggers on "/process", "/process [file]", "process this end to end", "full pipeline".
allowed-tools: Read, Write, Edit, Grep, Glob, Bash
argument-hint: " [file path] [--structure|--capture]"
---

## Execute

Target: `$ARGUMENTS`

Parse:
- source file path, required; must be a file in the inbox folder
- exactly one mode: `--structure` or `--capture`; if absent, ask the user which mode to use

Run from the vault root. Do not create durable recovery state.

## State shape

Pass this state between phases:

```json
{
  "batch": "<source-basename>",
  "source": "archive/<date>-<batch>.md",
  "artifacts": [
    {"kind": "note", "path": "notes/example.md"},
    {"kind": "enrichment", "path": "notes/existing.md"}
  ]
}
```

All three fields are required. `artifacts` is the single channel for every file the pipeline creates or edits: new notes as `note`, edited existing notes and topic maps as `enrichment`. The inbox is gitignored, so the moved inbox source is never staged.

## Flow

0. Run the Obsidian readiness gate before seed or any file changes:

   ```bash
   command -v obsidian >/dev/null 2>&1
   pgrep -x Obsidian >/dev/null 2>&1
   test -d .obsidian
   obsidian unresolved >/dev/null 2>&1
   ```

   Run each shell check in its own Bash tool call, in this order. Do not combine
   the checks or add shell wrappers, loops, pipes, or other commands. On any
   failure, stop before running `vault seed`, writing files, archiving the source,
   staging changes, or attempting recovery. Emit exactly:

   ```json
   {"status":"error","error":"obsidian is not ready for this vault","next_step":"Open this folder as a vault in Obsidian, leave Obsidian running, then rerun /process."}
   ```

1. Seed the source:

   ```bash
   uv run --project ops/tooling --locked vault seed --source "$SOURCE"
   ```

   Stop on non-zero exit. Parse the JSON result and keep `batch` and `source`.

2. Invoke `/structure` or `/capture` with the current state JSON.

3. Invoke `/connect` with the validated state JSON.

4. Invoke `/verify` with the updated state JSON.

5. Commit the final state yourself:

   - Build the named path list from `source`, every `artifacts[].path`, and always `ops/tags.yaml`; staging an unchanged file is a no-op.
   - Deduplicate the list while preserving root-relative paths.
   - Stage only those paths with `git add -A -- <named paths>`.
   - If `git diff --cached --quiet -- <named paths>` reports no staged diff, stop and report that there are no pipeline changes to commit.
   - Commit with the fixed message `pipeline: <batch>`.
   - Do not stage all workspace changes.

6. Refresh semantic search after the commit:

   ```bash
   qmd update && qmd embed
   ```

   If refresh fails, report the commit hash and the qmd refresh error. Do not amend, roll back, retry, or stage additional files.

## Output

Emit a concise human summary after the commit succeeds:

- batch id
- source path
- artifact paths
- commit hash
- qmd refresh status

On any final handled runtime failure, surface the returned JSON and stop. Do not attempt any other recovery, extra cleanup, or manual Git staging.
