# Second Brain Vault Tooling

This project is generated into each Second Brain vault. Runtime commands use:

```bash
uv run vault <command>
```

Intended commands:

```bash
uv run vault seed --source "<file>"
uv run vault validate --path "notes/example.md"
uv run vault validate --all
printf '%s' "$PIPELINE_STATE" | uv run vault validate --artifacts
```

Development checks:

```bash
uv run ruff check src tests
uv run pytest
```
