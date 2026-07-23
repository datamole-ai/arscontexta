---
name: structure
description: Internal pipeline skill -- groups source-backed claims into structured notes. Invoked by /process as a subagent; do not invoke directly.
context: fork
allowed-tools: Read, Write, Edit, Grep, Glob, Bash
---

## Execute

Target: `$ARGUMENTS`

Parse the target as pipeline state JSON. It must contain:

```json
{"batch":"<batch>","source":"archive/<date>-<batch>.md","artifacts":[]}
```

If state is missing or invalid, emit:

```json
{"status":"error","error":"structure requires pipeline state JSON"}
```

Read:

```bash
cat ops/schema.yaml
cat ops/tags.yaml
```

Then read the entire `source` file.

## Rules

- Do not call qmd.
- Carry state only through the provided pipeline JSON; do not create durable recovery files.
- Do not include wiki links in the body unless they are directly present in the source; graph weaving belongs to `/connect`.
- Use `ops/schema.yaml` as the schema source. Output notes must include every `required` field and satisfy `enums` and deterministic constraints.
- Set `content_type: note` on every note this skill writes.
- Set `granularity: distilled` on every note this skill writes. `verbatim` is reserved for notes written by `vault capture`.
- When `tags` is not empty, use Obsidian YAML list form. Omit leading `#`, avoid spaces, and use `/` for nested tags.
- Choose tags from the `ops/tags.yaml` registry. For a family entry (`x/*`), fill in the value, e.g. `customer/lely`. Only when no entry fits, append a new entry with `tag` and a one-sentence `meaning` to `ops/tags.yaml` before writing the note; prefer a family (`x/*`) when the attribute has an open set of values, an exact tag otherwise. Never edit or remove existing entries. Do not list `ops/tags.yaml` in `artifacts`.
- Write notes directly under `notes/`.
- For enrichments, edit existing note Markdown directly and include the edited path as an artifact with `kind: "enrichment"`.

## Source fidelity

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
printf '%s' "$PIPELINE_STATE" | uv run --project ops/tooling vault validate --artifacts
```

If validation fails, fix the Markdown once and rerun validation. If it still fails, emit the failure JSON and stop.

## Output

Emit the validated JSON object as the final message. No prose, headings, or markdown fences.
