from __future__ import annotations

import shutil
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

from vault.errors import VaultError
from vault.markdown import slug
from vault.paths import VaultPaths

SeedMode = Literal["structure", "capture"]


def seed_source(paths: VaultPaths, source: Path, mode: SeedMode) -> dict:
    source = paths.require_inside_root(paths.absolute(source), command="seed")
    source_basename = slug(source.stem)
    if not source_basename:
        raise VaultError("source basename is empty after normalization", command="seed")

    today = datetime.now(UTC).strftime("%Y-%m-%d")
    archive_source = paths.archive_dir / f"{today}-{source_basename}.md"
    from_inbox = source.is_relative_to(paths.inbox_dir.resolve())

    if archive_source.exists():
        if from_inbox and not source.exists():
            return _seed_result(paths, source_basename, archive_source, source, from_inbox)
        raise VaultError(
            f"archive source already exists: {paths.rel(archive_source)}",
            command="seed",
            batch=source_basename,
        )

    if not source.exists() or not source.is_file():
        raise VaultError(
            f"source file not found: {paths.rel(source)}",
            command="seed",
            source=paths.rel(source),
        )

    archive_source.parent.mkdir(parents=True, exist_ok=True)
    if from_inbox:
        shutil.move(source, archive_source)
    else:
        shutil.copy2(source, archive_source)

    return _seed_result(paths, source_basename, archive_source, source, from_inbox)


def _seed_result(
    paths: VaultPaths,
    batch: str,
    archive_source: Path,
    original_source: Path,
    from_inbox: bool,
) -> dict:
    result = {
        "ok": True,
        "command": "seed",
        "batch": batch,
        "source": paths.rel(archive_source),
    }
    if from_inbox:
        result["commit_paths"] = [paths.rel(original_source)]
    return result
