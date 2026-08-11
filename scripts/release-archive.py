#!/usr/bin/env python3
"""Build and verify the Second Brain release archive."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path, PurePosixPath
from typing import NamedTuple

ARCHIVE_NAME = "second-brain.zip"
PLUGIN_NAME = "second-brain"
MANIFEST_PATH = ".claude-plugin/plugin.json"
COPY_SCRIPT_PATH = "skills/setup/scripts/copy-template.sh"
FIXED_TIMESTAMP = (1980, 1, 1, 0, 0, 0)

EXACT_PATHS = (
    MANIFEST_PATH,
    "skills/setup/SKILL.md",
    COPY_SCRIPT_PATH,
    "vault-tooling/pyproject.toml",
)
DIRECTORY_PATHS = (
    "template",
    "vault-tooling/src/vault",
)
PATHS_TO_PACKAGE = (*EXACT_PATHS, *DIRECTORY_PATHS)
EXECUTABLE_PATHS = frozenset({COPY_SCRIPT_PATH})
FORBIDDEN_PARTS = frozenset(
    {
        ".DS_Store",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        "__pycache__",
    }
)
FORBIDDEN_SUFFIXES = (".pyc", ".pyo", ".swp", "~")
VERSION_PATTERN = re.compile(r"(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)")
TAG_PATTERN = re.compile(r"v(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)")


class ReleaseError(Exception):
    """A release archive does not satisfy the package contract."""


class SourceEntry(NamedTuple):
    path: str
    mode: int
    content: bytes


def repository_root() -> Path:
    root = Path(__file__).resolve().parent.parent
    if not (root / MANIFEST_PATH).is_file():
        raise ReleaseError(f"cannot find {MANIFEST_PATH} below {root}")
    return root


def is_allowed_path(path: str) -> bool:
    return path in EXACT_PATHS or any(
        path.startswith(f"{directory}/") for directory in DIRECTORY_PATHS
    )


def validate_path(path: str) -> None:
    parsed = PurePosixPath(path)
    if parsed.is_absolute() or ".." in parsed.parts or str(parsed) != path:
        raise ReleaseError(f"unsafe archive path: {path!r}")
    if not is_allowed_path(path):
        raise ReleaseError(f"development-only path selected for release: {path}")
    if FORBIDDEN_PARTS.intersection(parsed.parts) or path.endswith(FORBIDDEN_SUFFIXES):
        raise ReleaseError(f"generated or temporary file selected for release: {path}")


def expected_mode(path: str) -> int:
    return 0o100755 if path in EXECUTABLE_PATHS else 0o100644


def read_source_entries(root: Path) -> list[SourceEntry]:
    command = ["git", "ls-files", "--stage", "-z", "--", *PATHS_TO_PACKAGE]
    result = subprocess.run(command, cwd=root, check=True, capture_output=True)
    entries: list[SourceEntry] = []

    for record in result.stdout.split(b"\0"):
        if not record:
            continue
        metadata, separator, encoded_path = record.partition(b"\t")
        if not separator:
            raise ReleaseError("git returned a malformed index record")
        mode_text, _object_id, stage = metadata.decode("ascii").split()
        path = encoded_path.decode("utf-8")
        validate_path(path)
        if stage != "0":
            raise ReleaseError(f"cannot package an unresolved index entry: {path}")

        source = root / path
        if source.is_symlink() or not source.is_file():
            raise ReleaseError(f"release input must be a regular file: {path}")

        mode = int(mode_text, 8)
        required_mode = expected_mode(path)
        if mode != required_mode:
            raise ReleaseError(
                f"unexpected git mode for {path}: {mode:o}; expected {required_mode:o}"
            )
        entries.append(SourceEntry(path, mode, source.read_bytes()))

    entries.sort(key=lambda entry: entry.path)
    paths = {entry.path for entry in entries}
    missing = sorted(set(EXACT_PATHS) - paths)
    if missing:
        raise ReleaseError(f"release inputs are missing required files: {', '.join(missing)}")
    for directory in DIRECTORY_PATHS:
        if not any(path.startswith(f"{directory}/") for path in paths):
            raise ReleaseError(f"release inputs are empty below {directory}/")
    if len(paths) != len(entries):
        raise ReleaseError("release inputs contain duplicate paths")
    return entries


def manifest_version(content: bytes, source: str) -> str:
    try:
        manifest = json.loads(content)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ReleaseError(f"invalid JSON in {source}: {error}") from error
    if not isinstance(manifest, dict):
        raise ReleaseError(f"manifest in {source} must be a JSON object")
    if manifest.get("name") != PLUGIN_NAME:
        raise ReleaseError(f"manifest in {source} must name the plugin {PLUGIN_NAME!r}")
    version = manifest.get("version")
    if not isinstance(version, str) or VERSION_PATTERN.fullmatch(version) is None:
        raise ReleaseError(f"manifest in {source} must have an X.Y.Z version")
    return version


def validate_tag(tag: str | None, version: str) -> None:
    if tag is None:
        return
    if TAG_PATTERN.fullmatch(tag) is None:
        raise ReleaseError(f"release tag must have the form vX.Y.Z, got {tag!r}")
    expected = f"v{version}"
    if tag != expected:
        raise ReleaseError(f"release tag {tag!r} does not match plugin version {version!r}")


def build_archive(root: Path, output: Path, tag: str | None) -> None:
    entries = read_source_entries(root)
    version = manifest_version(
        next(entry.content for entry in entries if entry.path == MANIFEST_PATH),
        str(root / MANIFEST_PATH),
    )
    validate_tag(tag, version)

    output = output.resolve()
    if output.name != ARCHIVE_NAME and output.suffix != ".zip":
        raise ReleaseError(f"archive output must have a .zip suffix: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)

    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            dir=output.parent,
            prefix=f".{output.name}.",
            suffix=".tmp",
            delete=False,
        ) as temporary:
            temporary_path = Path(temporary.name)

        with zipfile.ZipFile(temporary_path, "w", compression=zipfile.ZIP_STORED) as archive:
            for entry in entries:
                info = zipfile.ZipInfo(entry.path, date_time=FIXED_TIMESTAMP)
                info.compress_type = zipfile.ZIP_STORED
                info.create_system = 3
                info.external_attr = entry.mode << 16
                archive.writestr(info, entry.content)
        os.chmod(temporary_path, 0o644)
        os.replace(temporary_path, output)
    except Exception:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)
        raise

    print(f"built {output} with {len(entries)} files for plugin version {version}")


def verify_archive(root: Path, archive_path: Path, tag: str | None) -> None:
    entries = read_source_entries(root)
    expected = {entry.path: entry for entry in entries}
    source_version = manifest_version(expected[MANIFEST_PATH].content, str(root / MANIFEST_PATH))
    validate_tag(tag, source_version)

    try:
        archive = zipfile.ZipFile(archive_path, "r")
    except (FileNotFoundError, zipfile.BadZipFile) as error:
        raise ReleaseError(f"cannot read release archive {archive_path}: {error}") from error

    with archive:
        if archive.comment:
            raise ReleaseError("release archive must not have a ZIP comment")
        infos = archive.infolist()
        names = [info.filename for info in infos]
        if len(names) != len(set(names)):
            raise ReleaseError("release archive contains duplicate paths")
        for name in names:
            validate_path(name)

        actual_paths = set(names)
        expected_paths = set(expected)
        missing = sorted(expected_paths - actual_paths)
        extra = sorted(actual_paths - expected_paths)
        if missing or extra:
            details = []
            if missing:
                details.append(f"missing: {', '.join(missing)}")
            if extra:
                details.append(f"unexpected: {', '.join(extra)}")
            raise ReleaseError("archive membership mismatch; " + "; ".join(details))
        if names != sorted(names):
            raise ReleaseError("release archive entries must be sorted")

        bad_crc = archive.testzip()
        if bad_crc is not None:
            raise ReleaseError(f"CRC check failed for {bad_crc}")

        for info in infos:
            entry = expected[info.filename]
            if info.is_dir():
                raise ReleaseError(f"release archive contains a directory entry: {info.filename}")
            if info.date_time != FIXED_TIMESTAMP:
                raise ReleaseError(f"non-deterministic timestamp on {info.filename}")
            if info.compress_type != zipfile.ZIP_STORED:
                raise ReleaseError(f"unexpected compression method on {info.filename}")
            if info.create_system != 3:
                raise ReleaseError(f"missing Unix metadata on {info.filename}")
            if info.extra or info.comment:
                raise ReleaseError(f"unexpected ZIP metadata on {info.filename}")
            mode = (info.external_attr >> 16) & 0xFFFF
            if mode != entry.mode:
                raise ReleaseError(
                    f"archive mode for {info.filename} is {mode:o}; expected {entry.mode:o}"
                )
            if archive.read(info) != entry.content:
                raise ReleaseError(f"archive content differs from source: {info.filename}")

        archive_version = manifest_version(
            archive.read(MANIFEST_PATH), f"{archive_path}:{MANIFEST_PATH}"
        )
        if archive_version != source_version:
            raise ReleaseError(
                f"archive version {archive_version!r} does not match "
                f"source version {source_version!r}"
            )
        validate_tag(tag, archive_version)

    print(
        f"verified {archive_path.resolve()} with {len(entries)} files "
        f"for plugin version {source_version}"
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    build_parser = subparsers.add_parser("build", help="build a deterministic release ZIP")
    build_parser.add_argument("--output", type=Path, required=True, help="path for the release ZIP")
    build_parser.add_argument("--tag", help="require this vX.Y.Z tag to match plugin.json")

    verify_parser = subparsers.add_parser("verify", help="verify release ZIP contents and metadata")
    verify_parser.add_argument("archive", type=Path, help="release ZIP to verify")
    verify_parser.add_argument("--tag", help="require this vX.Y.Z tag to match plugin.json")

    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = repository_root()
    try:
        if args.command == "build":
            build_archive(root, args.output, args.tag)
        else:
            verify_archive(root, args.archive, args.tag)
    except (ReleaseError, subprocess.CalledProcessError, OSError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
