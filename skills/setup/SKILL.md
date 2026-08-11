---
name: setup
description: Scaffold a complete knowledge system. Checks prerequisites, derives starter tags, copies the fixed vault template, validates it, and commits it. Triggers on "/setup", "set up my knowledge system", "create my vault".
disable-model-invocation: true
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion
---

You are the Second Brain setup engine. Only the starter tag registry is customized from the setup conversation.

## Phase 1: Prerequisite gate and onboarding

Verify required local tooling before asking questions or writing files:

```bash
command -v uv
command -v qmd
command -v obsidian
command -v git
qmd -v
```

If a command is missing or `qmd` is older than v2, stop with concise installation instructions.

### Onboarding

Output this text exactly:

```
second brain

I'll build a local markdown knowledge system that your agent can operate
across sessions.

What I'll create:

  - connected notes in plain markdown
  - an inbox-to-notes processing pipeline
  - topic maps for navigation
  - health checks and schema
  - agent self-knowledge so future sessions keep continuity

What I need from you:

Tell me what you need to filter, group, or find later. I'll turn those
attributes into a small starter tag registry.

I'll use fixed defaults for folders, note types, navigation, prose, and
workflow. Before writing files, I'll show you the proposed starter tags.

What attributes matter when you look for something again?
```

If the user answers the final question in the same message, treat it as the opening response.

---

## Phase 2: Understanding

Record attributes and groupings the user wants to filter or browse by. These are candidates for `ops/tags.yaml`.

Do not derive names, prose, folders, content types, navigation terms, or workflow choices.

Ask at most three conversational follow-up questions when a tag candidate is unclear. Confirm whether it should be:

- an exact tag, such as `decision`
- an open family, such as `project/*`

Proceed when the user signals readiness or after four conversation turns, whichever comes first. If no useful starter tags emerge, use an empty registry.

---

## Phase 3: Tag derivation

Create a small set of `{tag, meaning}` entries:

- Use `x/*` for an open family of values and an exact tag otherwise.
- Omit the leading `#`, use `/` for nesting, allow no spaces, and require at least one non-numeric character.
- Give every entry a one-sentence meaning.
- Prefer `tags: []` to speculative entries.

Do not present this internal reasoning.

---

## Phase 4: Proposal

Present one compact proposal containing:

- One sentence stating that folders, schema, navigation, prose, and workflow use fixed defaults.
- The proposed starter tag entries, or `tags: []`.

End with: **"Would you like me to adjust anything before I create this?"**

Adjust starter tags when requested. Keep every other part of the template fixed. If the user asks for another customization, explain that setup only customizes tags.

Do not write files before approval.

---

## Phase 5: Generation

Run all four steps directly. Do not invoke agents or author fixed artifacts from memory.

### Step 1: Copy the fixed template

Run from the empty vault root:

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/setup/scripts/copy-template.sh" "$PWD"
```

The script copies the root `template/` tree, which contains:

- fixed `CLAUDE.md`, the hub MOC, and `ops/schema.yaml`
- the empty governed registry at `ops/tags.yaml`
- all six skills under `.claude/skills/`
- the vault `.gitignore`

The script copies the template and the reviewed runtime snapshot into `ops/tooling/`, including
`uv.lock`.

Stop and surface the command output if the script fails. Do not edit `CLAUDE.md`,
`notes/index.md`, `ops/schema.yaml`, the copied lockfile, or the copied skills.

### Step 2: Write starter tags

Edit only the `tags` list in `ops/tags.yaml`. Preserve its header comments. Each entry must contain `tag` and `meaning`:

```yaml
tags:
  - tag: project/*
    meaning: The project this note concerns
  - tag: decision
    meaning: A choice that affects later work
```

The entries above show the shape only. Write the approved entries from Phase 4. Leave `tags: []` unchanged when no starter tags were approved.

### Step 3: Initialize semantic search

Create the project-local qmd collection:

```bash
qmd init
qmd collection add . --name notes --mask "notes/**/*.md"
qmd update
qmd embed
```

Stop and surface the command output if any command fails.

### Step 4: Validate and commit

Run:

```bash
uv run --project ops/tooling --locked vault validate --all
```

Continue only when it returns JSON with `"ok": true`. Then run:

```bash
git init
git add -A
git commit -m "Initial vault generation by Second Brain"
```

Stop and surface any validation or Git error.

---

## Phase 6: Summary

Present clean Markdown with no decorative Unicode or ASCII art:

```
second brain

Your knowledge system is ready.

Created:
  notes/, inbox/, archive/, and ops/
  CLAUDE.md
  notes/index.md
  ops/schema.yaml
  ops/tags.yaml
  six skills in .claude/skills/
  vault-local Python tooling in ops/tooling/

Available commands:
  /process                        -- process one inbox source
  /health                         -- run vault diagnostics

Lifecycle:
  Notes and normal vault content remain editable and can grow over time.
  The copied template, skills, schema, and tooling are a fixed snapshot.
  Plugin updates affect only vaults generated later.
  There is no second-brain upgrade command. To adopt a newer system,
  create a new vault and migrate content deliberately.

IMPORTANT: Restart Claude Code now to activate the generated skills.

Next steps:
  1. Quit and restart Claude Code
  2. Open this folder as an Obsidian vault and leave Obsidian running
  3. Add a file to inbox/
  4. Run /process with the file path and either --structure or --capture
```
