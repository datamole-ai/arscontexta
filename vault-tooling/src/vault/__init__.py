from __future__ import annotations

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as package_version

_DISTRIBUTION_NAME = "dtml-second-brain"

try:
    __version__ = package_version(_DISTRIBUTION_NAME)
except PackageNotFoundError:
    __version__ = "0+unknown"
