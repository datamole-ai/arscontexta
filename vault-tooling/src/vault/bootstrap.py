from __future__ import annotations

import typer

from vault.capture.command import register as register_capture
from vault.seed.command import register as register_seed
from vault.shared.output import emit_json
from vault.validation.command import register as register_validation

HELP_OPTIONS = ["-h", "--help"]


def create_app() -> typer.Typer:
    app = typer.Typer(
        add_completion=False,
        context_settings={"help_option_names": HELP_OPTIONS},
        pretty_exceptions_enable=False,
        rich_markup_mode=None,
    )

    @app.callback(invoke_without_command=True)
    def root(ctx: typer.Context) -> None:
        if ctx.invoked_subcommand is None:
            emit_json(
                {
                    "ok": True,
                    "commands": sorted(
                        command.name
                        for command in app.registered_commands
                        if command.name is not None
                    ),
                }
            )
            raise typer.Exit()

    register_seed(app)
    register_capture(app)
    register_validation(app)
    return app
