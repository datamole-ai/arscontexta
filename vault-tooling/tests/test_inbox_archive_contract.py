from __future__ import annotations

import json
from pathlib import Path

from conftest import write_note
from typer.testing import CliRunner

from vault.cli import app

runner = CliRunner()


def invoke_json(args: list[str], *, input: str | None = None) -> tuple[int, dict]:
    result = runner.invoke(app, args, input=input)
    assert result.stdout, result.stderr
    return result.exit_code, json.loads(result.stdout)


def run_json(args: list[str], *, input: str | None = None) -> dict:
    exit_code, payload = invoke_json(args, input=input)
    assert exit_code == 0, payload
    return payload


def test_seed_moves_inbox_file_to_archive(vault: Path) -> None:
    source = vault / "inbox" / "Source File.md"
    source.write_text("# Source\n", encoding="utf-8")

    result = run_json(["seed", "--source", "inbox/Source File.md"])

    assert result["source"].startswith("archive/")
    assert "commit_paths" not in result, "seed must not name the gitignored inbox path"
    assert (vault / result["source"]).read_text(encoding="utf-8") == "# Source\n"
    assert not source.exists()


def test_seed_rejects_non_inbox_source(vault: Path) -> None:
    source = vault / "Root Source.md"
    source.write_text("# Root\n", encoding="utf-8")

    exit_code, failure = invoke_json(["seed", "--source", "Root Source.md"])

    assert exit_code == 1
    assert failure["command"] == "seed"
    assert "source is outside inbox" in failure["errors"][0]
    assert source.exists()


def test_seed_reruns_after_inbox_file_was_moved(vault: Path) -> None:
    source = vault / "inbox" / "Source File.md"
    source.write_text("# Source\n", encoding="utf-8")
    first = run_json(["seed", "--source", "inbox/Source File.md"])

    second = run_json(["seed", "--source", "inbox/Source File.md"])

    assert second == first
    assert not source.exists()


def test_seed_rejects_existing_archive_when_inbox_file_exists(vault: Path) -> None:
    source = vault / "inbox" / "Source File.md"
    source.write_text("# Source\n", encoding="utf-8")
    run_json(["seed", "--source", "inbox/Source File.md"])
    source.write_text("# Different\n", encoding="utf-8")

    exit_code, failure = invoke_json(["seed", "--source", "inbox/Source File.md"])

    assert exit_code == 1
    assert failure["command"] == "seed"
    assert failure["batch"] == "source-file"
    assert "archive source already exists" in failure["errors"][0]


def test_validate_artifacts_drops_legacy_commit_paths(vault: Path) -> None:
    write_note(vault / "notes" / "good.md", "Good")
    state = {
        "batch": "batch",
        "source": "archive/2026-05-22-batch.md",
        "artifacts": [{"kind": "note", "path": "notes/good.md"}],
        "commit_paths": ["inbox/batch.md"],
    }

    result = run_json(["validate", "--artifacts"], input=json.dumps(state))

    assert result["ok"] is True
    assert "commit_paths" not in result, "artifacts is the only channel into the commit"
