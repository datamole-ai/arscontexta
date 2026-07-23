from __future__ import annotations

import json
from pathlib import Path

from conftest import write_note
from typer.testing import CliRunner

from vault.cli import app
from vault.validation.markdown import verbatim_payload

runner = CliRunner()

SOURCE_REL = "archive/2026-06-01-src.md"


def invoke_json(args: list[str], *, input: str | None = None) -> tuple[int, dict]:
    result = runner.invoke(app, args, input=input)
    assert result.stdout, result.stderr
    return result.exit_code, json.loads(result.stdout)


def run_json(args: list[str], *, input: str | None = None) -> dict:
    exit_code, payload = invoke_json(args, input=input)
    assert exit_code == 0, payload
    return payload


def write_archived_source(vault: Path, text: str) -> Path:
    path = vault / SOURCE_REL
    path.write_text(text, encoding="utf-8")
    return path


def capture_args(**overrides: str) -> list[str]:
    options = {
        "--source": SOURCE_REL,
        "--title": "My Title",
        "--description": "Captured source",
    }
    options.update(overrides)
    return ["capture", *(part for item in options.items() for part in item)]


def note_body(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    return text[text.find("\n---\n", 4) + len("\n---\n") :]


def test_capture_writes_verbatim_note_and_result(vault: Path) -> None:
    write_archived_source(vault, "# Source\n\nBody text.\n")

    result = run_json(capture_args())

    assert result == {
        "ok": True,
        "command": "capture",
        "source": SOURCE_REL,
        "note": "notes/my-title.md",
    }
    assert (vault / "notes" / "my-title.md").read_text(encoding="utf-8") == (
        "---\n"
        "content_type: note\n"
        "granularity: verbatim\n"
        "description: Captured source\n"
        "tags: []\n"
        "---\n"
        "\n"
        "# My Title\n"
        "\n"
        "```text\n"
        "# Source\n"
        "\n"
        "Body text.\n"
        "```\n"
        "\n"
        "---\n"
        "\n"
        f"Source: {SOURCE_REL}\n"
    )


def test_capture_wraps_fenced_source_with_longer_fence(vault: Path) -> None:
    source_text = 'Intro\n\n```python\nprint("hi")\n```\n'
    write_archived_source(vault, source_text)

    result = run_json(capture_args())

    note_path = vault / result["note"]
    assert f"````text\n{source_text}````\n" in note_path.read_text(encoding="utf-8")
    assert verbatim_payload(note_body(note_path)) == source_text


def test_capture_appends_newline_when_source_lacks_one(vault: Path) -> None:
    write_archived_source(vault, "no trailing newline")

    result = run_json([*capture_args(), "--tag", "draft"])

    note_text = (vault / result["note"]).read_text(encoding="utf-8")
    assert note_text.endswith(f"```text\nno trailing newline\n```\n\n---\n\nSource: {SOURCE_REL}\n")
    assert "tags:\n  - draft\n" in note_text


def test_capture_never_overwrites_existing_note(vault: Path) -> None:
    write_archived_source(vault, "# Source\n")
    (vault / "notes" / "my-title.md").write_text("existing\n", encoding="utf-8")

    exit_code, failure = invoke_json(capture_args())

    assert exit_code == 1
    assert failure["command"] == "capture"
    assert failure["errors"] == ["note already exists: notes/my-title.md"]
    assert "retryable" not in failure
    assert (vault / "notes" / "my-title.md").read_text(encoding="utf-8") == "existing\n"


def test_capture_rejects_source_outside_archive(vault: Path) -> None:
    (vault / "inbox" / "src.md").write_text("# Source\n", encoding="utf-8")

    exit_code, failure = invoke_json(capture_args(**{"--source": "inbox/src.md"}))

    assert exit_code == 1
    assert failure["command"] == "capture"
    assert "source is outside archive: inbox/src.md" in failure["errors"][0]
    assert "retryable" not in failure


def test_capture_rejects_long_description_and_leaves_no_file(vault: Path) -> None:
    write_archived_source(vault, "# Source\n")

    exit_code, failure = invoke_json(capture_args(**{"--description": "x" * 201}))

    assert exit_code == 1
    assert failure["command"] == "capture"
    assert failure["errors"] == ["description exceeds max length: 200"]
    assert failure["retryable"] is True
    assert not (vault / "notes" / "my-title.md").exists()


def test_validate_artifacts_checks_verbatim_bytes(vault: Path) -> None:
    write_archived_source(vault, "# Source\n\nBody text.\n")
    result = run_json(capture_args())
    state = json.dumps(
        {
            "batch": "src",
            "source": result["source"],
            "artifacts": [{"kind": "note", "path": result["note"]}],
        }
    )

    assert run_json(["validate", "--artifacts"], input=state)["ok"] is True

    note_path = vault / result["note"]
    note_path.write_text(
        note_path.read_text(encoding="utf-8").replace("Body text.", "Body texx."),
        encoding="utf-8",
    )
    exit_code, failure = invoke_json(["validate", "--artifacts"], input=state)

    assert exit_code == 1
    assert failure["failures"] == [
        {
            "path": result["note"],
            "errors": [f"verbatim note differs from archived source: {SOURCE_REL}"],
        }
    ]


def test_validate_artifacts_checks_enrichments_against_recorded_source(vault: Path) -> None:
    write_archived_source(vault, "# Earlier batch source\n")
    earlier = run_json(capture_args())

    current_source = "archive/2026-06-02-next.md"
    (vault / current_source).write_text("# Next batch source\n", encoding="utf-8")
    write_note(vault / "notes" / "next-note.md", "Next Note")
    state = json.dumps(
        {
            "batch": "next",
            "source": current_source,
            "artifacts": [
                {"kind": "note", "path": "notes/next-note.md"},
                {"kind": "enrichment", "path": earlier["note"]},
            ],
        }
    )

    # Intact: the enrichment's payload matches its own recorded source, so the
    # differing batch source is irrelevant.
    assert run_json(["validate", "--artifacts"], input=state)["ok"] is True

    note_path = vault / earlier["note"]
    note_path.write_text(
        note_path.read_text(encoding="utf-8").replace("Earlier batch", "Tampered batch"),
        encoding="utf-8",
    )
    exit_code, failure = invoke_json(["validate", "--artifacts"], input=state)

    assert exit_code == 1
    assert failure["ok"] is False
    assert failure["failures"] == [
        {
            "path": earlier["note"],
            "errors": [f"verbatim note differs from archived source: {SOURCE_REL}"],
        }
    ]


def write_verbatim_note(path: Path, payload: str, footer: str) -> None:
    path.write_text(
        "---\n"
        "content_type: note\n"
        "granularity: verbatim\n"
        "description: Manual verbatim note\n"
        "tags: []\n"
        "---\n"
        "\n"
        "# Manual\n"
        "\n"
        "```text\n"
        f"{payload}"
        "```\n"
        f"{footer}",
        encoding="utf-8",
    )


def test_validate_all_flags_verbatim_note_missing_source_line(vault: Path) -> None:
    write_archived_source(vault, "# Source\n")
    write_verbatim_note(vault / "notes" / "no-source.md", "# Source\n", "")

    exit_code, failure = invoke_json(["validate", "--all"])

    assert exit_code == 1
    assert failure["failures"] == [
        {"path": "notes/no-source.md", "errors": ["verbatim note missing Source line"]}
    ]


def test_validate_all_flags_source_outside_archive(vault: Path) -> None:
    (vault / "inbox" / "src.md").write_text("# Source\n", encoding="utf-8")
    write_verbatim_note(
        vault / "notes" / "escapee.md", "# Source\n", "\n---\n\nSource: inbox/src.md\n"
    )

    exit_code, failure = invoke_json(["validate", "--all"])

    assert exit_code == 1
    assert failure["failures"] == [
        {"path": "notes/escapee.md", "errors": ["source is outside archive: inbox/src.md"]}
    ]


def test_validate_all_flags_missing_source_file(vault: Path) -> None:
    write_verbatim_note(
        vault / "notes" / "orphan.md", "# Source\n", f"\n---\n\nSource: {SOURCE_REL}\n"
    )

    exit_code, failure = invoke_json(["validate", "--all"])

    assert exit_code == 1
    assert failure["failures"] == [
        {
            "path": "notes/orphan.md",
            "errors": [f"source file not found for verbatim check: {SOURCE_REL}"],
        }
    ]


def test_validate_all_catches_corrupted_verbatim_payload(vault: Path) -> None:
    write_archived_source(vault, "# Source\n\nBody text.\n")
    result = run_json(capture_args())

    assert run_json(["validate", "--all"])["ok"] is True

    note_path = vault / result["note"]
    note_path.write_text(
        note_path.read_text(encoding="utf-8").replace("Body text.", "Body texx."),
        encoding="utf-8",
    )
    exit_code, failure = invoke_json(["validate", "--all"])

    assert exit_code == 1
    assert failure["failures"] == [
        {
            "path": result["note"],
            "errors": [f"verbatim note differs from archived source: {SOURCE_REL}"],
        }
    ]


def test_validate_all_flags_verbatim_note_without_fence(vault: Path) -> None:
    (vault / "notes" / "no-fence.md").write_text(
        "---\n"
        "content_type: note\n"
        "granularity: verbatim\n"
        "description: Missing fence\n"
        "tags: []\n"
        "---\n"
        "# No Fence\n",
        encoding="utf-8",
    )

    exit_code, failure = invoke_json(["validate", "--all"])

    assert exit_code == 1
    assert failure["failures"] == [
        {"path": "notes/no-fence.md", "errors": ["verbatim note missing fenced source block"]}
    ]
