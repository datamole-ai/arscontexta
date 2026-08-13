# Running scenarios

Each directory under `tests/scenarios/` is a real-tool evaluation. An agent runs the
scenario with Claude Code and saves the resulting vault, logs, and evaluation.

## Run a scenario

1. Create the run from repo, by passing the scenario name to `create-scenario-run.sh`, then start the candidate from its empty vault.
2. Run the files under `prompts/` in filename order with `run-claude-turn.sh`. Resume
   only the setup follow-up; use a fresh session for every other turn.
3. Register the generated vault in Obsidian after setup succeeds.
4. Process files under `inbox/` in filename order. Use a fresh Claude session for each
   file.
5. If the scenario has a `questions/` directory, run its prompts in filename order after
   every source has been processed. Use a fresh Claude session for each question and
   save each prompt and log in the run. Do not expose the scenario's `eval.md` to the
   candidate or copy it into the vault.
6. Lastly read `tests/scenarios/general-eval.md` and run the evaluation against the final
   vault, logs, and the scenario's `eval.md` when it exists.

## General instructions

Fail fast on candidate or vault failures. Do not repair or rerun the candidate; preserve
the failed run. Use only retries authorized by the active skill.

Runner failures are not scenario results. If one occurs before model output or a tool
call, fix it and retry the turn. Otherwise restart the scenario from a fresh run.

```bash
# Setup opening
tests/scripts/run-claude-turn.sh "$RUN_ROOT" "$LABEL" "$PROMPT" --setup

# Setup follow-up
tests/scripts/run-claude-turn.sh \
  "$RUN_ROOT" "$LABEL" "$PROMPT" --setup --resume "$SESSION_ID"

# Processing and questions
tests/scripts/run-claude-turn.sh "$RUN_ROOT" "$LABEL" "$PROMPT"
```

The script exports `.env`, isolates Claude config, runs from the vault, writes both logs,
and refuses to overwrite them.
