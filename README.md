# Second Brain

Second Brain is a Claude Code plugin that generates a local Markdown knowledge system with fixed defaults and a small starter tag registry.

## Install

Install [Claude Code](https://docs.anthropic.com/en/docs/claude-code), [uv](https://docs.astral.sh/uv/), [qmd](https://github.com/tobi/qmd) v2+, and the Obsidian CLI. Then run:

```text
/plugin marketplace add /path/to/second-brain
/plugin install second-brain@datamole-ai-second-brain
```

Restart Claude Code and run `/second-brain:setup`. Setup checks the prerequisites, asks which starter tags matter, copies the fixed system, and validates it.

When setup finishes:

1. Restart Claude Code so the generated skills load.
2. Open the generated folder as an Obsidian vault and leave Obsidian running.
3. Add a file to `inbox/` and run `/process`.

## What it creates

Every vault uses:

- `notes/` for a flat, linked knowledge graph
- `inbox/` for new material
- `archive/` for processed sources
- `ops/` for schema, tooling, and coordination

Setup customizes only the starter entries in `ops/tags.yaml`. Storage, prose, navigation, the four-field note schema (`content_type`, `granularity`, `description`, `tags`), and the Record → Reduce → Connect → Verify pipeline stay fixed. `content_type` is always `moc` or `note`.

### Vault versions

The root `.second-brain` file is both the vault marker and a JSON version manifest. It records:

- `generator_version`: the Second Brain plugin release that generated the vault
- `template_version`: the version of the fixed vault format copied by setup
- `runtime_version`: the version of the `dtml-second-brain` package copied to `ops/tooling/`

The manifest stays with the vault, so users can identify which plugin, template format, and runtime it received even after they uninstall the plugin.

## Commands

| Command | Purpose |
|---|---|
| `/second-brain:setup` | Generate a vault |
| `/process` | Process one inbox source end to end |
| `/health` | Diagnose the vault |

`/process` preserves or distills the source, connects the result, verifies it, and commits the successful batch.

## Develop

Reinstall the plugin after a change:

```text
/plugin uninstall second-brain@datamole-ai-second-brain
/plugin install second-brain@datamole-ai-second-brain
```

See [CLAUDE.md](CLAUDE.md) for the code map and change-specific checks, and [vault-tooling/README.md](vault-tooling/README.md) for the runtime CLI.

When changing a plugin or runtime version, run the manifest consistency test:

```bash
python3 -m unittest tests/test_version_manifest.py
```
