from __future__ import annotations

from vault.bootstrap import create_app

app = create_app()


def main() -> None:
    app()
