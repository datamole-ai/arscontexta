from __future__ import annotations

import json
from pathlib import Path

import pytest


@pytest.fixture
def vault(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    (tmp_path / ".arscontexta").touch()
    (tmp_path / "notes").mkdir()
    (tmp_path / "inbox").mkdir()
    (tmp_path / "archive").mkdir()
    (tmp_path / "ops" / "templates").mkdir(parents=True)
    (tmp_path / "ops" / "derivation-manifest.yaml").write_text(
        """
---
vocabulary:
  note_collection: "notes"
  inbox: "inbox"
  archive: "archive"
  note: "note"
  note_plural: "notes"
  topic_map: "topic map"
  topic_maps: "topic maps"
  qmd_collection: "notes"
""".lstrip(),
        encoding="utf-8",
    )
    (tmp_path / "ops" / "templates" / "note.md").write_text(
        """---
_schema:
  required:
    - content_type
    - granularity
    - description
    - created_at
    - tags
  enums:
    granularity:
      - structure
      - capture
    content_type:
      - claim
      - source
  constraints:
    description:
      max_length: 200
    created_at:
      format: "ISO 8601 date (YYYY-MM-DD)."
    tags:
      format: "Array of strings."
content_type: ""
granularity: structure
description: ""
created_at: YYYY-MM-DD
tags: []
---
# Template
""",
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    return tmp_path


def write_note(path: Path, title: str, links: str = "", tags: list[str] | None = None) -> None:
    payload = {
        "content_type": "claim",
        "granularity": "structure",
        "description": f"Description for {title}",
        "created_at": "2026-05-11",
        "tags": tags or [],
    }
    path.write_text(
        "---\n"
        + "\n".join(
            f"{key}: {json.dumps(value) if isinstance(value, list) else value}"
            for key, value in payload.items()
        )
        + "\n---\n"
        + f"# {title}\n\n{links}\n",
        encoding="utf-8",
    )
