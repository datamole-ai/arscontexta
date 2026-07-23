from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from vault.shared.errors import VaultError

NOTES_DIR = "notes"
ARCHIVE_DIR = "archive"
INBOX_DIR = "inbox"


@dataclass(frozen=True)
class VaultPaths:
    root: Path
    note_collection_dir: Path
    archive_dir: Path
    inbox_dir: Path

    @classmethod
    def discover(cls, start: Path | None = None) -> VaultPaths:
        current = (start or Path.cwd()).resolve()
        for candidate in [current, *current.parents]:
            if (candidate / ".second-brain").exists():
                return cls(
                    root=candidate,
                    note_collection_dir=candidate / NOTES_DIR,
                    archive_dir=candidate / ARCHIVE_DIR,
                    inbox_dir=candidate / INBOX_DIR,
                )
        raise VaultError(".second-brain marker not found; run from a generated vault")

    @property
    def schema_file(self) -> Path:
        return self.root / "ops" / "schema.yaml"

    @property
    def tags_file(self) -> Path:
        return self.root / "ops" / "tags.yaml"

    def rel(self, path: Path) -> str:
        try:
            return path.resolve().relative_to(self.root).as_posix()
        except ValueError:
            return path.as_posix()

    def absolute(self, value: str | Path) -> Path:
        path = Path(value)
        if path.is_absolute():
            return path
        return self.root / path

    def require_inside_root(self, path: Path, *, command: str) -> Path:
        resolved = path.resolve()
        try:
            resolved.relative_to(self.root.resolve())
        except ValueError as exc:
            raise VaultError(
                f"path is outside vault: {path}",
                command=command,
                path=self.rel(path),
            ) from exc
        return resolved

    def require_inside_notes(self, path: Path, *, command: str) -> Path:
        resolved = self.require_inside_root(path, command=command)
        try:
            resolved.relative_to(self.note_collection_dir.resolve())
        except ValueError as exc:
            raise VaultError(
                f"path is outside note collection: {self.rel(path)}",
                command=command,
                path=self.rel(path),
            ) from exc
        return resolved

    def require_inside_inbox(self, path: Path, *, command: str) -> Path:
        resolved = self.require_inside_root(path, command=command)
        try:
            resolved.relative_to(self.inbox_dir.resolve())
        except ValueError as exc:
            raise VaultError(
                f"source is outside inbox: {self.rel(path)}",
                command=command,
                path=self.rel(path),
            ) from exc
        return resolved

    def require_inside_archive(self, path: Path, *, command: str) -> Path:
        resolved = self.require_inside_root(path, command=command)
        try:
            resolved.relative_to(self.archive_dir.resolve())
        except ValueError as exc:
            raise VaultError(
                f"source is outside archive: {self.rel(path)}",
                command=command,
                path=self.rel(path),
            ) from exc
        return resolved
