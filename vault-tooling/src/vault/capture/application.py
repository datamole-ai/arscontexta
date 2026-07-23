from __future__ import annotations

import re

import yaml

from vault.capture.models import CaptureInput
from vault.shared.errors import VaultError
from vault.shared.naming import slug
from vault.shared.paths import VaultPaths
from vault.validation.application import load_schema, validate_note

SOURCE_FENCE_RE = re.compile(r"^(`{3,})", re.MULTILINE)


def capture_note(paths: VaultPaths, request: CaptureInput) -> dict:
    source = paths.require_inside_archive(paths.absolute(request.source), command="capture")
    if not source.exists() or not source.is_file():
        raise VaultError(
            f"source file not found: {paths.rel(source)}",
            command="capture",
            source=paths.rel(source),
        )

    schema = load_schema(paths)
    if request.out is not None:
        note_path = paths.require_inside_notes(paths.absolute(request.out), command="capture")
    else:
        note_slug = slug(request.title)
        if not note_slug:
            raise VaultError("title slug is empty after normalization", command="capture")
        note_path = paths.note_collection_dir / f"{note_slug}.md"
    if note_path.exists():
        raise VaultError(f"note already exists: {paths.rel(note_path)}", command="capture")

    source_text = source.read_text(encoding="utf-8")
    longest_run = max(
        (len(match.group(1)) for match in SOURCE_FENCE_RE.finditer(source_text)),
        default=0,
    )
    fence = "`" * max(3, longest_run + 1)
    payload = source_text if source_text.endswith("\n") else source_text + "\n"

    frontmatter = yaml.safe_dump(
        {
            "content_type": "note",
            "granularity": "verbatim",
            "description": request.description,
        },
        sort_keys=False,
        allow_unicode=True,
        default_flow_style=False,
    )
    if request.tags:
        tags_block = "tags:\n" + "".join(f"  - {tag}\n" for tag in request.tags)
    else:
        tags_block = "tags: []\n"

    note_path.parent.mkdir(parents=True, exist_ok=True)
    note_path.write_text(
        f"---\n{frontmatter}{tags_block}---\n\n# {request.title}\n\n"
        f"{fence}text\n{payload}{fence}\n\n---\n\nSource: {paths.rel(source)}\n",
        encoding="utf-8",
    )

    errors = validate_note(paths, note_path, schema)
    if errors:
        note_path.unlink()
        raise VaultError("; ".join(errors), command="capture")

    return {
        "ok": True,
        "command": "capture",
        "source": paths.rel(source),
        "note": paths.rel(note_path),
    }
