---
name: run-scenario
description: Run a real-tool scenario, delegate its evaluation, and diagnose failures.
---
Follow `tests/README.md` to run the requested scenario, delegating its final evaluation through the agent tool with `fork_turns: "none"`, `model: "gpt-5.6-sol"`, and `reasoning_effort: "medium"`. Require the evaluator to use these settings for every individual evaluator agent. It must only run the evaluation and return the report verbatim, without investigating failures or suggesting fixes. The main agent must process the report, investigate every failure, and suggest fixes.
