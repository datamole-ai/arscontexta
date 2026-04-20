# Ars Contexta

**A second brain for your agent.**

A Claude Code plugin that generates complete knowledge systems from conversation.
You describe how you think and work. The engine derives a cognitive architecture
-- folder structure, context files, processing pipeline, hooks, navigation maps,
and note templates -- tailored to your domain and backed by 249 research claims.

No templates. No configuration. Just conversation.

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
- **Automation** -- hooks that enforce structure on every write, detect maintenance
  needs, and capture session state. `/pipeline` produces a single commit at the end of each batch.
- **Navigation** -- Maps of Content (MOCs) at hub, domain, and topic levels.
- **Templates** -- note templates with `_schema` blocks as single source of truth.
- **A user manual** -- 7 pages of domain-native documentation generated alongside.

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
| **Derivation** | Maps signals to eight configuration dimensions with confidence scoring |
| **Proposal** | Shows what will be generated and why, in your vocabulary |
| **Generation** | Produces all files: context file, folders, templates, skills, hooks, manual |
| **Validation** | Checks all 14 kernel primitives, runs pipeline smoke test |

The whole process takes about 20 minutes. It's token-intensive because the engine
reads research claims, reasons about your domain, and generates substantial output.
This is a one-time investment -- after setup, your agent remembers.

For advanced users: `/arscontexta:setup --advanced` to configure dimensions directly.

---

## Three-Space Architecture

Every generated system separates content into three spaces:

| Space | Purpose | Growth |
|-------|---------|--------|
| **self/** | Agent persistent mind -- identity, methodology, goals | Slow (tens of files) |
| **notes/** | Knowledge graph -- the reason the system exists | Steady (10-50/week) |
| **ops/** | Operational coordination -- queue state, sessions | Fluctuating |

Names adapt to your domain (`notes/` might become `reflections/`, `claims/`,
or `decisions/`), but the separation is invariant.

---

## Commands

### Plugin-Level (always available)

| Command | What It Does |
|---------|-------------|
| `/arscontexta:setup` | Conversational onboarding -- generates your full system |
| `/arscontexta:health` | Run diagnostic checks on your vault |

### Generated (available after setup)

#### Pipeline

| Command | What It Does |
|---------|-------------|
| `/pipeline` | End-to-end source processing |

#### Pipeline Sub-Skills

| Command | What It Does |
|---------|-------------|
| `/seed` | Create processing task with duplicate detection |
| `/structure` | Extract grouped insights preserving shared context |
| `/capture` | Verbatim capture — preserves source without transformation |
| `/create` | Create a new note |
| `/enrich` | Enrich an existing note |
| `/reflect` | Find connections, update MOCs |
| `/reweave` | Update older notes with new connections |
| `/verify` | Combined quality check: description + schema + health |
| `/archive-batch` | Archive batch of notes |

#### Operational

| Command | What It Does |
|---------|-------------|
| `/stats` | Vault metrics |
| `/graph` | Graph analysis |

#### Meta-Cognitive

| Command | What It Does |
|---------|-------------|
| `/rethink` | Challenge system assumptions |
| `/remember` | Mine session learnings |
| `/refactor` | Structural improvements |

---

## Processing Pipeline

The vault implements the **6 Rs**, extending Cornell Note-Taking's 5 Rs with a
meta-cognitive layer:

| Phase | What Happens | Command |
|-------|-------------|---------|
| **Record** | Zero-friction capture into inbox/ | Manual |
| **Reduce** | Extract insights with domain-native categories | `/structure`, `/capture` |
| **Reflect** | Find connections, update MOCs | `/reflect` |
| **Reweave** | Update older notes with new context | `/reweave` |
| **Verify** | Description + schema + health checks | `/verify` |
| **Rethink** | Challenge system assumptions | `/rethink` |

---

## Hooks

| Hook | Event | What It Does |
|------|-------|-------------|
| **Session Orient** | `SessionStart` | Injects workspace tree, loads identity, surfaces maintenance signals |

---

## The Research Graph

The `methodology/` directory contains **249 interconnected research claims**
about tools for thought, knowledge management, and agent-native cognitive
architecture. These claims back every configuration decision.

### Synthesizes

Zettelkasten -- Cornell Note-Taking -- Evergreen Notes -- PARA -- GTD -- Memory
Palaces -- Cognitive Science (extended mind, spreading activation, generation
effect) -- Network Theory (small-world topology, betweenness centrality) --
Agent Architecture (context windows, session boundaries, multi-agent patterns)

### How Claims Back Decisions

Every kernel primitive includes `cognitive_grounding` linking to specific research:

- **MOC hierarchy** -- context-switching cost research (Leroy 2009)
- **Description field** -- progressive disclosure principles
- **Wiki links** -- spreading activation theory

---

## Semantic Search (optional)

[qmd](https://github.com/tobi/qmd) adds concept matching across vocabularies.
Not required -- the system works fully with ripgrep + MOC traversal.

`/setup` should perform this configuration automatically when semantic search is active.
The commands below are manual fallback/setup verification.

```bash
# Install qmd
npm install -g @tobilu/qmd
# or
bun install -g @tobilu/qmd

cd your-vault/
qmd collection add . --name <notes_directory_name> --mask "<notes_directory_name>/**/*.md"
qmd embed
```

Create or merge `.mcp.json` in the vault root:

```json
{
  "mcpServers": {
    "qmd": {
      "command": "qmd",
      "args": ["mcp"],
      "autoapprove": [
        "mcp__qmd__query",
        "mcp__qmd__get",
        "mcp__qmd__multi_get",
        "mcp__qmd__status"
      ]
    }
  }
}
```

Keep qmd MCP configuration and tool preapproval in `.mcp.json`.

---

## Prerequisites

| Dependency | Required | Purpose |
|-----------|----------|---------|
| [Claude Code](https://docs.anthropic.com/en/docs/claude-code) v1.0.33+ | Yes | Plugin host |
| `tree` | Yes | Workspace structure injection |
| `ripgrep` (`rg`) | Yes | YAML queries, schema validation |
| [qmd](https://github.com/tobi/qmd) | Optional | Semantic search |

---

## Project Structure

```
arscontexta/
|-- .claude-plugin/
|   |-- plugin.json              # Plugin manifest
|   +-- marketplace.json         # Marketplace listing
|-- skills/                      # Plugin-level commands
|   |-- setup/                   # Conversational onboarding
|   +-- health/                  # Diagnostic checks
|-- skill-sources/               # 16 generated command templates
|   |-- reduce/                  # Extract insights
|   |-- reflect/                 # Find connections
|   |-- reweave/                 # Backward pass
|   |-- verify/                  # Combined quality check
|   +-- ...                      # 12 more processing commands
|-- hooks/
|   |-- hooks.json               # Hook configuration
|   +-- scripts/                 # Hook implementations
|-- generators/
|   |-- claude-md.md             # CLAUDE.md template
|   +-- features/                # 17 composable feature blocks
|-- methodology/                 # 249 research claims
|-- reference/                   # Core reference documents
|   |-- kernel.yaml              # 14 kernel primitives
|   |-- three-spaces.md          # Architecture spec
|   +-- use-case-presets.md      # Pre-validated configs
|-- presets/                     # Pre-validated configurations
|-- scripts/                     # Utility scripts
+-- README.md
```

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

### Key Files for Contributors

- `reference/kernel.yaml` -- 14 primitives every system must include
- `generators/features/*.md` -- composable feature blocks
- `skill-sources/*/SKILL.md` -- generated command templates
- `skills/setup/SKILL.md` -- the derivation engine
- `reference/use-case-presets.md` -- preset definitions
