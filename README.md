# Ars Contexta

**A second brain for your agent.**

A Claude Code plugin that generates complete knowledge systems from conversation.
You describe how you think and work. The engine derives a cognitive architecture
-- folder structure, context files, processing pipeline, hooks, navigation maps,
and note templates -- tailored to your domain and backed by 242 research claims.

No templates. No configuration. Just conversation.

---

## Prerequisites

Install these before running `/arscontexta:setup`. All six are expected — the generated system assumes they are present and its skills call them directly.

| Dependency | Purpose |
|-----------|---------|
| [Claude Code](https://docs.anthropic.com/en/docs/claude-code) | Plugin host |
| `tree` | Workspace structure injection |
| `ripgrep` (`rg`) | YAML queries, schema validation |
| [uv](https://docs.astral.sh/uv/) | Runs and locks vault-local Python tooling |
| [qmd](https://github.com/tobi/qmd) v2+ | Semantic search (invariant kernel primitive — see below) |
| Obsidian CLI (`obsidian`) | Vault-native file, link, property, and graph facts |

---

## Installation

1. Add the marketplace to Claude Code:
   ```
   /plugin marketplace add datamole-ai-arscontexta/arscontexta
   ```

2. Install the plugin:
   ```
   /plugin install arscontexta@datamole-ai-arscontexta
   ```

3. Restart Claude Code, then run:
   ```
   /arscontexta:setup
   ```

4. Answer 2-6 questions about your domain (~20 minutes -- token-intensive but one-time)

5. The engine generates your complete knowledge system

6. Restart Claude Code again to activate generated hooks and skills

---

## What It Does

Most AI tools start every session blank. Ars Contexta changes that by generating
a persistent thinking system derived from how you actually work.

**What you get:**

- **A vault** -- plain markdown files connected by wiki links, forming a traversable
  knowledge graph. No database, no cloud, no lock-in.
- **A processing pipeline** -- skills that extract insights, find connections, update
  old notes with new context, and verify quality.
- **Vault-local tooling** -- a copied `uv` Python project with two deterministic
  runtime commands: `seed` and `validate`.
- **Automation** -- hooks that enforce structure on every write, detect maintenance
  needs, and capture session state. `/pipeline` produces a single commit at the end of each batch.
- **Navigation** -- Maps of Content (MOCs) at hub, domain, and topic levels.
- **Templates** -- note templates with `_schema` blocks as single source of truth.

**The key differentiator:** derivation, not templating. Every choice traces to
specific research claims. The engine reasons from principles about what your
domain needs and why.

---

## The Setup Flow

`/arscontexta:setup` runs a 6-phase process:

| Phase | What Happens |
|-------|-------------|
| **Detection** | Detects Claude Code environment and capabilities |
| **Understanding** | 2-4 conversation turns where you describe your domain |
| **Derivation** | Maps signals to vocabulary, schema, and workflow |
| **Proposal** | Shows what will be generated and why, in your vocabulary |
| **Generation** | Produces all files: context file, folders, templates, skills, hooks, and hub MOC |
| **Validation** | Checks generated dependencies and deterministic runtime validation |

The whole process takes about 20 minutes. It's token-intensive because the engine
reads research claims, reasons about your domain, and generates substantial output.
This is a one-time investment -- after setup, your agent remembers.

---

## Three-Space Architecture

Every generated system separates content into three spaces:

| Space | Purpose | Growth |
|-------|---------|--------|
| **self/** | Agent persistent mind -- identity, methodology, goals | Slow (tens of files) |
| **notes/** | Knowledge graph -- the reason the system exists | Steady (10-50/week) |
| **ops/** | Operational coordination -- templates, derivation, sessions | Fluctuating |

Names adapt to your domain (`notes/` might become `reflections/`, `claims/`,
or `decisions/`), but the separation is invariant.

---

## Commands

### Plugin-Level

| Command | What It Does |
|---------|-------------|
| `/arscontexta:setup` | Conversational onboarding -- generates your full system |

### Generated (available after setup)

#### Pipeline

| Command | What It Does |
|---------|-------------|
| `/pipeline` | End-to-end source processing |

#### Pipeline Sub-Skills

| Command | What It Does |
|---------|-------------|
| `/seed` | Pipeline-internal source archival and initial state |
| `/structure` | Group claims into finished notes and apply enrichments to existing notes |
| `/capture` | Verbatim capture — preserves source without transformation |
| `/connect` | Run qmd discovery, gather Obsidian graph facts, update MOCs |
| `/verify` | Obsidian link checks plus deterministic schema validation |

#### Operational

| Command | What It Does |
|---------|-------------|
| `/health` | Obsidian diagnostics plus `validate --all` |

---

## Processing Pipeline


| Phase | What Happens | Command |
|-------|-------------|---------|
| **Record** | Zero-friction capture into inbox/ | User action |
| **Reduce** | Extract insights with domain-native categories | `/structure`, `/capture` |
| **Connect** | Find connections, update MOCs, reconsider older notes | `/connect` |
| **Verify** | Obsidian link checks plus deterministic schema validation | `/verify` |

---

## Hooks

| Hook | Event | What It Does |
|------|-------|-------------|
| **Session Orient** | `SessionStart` | Injects workspace tree, loads identity, surfaces maintenance signals |

---

## Development

Clone this repo and add the marketplace to Claude Code:

```
/plugin marketplace add ~/path-to-arscontexta
```

Install the plugin:

```
/plugin install arscontexta@datamole-ai-arscontexta
```

Every time you make changes, re-install the plugin:

```
/plugin uninstall arscontexta@datamole-ai-arscontexta
/plugin install arscontexta@datamole-ai-arscontexta
```
