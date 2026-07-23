from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from vault.capture.application import capture_note
from vault.capture.models import CaptureInput
from vault.shared.model_validation import validate_model
from vault.shared.output import run_json
from vault.shared.paths import VaultPaths


def capture(
    source: Annotated[
        Path, typer.Option("--source", help="Archived source file to preserve verbatim")
    ],
    title: Annotated[str, typer.Option("--title", help="Note title")],
    description: Annotated[str, typer.Option("--description", help="Note description")],
    tag: Annotated[
        list[str] | None, typer.Option("--tag", help="Tag for the note frontmatter (repeatable)")
    ] = None,
    out: Annotated[
        Path | None, typer.Option("--out", help="Note path to write instead of the slugged title")
    ] = None,
) -> None:
    """Write a verbatim note that embeds an archived source byte-exactly."""

    def run() -> dict:
        request = validate_model(
            CaptureInput,
            {
                "source": source,
                "title": title,
                "description": description,
                "tags": list(tag or []),
                "out": out,
            },
            command="capture",
            inline_locations=frozenset({"description"}),
            retryable=True,
        )
        return capture_note(VaultPaths.discover(), request)

    run_json(run)


def register(app: typer.Typer) -> None:
    app.command("capture")(capture)
