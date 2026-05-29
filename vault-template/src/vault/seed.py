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
    source = source if source.is_absolute() else paths.root / source
    if not source.exists() or not source.is_file():
        raise VaultError(
            f"source file not found: {paths.rel(source)}",
            command="seed",
            source=paths.rel(source),
        )
    paths.require_inside_root(source, command="seed")

    source_basename = slug(source.stem)
    if not source_basename:
        raise VaultError("source basename is empty after normalization", command="seed")

    today = datetime.now(UTC).strftime("%Y-%m-%d")
    archive_source = paths.archive_dir / f"{today}-{source_basename}.md"
    if archive_source.exists():
        raise VaultError(
            f"archive source already exists: {paths.rel(archive_source)}",
            command="seed",
            batch=source_basename,
        )

    archive_source.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, archive_source)

    return {
        "ok": True,
        "command": "seed",
        "batch": source_basename,
        "source": paths.rel(archive_source),
    }
