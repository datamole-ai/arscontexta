from __future__ import annotations

import shutil
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

from arscontexta_vault.errors import VaultError
from arscontexta_vault.markdown import slug
from arscontexta_vault.paths import VaultPaths

SeedMode = Literal["structure", "capture"]


def _archive_source_name(source: Path) -> str:
    suffix = source.suffix or ".md"
    return f"source{suffix}"


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
    archive_folder = paths.archive_dir / f"{today}-{source_basename}"
    if archive_folder.exists():
        raise VaultError(
            f"archive folder already exists: {paths.rel(archive_folder)}",
            command="seed",
            batch=source_basename,
        )

    archive_folder.mkdir(parents=True, exist_ok=False)
    final_source = archive_folder / _archive_source_name(source)
    shutil.copy2(source, final_source)

    return {
        "ok": True,
        "command": "seed",
        "batch": source_basename,
        "source": paths.rel(final_source),
    }
