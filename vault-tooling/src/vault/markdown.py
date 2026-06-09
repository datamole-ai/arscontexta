from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

from vault.errors import VaultError


class FrontmatterLoader(yaml.SafeLoader):
    pass


def _construct_mapping(loader: FrontmatterLoader, node: yaml.nodes.MappingNode, deep: bool = False):
    mapping: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            raise yaml.YAMLError(f"duplicate property: {key}")
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


FrontmatterLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    _construct_mapping,
)


def parse_frontmatter(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise VaultError(f"{path}: missing opening frontmatter delimiter")
    end = text.find("\n---", 4)
    if end == -1:
        raise VaultError(f"{path}: missing closing frontmatter delimiter")
    raw_frontmatter = text[4:end]
    try:
        parsed = yaml.load(raw_frontmatter, Loader=FrontmatterLoader) or {}
    except yaml.YAMLError as exc:
        raise VaultError(f"{path}: malformed YAML frontmatter: {exc}") from exc
    if not isinstance(parsed, dict):
        raise VaultError(f"{path}: YAML frontmatter must be a mapping")
    return parsed


def parse_yaml_mapping(path: Path) -> dict[str, Any]:
    try:
        parsed = yaml.load(path.read_text(encoding="utf-8"), Loader=FrontmatterLoader) or {}
    except yaml.YAMLError as exc:
        raise VaultError(f"{path}: malformed YAML: {exc}") from exc
    if not isinstance(parsed, dict):
        raise VaultError(f"{path}: YAML must be a mapping")
    return parsed


def slug(value: str) -> str:
    lowered = value.strip().lower()
    lowered = re.sub(r"\.md$", "", lowered)
    lowered = re.sub(r"[^a-z0-9]+", "-", lowered)
    return lowered.strip("-")
