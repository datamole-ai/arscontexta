from __future__ import annotations

import json
import subprocess
import tempfile
import tomllib
import unittest
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = REPOSITORY_ROOT / "template" / ".second-brain"
RELEASE_PROJECT_PATH = REPOSITORY_ROOT / "pyproject.toml"
EXPECTED_FIELDS = {
    "generator_version",
    "template_version",
    "runtime_version",
}


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


class VersionManifestTest(unittest.TestCase):
    def test_manifest_matches_generator_and_runtime_sources(self) -> None:
        manifest = read_json(MANIFEST_PATH)
        plugin = read_json(REPOSITORY_ROOT / ".claude-plugin" / "plugin.json")
        generator_version = read_project_version(RELEASE_PROJECT_PATH)

        self.assertEqual(set(manifest), EXPECTED_FIELDS)
        for field in EXPECTED_FIELDS:
            with self.subTest(field=field):
                self.assertIsInstance(manifest[field], str)
                self.assertTrue(manifest[field])

        self.assertEqual(plugin["version"], generator_version)
        self.assertEqual(manifest["generator_version"], generator_version)
        self.assertIn(
            f"/releases/download/{generator_version}/second-brain.zip",
            (REPOSITORY_ROOT / "README.md").read_text(encoding="utf-8"),
        )
        self.assertEqual(
            manifest["runtime_version"],
            read_project_version(REPOSITORY_ROOT / "vault-tooling" / "pyproject.toml"),
        )

    def test_copy_path_preserves_manifest_and_runtime_version(self) -> None:
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

            manifest = read_json(vault_root / ".second-brain")
            self.assertEqual(
                manifest["runtime_version"],
                read_project_version(vault_root / "ops" / "tooling" / "pyproject.toml"),
            )


if __name__ == "__main__":
    unittest.main()
