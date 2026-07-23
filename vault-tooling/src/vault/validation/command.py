from __future__ import annotations

import sys
from pathlib import Path
from typing import Annotated

import typer
from pydantic import ValidationError

from vault.shared.output import run_json
from vault.shared.paths import VaultPaths
from vault.validation.application import validate_all, validate_artifacts, validate_path
from vault.validation.models import ValidateInput


def validate(
    path: Annotated[Path | None, typer.Option("--path", help="Validate one note")] = None,
    all_notes: Annotated[bool, typer.Option("--all", help="Validate all notes")] = False,
    artifacts: Annotated[
        bool,
        typer.Option("--artifacts", help="Validate artifact paths from pipeline state on stdin"),
    ] = False,
) -> None:
    """Validate notes against ops/schema.yaml."""
    try:
        request = ValidateInput(path=path, all_notes=all_notes, artifacts=artifacts)
    except ValidationError as exc:
        raise typer.BadParameter("use exactly one of --path, --all, or --artifacts") from exc

    def run() -> dict:
        paths = VaultPaths.discover()
        if request.path is not None:
            return validate_path(paths, request.path)
        if request.all_notes:
            return validate_all(paths)
        return validate_artifacts(paths, sys.stdin)

    run_json(run)


def register(app: typer.Typer) -> None:
    app.command("validate")(validate)
