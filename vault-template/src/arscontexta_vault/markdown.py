from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

from arscontexta_vault.errors import VaultError


def parse_frontmatter(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise VaultError(f"{path}: missing opening frontmatter delimiter")
    end = text.find("\n---", 4)
    if end == -1:
        raise VaultError(f"{path}: missing closing frontmatter delimiter")
    raw_frontmatter = text[4:end]
    try:
        parsed = yaml.safe_load(raw_frontmatter) or {}
    except yaml.YAMLError as exc:
        raise VaultError(f"{path}: malformed YAML frontmatter: {exc}") from exc
    if not isinstance(parsed, dict):
        raise VaultError(f"{path}: YAML frontmatter must be a mapping")
    return parsed


def slug(value: str) -> str:
    lowered = value.strip().lower()
    lowered = re.sub(r"\.md$", "", lowered)
    lowered = re.sub(r"[^a-z0-9]+", "-", lowered)
    return lowered.strip("-")
