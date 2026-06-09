from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from vault import __version__
from vault.output import emit_json, run_json
from vault.paths import VaultPaths
from vault.seed import seed_source
from vault.validate import validate_all, validate_artifacts, validate_path

APP_NAME = "vault"
HELP_OPTIONS = ["-h", "--help"]

app = typer.Typer(
    add_completion=False,
    context_settings={"help_option_names": HELP_OPTIONS},
    pretty_exceptions_enable=False,
)


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"{APP_NAME} {__version__}")
        raise typer.Exit()


@app.callback(invoke_without_command=True)
def root(
    ctx: typer.Context,
    version: Annotated[
        bool,
        typer.Option(
            "--version",
            callback=_version_callback,
            help="Show version and exit.",
            is_eager=True,
        ),
    ] = False,
) -> None:
    _ = version
    if ctx.invoked_subcommand is None:
        emit_json(
            {
                "ok": True,
                "commands": sorted(
                    command.name or command.callback.__name__
                    for command in app.registered_commands
                ),
            }
        )
        raise typer.Exit()


@app.command("seed")
def seed(
    source: Annotated[Path, typer.Option("--source", help="Source file to archive")],
) -> None:
    """Archive an inbox source and emit batch pipeline state."""
    run_json(lambda: seed_source(VaultPaths.discover(), source))


@app.command("validate")
def validate(
    path: Annotated[Path | None, typer.Option("--path", help="Validate one note")] = None,
    all_notes: Annotated[bool, typer.Option("--all", help="Validate all notes")] = False,
    artifacts: Annotated[
        bool,
        typer.Option("--artifacts", help="Validate artifact paths from pipeline state on stdin"),
    ] = False,
) -> None:
    """Validate notes against ops/schema.yaml."""
    modes = [path is not None, all_notes, artifacts]
    if sum(modes) != 1:
        raise typer.BadParameter("use exactly one of --path, --all, or --artifacts")

    def run() -> dict:
        paths = VaultPaths.discover()
        if path is not None:
            return validate_path(paths, path)
        if all_notes:
            return validate_all(paths)
        return validate_artifacts(paths)

    run_json(run)


def main() -> None:
    app()
