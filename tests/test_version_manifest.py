from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import tomllib
import unittest
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = REPOSITORY_ROOT / "template" / ".second-brain"
PRODUCT_NAME = "second-brain-release-tools"
RUNTIME_NAME = "dtml-second-brain"


def read_json(path: Path) -> dict[str, object]:
    with path.open(encoding="utf-8") as stream:
        value = json.load(stream)
    if not isinstance(value, dict):
        raise TypeError(f"expected a JSON object in {path}")
    return value


def read_project_version(path: Path) -> str:
    with path.open("rb") as stream:
        value = tomllib.load(stream)["project"]["version"]
    if not isinstance(value, str):
        raise TypeError(f"expected project.version to be a string in {path}")
    return value


def read_locked_version(path: Path, package_name: str) -> str:
    with path.open("rb") as stream:
        packages = tomllib.load(stream)["package"]
    matches = [package["version"] for package in packages if package["name"] == package_name]
    if len(matches) != 1 or not isinstance(matches[0], str):
        raise ValueError(f"expected one locked version for {package_name!r} in {path}")
    return matches[0]


class VersionManifestTest(unittest.TestCase):
    def test_every_product_version_matches_the_root_project(self) -> None:
        version = read_project_version(REPOSITORY_ROOT / "pyproject.toml")
        plugin = read_json(REPOSITORY_ROOT / ".claude-plugin" / "plugin.json")
        marketplace = read_json(REPOSITORY_ROOT / ".claude-plugin" / "marketplace.json")

        self.assertEqual(read_json(MANIFEST_PATH), {"version": version})
        self.assertEqual(plugin["version"], version)
        self.assertEqual(marketplace["metadata"]["version"], version)
        self.assertEqual(
            read_project_version(REPOSITORY_ROOT / "vault-tooling" / "pyproject.toml"),
            version,
        )
        self.assertEqual(read_locked_version(REPOSITORY_ROOT / "uv.lock", PRODUCT_NAME), version)
        self.assertEqual(
            read_locked_version(REPOSITORY_ROOT / "vault-tooling" / "uv.lock", RUNTIME_NAME),
            version,
        )

    def test_copy_path_preserves_the_product_version(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            vault_root = Path(temporary_directory)
            result = subprocess.run(
                [
                    "bash",
                    str(REPOSITORY_ROOT / "skills" / "setup" / "scripts" / "copy-template.sh"),
                    str(vault_root),
                ],
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(
                (vault_root / ".second-brain").read_bytes(),
                MANIFEST_PATH.read_bytes(),
            )

            version = read_json(vault_root / ".second-brain")["version"]
            self.assertEqual(
                read_project_version(vault_root / "ops" / "tooling" / "pyproject.toml"),
                version,
            )
            self.assertEqual(
                read_locked_version(vault_root / "ops" / "tooling" / "uv.lock", RUNTIME_NAME),
                version,
            )

    def test_release_sync_updates_every_product_version(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            repository = Path(temporary_directory)
            for relative_path in [
                Path(".claude-plugin/plugin.json"),
                Path(".claude-plugin/marketplace.json"),
                Path("template/.second-brain"),
                Path("vault-tooling/pyproject.toml"),
                Path("vault-tooling/uv.lock"),
            ]:
                target = repository / relative_path
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(REPOSITORY_ROOT / relative_path, target)

            result = subprocess.run(
                [
                    "bash",
                    "-c",
                    'source "$1"; cd "$2"; sync_product_version "$3"',
                    "sync-product-version",
                    str(REPOSITORY_ROOT / "scripts" / "prepare-release.sh"),
                    str(repository),
                    "2.3.4",
                ],
                check=False,
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(
                read_json(repository / "template" / ".second-brain"),
                {"version": "2.3.4"},
            )
            self.assertEqual(
                read_json(repository / ".claude-plugin" / "plugin.json")["version"],
                "2.3.4",
            )
            self.assertEqual(
                read_json(repository / ".claude-plugin" / "marketplace.json")["metadata"][
                    "version"
                ],
                "2.3.4",
            )
            self.assertEqual(
                read_project_version(repository / "vault-tooling" / "pyproject.toml"),
                "2.3.4",
            )
            self.assertEqual(
                read_locked_version(repository / "vault-tooling" / "uv.lock", RUNTIME_NAME),
                "2.3.4",
            )


if __name__ == "__main__":
    unittest.main()
