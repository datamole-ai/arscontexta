---
name: health
description: Run read-only vault diagnostics with Obsidian CLI plus deterministic schema validation. Triggers on "/health", "check vault health", "vault diagnostics".
context: fork
model: sonnet
disable-model-invocation: true
---

## Execute

Run read-only diagnostics from the vault root.

Obsidian-owned facts:

```bash
obsidian unresolved
obsidian orphans
obsidian deadends
obsidian properties
obsidian tags
```

Run each Obsidian command in its own Bash tool call. The command string must
start with `obsidian` and contain exactly one invocation. Do not add leading
commands, loops, pipes, semicolons, `&&`, or shell command substitutions.

Deterministic schema checks:

```bash
uv run --project ops/tooling --locked vault validate --all
```

Rules:

- Use stdout output only; do not write files.
- Report measured vault facts only.

## Output

Emit one compact JSON object with:

```json
{
  "ok": true,
  "skill": "health",
  "obsidian": {
    "unresolved": "<summary>",
    "orphans": "<summary>",
    "deadends": "<summary>",
    "properties": "<summary>",
    "tags": "<summary>"
  },
  "validation": {"ok": true, "checked": 0, "failures": []}
}
```

Use `ok: false` when any diagnostic fails. No prose, headings, or markdown fences.
