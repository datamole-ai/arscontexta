# CLAUDE.md

**Ars Contexta** — Claude Code plugin. Conversational derivation engine: a conversation about how the user works produces a bespoke knowledge system (folders, notes, processing skills, hooks, manual) backed by 249 wiki-linked research claims. **This repo is the engine, not a vault** — do not scaffold one here. `README.md` has the product pitch; this file navigates the code.

## Quick Map

| Task | Go to |
|---|---|
| Derivation engine (onboarding → generation) | `skills/setup/SKILL.md` |
| Diagnostic command | `skills/health/SKILL.md` |
| Processing command templates (copied into generated vaults) | `skill-sources/<name>/SKILL.md` |
| Generated CLAUDE.md composition | `generators/claude-md.md` + `generators/features/*.md` |
| Architectural invariants (14 primitives) | `reference/kernel.yaml` |
| Research graph (249 claims) | `methodology/*.md` — indexed via `reference/claim-map.md` |
| Hook behavior | `hooks/hooks.json` + `hooks/scripts/*.sh` |
| Starting configurations | `presets/{personal,research,experimental}/` |
| Plugin manifest / version | `.claude-plugin/plugin.json` |
| Author scratchpad | `todo.md` |

## Directory Layout

```
.claude-plugin/   plugin.json, marketplace.json      plugin registration
skills/           setup/, health/                    plugin-level commands (user-invoked)
skill-sources/    15 command templates               copied into generated vaults
generators/       claude-md.md + features/ (16)      composed into generated CLAUDE.md
hooks/            hooks.json, scripts/*.sh           SessionStart + PostToolUse(Write)
methodology/      249 claim notes                    wiki-linked research graph
reference/        canonical design docs              see index below
presets/          personal/, research/, experimental preset configs + starter content
docs/             superpowers/{plans,specs}          design specs
```

## Core Concepts

1. **Kernel** — 14 invariant primitives every generated vault must satisfy. `reference/kernel.yaml` + `reference/validate-kernel.sh`.
2. **Three-space architecture** — `self/` (agent mind) · `notes/` (knowledge graph) · `ops/` (coordination). Names adapt per domain; separation is invariant. `reference/three-spaces.md`.
3. **Derivation, not templating** — engine reasons from claims to architecture. Every dimension choice traces to research. `reference/dimension-claim-map.md`.
4. **6 Rs pipeline** — Record, Reduce, Reflect, Reweave, Verify, Rethink. One skill per R.
5. **Vocabulary transforms** — universal terms → domain-native. `reference/vocabulary-transforms.md`.

## skill-sources/ by Pipeline Phase

| Phase | Skills |
|---|---|
| Reduce | `structure/`, `capture/` |
| Mutate | `seed/`, `create/` |
| Reflect | `reflect/` |
| Reweave | `reweave/` |
| Verify | `verify/` |
| Meta | `rethink/`, `remember/`, `refactor/` |
| Orchestration | `pipeline/` |
| Reporting | `stats/`, `graph/`, `archive-batch/` |

Each `SKILL.md` uses `{DOMAIN:…}` placeholders that the derivation engine rewrites at generation.

## reference/ Index

| File | Content |
|---|---|
| `kernel.yaml` | 14 invariants |
| `three-spaces.md` | self/notes/ops architecture |
| `components.md` | per-component build blueprints |
| `methodology.md` | portable TFT research distillation |
| `claim-map.md` | topic → claim lookup |
| `dimension-claim-map.md` | dimension → backing claims |
| `interaction-constraints.md` | incoherent-combination rules |
| `use-case-presets.md` | pre-validated starting configs |
| `tradition-presets.md` | Zettelkasten / PARA / GTD / Cornell anchors |
| `vocabulary-transforms.md` | universal → domain-native maps |
| `conversation-patterns.md` | worked derivation examples |
| `failure-modes.md` | how vaults die (warnings injected into vaults) |
| `session-lifecycle.md` | orient / work / persist spec |
| `evolution-lifecycle.md` | post-scaffold growth patterns |
| `self-space.md` | agent-identity generation guide |
| `semantic-vs-keyword.md` | search modality selection |
| `derivation-validation.md` | 9 coherence tests |
| `testing-milestones.md` | 7 validation layers |
| `templates/` | `moc.md`, `note.md`, `session-log.md` |
| `validate-kernel.sh` | kernel conformance checker |

## generators/features/ (composable CLAUDE.md blocks)

One file per feature; `skills/setup/` enables a subset based on derived config:

`ethical-guardrails`, `graph-analysis`, `helper-functions`, `maintenance`, `methodology-knowledge`, `mocs`, `multi-domain`, `note-granularity`, `processing-pipeline`, `schema`, `self-evolution`, `self-space`, `semantic-search`, `session-rhythm`, `templates`, `wiki-links`.

## Hooks

| Script | Event | Purpose |
|---|---|---|
| `session-orient.sh` | SessionStart | Inject tree + identity + maintenance signals |
| `auto-commit.sh` | PostToolUse(Write, async) | Git auto-commit, non-blocking |
| `vaultguard.sh` | helper | Early-exit outside vaults; do not bypass |

## Working in This Repo

- **Do not scaffold a vault here.** Hooks are gated by `vaultguard.sh`; leave it that way.
- **Derivation changes are high blast radius.** After touching `skills/setup/SKILL.md`, `reference/interaction-constraints.md`, or `reference/tradition-presets.md`, rerun the tests in `reference/derivation-validation.md`.
- **Research claims are the source of truth.** Back configuration decisions via `reference/claim-map.md` + `methodology/`. New claims: one file per claim, prose-as-title, wiki-linked.
- **Don't duplicate `README.md`.** Product pitch and install steps live there only.
- **Check `todo.md`** before proposing overlapping changes.
- **Dev reinstall cycle** (`/plugin uninstall … && /plugin install …`) documented in `README.md § Development`.
