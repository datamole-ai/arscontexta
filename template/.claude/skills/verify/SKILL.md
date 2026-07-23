---
name: verify
description: Internal pipeline skill -- checks final artifacts with Obsidian CLI and deterministic runtime validation. Invoked by /process as a subagent.
context: fork
model: haiku
allowed-tools: Bash
---

## Execute

Final response must be raw JSON only: no prose, headings, or Markdown fences.

Target: `$ARGUMENTS`

Parse the target as pipeline state JSON. If missing, emit:

```json
{"status":"error","error":"verify requires pipeline state JSON"}
```

## Checks

Use Obsidian CLI for vault-native graph facts:

```bash
obsidian unresolved verbose format=json
obsidian links path="<artifact path>"
obsidian backlinks path="<artifact path>"
```

Run `unresolved` once. Run `links` and `backlinks` once for every
`artifacts[].path`, using that exact root-relative path.

Run each Obsidian command in its own Bash tool call. The command string must
start with `obsidian` and contain exactly one invocation. Do not add leading
commands, loops, pipes, semicolons, `&&`, or shell command substitutions.

Use the runtime only for deterministic schema/artifact validation:

```bash
printf '%s' "$PIPELINE_STATE" | uv run --project ops/tooling vault validate --artifacts
```

Rules:

- Do not judge source faithfulness, description quality, or connection quality here.
- Fail if any artifact path has unresolved links, missing files, invalid frontmatter, invalid enum values, overlong descriptions, malformed tags, or tags not registered in `ops/tags.yaml`.

## Output

On success, emit the validated lean pipeline state JSON. On failure, emit a compact JSON object with `status: "error"` and the failing paths/errors.
