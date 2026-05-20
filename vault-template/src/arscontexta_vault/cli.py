from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from arscontexta_vault.output import emit_json, run_json
from arscontexta_vault.paths import VaultPaths
from arscontexta_vault.seed import SeedMode, seed_source
from arscontexta_vault.validate import validate_all, validate_artifacts, validate_path

app = typer.Typer(add_completion=False, pretty_exceptions_enable=False)


@app.callback(invoke_without_command=True)
def root(ctx: typer.Context) -> None:
    if ctx.invoked_subcommand is None:
        emit_json(
            {
                "ok": True,
                "commands": [
                    "seed",
                    "validate",
                ],
            }
        )
        raise typer.Exit()


@app.command("seed")
def seed(
    source: Annotated[Path, typer.Option("--source", help="Source file to archive")],
    mode: Annotated[SeedMode, typer.Option("--mode", help="Processing mode")],
) -> None:
    run_json(lambda: seed_source(VaultPaths.discover(), source, mode))


@app.command("validate")
def validate(
    path: Annotated[Path | None, typer.Option("--path", help="Validate one note")] = None,
    all_notes: Annotated[bool, typer.Option("--all", help="Validate all notes")] = False,
    artifacts: Annotated[
        bool,
        typer.Option("--artifacts", help="Validate artifact paths from pipeline state on stdin"),
    ] = False,
) -> None:
    modes = [path is not None, all_notes, artifacts]
    if sum(modes) != 1:
        raise typer.BadParameter("use exactly one of --path, --all, or --artifacts")

    paths = VaultPaths.discover()
    if path is not None:
        run_json(lambda: validate_path(paths, path))
    elif all_notes:
        run_json(lambda: validate_all(paths))
    else:
        run_json(lambda: validate_artifacts(paths))


def main() -> None:
    app()
