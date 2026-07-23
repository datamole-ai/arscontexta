from __future__ import annotations

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from vault.cli import app
from vault.shared.errors import VaultError
from vault.shared.model_validation import validate_model
from vault.validation.models import NoteFrontmatter, TagRegistryFile, VaultSchema

runner = CliRunner()


def invoke_json(args: list[str], *, input: str | None = None) -> tuple[int, dict]:
    result = runner.invoke(app, args, input=input)
    assert result.stdout, result.stderr
    return result.exit_code, json.loads(result.stdout)


def test_capture_reports_all_input_violations_before_writing(vault: Path) -> None:
    source = vault / "archive" / "2026-06-01-source.md"
    source.write_text("# Source\n", encoding="utf-8")

    exit_code, payload = invoke_json(
        [
            "capture",
            "--source",
            "archive/2026-06-01-source.md",
            "--title",
            "   ",
            "--description",
            "x" * 201,
            "--tag",
            "#bad tag",
        ]
    )

    assert exit_code == 1
    assert payload == {
        "ok": False,
        "command": "capture",
        "errors": [
            "title: must be a non-empty string",
            "description exceeds max length: 200",
            "tags[0]: must omit leading #; must not contain spaces",
        ],
        "retryable": True,
    }
    assert not list((vault / "notes").glob("*.md"))
    assert all(
        "pydantic" not in error.lower() and "http" not in error for error in payload["errors"]
    )


@pytest.mark.parametrize(
    ("model", "value", "expected"),
    [
        (VaultSchema, {"required": "content_type"}, "required: must be a list"),
        (TagRegistryFile, {"tags": [{"tag": "topic"}]}, "tags[0].meaning: is required"),
        (NoteFrontmatter, {"tags": "topic"}, "tags: must be a list"),
    ],
)
def test_structural_models_are_strict_and_do_not_leak_pydantic(
    model: type,
    value: object,
    expected: str,
) -> None:
    with pytest.raises(VaultError) as caught:
        validate_model(model, value)

    payload = caught.value.payload()
    errors = payload["errors"]
    assert errors == [expected]
    assert "retryable" not in payload
    assert all("pydantic" not in error.lower() and "http" not in error for error in errors)


@pytest.mark.parametrize(
    ("field", "expected"),
    [
        ("content_type", "content_type: must be a string"),
        ("tags", "tags: must be a list"),
        ("aliases", "aliases: must be a list"),
    ],
)
def test_frontmatter_rejects_explicit_nulls(field: str, expected: str) -> None:
    with pytest.raises(VaultError) as caught:
        validate_model(NoteFrontmatter, {field: None})

    payload = caught.value.payload()
    assert payload["errors"] == [expected]
    assert "retryable" not in payload


def test_validate_names_invalid_schema_field(vault: Path) -> None:
    (vault / "ops" / "schema.yaml").write_text(
        "required: content_type\n",
        encoding="utf-8",
    )

    exit_code, payload = invoke_json(["validate", "--all"])

    assert exit_code == 1
    assert payload["errors"] == ["ops/schema.yaml: required: must be a list"]


def test_validate_artifacts_rejects_bad_envelope_and_aggregates_bad_artifact(
    vault: Path,
) -> None:
    missing_fields_exit, missing_fields = invoke_json(["validate", "--artifacts"], input="{}")

    assert missing_fields_exit == 1
    assert missing_fields["errors"] == [
        "pipeline state.batch: is required",
        "pipeline state.source: is required",
        "pipeline state.artifacts: is required",
    ]

    (vault / "notes" / "good.md").write_text(
        "---\n"
        "content_type: note\n"
        "granularity: distilled\n"
        "description: Good note\n"
        "tags: []\n"
        "---\n"
        "# Good\n",
        encoding="utf-8",
    )
    exit_code, payload = invoke_json(
        ["validate", "--artifacts"],
        input=json.dumps(
            {
                "batch": "batch",
                "source": "archive/2026-06-01-source.md",
                "artifacts": [
                    {"kind": 1, "path": "notes/bad.md"},
                    {"kind": "note", "path": "notes/good.md"},
                ],
            }
        ),
    )

    assert exit_code == 1
    assert payload["failures"] == [
        {"path": "notes/bad.md", "errors": ["artifacts[0].kind: must be a string"]}
    ]
    assert all("pydantic" not in error.lower() for error in payload["failures"][0]["errors"])


def test_validate_mode_is_a_typer_error_while_capture_input_is_json(vault: Path) -> None:
    capture_exit, capture_payload = invoke_json(
        [
            "capture",
            "--source",
            "archive/missing.md",
            "--title",
            " ",
            "--description",
            "Description",
        ]
    )
    validate_result = runner.invoke(app, ["validate"])

    assert capture_exit == 1
    assert capture_payload["errors"] == ["title: must be a non-empty string"]
    assert validate_result.exit_code == 2


def test_validate_rejects_removed_created_at_property(vault: Path) -> None:
    (vault / "notes" / "dated.md").write_text(
        "---\n"
        "content_type: note\n"
        "granularity: distilled\n"
        "description: Note with removed metadata\n"
        "created_at: 2026-06-01\n"
        "tags: []\n"
        "---\n"
        "# Dated\n",
        encoding="utf-8",
    )

    exit_code, payload = invoke_json(["validate", "--path", "notes/dated.md"])

    assert exit_code == 1
    assert payload["errors"] == [
        "unknown property: created_at; use tags for conversation-derived attributes"
    ]


def test_validate_artifacts_names_malformed_json(vault: Path) -> None:
    exit_code, payload = invoke_json(["validate", "--artifacts"], input="{not json")

    assert exit_code == 1
    assert payload["errors"] == ["pipeline state: invalid JSON"]


def test_validate_artifacts_rejects_blank_artifact_fields(vault: Path) -> None:
    exit_code, payload = invoke_json(
        ["validate", "--artifacts"],
        input=json.dumps(
            {
                "batch": "batch",
                "source": "archive/2026-06-01-source.md",
                "artifacts": [{"kind": " ", "path": ""}],
            }
        ),
    )

    assert exit_code == 1
    assert payload["failures"] == [
        {
            "path": "",
            "errors": [
                "artifacts[0].kind: must be a non-empty string",
                "artifacts[0].path: must be a non-empty string",
            ],
        }
    ]
