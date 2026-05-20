---
name: verify
description: Internal pipeline skill -- checks final artifacts with Obsidian CLI and deterministic runtime validation. Invoked by /pipeline as a subagent.
context: fork
model: haiku
allowed-tools: Bash
---

## Execute

Target: `$ARGUMENTS`

Parse the target as pipeline state JSON. If missing, emit:

```json
{"status":"error","error":"verify requires pipeline state JSON"}
```

## Checks

Use Obsidian CLI for vault-native graph facts:

```bash
obsidian unresolved
obsidian links
obsidian backlinks
```

Use the runtime only for deterministic Ars schema/artifact validation:

```bash
printf '%s' "$PIPELINE_STATE" | uv run arscontexta-vault validate --artifacts
```

Rules:

- Do not call `uv run arscontexta-vault verify`; that runtime command does not exist.
- Do not call `complete-verify`.
- Do not mutate queue state.
- Do not judge source faithfulness, description quality, or connection quality here.
- Fail if any artifact path has unresolved links, missing files, invalid frontmatter, invalid enum values, bad dates, overlong descriptions, or malformed tags.

## Output

On success, emit the validated lean pipeline state JSON. On failure, emit a compact JSON object with `status: "error"` and the failing paths/errors. No prose, headings, or markdown fences.
