# Ars Contexta Vault Tooling

This project is generated into each Ars Contexta vault. Runtime commands use:

```bash
uv run arscontexta-vault <command>
```

Intended commands:

```bash
uv run arscontexta-vault seed --source "<file>" --mode structure
uv run arscontexta-vault seed --source "<file>" --mode capture
uv run arscontexta-vault validate --path "notes/example.md"
uv run arscontexta-vault validate --all
printf '%s' "$PIPELINE_STATE" | uv run arscontexta-vault validate --artifacts
```

Development checks:

```bash
uv run ruff check src tests
uv run pytest
```
