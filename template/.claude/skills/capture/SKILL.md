---
name: capture
description: Internal pipeline skill -- preserves source material verbatim with frontmatter. Invoked by /process as a subagent; do not invoke directly.
context: fork
model: sonnet
allowed-tools: Read, Write, Edit, Grep, Glob, Bash
---

## Execute

Target: `$ARGUMENTS`

Parse the target as pipeline state JSON with `batch` and `source`. If missing, emit:

```json
{"status":"error","error":"capture requires pipeline state JSON"}
```

Read:

```bash
cat ops/tags.yaml
```

Then read the entire `source` file.

## Rules

- Never copy source content by hand. `vault capture` embeds the source bytes mechanically; your job is only the judgment fields below.
- Do not call qmd.
- Carry state only through the provided pipeline JSON; do not create durable recovery files.
- Graph connection work belongs to `/connect`; the note this skill produces carries no links, and its only footer is the `Source:` line `vault capture` writes.
- Title and description must describe what the captured content contains without adding interpretation.
- Choose tags from the `ops/tags.yaml` registry. For a family entry (`x/*`), fill in the value, e.g. `customer/lely`. Only when no entry fits, append a new entry with `tag` and a one-sentence `meaning` to `ops/tags.yaml` before writing the note; prefer a family (`x/*`) when the attribute has an open set of values, an exact tag otherwise. Never edit or remove existing entries. Do not list `ops/tags.yaml` in `artifacts`.

## Write the note

Decide three things from the source: a prose title, a source-bounded description (<=200 chars), and any tags (omit leading `#`, no spaces, `/` for nesting). Then run:

```bash
uv run --project ops/tooling vault capture \
  --source "$SOURCE" \
  --title "<prose title describing the captured content>" \
  --description "<source-bounded description>" \
  --tag "<tag>"
```

Repeat `--tag` per tag; omit it for no tags. The command writes the note to `notes/` with `content_type: note` and `granularity: verbatim`. It embeds the source byte-exactly in a fenced block, adds a `Source:` provenance footer naming the archived source, and emits JSON with the written `note` path. On the first `"ok": false`, rerun the same `vault capture` command if `"retryable"` is exactly `true`, else emit the failure JSON and stop.

Append the returned path to state as `{"kind": "note", "path": "<note>"}`.

## Validation

Validate lean state:

```bash
printf '%s' "$PIPELINE_STATE" | uv run --project ops/tooling vault validate --artifacts
```

Validation byte-compares the note's fenced payload against the source named in its `Source:` footer; it fails if anything altered the content. Fix deterministic validation failures once (wrong enum value, bad tag form), never by editing the fenced block or the `Source:` line. If validation still fails, emit the failure JSON and stop.

## Output

Emit the validated JSON object as the final message. No prose, headings, or markdown fences.
