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
uv run arscontexta-vault seed --source "$FILE" --mode structure
uv run arscontexta-vault seed --source "$FILE" --mode capture
```

The runtime:

- validates the source path
- copies the source into `archive/<date>-<batch>/source.<ext>`
- emits only `ok`, `command`, `batch`, and `source`
- does not create durable queue entries

## Output

Emit the runtime JSON object as the final message. No prose, headings, or markdown fences.
