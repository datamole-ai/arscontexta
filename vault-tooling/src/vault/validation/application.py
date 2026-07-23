from __future__ import annotations

from pathlib import Path
from typing import Any, TextIO, cast

from pydantic import ValidationError

from vault.shared.errors import VaultError
from vault.shared.model_validation import format_validation_errors, validate_model
from vault.shared.paths import VaultPaths
from vault.validation.markdown import (
    parse_note,
    parse_yaml_mapping,
    verbatim_payload,
    verbatim_source,
)
from vault.validation.models import (
    Artifact,
    NoteFrontmatter,
    PipelineEnvelope,
    PipelineState,
    TagRegistryFile,
    VaultSchema,
)

DEPRECATED_PROPERTIES = {
    "tag": "tags",
    "alias": "aliases",
    "cssclass": "cssclasses",
}
OBSIDIAN_DEFAULT_PROPERTIES = {"aliases", "cssclasses"}


def load_schema(paths: VaultPaths) -> VaultSchema:
    if not paths.schema_file.exists():
        raise VaultError("ops/schema.yaml not found", command="validate")
    schema = parse_yaml_mapping(paths.schema_file)
    try:
        return validate_model(VaultSchema, schema, command="validate")
    except VaultError as exc:
        errors = [f"ops/schema.yaml: {error}" for error in exc.payload()["errors"]]
        raise VaultError(errors[0], command="validate", errors=errors) from exc


def _enum_values(schema: VaultSchema, field: str) -> list[Any]:
    return [value for value in schema.enums.get(field, []) if value is not None]


# (exact tags, family prefixes); None means no ops/tags.yaml, so membership goes unchecked.
TagRegistry = tuple[frozenset[str], tuple[str, ...]]


def _load_tag_registry(paths: VaultPaths) -> TagRegistry | None:
    if not paths.tags_file.exists():
        return None
    registry = parse_yaml_mapping(paths.tags_file)
    try:
        entries = validate_model(TagRegistryFile, registry, command="validate").tags
    except VaultError as exc:
        errors = [f"ops/tags.yaml: {error}" for error in exc.payload()["errors"]]
        raise VaultError(errors[0], command="validate", errors=errors) from exc
    exact: set[str] = set()
    families: list[str] = []
    seen: set[str] = set()
    for entry in entries:
        tag = entry.tag
        if tag in seen:
            raise VaultError(f"ops/tags.yaml has duplicate tag: {tag}", command="validate")
        seen.add(tag)
        prefix = tag[:-2] if tag.endswith("/*") else None
        if prefix == "":
            raise VaultError(
                f"ops/tags.yaml family entry requires a prefix before /*: {tag}",
                command="validate",
            )
        comparable = tag if prefix is None else prefix
        if "*" in comparable:
            raise VaultError(
                f"ops/tags.yaml allows * only as a trailing /*: {tag}", command="validate"
            )
        format_errors = _validate_tag(comparable)
        if format_errors:
            raise VaultError(
                f"ops/tags.yaml has invalid tag: {format_errors[0]}", command="validate"
            )
        if prefix is None:
            exact.add(tag)
        else:
            families.append(prefix)
    return frozenset(exact), tuple(families)


def _tag_registered(tag: str, registry: TagRegistry) -> bool:
    exact, families = registry
    if tag in exact:
        return True
    return any(tag.startswith(prefix + "/") and len(tag) > len(prefix) + 1 for prefix in families)


def validate_note(
    paths: VaultPaths,
    path: Path,
    schema: VaultSchema | None = None,
    registry: TagRegistry | None = None,
) -> list[str]:
    schema = schema or load_schema(paths)
    registry = registry if registry is not None else _load_tag_registry(paths)
    note_path = paths.absolute(path)
    errors: list[str] = []

    try:
        note_path = paths.require_inside_notes(note_path, command="validate")
    except VaultError as exc:
        return exc.payload().get("errors", [str(exc)])

    if not note_path.exists() or not note_path.is_file():
        return [f"file not found: {paths.rel(note_path)}"]

    try:
        frontmatter, body = parse_note(note_path)
    except VaultError as exc:
        return [exc.message]

    try:
        NoteFrontmatter.model_validate(frontmatter)
    except ValidationError as exc:
        frontmatter_errors = format_validation_errors(
            exc,
            inline_locations=frozenset({"description"}),
        )
        invalid_fields = {
            detail["loc"][0]
            for detail in exc.errors(include_url=False)
            if detail.get("loc") and isinstance(detail["loc"][0], str)
        }
    else:
        frontmatter_errors = []
        invalid_fields = set()
    errors.extend(_frontmatter_structure_errors(frontmatter_errors))

    required = schema.required

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
        if field not in invalid_fields:
            allowed = _enum_values(schema, field)
            if allowed and frontmatter[field] not in allowed:
                errors.append(f"invalid {field}: {frontmatter[field]}")

    tags = frontmatter.get("tags")
    if "tags" in frontmatter and "tags" not in invalid_fields:
        for tag in cast(list[str], tags):
            tag_errors = _validate_tag(tag)
            errors.extend(tag_errors)
            if not tag_errors and registry is not None and not _tag_registered(tag, registry):
                errors.append(
                    f"tag not in ops/tags.yaml: {tag}; "
                    "use a registered tag or append an entry with tag and meaning"
                )

    if frontmatter.get("granularity") == "verbatim":
        errors.extend(_verbatim_provenance_errors(paths, body))

    return errors


def _frontmatter_structure_errors(messages: list[str]) -> list[str]:
    """Keep the long-standing note diagnostics while Pydantic guards scalar types."""

    replacements = {
        "description: must be a string": "description must be a non-empty string",
        "tags: must be a list": "tags must be a list",
        "tags[": "tags must contain only strings",
        "aliases: must be a list": "aliases must be a list of strings",
        "aliases[": "aliases must be a list of strings",
        "cssclasses: must be a list": "cssclasses must be a list of strings",
        "cssclasses[": "cssclasses must be a list of strings",
    }
    errors: list[str] = []
    for message in messages:
        replacement = next(
            (value for prefix, value in replacements.items() if message.startswith(prefix)), message
        )
        if replacement not in errors:
            errors.append(replacement)
    return errors


def _verbatim_provenance_errors(paths: VaultPaths, body: str) -> list[str]:
    try:
        payload = verbatim_payload(body)
        source_rel = verbatim_source(body)
    except VaultError as exc:
        return [exc.message]
    try:
        source_path = paths.require_inside_archive(paths.absolute(source_rel), command="validate")
    except VaultError as exc:
        return [exc.message]
    if not source_path.exists() or not source_path.is_file():
        return [f"source file not found for verbatim check: {source_rel}"]
    source_text = source_path.read_text(encoding="utf-8")
    if payload not in (source_text, source_text + "\n"):
        return [f"verbatim note differs from archived source: {source_rel}"]
    return []


def _validate_tag(tag: str) -> list[str]:
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
    return errors


def validate_path(paths: VaultPaths, path: Path) -> dict:
    errors = validate_note(paths, path)
    rel_path = paths.rel(paths.absolute(path))
    if errors:
        return {"ok": False, "command": "validate", "path": rel_path, "errors": errors}
    return {"ok": True, "command": "validate", "path": rel_path}


def validate_all(paths: VaultPaths) -> dict:
    schema = load_schema(paths)
    registry = _load_tag_registry(paths)
    failures: list[dict[str, Any]] = []
    checked = 0
    for path in sorted(paths.note_collection_dir.rglob("*.md")):
        checked += 1
        errors = validate_note(paths, path, schema, registry)
        if errors:
            failures.append({"path": paths.rel(path), "errors": errors})

    return {
        "ok": not failures,
        "command": "validate",
        "checked": checked,
        "failures": failures,
    }


def _read_pipeline_state(stream: TextIO) -> PipelineEnvelope:
    if stream.isatty():
        raise VaultError("no pipeline state on stdin; pipe the state JSON", command="validate")
    raw = stream.read()
    return validate_model(
        PipelineEnvelope,
        raw,
        command="validate",
        location_prefix=("pipeline state",),
        json_input=True,
    )


def validate_artifacts(paths: VaultPaths, stream: TextIO) -> dict:
    envelope = _read_pipeline_state(stream)
    batch = envelope.batch
    source = envelope.source

    schema = load_schema(paths)
    registry = _load_tag_registry(paths)
    failures: list[dict[str, Any]] = []
    clean_artifacts: list[Artifact] = []
    for index, raw_artifact in enumerate(envelope.artifacts):
        try:
            artifact = validate_model(
                Artifact,
                raw_artifact,
                command="validate",
                location_prefix=("artifacts", index),
            )
        except VaultError as exc:
            path = raw_artifact.get("path", "") if isinstance(raw_artifact, dict) else ""
            failures.append(
                {
                    "path": path if isinstance(path, str) else "",
                    "errors": exc.payload()["errors"],
                }
            )
            continue
        errors = validate_note(paths, Path(artifact.path), schema, registry)
        if errors:
            failures.append({"path": artifact.path, "errors": errors})
            continue
        clean_artifacts.append(artifact)

    if failures:
        return {
            "ok": False,
            "command": "validate",
            "batch": batch,
            "source": source,
            "failures": failures,
        }
    state = PipelineState(batch=batch, source=source, artifacts=clean_artifacts)
    return {
        "ok": True,
        "command": "validate",
        "batch": batch,
        "source": source,
        "artifacts": [artifact.model_dump() for artifact in state.artifacts],
    }
