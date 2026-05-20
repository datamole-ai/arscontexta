from __future__ import annotations

from typing import Any


class VaultError(RuntimeError):
    """Expected operational failure that should be returned as command JSON."""

    def __init__(self, message: str, *, command: str | None = None, **fields: Any) -> None:
        super().__init__(message)
        self.message = message
        self.command = command
        self.fields = fields

    def payload(self) -> dict[str, Any]:
        payload: dict[str, Any] = {"ok": False}
        if self.command:
            payload["command"] = self.command
        payload.update(self.fields)
        if "errors" not in payload:
            payload["errors"] = [self.message]
        return payload
