---
name: capture
description: Internal pipeline skill -- preserves source material verbatim with frontmatter. Invoked by /pipeline as a subagent; do not invoke directly.
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
cat ops/derivation-manifest.yaml
cat ops/templates/note.md
```

Then read the entire `source` file.

## Rules

- Preserve the source content verbatim inside a fenced block.
- Do not call qmd.
- Do not gather semantic neighbors.
- Carry state only through the provided pipeline JSON; do not create durable recovery files.
- Graph connection work belongs to `/connect`; this skill may include only minimal source-bounded topic/footer placeholders.
- Title and description must describe what the captured content contains without adding interpretation.
- Use `ops/templates/note.md` for required fields, enum values, and deterministic constraints.

## Note Shape

~~~markdown
---
content_type: <valid content_type enum>
granularity: capture
description: <source-bounded description, <=200 chars>
created_at: <YYYY-MM-DD>
tags: []
---

# <prose title describing the captured content>

```text
<source content exactly as received>
```

---

Topics:
- [[<topic map>]]
~~~

## Validation

After writing the capture note, validate lean state:

```bash
printf '%s' "$PIPELINE_STATE" | uv run arscontexta-vault validate --artifacts
```

Fix deterministic validation failures once. If validation still fails, emit the failure JSON and stop.

## Output

Emit the validated JSON object as the final message. No prose, headings, or markdown fences.
