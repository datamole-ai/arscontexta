# Running scenarios

Each directory under `tests/scenarios/` is a real-tool evaluation. An agent runs the
scenario with Claude Code and saves the resulting vault, logs, and evaluation.

## Run a scenario

1. Create the run from repo, by passing the scenario name to `create-scenario-run.sh`, then start the candidate from its empty vault.
2. Run the files under `prompts/` in filename order with `claude -p`. Add
   `--resume <session-id>` for setup follow-ups; use a fresh session for every other turn.
3. Register the generated vault in Obsidian after setup succeeds.
4. Process files under `inbox/` in filename order. Use a fresh `claude -p` session for each
   file.
5. Lastly read tests/scenarios/general-eval.md and run the evaluation against the final vault.

## General instructions

Fail fast and do not repair or rerun the candidate from the harness. A candidate may use only retries that its active skill explicitly authorizes within the same turn. Preserve failed runs for inspection.

Use this command shape for every Claude turn:

```bash
if [ -f "$REPO_ROOT/.env" ]; then
  set -a
  . "$REPO_ROOT/.env"
  set +a
fi
export CLAUDE_CONFIG_DIR="$RUN_ROOT/claude-config"

claude -p \
  --settings "$REPO_ROOT/tests/claude-scenario-settings.json" \
  --plugin-dir "$REPO_ROOT" \
  --permission-mode auto \
  --model sonnet \
  --effort high \
  --output-format stream-json \
  --include-partial-messages \
  --verbose \
  < "$PROMPT" \
  2> "$RUN_ROOT/logs/$LABEL.stderr.log" \
  | tee "$RUN_ROOT/logs/$LABEL.stream.jsonl"
```
