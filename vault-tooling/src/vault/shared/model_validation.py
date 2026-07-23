from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, ValidationError

from vault.shared.errors import VaultError


def nonblank(value: str) -> str:
    if not value.strip():
        raise ValueError("must be a non-empty string")
    return value


class FrozenForbidExtras(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class FrozenIgnoreExtras(BaseModel):
    model_config = ConfigDict(extra="ignore", frozen=True)


def _format_location(location: tuple[Any, ...]) -> str:
    result = ""
    for part in location:
        if isinstance(part, int):
            result += f"[{part}]"
        elif result:
            result += f".{part}"
        else:
            result = str(part)
    return result


def format_validation_errors(
    error: ValidationError,
    *,
    location_prefix: tuple[Any, ...] = (),
    inline_locations: frozenset[str] = frozenset(),
) -> list[str]:
    """Return stable, human-readable Pydantic errors without implementation detail."""

    messages: list[str] = []
    phrases = {
        "missing": "is required",
        "string_type": "must be a string",
        "bool_type": "must be a boolean",
        "list_type": "must be a list",
        "dict_type": "must be a mapping",
        "model_type": "must be an object",
        "json_invalid": "invalid JSON",
        "extra_forbidden": "is not allowed",
        "path_type": "must be a path",
    }
    for detail in error.errors(include_url=False, include_context=False, include_input=False):
        message = phrases.get(detail["type"], detail["msg"])
        if message.startswith("Value error, "):
            message = message.removeprefix("Value error, ")
        location = _format_location(location_prefix + tuple(detail["loc"]))
        separator = " " if location in inline_locations else ": "
        messages.append(f"{location}{separator}{message}" if location else message)
    return messages


def validate_model[ModelT: BaseModel](
    model: type[ModelT],
    value: Any,
    *,
    command: str | None = None,
    location_prefix: tuple[Any, ...] = (),
    inline_locations: frozenset[str] = frozenset(),
    json_input: bool = False,
    **fields: Any,
) -> ModelT:
    """Validate untrusted data and expose failures as a command-safe ``VaultError``."""

    try:
        if json_input:
            return model.model_validate_json(value)
        return model.model_validate(value)
    except ValidationError as exc:
        messages = format_validation_errors(
            exc,
            location_prefix=location_prefix,
            inline_locations=inline_locations,
        )
        raise VaultError(
            messages[0] if messages else "invalid input",
            command=command,
            errors=messages or ["invalid input"],
            **fields,
        ) from exc
