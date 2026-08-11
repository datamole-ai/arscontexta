from __future__ import annotations

import argparse
import json
import re
import tomllib
from pathlib import Path

VERSION_PATTERN = re.compile(r"[0-9]+\.[0-9]+\.[0-9]+")
DOWNLOAD_PATTERN = re.compile(r"(releases/download/)v?[0-9]+\.[0-9]+\.[0-9]+(/second-brain\.zip)")


def project_version(root: Path) -> str:
    with (root / "pyproject.toml").open("rb") as stream:
        version = tomllib.load(stream)["project"]["version"]
    if not isinstance(version, str) or VERSION_PATTERN.fullmatch(version) is None:
        raise ValueError(f"invalid generator version: {version!r}")
    return version


def update_json_field(path: Path, field: str, version: str) -> None:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict) or field not in value:
        raise ValueError(f"missing {field!r} in {path}")
    value[field] = version
    path.write_text(f"{json.dumps(value, indent=2)}\n", encoding="utf-8")


def sync(root: Path) -> str:
    version = project_version(root)
    update_json_field(root / ".claude-plugin" / "plugin.json", "version", version)
    update_json_field(root / "template" / ".second-brain", "generator_version", version)

    readme_path = root / "README.md"
    readme = readme_path.read_text(encoding="utf-8")
    readme, replacements = DOWNLOAD_PATTERN.subn(rf"\g<1>{version}\g<2>", readme)
    if replacements != 1:
        raise ValueError(f"expected one versioned release URL in {readme_path}")
    readme_path.write_text(readme, encoding="utf-8")
    return version


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("repository", nargs="?", type=Path, default=Path(__file__).parents[1])
    arguments = parser.parse_args()

    root = arguments.repository.resolve()
    print(sync(root))


if __name__ == "__main__":
    main()
