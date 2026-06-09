# CLAUDE.md

**Second Brain** is a Claude Code plugin. A setup conversation about how the user works produces a bespoke knowledge system with folders, notes, a schema, processing skills, and navigation. **This repo is the engine, not a vault.** Do not scaffold one here. `README.md` has the product pitch and install steps; this file navigates the code.

## Quick map

| Task | Go to |
|---|---|
| Derivation engine (all six setup phases) | `skills/setup/SKILL.md` |
| Processing skill templates copied into generated vaults | `skill-sources/<name>/SKILL.md` |
| Python tooling copied into generated vaults | `vault-tooling/` |
| Plugin manifest and version | `.claude-plugin/plugin.json` |

## Directory layout

```
.claude-plugin/   plugin.json, marketplace.json   plugin registration
skills/setup/     SKILL.md                        the /second-brain:setup command
skill-sources/    6 skill templates               copied into generated vaults at setup
vault-tooling/    uv Python project               copied verbatim into each vault root
```

## Core concepts

1. **Derivation, not templating.** Only vocabulary is derived from the conversation. The architecture is fixed: folder separation, schema, skill set, and pipeline are the same in every generated vault.
2. **Fixed five-field schema.** Every note has `content_type`, `granularity`, `description`, `created_at`, `tags`. No other fields, ever. The `content_type` enum is derived from the user's vocabulary plus the reserved `moc` value. Requested attributes become tag vocabulary, not fields.
3. **Three-space layout.** A flat note collection, `self/` for agent identity, and `ops/` for coordination, plus inbox and archive folders. Folder names adapt per domain; the separation does not.
4. **Four-phase pipeline.** Record, Reduce, Connect, Verify. `/process` orchestrates the full run and commits each successful batch.
5. **Vocabulary resolves at runtime.** Skill sources carry no generation-time placeholders; setup copies them verbatim and they read `ops/derivation-manifest.yaml` at invocation time. The only generation-time substitution left is the `{DOMAIN:...}` identity template inside setup's Pipeline Step 2.

## How setup works

`skills/setup/SKILL.md` runs six phases: prerequisite gate, understanding, derivation, proposal, generation, validation. Generation is a 9-step pipeline. The main agent writes `ops/derivation.md` first as the source of truth, then folders, identity, the runtime manifest, `ops/schema.yaml`, and a verbatim copy of the 6 skill sources. Two subagents then run in parallel: a context agent (generated CLAUDE.md plus `/ask`) and a hub agent (hub MOC). The main agent finishes with qmd semantic search setup and a git commit, then validates with `uv run vault validate --all`.

## skill-sources/ by pipeline phase

| Phase | Skills |
|---|---|
| Record | `uv run vault seed` (CLI, no skill) |
| Reduce | `structure/`, `capture/` |
| Connect | `connect/` |
| Verify | `verify/` |
| Orchestration | `process/` |
| Diagnostics | `health/` |

Setup's Pipeline Step 5 copies all 6 skills verbatim into `.claude/skills/`. Command names and skill bodies are universal; domain vocabulary reaches them at runtime through `ops/derivation-manifest.yaml`.

## vault-tooling/

A static uv project copied into each vault root with `cp -R`, not a scaffolder. It provides the deterministic runtime commands `uv run vault seed` and `uv run vault validate`. Develop and test it in place:

```bash
cd vault-tooling
uv run ruff check src tests
uv run pytest
```

## Working in this repo

- **Do not scaffold a vault here.** This repo is the engine, not a generated vault.
- **`skills/setup/SKILL.md` is high blast radius.** It shapes every generated vault; change it carefully.
- **Editing `skill-sources/`.** Skills are copied verbatim into vaults — no placeholders. Keep folder references resolvable through `ops/derivation-manifest.yaml` (tooling requires the `note_collection`, `inbox`, and `archive` keys).
- **Editing `vault-tooling/`.** Run ruff and pytest there before committing.
- **Don't duplicate `README.md`.** Product pitch, prerequisites, commands, and the dev reinstall cycle live there only.
