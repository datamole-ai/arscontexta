# Second Brain vault tooling

Setup copies this project's runtime snapshot (`pyproject.toml`, `uv.lock`, and `src/vault/`) into each vault at `ops/tooling/`; this README and the tests stay in the engine checkout. Inside a vault, uv uses the copied lock automatically:

```bash
uv run --project ops/tooling vault <command>
```

The bare `uv run vault <command>` form below works from this directory during development.

The package is organized as a CLI application with an explicit composition root:

```text
vault/
├── cli.py                   # stable executable entrypoint
├── bootstrap.py             # Typer app construction and command registration
├── shared/                  # errors, output, paths, and cross-domain helpers
├── seed/                    # command adapter, application logic, and models
├── capture/                 # command adapter, application logic, and models
└── validation/              # command adapter, application logic, models, and parsing
```

Domain packages own their inputs and behavior. `shared/` contains only infrastructure used by
multiple domains; dependencies point from commands into application code, never back into the CLI.

Intended commands:

```bash
uv run vault seed --source "<file>"
uv run vault capture --source "<archived file>" --title "<title>" --description "<text>" [--tag <tag>]...
uv run vault validate --path "notes/example.md"
uv run vault validate --all
printf '%s' "$PIPELINE_STATE" | uv run vault validate --artifacts
```

Development checks:

```bash
uv run ruff check src tests
uv run ty check
uv run pytest
```
