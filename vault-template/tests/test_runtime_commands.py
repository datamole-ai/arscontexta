from __future__ import annotations

import json
from pathlib import Path

from conftest import write_note
from typer.testing import CliRunner

from arscontexta_vault.cli import app

runner = CliRunner()


def invoke_json(args: list[str], *, input: str | None = None) -> tuple[int, dict]:
    result = runner.invoke(app, args, input=input)
    assert result.stdout, result.stderr
    return result.exit_code, json.loads(result.stdout)


def run_json(args: list[str], *, input: str | None = None) -> dict:
    exit_code, payload = invoke_json(args, input=input)
    assert exit_code == 0, payload
    return payload


def test_root_lists_only_intended_runtime_commands(vault: Path) -> None:
    result = run_json([])

    assert result == {"ok": True, "commands": ["seed", "validate"]}


def test_seed_archives_source_and_emits_lean_state(vault: Path) -> None:
    source = vault / "inbox" / "Source File.md"
    source.write_text("# Source\n", encoding="utf-8")

    result = run_json(["seed", "--source", "inbox/Source File.md", "--mode", "structure"])

    assert result["ok"] is True
    assert result["command"] == "seed"
    assert result["batch"] == "source-file"
    assert set(result) == {"ok", "command", "batch", "source"}
    assert result["source"].startswith("archive/")
    assert result["source"].endswith("/source.md")
    assert (vault / result["source"]).read_text(encoding="utf-8") == "# Source\n"
    assert source.exists()
    assert not (vault / "ops" / "queue" / "queue.json").exists()


def test_validate_path_success_and_handled_failure(vault: Path) -> None:
    write_note(vault / "notes" / "good.md", "Good")
    (vault / "notes" / "bad.md").write_text(
        "---\n"
        "content_type: draft\n"
        "granularity: structure\n"
        "created_at: bad\n"
        "tags: nope\n"
        "---\n"
        "# Bad\n",
        encoding="utf-8",
    )

    assert run_json(["validate", "--path", "notes/good.md"]) == {
        "ok": True,
        "command": "validate",
        "path": "notes/good.md",
    }

    exit_code, failure = invoke_json(["validate", "--path", "notes/bad.md"])

    assert exit_code == 1
    assert failure["ok"] is False
    assert failure["command"] == "validate"
    assert failure["path"] == "notes/bad.md"
    assert "missing required field: description" in failure["errors"]
    assert "invalid content_type: draft" in failure["errors"]
    assert "created_at must use YYYY-MM-DD" in failure["errors"]
    assert "tags must be a list" in failure["errors"]


def test_validate_all_and_artifacts(vault: Path) -> None:
    write_note(vault / "notes" / "good.md", "Good")
    state = {
        "batch": "batch",
        "source": "archive/batch/source.md",
        "artifacts": [{"kind": "note", "path": "notes/good.md"}],
        "commit_paths": ["notes/topic-map.md"],
    }

    assert run_json(["validate", "--all"]) == {
        "ok": True,
        "command": "validate",
        "checked": 1,
        "failures": [],
    }
    assert run_json(["validate", "--artifacts"], input=json.dumps(state)) == {
        "ok": True,
        "command": "validate",
        "batch": "batch",
        "source": "archive/batch/source.md",
        "artifacts": [{"kind": "note", "path": "notes/good.md"}],
        "commit_paths": ["notes/topic-map.md"],
    }


def test_invalid_validate_mode_exits_2(vault: Path) -> None:
    result = runner.invoke(app, ["validate"])

    assert result.exit_code == 2
