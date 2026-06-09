# e2e harness

End-to-end tests for the Second Brain Claude Code plugin. Drives the plugin headlessly, asserts
deterministic contracts, and does not care about prose.

## Prerequisites

- `uv` installed and on PATH
- `claude` CLI installed, authenticated, and on PATH
- Obsidian and qmd are NOT required — both are shimmed

## How to run

```bash
cd e2e
uv run pytest test_harness.py -v          # token-free self-tests; run these first
uv run pytest test_scenarios.py -v        # expensive e2e tests; real tokens, real minutes
```

Environment variables:

| Variable | Effect |
|---|---|
| `E2E_MODEL` | Claude model for the driven sessions (default `claude-opus-4-8`) |
| `E2E_EFFORT` | Effort level for the driven sessions (default `low`) |
| `E2E_VAULT` | Skip setup; point at an already-generated vault to reuse across runs |

## How to add a scenario

1. Create `scenarios/<name>/scenario.yaml` following the researcher example.
2. Add inbox fixtures under `scenarios/<name>/inbox/`.
3. `conftest.py` discovers all `scenarios/*/scenario.yaml` automatically.

When `scenario.yaml` has no `process_runs` key, every `.md` file in the scenario's `inbox/`
becomes a process run with `mode: structure`, `min_new_notes: 1`, and the batch name derived
from the filename (lowercase, non-alphanumerics to hyphens). Declare `process_runs` explicitly
only to override mode or expectations.

Runs are strictly sequential, in lexicographic filename order — each run must pass its
assertions before the next starts. Use numeric prefixes (`01-kickoff.md`, `02-experiment.md`)
to control the order.

## Cost and time warning

Each scenario run invokes the Claude API with real tokens. A setup run costs roughly the same as
several hundred lines of generated code. A full e2e suite (setup + process) takes several minutes.
Do not run `test_scenarios.py` in CI without an explicit budget gate.

## Forensics

Each run lands in `.runs/<UTC-timestamp>-<scenario>/` with:

- `vault/` — the generated vault
- `turns/` — raw JSON for every claude turn (`NN.json`)
- `shim.log` — every shim invocation

`.runs/` is never auto-deleted. Clean it manually when disk space matters.
