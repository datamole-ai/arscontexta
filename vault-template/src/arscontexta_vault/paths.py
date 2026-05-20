from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from arscontexta_vault.errors import VaultError


@dataclass(frozen=True)
class VaultPaths:
    root: Path
    note_collection_dir: Path
    archive_dir: Path

    @classmethod
    def discover(cls, start: Path | None = None) -> VaultPaths:
        current = (start or Path.cwd()).resolve()
        for candidate in [current, *current.parents]:
            if (candidate / ".arscontexta").exists():
                manifest_path = candidate / "ops" / "derivation-manifest.yaml"
                if not manifest_path.exists():
                    raise VaultError("ops/derivation-manifest.yaml not found")
                data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
                if not isinstance(data, dict) or not isinstance(data.get("vocabulary"), dict):
                    raise VaultError("ops/derivation-manifest.yaml lacks vocabulary mapping")
                vocabulary = data["vocabulary"]
                return cls(
                    root=candidate,
                    note_collection_dir=candidate / _vocab(vocabulary, "note_collection"),
                    archive_dir=candidate / _vocab(vocabulary, "archive"),
                )
        raise VaultError(".arscontexta marker not found; run from a generated vault")

    @property
    def template_note(self) -> Path:
        return self.root / "ops" / "templates" / "note.md"

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


def _vocab(vocabulary: object, key: str) -> str:
    if not isinstance(vocabulary, dict):
        raise VaultError("ops/derivation-manifest.yaml lacks vocabulary mapping")
    value = vocabulary.get(key)
    if not isinstance(value, str) or not value:
        raise VaultError(f"vocabulary.{key} missing from ops/derivation-manifest.yaml")
    return value
