from __future__ import annotations

from pathlib import Path
from typing import Any

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StrictBool,
    StrictStr,
    field_validator,
    model_validator,
)

from vault.shared.model_validation import FrozenForbidExtras, FrozenIgnoreExtras, nonblank


class ValidateInput(FrozenForbidExtras):
    path: Path | None = None
    all_notes: StrictBool = False
    artifacts: StrictBool = False

    @model_validator(mode="after")
    def select_exactly_one_mode(self) -> ValidateInput:
        if sum((self.path is not None, self.all_notes, self.artifacts)) != 1:
            raise ValueError("use exactly one of --path, --all, or --artifacts")
        return self


class PipelineEnvelope(FrozenIgnoreExtras):
    batch: StrictStr
    source: StrictStr
    artifacts: list[Any]

    @field_validator("batch", "source")
    @classmethod
    def validate_pipeline_string(cls, value: str) -> str:
        return nonblank(value)


class Artifact(FrozenIgnoreExtras):
    kind: StrictStr
    path: StrictStr

    @field_validator("kind", "path")
    @classmethod
    def validate_artifact_string(cls, value: str) -> str:
        return nonblank(value)


class PipelineState(FrozenIgnoreExtras):
    batch: StrictStr
    source: StrictStr
    artifacts: list[Artifact]

    @field_validator("batch", "source")
    @classmethod
    def validate_pipeline_string(cls, value: str) -> str:
        return nonblank(value)


class VaultSchema(FrozenIgnoreExtras):
    required: list[StrictStr] = Field(default_factory=list)
    enums: dict[StrictStr, list[Any]] = Field(default_factory=dict)


class TagEntry(FrozenIgnoreExtras):
    tag: StrictStr
    meaning: StrictStr

    @field_validator("tag", "meaning")
    @classmethod
    def validate_text(cls, value: str) -> str:
        return nonblank(value)


class TagRegistryFile(FrozenIgnoreExtras):
    tags: list[TagEntry]


class NoteFrontmatter(BaseModel):
    """Known frontmatter fields; unknown fields remain available for validation."""

    model_config = ConfigDict(extra="allow", frozen=True)

    content_type: StrictStr | None = None
    granularity: StrictStr | None = None
    description: StrictStr | None = None
    tags: list[StrictStr] | None = None
    aliases: list[StrictStr] | None = None
    cssclasses: list[StrictStr] | None = None

    @field_validator("content_type", "granularity", mode="before")
    @classmethod
    def validate_required_text_when_present(cls, value: Any) -> Any:
        if value is None:
            raise ValueError("must be a string")
        return value

    @field_validator("tags", "aliases", "cssclasses", mode="before")
    @classmethod
    def validate_string_list_when_present(cls, value: Any) -> Any:
        if value is None:
            raise ValueError("must be a list")
        return value

    @field_validator("description")
    @classmethod
    def validate_description(cls, value: str | None) -> str:
        if value is None:
            raise ValueError("must be a non-empty string")
        nonblank(value)
        if len(value) > 200:
            raise ValueError("exceeds max length: 200")
        return value
