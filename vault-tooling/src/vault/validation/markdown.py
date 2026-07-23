from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml
from yaml.resolver import BaseResolver

from vault.shared.errors import VaultError


class FrontmatterLoader(yaml.SafeLoader):
    # Keep timestamp-like scalars as text so string fields stay strings.
    yaml_implicit_resolvers = {
        key: [(tag, pattern) for tag, pattern in resolvers if tag != "tag:yaml.org,2002:timestamp"]
        for key, resolvers in yaml.SafeLoader.yaml_implicit_resolvers.items()
    }


def _construct_mapping(
    loader: FrontmatterLoader,
    node: yaml.nodes.MappingNode,
    deep: bool = False,
) -> dict[Any, Any]:
    mapping: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            raise yaml.YAMLError(f"duplicate property: {key}")
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


FrontmatterLoader.add_constructor(
    BaseResolver.DEFAULT_MAPPING_TAG,
    _construct_mapping,
)


FENCE_RUN_RE = re.compile(r"^`{3,}")
FENCE_OPEN_RE = re.compile(r"^(`{3,})(\S*)$")


def parse_note(path: Path) -> tuple[dict[str, Any], str]:
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
    body_start = text.find("\n", end + 1)
    body = "" if body_start == -1 else text[body_start + 1 :]
    return parsed, body


SOURCE_LINE_RE = re.compile(r"^Source: (.+)$")


def _verbatim_fence_bounds(lines: list[str]) -> tuple[int, int]:
    opener_index = None
    fence_length = 0
    for index, line in enumerate(lines):
        if FENCE_RUN_RE.match(line):
            opener = FENCE_OPEN_RE.match(line)
            if opener is None:
                raise VaultError("verbatim note missing fenced source block")
            opener_index = index
            fence_length = len(opener.group(1))
            break
    if opener_index is None:
        raise VaultError("verbatim note missing fenced source block")

    for index in range(opener_index + 1, len(lines)):
        stripped = lines[index].rstrip()
        if len(stripped) >= fence_length and set(stripped) == {"`"}:
            return opener_index, index
    raise VaultError("verbatim note fence is unclosed")


def verbatim_payload(text: str) -> str:
    """Extract the single outer fenced payload from a verbatim note body."""
    lines = text.split("\n")
    opener_index, closer_index = _verbatim_fence_bounds(lines)

    if any(FENCE_RUN_RE.match(line) for line in lines[closer_index + 1 :]):
        raise VaultError("verbatim note has extra fences outside the source block")

    return "".join(line + "\n" for line in lines[opener_index + 1 : closer_index])


def verbatim_source(text: str) -> str:
    """Extract the recorded archive path from a verbatim note's provenance footer."""
    lines = text.split("\n")
    # Scan only past the closing fence so payload lines can never match.
    _, closer_index = _verbatim_fence_bounds(lines)
    for line in lines[closer_index + 1 :]:
        match = SOURCE_LINE_RE.match(line)
        if match:
            return match.group(1)
    raise VaultError("verbatim note missing Source line")


def parse_yaml_mapping(path: Path) -> dict[str, Any]:
    try:
        parsed = yaml.load(path.read_text(encoding="utf-8"), Loader=FrontmatterLoader) or {}
    except yaml.YAMLError as exc:
        raise VaultError(f"{path}: malformed YAML: {exc}") from exc
    if not isinstance(parsed, dict):
        raise VaultError(f"{path}: YAML must be a mapping")
    return parsed
