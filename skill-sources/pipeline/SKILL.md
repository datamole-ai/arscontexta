---
name: process
description: End-to-end source processing -- seed, structure/capture, connect, verify, and commit. Triggers on "/process", "/process [file]", "process this end to end", "full pipeline".
allowed-tools: Read, Write, Edit, Grep, Glob, Bash
argument-hint: " [file path] [--structure|--capture]"
---

## Execute

Target: `$ARGUMENTS`

Parse:
- source file path, required
- exactly one mode: `--structure` or `--capture`; if absent, ask the user which mode to use

Read runtime vocabulary:

```bash
cat ops/derivation-manifest.yaml
```

Run from the vault root. The pipeline is a happy-path command: it carries one lean JSON object between phases and does not create durable recovery state.

## State Shape

Pass this lean state between phases:

```json
{
  "batch": "<source-basename>",
  "source": "archive/<date>-<batch>.md",
  "artifacts": [
    {"kind": "note", "path": "notes/example.md"},
    {"kind": "enrichment", "path": "notes/existing.md"}
  ],
  "commit_paths": ["notes/topic-map.md"]
}
```

Only `batch`, `source`, and `artifacts` are required. `commit_paths` is optional and is used when `/seed` moves an inbox source or `/connect` edits topic maps or other graph notes that are not already in `artifacts`.

## Flow

0. Run the Obsidian readiness gate before seed or any file changes:

   ```bash
   command -v obsidian >/dev/null 2>&1
   pgrep -x Obsidian >/dev/null 2>&1
   test -d .obsidian
   obsidian unresolved >/dev/null 2>&1
   ```

   Run these shell checks only, in this order. Suppress command output exactly as shown where redirection is present. On any failure, stop before invoking `/seed`, writing files, archiving the source, staging changes, or attempting recovery. Emit exactly:

   ```json
   {"status":"error","error":"obsidian is not ready for this vault","next_step":"Open this folder as a vault in Obsidian, leave Obsidian running, then rerun /process."}
   ```

1. Seed the source:

   ```bash
   uv run arscontexta-vault seed --source "$SOURCE" --mode "$MODE"
   ```

   Stop on non-zero exit. Parse the JSON result and keep `batch`, `source`, and optional `commit_paths`.

2. Invoke `/structure` or `/capture` with the current state JSON. The producer writes Markdown directly and then validates its artifacts with:

   ```bash
   printf '%s' "$PIPELINE_STATE" | uv run arscontexta-vault validate --artifacts
   ```

3. Invoke `/connect` with the validated state JSON. `/connect` owns qmd discovery, Obsidian graph facts, topic-map edits, and any `commit_paths` it adds.

4. Invoke `/verify` with the updated state JSON. `/verify` uses Obsidian CLI plus `validate --artifacts`; it does not mutate queue state.

5. Commit the final state yourself:

   - Build the named path list from `source`, every `artifacts[].path`, and every `commit_paths[]`.
   - Deduplicate the list while preserving root-relative paths.
   - Stage only those paths with `git add -A -- <named paths>`.
   - If `git diff --cached --quiet -- <named paths>` reports no staged diff, stop and report that there are no pipeline changes to commit.
   - Commit with the fixed message `pipeline: <batch>`.
   - Do not stage all workspace changes.

6. Refresh semantic search after the commit:

   ```bash
   bash .claude/hooks/qmd-sync.sh
   ```

   If sync fails, report the commit hash and the qmd sync error. Do not amend, roll back, retry, or stage additional files.

## Output

Emit a concise human summary after the commit succeeds:

- batch id
- source path
- artifact paths
- commit hash
- qmd sync status

On any handled runtime failure, surface the returned JSON and stop. Do not attempt recovery, queue repair, extra cleanup, or manual Git staging.
