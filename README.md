# Second Brain

Second Brain is a Claude Code plugin that generates a local Markdown knowledge system with fixed defaults and a small starter tag registry.

## Install from a release

Install [Claude Code](https://docs.anthropic.com/en/docs/claude-code) v2.1.128 or newer, [uv](https://docs.astral.sh/uv/), [qmd](https://github.com/tobi/qmd) v2+, Obsidian, and the Obsidian CLI. Create an empty target directory and start Claude Code with a pinned release:

```bash
mkdir my-second-brain
cd my-second-brain
claude --plugin-url https://github.com/datamole-ai/arscontexta/releases/download/v4.2.0/second-brain.zip
```

Run `/second-brain:setup` in that session. The plugin URL loads only for the current session, and the version in the URL pins the downloaded archive. Setup checks the prerequisites, asks which starter tags matter, copies the fixed system, and validates it.

For a persistent installation, add this repository as a marketplace from Claude Code:

```text
/plugin marketplace add datamole-ai/arscontexta
/plugin install second-brain@datamole-ai-second-brain
/reload-plugins
```

Then start Claude Code in an empty target directory and run `/second-brain:setup`.

When setup finishes:

1. Quit and restart Claude Code in the generated folder so its new project skills load.
2. Open the generated folder as an Obsidian vault and leave Obsidian running while you use `/process`.
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

## Vault lifecycle

The system copied into each vault is an immutable snapshot of the generator version that created it. Notes and other normal vault content remain editable and can grow over time, but the copied template, skills, schema, and tooling do not update in place.

Updating or reinstalling the plugin affects only vaults generated afterward. There is no `second-brain upgrade` command. To adopt a newer system, create a new vault and migrate content deliberately.

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

Build and verify the same archive published by the release workflow:

```bash
python3 scripts/release-archive.py build --output dist/second-brain.zip
python3 scripts/release-archive.py verify dist/second-brain.zip
```
