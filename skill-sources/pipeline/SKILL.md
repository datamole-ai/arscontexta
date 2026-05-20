---
name: pipeline
description: End-to-end source processing -- seed, structure/capture, connect, verify, and commit. Triggers on "/pipeline", "/pipeline [file]", "process this end to end", "full pipeline".
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
  "source": "archive/<date>-<batch>/source.md",
  "artifacts": [
    {"kind": "note", "path": "notes/example.md"},
    {"kind": "enrichment", "path": "notes/existing.md"}
  ],
  "commit_paths": ["notes/topic-map.md"]
}
```

Only `batch`, `source`, and `artifacts` are required. `commit_paths` is optional and is used by `/connect` when it edits topic maps or other graph notes that are not already in `artifacts`.

## Flow

1. Seed the source:

   ```bash
   uv run arscontexta-vault seed --source "$SOURCE" --mode structure
   uv run arscontexta-vault seed --source "$SOURCE" --mode capture
   ```

   Stop on non-zero exit. Parse the JSON result and keep only `batch` and `source`.

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

## Output

Emit a concise human summary after the commit succeeds:

- batch id
- source path
- artifact paths
- commit hash

On any handled runtime failure, surface the returned JSON and stop. Do not attempt recovery, queue repair, extra cleanup, or manual Git staging.
