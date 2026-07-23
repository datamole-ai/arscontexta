from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from vault.seed.application import seed_source
from vault.seed.models import SeedInput
from vault.shared.model_validation import validate_model
from vault.shared.output import run_json
from vault.shared.paths import VaultPaths


def seed(
    source: Annotated[Path, typer.Option("--source", help="Source file to archive")],
) -> None:
    """Archive an inbox source and emit batch pipeline state."""

    def run() -> dict:
        request = validate_model(SeedInput, {"source": source}, command="seed")
        return seed_source(VaultPaths.discover(), request)

    run_json(run)


def register(app: typer.Typer) -> None:
    app.command("seed")(seed)
