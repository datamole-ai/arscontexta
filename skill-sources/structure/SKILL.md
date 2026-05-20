---
name: structure
description: Internal pipeline skill -- groups source-backed claims into structured notes. Invoked by /pipeline as a subagent; do not invoke directly.
context: fork
allowed-tools: Read, Write, Edit, Grep, Glob, Bash
---

## Execute

Target: `$ARGUMENTS`

Parse the target as pipeline state JSON. It must contain:

```json
{"batch":"<batch>","source":"archive/<date>-<batch>/source.md","artifacts":[]}
```

If state is missing or invalid, emit:

```json
{"status":"error","error":"structure requires pipeline state JSON"}
```

Read:

```bash
cat ops/derivation-manifest.yaml
cat ops/templates/note.md
```

Then read the entire `source` file.

## Rules

- Produce source-bounded Markdown only.
- Do not call qmd.
- Do not gather semantic neighbors.
- Carry state only through the provided pipeline JSON; do not create durable recovery files.
- Do not include wiki links in the body unless they are directly present in the source; graph weaving belongs to `/connect`.
- Use `ops/templates/note.md` as the schema source. Output notes must include every `_schema.required` field and satisfy `_schema.enums` and deterministic constraints.
- Write notes directly under the configured note collection.
- For enrichments, edit existing note Markdown directly and include the edited path as an artifact with `kind: "enrichment"`.

## Source Fidelity

Every title, frontmatter description, section heading, body sentence, and footer phrase must be supported by the archived source unless explicitly marked as inference. Preserve source terms, uncertainty, scope, URLs, emails, and identifiers exactly when they are material to the note.

Group related claims generously, but split when grouping would confuse the reader or make the title overclaim. A structured note title should be a source-bounded proposition that fits after "because", "since", or "the insight that".

## Validation

After writing all artifacts, build lean state:

```json
{
  "batch": "<batch>",
  "source": "<source>",
  "artifacts": [
    {"kind": "note", "path": "<note path>"}
  ]
}
```

Validate it:

```bash
printf '%s' "$PIPELINE_STATE" | uv run arscontexta-vault validate --artifacts
```

If validation fails, fix the Markdown once and rerun validation. If it still fails, emit the failure JSON and stop.

## Output

Emit the validated JSON object as the final message. No prose, headings, or markdown fences.
