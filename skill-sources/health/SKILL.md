---
name: health
description: Run read-only vault diagnostics with Obsidian CLI plus deterministic schema validation. Triggers on "/health", "check vault health", "vault diagnostics".
context: fork
model: haiku
allowed-tools: Bash
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

Deterministic Ars schema checks:

```bash
uv run arscontexta-vault validate --all
```

Rules:

- Do not call `uv run arscontexta-vault health`; that runtime command does not exist.
- Use stdout output only; this is an ephemeral diagnostic workflow.
- Report measured vault facts only; do not invent persistent diagnostic state.

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
