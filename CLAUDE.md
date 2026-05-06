# CLAUDE.md

**Ars Contexta** — Claude Code plugin. Conversational derivation engine: a conversation about how the user works produces a bespoke knowledge system (folders, notes, processing skills, hooks, manual). **This repo is the engine, not a vault** — do not scaffold one here. `README.md` has the product pitch; this file navigates the code.

## Quick Map

| Task | Go to |
|---|---|
| Derivation engine (onboarding → generation) | `skills/setup/SKILL.md` |
| Diagnostic command | `skills/health/SKILL.md` |
| Processing command templates (copied into generated vaults) | `skill-sources/<name>/SKILL.md` |
| Generated CLAUDE.md composition | `generators/claude-md.md`  |
| Generated `/ask` skill | `generators/ask-router.md`  |
| Feature reference generation | `generators/features/*.md` → `ops/features/*.md` |
| Architectural invariants (14 primitives) | `reference/kernel.yaml` |
| Hook behavior | `hooks/hooks.json` + `hooks/scripts/*.sh` |
| Plugin manifest / version | `.claude-plugin/plugin.json` |
| Author scratchpad | `todo.md` |

## Directory Layout

```
.claude-plugin/   plugin.json, marketplace.json      plugin registration
skills/           setup/, health/                    plugin-level commands (user-invoked)
skill-sources/    8 command templates                copied into generated vaults
generators/       claude-md.md + features/ (12)      composed into generated CLAUDE.md
hooks/            hooks.json, scripts/*.sh           SessionStart
reference/        canonical design docs              see index below
docs/             superpowers/{plans,specs}          design specs
```

## Core Concepts

1. **Kernel** — 14 invariant primitives every generated vault must satisfy. `reference/kernel.yaml`.
2. **Three-space architecture** — `self/` (agent mind) · `notes/` (knowledge graph) · `ops/` (coordination). Names adapt per domain; separation is invariant. `reference/three-spaces.md`.
3. **Derivation, not templating** — engine reasons from claims to architecture. Every dimension choice traces to research.
4. **4-phase pipeline** — Record, Reduce, Connect, Verify.
5. **Vocabulary transforms** — universal terms → domain-native. `reference/vocabulary-transforms.md`.

## skill-sources/ by Pipeline Phase

| Phase | Skills |
|---|---|
| Reduce | `structure/`, `capture/` |
| Mutate | `seed/` |
| Connect | `connect/` |
| Verify | `verify/` |
| Orchestration | `pipeline/` |
| Reporting | `stats/`, `archive-batch/` |

Each `SKILL.md` uses `{DOMAIN:…}` placeholders that the derivation engine rewrites at generation.

## reference/ Index

| File | Content |
|---|---|
| `kernel.yaml` | 14 invariants |
| `three-spaces.md` | self/notes/ops architecture |
| `components.md` | per-component build blueprints |
| `interaction-constraints.md` | incoherent-combination rules |
| `use-case-presets.md` | pre-validated starting configs |
| `tradition-presets.md` | Zettelkasten / PARA / GTD / Cornell anchors |
| `vocabulary-transforms.md` | universal → domain-native maps |
| `failure-modes.md` | how vaults die (warnings injected into vaults) |
| `session-lifecycle.md` | orient / work / persist spec |
| `self-space.md` | agent-identity generation guide |
| `semantic-vs-keyword.md` | search modality selection |
| `templates/` | `moc.md`, `note.md` |

## generators/features/ (composable CLAUDE.md blocks)

One file per feature; `skills/setup/` enables a subset based on derived config:

`ethical-guardrails`, `helper-functions`, `maintenance`, `mocs`, `note-granularity`, `processing-pipeline`, `schema`, `self-space`, `semantic-search`, `session-rhythm`, `templates`, `wiki-links`.

## Hooks

| Script | Event | Purpose |
|---|---|---|
| `session-orient.sh` | SessionStart | Inject tree + identity + maintenance signals |
| `vaultguard.sh` | helper | Early-exit outside vaults; do not bypass |

## Working in This Repo

- **Do not scaffold a vault here.** Hooks are gated by `vaultguard.sh`; leave it that way.
- **Derivation changes are high blast radius.** `skills/setup/SKILL.md`, `reference/interaction-constraints.md`, and `reference/use-case-presets.md` shape every generated vault — change them carefully.
- **Don't duplicate `README.md`.** Product pitch and install steps live there only.
- **Check `todo.md`** before proposing overlapping changes.
- **Dev reinstall cycle** (`/plugin uninstall … && /plugin install …`) documented in `README.md § Development`.
