from __future__ import annotations

import json
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any

from vault.errors import VaultError
from vault.markdown import parse_frontmatter, parse_yaml_mapping
from vault.paths import VaultPaths

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
DEPRECATED_PROPERTIES = {
    "tag": "tags",
    "alias": "aliases",
    "cssclass": "cssclasses",
}
OBSIDIAN_DEFAULT_PROPERTIES = {"aliases", "cssclasses"}


def _load_schema(paths: VaultPaths) -> dict[str, Any]:
    if not paths.schema_file.exists():
        raise VaultError("ops/schema.yaml not found", command="validate")
    schema = parse_yaml_mapping(paths.schema_file)
    if not isinstance(schema, dict):
        raise VaultError("ops/schema.yaml must be a mapping", command="validate")
    return schema


def _enum_values(schema: dict[str, Any], field: str) -> list[Any]:
    enums = schema.get("enums")
    if not isinstance(enums, dict):
        return []
    values = enums.get(field)
    if not isinstance(values, list):
        return []
    return [value for value in values if value is not None]


def _tag_allowed_prefixes(schema: dict[str, Any], errors: list[str]) -> list[str]:
    constraints = schema.get("constraints")
    if not isinstance(constraints, dict):
        return []
    tags = constraints.get("tags")
    if not isinstance(tags, dict):
        return []
    prefixes = tags.get("allowed_prefixes", [])
    if prefixes is None:
        return []
    if not isinstance(prefixes, list):
        errors.append("schema.constraints.tags.allowed_prefixes must be a list")
        return []
    if any(not isinstance(prefix, str) or not prefix for prefix in prefixes):
        errors.append("schema.constraints.tags.allowed_prefixes must contain non-empty strings")
        return []
    return prefixes


def _as_date_string(value: Any) -> str | None:
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, str):
        return value
    return None


def validate_note(paths: VaultPaths, path: Path, schema: dict[str, Any] | None = None) -> list[str]:
    schema = schema or _load_schema(paths)
    note_path = paths.absolute(path)
    errors: list[str] = []

    try:
        note_path = paths.require_inside_notes(note_path, command="validate")
    except VaultError as exc:
        return exc.payload().get("errors", [str(exc)])

    if not note_path.exists() or not note_path.is_file():
        return [f"file not found: {paths.rel(note_path)}"]

    try:
        frontmatter = parse_frontmatter(note_path)
    except VaultError as exc:
        return [exc.message]

    required = schema.get("required", [])
    if not isinstance(required, list):
        errors.append("schema.required must be a list")
        required = []

    for field in required:
        if field not in frontmatter:
            errors.append(f"missing required field: {field}")

    allowed_properties = set(required) | OBSIDIAN_DEFAULT_PROPERTIES
    for field in frontmatter:
        if field in DEPRECATED_PROPERTIES:
            replacement = DEPRECATED_PROPERTIES[field]
            errors.append(f"deprecated Obsidian property: {field}; use {replacement}")
        if field not in allowed_properties:
            errors.append(
                f"unknown property: {field}; use tags for conversation-derived attributes"
            )
        if isinstance(frontmatter[field], dict):
            errors.append(f"nested properties are not Obsidian-compatible: {field}")
        allowed = _enum_values(schema, field)
        if allowed and frontmatter[field] not in allowed:
            errors.append(f"invalid {field}: {frontmatter[field]}")

    description = frontmatter.get("description")
    if "description" in frontmatter:
        if not isinstance(description, str) or not description.strip():
            errors.append("description must be a non-empty string")
        elif len(description) > 200:
            errors.append("description exceeds max length: 200")

    created_at = frontmatter.get("created_at")
    if "created_at" in frontmatter:
        created_at_text = _as_date_string(created_at)
        if created_at_text is None or DATE_RE.fullmatch(created_at_text) is None:
            errors.append("created_at must use YYYY-MM-DD")

    tags = frontmatter.get("tags")
    tag_allowed_prefixes = _tag_allowed_prefixes(schema, errors)
    if "tags" in frontmatter:
        if not isinstance(tags, list):
            errors.append("tags must be a list")
        elif any(not isinstance(tag, str) for tag in tags):
            errors.append("tags must contain only strings")
        else:
            for tag in tags:
                tag_errors = _validate_tag(tag, tag_allowed_prefixes)
                errors.extend(tag_errors)

    aliases = frontmatter.get("aliases")
    if "aliases" in frontmatter and (
        not isinstance(aliases, list) or any(not isinstance(alias, str) for alias in aliases)
    ):
        errors.append("aliases must be a list of strings")

    cssclasses = frontmatter.get("cssclasses")
    if "cssclasses" in frontmatter and (
        not isinstance(cssclasses, list)
        or any(not isinstance(cssclass, str) for cssclass in cssclasses)
    ):
        errors.append("cssclasses must be a list of strings")

    return errors


def _validate_tag(tag: str, allowed_prefixes: list[str]) -> list[str]:
    errors: list[str] = []
    if not tag:
        errors.append("tags must not contain empty strings")
    if tag.startswith("#"):
        errors.append(f"tag must omit leading #: {tag}")
    if any(character.isspace() for character in tag):
        errors.append(f"tag must not contain spaces: {tag}")
    comparable = tag.replace("/", "")
    if comparable and comparable.isdigit():
        errors.append(f"tag must contain at least one non-numeric character: {tag}")
    has_allowed_prefix = any(tag.startswith(prefix) for prefix in allowed_prefixes)
    if "/" in tag and allowed_prefixes and not has_allowed_prefix:
        allowed = ", ".join(allowed_prefixes)
        errors.append(f"namespaced tag must use an allowed prefix ({allowed}): {tag}")
    return errors


def validate_path(paths: VaultPaths, path: Path) -> dict:
    errors = validate_note(paths, path)
    rel_path = paths.rel(paths.absolute(path))
    if errors:
        return {"ok": False, "command": "validate", "path": rel_path, "errors": errors}
    return {"ok": True, "command": "validate", "path": rel_path}


def validate_all(paths: VaultPaths) -> dict:
    schema = _load_schema(paths)
    failures: list[dict[str, Any]] = []
    checked = 0
    for path in sorted(paths.note_collection_dir.rglob("*.md")):
        checked += 1
        errors = validate_note(paths, path, schema)
        if errors:
            failures.append({"path": paths.rel(path), "errors": errors})

    return {
        "ok": not failures,
        "command": "validate",
        "checked": checked,
        "failures": failures,
    }


def _read_pipeline_state() -> dict[str, Any]:
    if sys.stdin.isatty():
        raise VaultError("no pipeline state on stdin; pipe the state JSON", command="validate")
    raw = sys.stdin.read()
    try:
        state = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise VaultError(f"invalid pipeline state JSON: {exc}", command="validate") from exc
    if not isinstance(state, dict):
        raise VaultError("pipeline state must be a JSON object", command="validate")
    return state


def _require_string(state: dict[str, Any], key: str, **fields: Any) -> str:
    value = state.get(key)
    if not isinstance(value, str) or not value:
        raise VaultError(f"pipeline state requires {key}", command="validate", **fields)
    return value


def _commit_paths(state: dict[str, Any], batch: str) -> list[str]:
    values = state.get("commit_paths", [])
    invalid = not isinstance(values, list) or any(
        not isinstance(path, str) or not path for path in values
    )
    if invalid:
        raise VaultError("commit_paths must be a list of paths", command="validate", batch=batch)
    return values


def validate_artifacts(paths: VaultPaths) -> dict:
    state = _read_pipeline_state()
    batch = _require_string(state, "batch")
    source = _require_string(state, "source", batch=batch)
    artifacts = state.get("artifacts")
    if not isinstance(artifacts, list):
        raise VaultError("pipeline state requires artifacts list", command="validate", batch=batch)
    commit_paths = _commit_paths(state, batch)

    schema = _load_schema(paths)
    failures: list[dict[str, Any]] = []
    clean_artifacts: list[dict[str, str]] = []
    for artifact in artifacts:
        if not isinstance(artifact, dict):
            failures.append({"path": "", "errors": ["artifact must be an object"]})
            continue
        kind = artifact.get("kind")
        path = artifact.get("path")
        if not isinstance(kind, str) or not isinstance(path, str):
            failures.append(
                {"path": str(path or ""), "errors": ["artifact requires kind and path"]}
            )
            continue
        errors = validate_note(paths, Path(path), schema)
        if errors:
            failures.append({"path": path, "errors": errors})
            continue
        clean_artifacts.append({"kind": kind, "path": path})

    if failures:
        return {
            "ok": False,
            "command": "validate",
            "batch": batch,
            "source": source,
            "failures": failures,
        }
    result: dict[str, Any] = {
        "ok": True,
        "command": "validate",
        "batch": batch,
        "source": source,
        "artifacts": clean_artifacts,
    }
    if commit_paths:
        result["commit_paths"] = commit_paths
    return result
