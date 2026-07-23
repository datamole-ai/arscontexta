from __future__ import annotations

from pathlib import Path

from vault.shared.model_validation import FrozenForbidExtras


class SeedInput(FrozenForbidExtras):
    source: Path
