---
name: seed
description: Pipeline-internal helper that archives a source and emits initial lean pipeline state.
context: fork
model: haiku
allowed-tools: Bash
---

## Execute

The target must include a source path and exactly one mode: `--structure` or `--capture`.

Run from the vault root:

```bash
uv run arscontexta-vault seed --source "$FILE" --mode "$MODE"
```

The runtime:

- validates the source path
- moves inbox sources into `archive/<date>-<batch>.md`; copies non-inbox sources
- emits `ok`, `command`, `batch`, `source`, and optional `commit_paths` for moved inbox sources
- does not create durable queue entries

## Output

Emit the runtime JSON object as the final message. No prose, headings, or markdown fences.
