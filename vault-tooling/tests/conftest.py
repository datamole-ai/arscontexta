from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml


@pytest.fixture
def vault(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    (tmp_path / ".second-brain").touch()
    (tmp_path / "notes").mkdir()
    (tmp_path / "inbox").mkdir()
    (tmp_path / "archive").mkdir()
    (tmp_path / "ops").mkdir()
    (tmp_path / "ops" / "schema.yaml").write_text(
        """required:
  - content_type
  - granularity
  - description
  - tags
enums:
  granularity:
    - verbatim
    - distilled
  content_type:
    - moc
    - note
constraints:
  description:
    max_length: 200
  tags:
    format: "Array of strings."
""",
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    return tmp_path


def write_tag_registry(root: Path, entries: list[dict[str, str]]) -> None:
    (root / "ops" / "tags.yaml").write_text(yaml.safe_dump({"tags": entries}), encoding="utf-8")


def write_note(path: Path, title: str, links: str = "", tags: list[str] | None = None) -> None:
    payload = {
        "content_type": "note",
        "granularity": "distilled",
        "description": f"Description for {title}",
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
