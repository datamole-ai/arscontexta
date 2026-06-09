from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

from conftest import SHIMS, Scenario, _slug, discover_scenarios
from driver import setup_complete

E2E_DIR = Path(__file__).parent


def run_shim(name: str, args: list[str], shim_log: Path) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    env["PATH"] = f"{SHIMS}:{env.get('PATH', '')}"
    env["E2E_SHIM_LOG"] = str(shim_log)
    return subprocess.run(
        [name, *args],
        capture_output=True,
        text=True,
        env=env,
    )


def test_qmd_version(tmp_path):
    log = tmp_path / "shim.log"
    result = run_shim("qmd", ["-v"], log)
    assert result.returncode == 0
    assert "qmd 2.5.0" in result.stdout
    assert "qmd -v" in log.read_text()


def test_qmd_collections_list(tmp_path):
    log = tmp_path / "shim.log"
    result = run_shim("qmd", ["collections", "list"], log)
    assert result.returncode == 0
    assert "[]" in result.stdout
    assert "qmd collections list" in log.read_text()


def test_pgrep_obsidian(tmp_path):
    log = tmp_path / "shim.log"
    result = run_shim("pgrep", ["-x", "Obsidian"], log)
    assert result.returncode == 0
    assert "99999" in result.stdout
    assert "pgrep -x Obsidian" in log.read_text()


def test_obsidian_unresolved(tmp_path):
    log = tmp_path / "shim.log"
    result = run_shim("obsidian", ["unresolved"], log)
    assert result.returncode == 0
    assert result.stdout == ""
    assert "obsidian unresolved" in log.read_text()


def test_shim_log_captures_all_calls(tmp_path):
    log = tmp_path / "shim.log"
    run_shim("qmd", ["-v"], log)
    run_shim("qmd", ["collections", "list"], log)
    run_shim("obsidian", ["unresolved"], log)
    lines = log.read_text().splitlines()
    assert any("qmd -v" in l for l in lines)
    assert any("qmd collections list" in l for l in lines)
    assert any("obsidian unresolved" in l for l in lines)


def test_setup_complete_empty_dir(tmp_path):
    assert setup_complete(tmp_path) is False


def test_setup_complete_missing_manifest(tmp_path):
    (tmp_path / ".second-brain").touch()
    assert setup_complete(tmp_path) is False


def test_setup_complete_no_git(tmp_path):
    (tmp_path / ".second-brain").touch()
    (tmp_path / "ops").mkdir()
    (tmp_path / "ops" / "derivation-manifest.yaml").write_text("vocabulary: {}", encoding="utf-8")
    assert setup_complete(tmp_path) is False


def test_setup_complete_all_conditions_met(tmp_path):
    (tmp_path / ".second-brain").touch()
    (tmp_path / "ops").mkdir()
    (tmp_path / "ops" / "derivation-manifest.yaml").write_text("vocabulary: {}", encoding="utf-8")
    subprocess.run(["git", "init"], cwd=str(tmp_path), capture_output=True, check=True)
    subprocess.run(
        ["git", "commit", "--allow-empty", "-m", "init"],
        cwd=str(tmp_path),
        capture_output=True,
        check=True,
        env={**os.environ, "GIT_AUTHOR_NAME": "e2e", "GIT_AUTHOR_EMAIL": "e2e@local",
             "GIT_COMMITTER_NAME": "e2e", "GIT_COMMITTER_EMAIL": "e2e@local"},
    )
    assert setup_complete(tmp_path) is True


def test_slug_matches_vault_tooling():
    assert _slug("My Source File.md") == "my-source-file"
    assert _slug("Meeting Notes - Lely 2026.md") == "meeting-notes-lely-2026"
    assert _slug("paper-attention.md") == "paper-attention"


def test_process_runs_autodiscovered_from_inbox(tmp_path):
    scenario_dir = tmp_path / "sample"
    (scenario_dir / "inbox").mkdir(parents=True)
    (scenario_dir / "inbox" / "Lely Meeting.md").write_text("notes", encoding="utf-8")
    (scenario_dir / "scenario.yaml").write_text(
        "name: sample\n"
        "setup:\n"
        "  opening: hi\n"
        "  continuation: ok\n"
        "  max_turns: 3\n"
        "expect:\n"
        "  content_type_includes: [moc]\n",
        encoding="utf-8",
    )
    scenarios = discover_scenarios(tmp_path)
    assert len(scenarios) == 1
    runs = scenarios[0].process_runs
    assert runs == [
        {
            "fixture": "inbox/Lely Meeting.md",
            "mode": "structure",
            "expect": {"batch": "lely-meeting", "min_new_notes": 1},
        }
    ]


def test_scenario_discovery():
    scenarios = discover_scenarios()
    researcher = next((s for s in scenarios if s.name == "researcher"), None)
    assert researcher is not None, "researcher scenario not discovered"
    assert isinstance(researcher, Scenario)
    assert "machine learning researcher" in researcher.opening
    assert researcher.continuation == "Whatever you think is best - yes, create it exactly as proposed, no adjustments."
    assert researcher.max_turns == 6
    assert researcher.expect_vocabulary == {
        "note_collection": "claims",
        "inbox": "reading-pile",
        "archive": "processed",
    }
    assert "moc" in researcher.expect_content_type_includes
    assert "claim" in researcher.expect_content_type_includes
    assert len(researcher.process_runs) >= 1
    run = researcher.process_runs[0]
    assert run["fixture"] == "inbox/paper-attention.md"
    assert run["mode"] == "structure"
    assert run["expect"]["batch"] == "paper-attention"
    assert run["expect"]["min_new_notes"] >= 1
