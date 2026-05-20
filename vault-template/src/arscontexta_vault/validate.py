from __future__ import annotations

import json
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any

from arscontexta_vault.errors import VaultError
from arscontexta_vault.markdown import parse_frontmatter
from arscontexta_vault.paths import VaultPaths

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _load_schema(paths: VaultPaths) -> dict[str, Any]:
    if not paths.template_note.exists():
        raise VaultError("ops/templates/note.md not found", command="validate")
    schema = parse_frontmatter(paths.template_note).get("_schema")
    if not isinstance(schema, dict):
        raise VaultError("ops/templates/note.md lacks _schema mapping", command="validate")
    return schema


def _enum_values(schema: dict[str, Any], field: str) -> list[Any]:
    enums = schema.get("enums")
    if not isinstance(enums, dict):
        return []
    values = enums.get(field)
    if not isinstance(values, list):
        return []
    return [value for value in values if value is not None]


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
        errors.append("_schema.required must be a list")
        required = []

    for field in required:
        if field not in frontmatter:
            errors.append(f"missing required field: {field}")

    for field in frontmatter:
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
    if "tags" in frontmatter:
        if not isinstance(tags, list):
            errors.append("tags must be a list")
        elif any(not isinstance(tag, str) for tag in tags):
            errors.append("tags must contain only strings")

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
