from __future__ import annotations

import json
import re
from pathlib import Path

from conftest import write_note, write_tag_registry
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


def test_short_help_alias_is_available() -> None:
    result = runner.invoke(app, ["-h"])

    assert result.exit_code == 0
    assert "Usage: root [OPTIONS] COMMAND [ARGS]..." in result.stdout


def test_root_lists_only_intended_runtime_commands(vault: Path) -> None:
    result = run_json([])

    assert result == {"ok": True, "commands": ["capture", "seed", "validate"]}


def test_seed_archives_source_and_emits_lean_state(vault: Path) -> None:
    source = vault / "inbox" / "Source File.md"
    source.write_text("# Source\n", encoding="utf-8")

    result = run_json(["seed", "--source", "inbox/Source File.md"])

    assert result["ok"] is True
    assert result["command"] == "seed"
    assert result["batch"] == "source-file"
    assert set(result) == {"ok", "command", "batch", "source"}
    assert result["source"].startswith("archive/")
    assert result["source"].endswith("-source-file.md")
    assert re.fullmatch(r"archive/\d{4}-\d{2}-\d{2}-source-file\.md", result["source"])
    assert (vault / result["source"]).read_text(encoding="utf-8") == "# Source\n"
    assert not (vault / "archive" / "source-file").exists()
    assert not source.exists()
    assert not (vault / "ops" / "queue" / "queue.json").exists()


def test_validate_path_success_and_handled_failure(vault: Path) -> None:
    write_note(vault / "notes" / "good.md", "Good")
    (vault / "notes" / "bad.md").write_text(
        "---\n"
        "content_type: draft\n"
        "granularity: distilled\n"
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
    assert "tags must be a list" in failure["errors"]


def test_validate_rejects_obsidian_incompatible_properties(vault: Path) -> None:
    (vault / "notes" / "bad-tags.md").write_text(
        "---\n"
        "content_type: note\n"
        "granularity: distilled\n"
        "description: Bad tag examples\n"
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
    errors = failure["errors"]
    assert "deprecated Obsidian property: tag; use tags" in errors
    assert "unknown property: tag; use tags for conversation-derived attributes" in errors
    assert "unknown property: confidence; use tags for conversation-derived attributes" in errors
    assert "tag must omit leading #: #prefixed" in failure["errors"]
    assert "tag must not contain spaces: has space" in failure["errors"]
    assert "tag must contain at least one non-numeric character: 1984" in failure["errors"]


def test_validate_accepts_obsidian_default_properties(vault: Path) -> None:
    (vault / "notes" / "with-obsidian-defaults.md").write_text(
        "---\n"
        "content_type: note\n"
        "granularity: distilled\n"
        "description: Obsidian defaults example\n"
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


def test_validate_accepts_moc_content_type(vault: Path) -> None:
    (vault / "notes" / "index.md").write_text(
        "---\n"
        "content_type: moc\n"
        "granularity: distilled\n"
        "description: Entry point for the note collection\n"
        "tags: []\n"
        "---\n"
        "# index\n",
        encoding="utf-8",
    )

    assert run_json(["validate", "--path", "notes/index.md"]) == {
        "ok": True,
        "command": "validate",
        "path": "notes/index.md",
    }


def test_validate_enforces_tag_registry_only_when_tags_file_exists(
    vault: Path,
) -> None:
    write_note(vault / "notes" / "unchecked-tag.md", "Unchecked Tag", tags=["vendor/lely"])

    assert run_json(["validate", "--path", "notes/unchecked-tag.md"]) == {
        "ok": True,
        "command": "validate",
        "path": "notes/unchecked-tag.md",
    }

    write_tag_registry(
        vault,
        [
            {"tag": "mso", "meaning": "MSO customer work"},
            {"tag": "project/*", "meaning": "Project family"},
        ],
    )
    write_note(vault / "notes" / "family-tag.md", "Family Tag", tags=["project/mso"])
    write_note(vault / "notes" / "exact-tag.md", "Exact Tag", tags=["mso"])

    assert run_json(["validate", "--path", "notes/family-tag.md"]) == {
        "ok": True,
        "command": "validate",
        "path": "notes/family-tag.md",
    }
    assert run_json(["validate", "--path", "notes/exact-tag.md"]) == {
        "ok": True,
        "command": "validate",
        "path": "notes/exact-tag.md",
    }
    exit_code, failure = invoke_json(["validate", "--path", "notes/unchecked-tag.md"])

    assert exit_code == 1
    assert (
        "tag not in ops/tags.yaml: vendor/lely; "
        "use a registered tag or append an entry with tag and meaning"
    ) in failure["errors"]


def test_validate_tag_registry_family_and_exact_boundaries(vault: Path) -> None:
    write_tag_registry(
        vault,
        [
            {"tag": "pattern", "meaning": "A cross-cutting insight"},
            {"tag": "customer/*", "meaning": "The client account"},
        ],
    )
    write_note(vault / "notes" / "deep-child.md", "Deep Child", tags=["customer/lely/mio"])
    write_note(vault / "notes" / "bare-prefix.md", "Bare Prefix", tags=["customer"])
    write_note(vault / "notes" / "exact-child.md", "Exact Child", tags=["pattern/foo"])

    assert run_json(["validate", "--path", "notes/deep-child.md"]) == {
        "ok": True,
        "command": "validate",
        "path": "notes/deep-child.md",
    }
    rejected = [("notes/bare-prefix.md", "customer"), ("notes/exact-child.md", "pattern/foo")]
    for note, tag in rejected:
        exit_code, failure = invoke_json(["validate", "--path", note])

        assert exit_code == 1
        assert (
            f"tag not in ops/tags.yaml: {tag}; "
            "use a registered tag or append an entry with tag and meaning"
        ) in failure["errors"]


def test_validate_empty_tag_registry_rejects_every_tag(vault: Path) -> None:
    write_tag_registry(vault, [])
    write_note(vault / "notes" / "untagged.md", "Untagged")
    write_note(vault / "notes" / "tagged.md", "Tagged", tags=["pattern"])

    assert run_json(["validate", "--path", "notes/untagged.md"]) == {
        "ok": True,
        "command": "validate",
        "path": "notes/untagged.md",
    }
    exit_code, failure = invoke_json(["validate", "--path", "notes/tagged.md"])

    assert exit_code == 1
    assert (
        "tag not in ops/tags.yaml: pattern; "
        "use a registered tag or append an entry with tag and meaning"
    ) in failure["errors"]


def test_validate_rejects_malformed_tag_registry(vault: Path) -> None:
    write_note(vault / "notes" / "good.md", "Good")
    malformed = [
        "tags:\n  - tag: pattern\n",
        "tags:\n  - tag: pattern\n    meaning: One\n  - tag: pattern\n    meaning: Two\n",
        "tags: pattern\n",
        "tags:\n  - tag: '*'\n    meaning: Anything\n",
        "tags:\n  - tag: 'customer/*/extra'\n    meaning: Misplaced star\n",
        "tags:\n  - tag: '/*'\n    meaning: Empty prefix\n",
    ]

    for content in malformed:
        (vault / "ops" / "tags.yaml").write_text(content, encoding="utf-8")

        exit_code, payload = invoke_json(["validate", "--path", "notes/good.md"])

        assert exit_code == 1, content
        assert payload["ok"] is False
        assert any("ops/tags.yaml" in error for error in payload["errors"]), payload

        exit_code, payload = invoke_json(["validate", "--all"])

        assert exit_code == 1, content
        assert any("ops/tags.yaml" in error for error in payload["errors"]), payload


def test_validate_rejects_nested_note_properties(vault: Path) -> None:
    (vault / "notes" / "nested.md").write_text(
        "---\n"
        "content_type: note\n"
        "granularity: distilled\n"
        "description: Nested property example\n"
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
        "content_type: note\n"
        "content_type: moc\n"
        "granularity: distilled\n"
        "description: Duplicate property example\n"
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
        "source": "archive/2026-05-22-batch.md",
        "artifacts": [{"kind": "note", "path": "notes/good.md"}],
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
        "source": "archive/2026-05-22-batch.md",
        "artifacts": [{"kind": "note", "path": "notes/good.md"}],
    }


def test_invalid_validate_mode_exits_2(vault: Path) -> None:
    result = runner.invoke(app, ["validate"])

    assert result.exit_code == 2


def test_validate_missing_vault_returns_json(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)

    exit_code, payload = invoke_json(["validate", "--all"])

    assert exit_code == 1
    assert payload == {
        "ok": False,
        "errors": [".second-brain marker not found; run from a generated vault"],
    }
