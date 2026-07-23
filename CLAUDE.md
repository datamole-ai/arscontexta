# Second Brain engine

This repository generates vaults; it is not a vault. Never scaffold one here. User setup and usage belong in [README.md](README.md).

## Code map

| Change | Location |
|---|---|
| Setup flow and copy script | `skills/setup/` |
| Fixed vault template and copied skills | `template/` |
| Vault runtime CLI | `vault-tooling/` |
| Real-tool evaluations | `.claude/skills/run-scenario/`, `tests/scenarios/` |
| Plugin metadata | `.claude-plugin/plugin.json` |

## Contracts

- Vaults always use `notes/`, `inbox/`, `archive/`, and `ops/`.
- Every note has exactly `content_type`, `granularity`, `description`, and `tags`. `content_type` is `moc | note`; requested attributes become governed tags.
- The pipeline is Record → Reduce → Connect → Verify. `/process` commits each successful batch.
- Each vault has a project-local `.qmd/` index with one fixed collection named `notes`.
- Setup copies `template/` through `skills/setup/scripts/copy-template.sh`; only `ops/tags.yaml` varies with the setup conversation.
- Keep the skills under `template/.claude/skills/` generation-ready. Use fixed storage paths and do not add generation-time placeholders.
- Setup validates the vault before its initial commit. Treat `skills/setup/SKILL.md` as high blast radius.

## Checks

- For `vault-tooling/` changes, run `cd vault-tooling && uv run ruff check src tests && uv run ty check && uv run pytest`.
- To run a scenario, read `tests/README.md` and follow its agent workflow.
