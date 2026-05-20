from __future__ import annotations

import json
import sys
from typing import Any

import typer

from arscontexta_vault.errors import VaultError


def emit_json(value: Any) -> None:
    json.dump(value, sys.stdout, ensure_ascii=False, separators=(",", ":"))
    sys.stdout.write("\n")


def emit_error(exc: Exception) -> None:
    if isinstance(exc, VaultError):
        emit_json(exc.payload())
        return
    emit_json({"ok": False, "errors": [str(exc)]})


def run_json(fn):
    try:
        result = fn()
        emit_json(result)
        if isinstance(result, dict) and result.get("ok") is False:
            raise typer.Exit(1)
    except VaultError as exc:
        emit_error(exc)
        raise typer.Exit(1) from exc
