from __future__ import annotations

from pathlib import Path
from typing import Annotated

from pydantic import AfterValidator, Field, StrictStr, field_validator

from vault.shared.model_validation import FrozenForbidExtras, nonblank


def _capture_tag(value: str) -> str:
    violations: list[str] = []
    if not value:
        violations.append("must not be empty")
    if value.startswith("#"):
        violations.append("must omit leading #")
    if any(character.isspace() for character in value):
        violations.append("must not contain spaces")
    if value.replace("/", "").isdigit():
        violations.append("must contain at least one non-numeric character")
    if violations:
        raise ValueError("; ".join(violations))
    return value


CaptureTag = Annotated[StrictStr, AfterValidator(_capture_tag)]


class CaptureInput(FrozenForbidExtras):
    source: Path
    title: StrictStr
    description: StrictStr
    tags: list[CaptureTag] = Field(default_factory=list)
    out: Path | None = None

    @field_validator("title")
    @classmethod
    def normalize_title(cls, value: str) -> str:
        return nonblank(value).strip()

    @field_validator("description")
    @classmethod
    def validate_description(cls, value: str) -> str:
        nonblank(value)
        if len(value) > 200:
            raise ValueError("exceeds max length: 200")
        return value
