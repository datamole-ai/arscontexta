# Second Brain

Second Brain is a Claude Code plugin that generates a local Markdown knowledge system with fixed defaults and a small starter tag registry.

## Install from a release

Install [Claude Code](https://docs.anthropic.com/en/docs/claude-code) v2.1.129 or newer, [uv](https://docs.astral.sh/uv/), [qmd](https://github.com/tobi/qmd) v2+, Obsidian, and the Obsidian CLI. Then create an empty directory and start Claude Code with the latest release:

```bash
mkdir my-second-brain
cd my-second-brain
claude --plugin-url https://github.com/datamole-ai/arscontexta/releases/latest/download/second-brain.zip
```

Run `/second-brain:setup`. When setup finishes, restart Claude Code in the generated folder and open that folder as an Obsidian vault. Keep Obsidian running while you use the vault.

## Use it

Add a source file to `inbox/`, then run one of these commands:

| Command | Purpose |
|---|---|
| `/process inbox/source.md --structure` | Turn a source into distilled notes |
| `/process inbox/source.md --capture` | Preserve a source verbatim |
| `/health` | Check the vault |
