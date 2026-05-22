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


def test_validate_rejects_obsidian_incompatible_properties(vault: Path) -> None:
    (vault / "notes" / "bad-tags.md").write_text(
        "---\n"
        "content_type: claim\n"
        "granularity: structure\n"
        "description: Bad tag examples\n"
        "created_at: 2026-05-20\n"
        "tag: legacy\n"
        "tags:\n"
        "  - '#prefixed'\n"
        "  - has space\n"
        "  - '1984'\n"
        "confidence: high\n"
        "---\n"
        "# Bad Tags\n",
        encoding="utf-8",
    )

    exit_code, failure = invoke_json(["validate", "--path", "notes/bad-tags.md"])

    assert exit_code == 1
    assert "deprecated Obsidian property: tag; use tags" in failure["errors"]
    assert "unknown property: tag; use tags for conversation-derived attributes" in failure["errors"]
    assert "unknown property: confidence; use tags for conversation-derived attributes" in failure[
        "errors"
    ]
    assert "tag must omit leading #: #prefixed" in failure["errors"]
    assert "tag must not contain spaces: has space" in failure["errors"]
    assert "tag must contain at least one non-numeric character: 1984" in failure["errors"]


def test_validate_accepts_obsidian_default_properties(vault: Path) -> None:
    (vault / "notes" / "with-obsidian-defaults.md").write_text(
        "---\n"
        "content_type: claim\n"
        "granularity: structure\n"
        "description: Obsidian defaults example\n"
        "created_at: 2026-05-20\n"
        "tags:\n"
        "  - status/draft\n"
        "aliases:\n"
        "  - Alternate name\n"
        "cssclasses:\n"
        "  - wide-page\n"
        "---\n"
        "# With Obsidian Defaults\n",
        encoding="utf-8",
    )

    assert run_json(["validate", "--path", "notes/with-obsidian-defaults.md"]) == {
        "ok": True,
        "command": "validate",
        "path": "notes/with-obsidian-defaults.md",
    }


def test_validate_rejects_nested_note_properties(vault: Path) -> None:
    (vault / "notes" / "nested.md").write_text(
        "---\n"
        "content_type: claim\n"
        "granularity: structure\n"
        "description: Nested property example\n"
        "created_at: 2026-05-20\n"
        "tags: []\n"
        "aliases:\n"
        "  nested: value\n"
        "---\n"
        "# Nested\n",
        encoding="utf-8",
    )

    exit_code, failure = invoke_json(["validate", "--path", "notes/nested.md"])

    assert exit_code == 1
    assert "nested properties are not Obsidian-compatible: aliases" in failure["errors"]
    assert "aliases must be a list of strings" in failure["errors"]


def test_validate_rejects_duplicate_yaml_properties(vault: Path) -> None:
    (vault / "notes" / "duplicate.md").write_text(
        "---\n"
        "content_type: claim\n"
        "content_type: source\n"
        "granularity: structure\n"
        "description: Duplicate property example\n"
        "created_at: 2026-05-20\n"
        "tags: []\n"
        "---\n"
        "# Duplicate\n",
        encoding="utf-8",
    )

    exit_code, failure = invoke_json(["validate", "--path", "notes/duplicate.md"])

    assert exit_code == 1
    assert any("duplicate property: content_type" in error for error in failure["errors"])


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
