from __future__ import annotations

import json
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass
class TurnResult:
    text: str
    session_id: str
    is_error: bool
    raw: dict


@dataclass
class SetupResult:
    vault: Path
    turns: list[TurnResult]
    vocabulary: dict


def claude_turn(
    prompt: str,
    cwd: Path,
    env: dict,
    resume: str | None = None,
    plugin_dir: Path | None = None,
    timeout_s: int = 1500,
    log_path: Path | None = None,
) -> TurnResult:
    cmd = ["claude", "-p", prompt, "--output-format", "json", "--dangerously-skip-permissions"]
    if plugin_dir is not None:
        cmd += ["--plugin-dir", str(plugin_dir)]
    if resume is not None:
        cmd += ["--resume", resume]
    model = env.get("E2E_MODEL") or os.environ.get("E2E_MODEL") or "claude-opus-4-8"
    effort = env.get("E2E_EFFORT") or os.environ.get("E2E_EFFORT") or "low"
    cmd += ["--model", model, "--effort", effort]

    result = subprocess.run(
        cmd,
        cwd=str(cwd),
        env=env,
        capture_output=True,
        text=True,
        timeout=timeout_s,
    )

    raw_stdout = result.stdout.strip()
    if log_path is not None:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_path.write_text(raw_stdout, encoding="utf-8")

    try:
        payload = json.loads(raw_stdout) if raw_stdout else {}
    except json.JSONDecodeError:
        payload = {"raw_output": raw_stdout, "stderr": result.stderr}

    text = payload.get("result") or ""
    session_id = payload.get("session_id") or ""
    is_error = result.returncode != 0 or bool(payload.get("is_error"))

    return TurnResult(text=text, session_id=session_id, is_error=is_error, raw=payload)


def setup_complete(vault: Path) -> bool:
    if not (vault / ".second-brain").exists():
        return False
    if not (vault / "ops" / "derivation-manifest.yaml").exists():
        return False
    result = subprocess.run(
        ["git", "-C", str(vault), "rev-parse", "HEAD"],
        capture_output=True,
    )
    return result.returncode == 0


def run_setup(
    scenario,
    vault: Path,
    env: dict,
    plugin_dir: Path,
    run_dir: Path,
) -> SetupResult:
    turns_dir = run_dir / "turns"
    turns_dir.mkdir(parents=True, exist_ok=True)
    turns: list[TurnResult] = []

    turn_idx = 0
    log_path = turns_dir / f"{turn_idx:02d}.json"
    turn = claude_turn(
        f"/second-brain:setup {scenario.opening}",
        cwd=vault,
        env=env,
        plugin_dir=plugin_dir,
        log_path=log_path,
    )
    turns.append(turn)

    while not setup_complete(vault):
        if len(turns) >= scenario.max_turns:
            raise AssertionError(
                f"setup_complete still False after {len(turns)} turns "
                f"(max_turns={scenario.max_turns}). Last turn:\n{turns[-1].text}"
            )
        turn_idx = len(turns)
        log_path = turns_dir / f"{turn_idx:02d}.json"
        turn = claude_turn(
            scenario.continuation,
            cwd=vault,
            env=env,
            resume=turns[-1].session_id,
            plugin_dir=plugin_dir,
            log_path=log_path,
        )
        turns.append(turn)

    manifest_path = vault / "ops" / "derivation-manifest.yaml"
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    vocabulary = manifest.get("vocabulary", {})

    return SetupResult(vault=vault, turns=turns, vocabulary=vocabulary)


def run_process(
    vault: Path,
    rel_source: str,
    mode: str,
    env: dict,
    run_dir: Path,
) -> TurnResult:
    turns_dir = run_dir / "turns"
    existing = sorted(turns_dir.glob("*.json")) if turns_dir.exists() else []
    next_idx = len(existing)
    log_path = turns_dir / f"{next_idx:02d}.json"

    return claude_turn(
        f"/process {rel_source} --{mode}",
        cwd=vault,
        env=env,
        log_path=log_path,
    )
