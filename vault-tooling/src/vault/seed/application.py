from __future__ import annotations

import shutil
from datetime import UTC, datetime
from pathlib import Path

from vault.seed.models import SeedInput
from vault.shared.errors import VaultError
from vault.shared.naming import slug
from vault.shared.paths import VaultPaths


def seed_source(paths: VaultPaths, request: SeedInput) -> dict:
    source = paths.require_inside_inbox(paths.absolute(request.source), command="seed")
    source_basename = slug(source.stem)
    if not source_basename:
        raise VaultError("source basename is empty after normalization", command="seed")

    today = datetime.now(UTC).strftime("%Y-%m-%d")
    archive_source = paths.archive_dir / f"{today}-{source_basename}.md"

    if archive_source.exists():
        if not source.exists():
            return _seed_result(paths, source_basename, archive_source)
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
    shutil.move(source, archive_source)

    return _seed_result(paths, source_basename, archive_source)


def _seed_result(paths: VaultPaths, batch: str, archive_source: Path) -> dict:
    return {
        "ok": True,
        "command": "seed",
        "batch": batch,
        "source": paths.rel(archive_source),
    }
