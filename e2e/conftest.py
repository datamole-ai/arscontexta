from __future__ import annotations

import datetime
import os
import re
import shutil
from dataclasses import dataclass
from pathlib import Path

import pytest
import yaml

from driver import SetupResult, run_setup

REPO_ROOT = Path(__file__).resolve().parent.parent
SHIMS = Path(__file__).parent / "shims"


@dataclass(frozen=True)
class Scenario:
    name: str
    opening: str
    continuation: str
    max_turns: int
    expect_vocabulary: dict
    expect_content_type_includes: list
    process_runs: list


def _slug(value: str) -> str:
    # must mirror vault-tooling/src/vault/markdown.py:slug — batches are asserted by name
    lowered = value.strip().lower()
    lowered = re.sub(r"\.md$", "", lowered)
    lowered = re.sub(r"[^a-z0-9]+", "-", lowered)
    return lowered.strip("-")


def _default_process_runs(scenario_dir: Path) -> list[dict]:
    return [
        {
            "fixture": f"inbox/{p.name}",
            "mode": "structure",
            "expect": {"batch": _slug(p.name), "min_new_notes": 1},
        }
        for p in sorted((scenario_dir / "inbox").glob("*.md"))
    ]


def discover_scenarios(scenarios_dir: Path | None = None) -> list[Scenario]:
    if scenarios_dir is None:
        scenarios_dir = Path(__file__).parent / "scenarios"
    result = []
    for yaml_path in sorted(scenarios_dir.glob("*/scenario.yaml")):
        raw = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
        process_runs = raw.get("process_runs")
        if process_runs is None:
            process_runs = _default_process_runs(yaml_path.parent)
        result.append(
            Scenario(
                name=raw["name"],
                opening=raw["setup"]["opening"],
                continuation=raw["setup"]["continuation"],
                max_turns=raw["setup"]["max_turns"],
                expect_vocabulary=raw["expect"].get("vocabulary", {}),
                expect_content_type_includes=raw["expect"].get("content_type_includes", []),
                process_runs=process_runs,
            )
        )
    return result


def shimmed_env(run_dir: Path) -> dict:
    env = dict(os.environ)
    env["PATH"] = f"{SHIMS}:{env.get('PATH', '')}"
    env["E2E_SHIM_LOG"] = str(run_dir / "shim.log")
    env["GIT_AUTHOR_NAME"] = "e2e"
    env["GIT_AUTHOR_EMAIL"] = "e2e@local"
    env["GIT_COMMITTER_NAME"] = "e2e"
    env["GIT_COMMITTER_EMAIL"] = "e2e@local"
    return env


def _build_setup_result_from_existing(vault: Path) -> SetupResult:
    manifest_path = vault / "ops" / "derivation-manifest.yaml"
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    vocabulary = manifest.get("vocabulary", {})
    return SetupResult(vault=vault, turns=[], vocabulary=vocabulary)


@pytest.fixture(
    scope="module",
    params=[s.name for s in discover_scenarios()],
)
def generated_vault(request: pytest.FixtureRequest):
    scenario_name = request.param
    scenario = next(s for s in discover_scenarios() if s.name == scenario_name)

    existing_vault_env = os.environ.get("E2E_VAULT")
    if existing_vault_env:
        vault = Path(existing_vault_env)
        setup_result = _build_setup_result_from_existing(vault)
        run_dir = vault.parent
        env = shimmed_env(run_dir)
        yield scenario, setup_result, run_dir, env
        return

    timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = Path(__file__).parent / ".runs" / f"{timestamp}-{scenario_name}"
    vault = run_dir / "vault"
    vault.mkdir(parents=True)
    (run_dir / "turns").mkdir(parents=True)

    env = shimmed_env(run_dir)

    setup_result = run_setup(
        scenario=scenario,
        vault=vault,
        env=env,
        plugin_dir=REPO_ROOT,
        run_dir=run_dir,
    )

    yield scenario, setup_result, run_dir, env
