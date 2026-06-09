# Second Brain

Second Brain is a Claude Code plugin that turns a setup conversation into a local Markdown knowledge system for your agent.

You describe what you want to track, remember, or think through. The plugin derives the folders, context files, processing skills, navigation maps, and note schema for that work. The result is a generated vault, not a template copied into this repo.

## Contents

- [Install](#install)
- [Prerequisites](#prerequisites)
- [What setup creates](#what-setup-creates)
- [Setup flow](#setup-flow)
- [Generated architecture](#generated-architecture)
- [Commands](#commands)
- [Processing pipeline](#processing-pipeline)
- [Development](#development)

## Install

The plugin is not published to a marketplace. Install it from a local copy of this repository.

Make sure the [prerequisites](#prerequisites) are installed before you run setup.

Get this repository onto your machine, then run these commands inside Claude Code with the path to your copy:

```text
/plugin marketplace add /path/to/second-brain
/plugin install second-brain@datamole-ai-second-brain
```

Restart Claude Code, then run:

```text
/second-brain:setup
```

Setup asks a short set of questions about your domain. It usually takes about 20 minutes because the plugin reads its references, derives your vocabulary, and writes the generated system.

After setup finishes:

1. Restart Claude Code again so generated skills load.
2. Open the generated folder as an Obsidian vault and leave Obsidian running before using `/process`.

## Prerequisites

Install these before running `/second-brain:setup`. Setup checks them before it writes files.

| Dependency | Purpose |
|-----------|---------|
| [Claude Code](https://docs.anthropic.com/en/docs/claude-code) | Plugin host |
| [uv](https://docs.astral.sh/uv/) | Vault-local Python tooling |
| [qmd](https://github.com/tobi/qmd) v2+ | Semantic search |
| Obsidian CLI (`obsidian`) | Vault-native file, link, property, and graph facts |

## What setup creates

- A vault of plain Markdown files connected by wiki links.
- An inbox-to-notes processing pipeline.
- Vault-local tooling, copied as a `uv` Python project, with deterministic `seed` and `validate` commands.
- Maps of Content for hub, domain, and topic navigation.
- `ops/schema.yaml`, the schema contract for note properties.

The main choice is derivation instead of templating. Setup uses your vocabulary, maps it to the fixed architecture, then records why those choices were made.

## Setup flow

`/second-brain:setup` runs this process:

| Phase | What happens |
|-------|--------------|
| Detection | Checks Claude Code and required local tools |
| Understanding | Asks 2-4 conversation turns about your domain |
| Derivation | Maps your vocabulary to folders, note types, tags, and navigation |
| Proposal | Shows what will be generated before writing files |
| Generation | Writes the context file, folders, schema, skills, and hub MOC |
| Validation | Checks generated dependencies and deterministic runtime validation |

## Generated architecture

Every generated system separates content into three spaces:

| Space | Purpose | Growth |
|-------|---------|--------|
| `self/` | Agent identity | Slow, usually a few files |
| `notes/` | The knowledge graph | Steady, often 10-50 files per week |
| `ops/` | Schema, derivation records, sessions, and coordination | Fluctuating |

Names adapt to your domain. For example, `notes/` might become `reflections/`, `claims/`, or `decisions/`. The separation stays the same.

## Commands

### Plugin-level

| Command | What it does |
|---------|--------------|
| `/second-brain:setup` | Runs conversational setup and generates the full system |

### Generated after setup

| Command | What it does |
|---------|--------------|
| `/process` | Runs end-to-end source processing |
| `/structure` | Turns source material into finished notes |
| `/capture` | Preserves source material verbatim |
| `/connect` | Runs qmd discovery, gathers Obsidian graph facts, and updates MOCs |
| `/verify` | Checks Obsidian links and deterministic schema validation |
| `/health` | Runs Obsidian diagnostics plus `validate --all` |

## Processing pipeline

| Phase | What happens | Command |
|-------|--------------|---------|
| Record | Capture source material into the inbox | User action |
| Reduce | Extract notes or preserve source text | `/structure`, `/capture` |
| Connect | Find links, update MOCs, and reconsider older notes | `/connect` |
| Verify | Check links and schema before the batch is committed | `/verify` |

`/process` orchestrates the full pipeline and creates one git commit at the end of each successful batch.

## Development

Install from your local copy as described in [Install](#install). Reinstall after each change:

```text
/plugin uninstall second-brain@datamole-ai-second-brain
/plugin install second-brain@datamole-ai-second-brain
```
