from __future__ import annotations

import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SYNC_SCRIPT = REPOSITORY_ROOT / "scripts" / "sync-generator-version.py"


def load_sync_module():
    spec = importlib.util.spec_from_file_location("sync_generator_version", SYNC_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {SYNC_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ReleaseVersionTest(unittest.TestCase):
    def test_sync_updates_only_generator_versions(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            (root / ".claude-plugin").mkdir()
            (root / "template").mkdir()
            (root / "pyproject.toml").write_text(
                '[project]\nname = "release-test"\nversion = "2.3.4"\n',
                encoding="utf-8",
            )
            (root / ".claude-plugin" / "plugin.json").write_text(
                '{"name": "second-brain", "version": "1.0.0"}\n',
                encoding="utf-8",
            )
            (root / "template" / ".second-brain").write_text(
                json.dumps(
                    {
                        "generator_version": "1.0.0",
                        "template_version": "1.0.0",
                        "runtime_version": "0.1.0",
                    }
                ),
                encoding="utf-8",
            )
            (root / "README.md").write_text(
                "https://example.test/releases/download/v1.0.0/second-brain.zip\n",
                encoding="utf-8",
            )

            module = load_sync_module()
            version = module.sync(root)

            plugin = json.loads((root / ".claude-plugin" / "plugin.json").read_text())
            manifest = json.loads((root / "template" / ".second-brain").read_text())
            self.assertEqual(version, "2.3.4")
            self.assertEqual(plugin["version"], "2.3.4")
            self.assertEqual(manifest["generator_version"], "2.3.4")
            self.assertEqual(manifest["template_version"], "1.0.0")
            self.assertEqual(manifest["runtime_version"], "0.1.0")
            self.assertIn(
                "/releases/download/2.3.4/second-brain.zip",
                (root / "README.md").read_text(),
            )

    def test_prepare_release_maps_conventional_bumps(self) -> None:
        script = REPOSITORY_ROOT / "scripts" / "prepare-release.sh"

        def select(released: str, conventional: str) -> str:
            result = subprocess.run(
                [
                    "bash",
                    "-c",
                    'source "$1"; select_release_bump "$2" "$3"',
                    "select-release-bump",
                    str(script),
                    released,
                    conventional,
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            return result.stdout.strip()

        self.assertEqual(select("1.2.3", "2.0.0"), "minor")
        self.assertEqual(select("1.2.3", "1.3.0"), "patch")
        self.assertEqual(select("1.2.3", "1.2.4"), "patch")
        self.assertEqual(select("1.2.3", "1.2.3"), "none")

        contents = script.read_text()
        self.assertIn("convco version --prefix '' --bump", contents)
        self.assertIn('uv version --bump "$bump"', contents)

    def test_release_workflows_bind_the_merge_to_the_preparation_base(self) -> None:
        prepare = (
            REPOSITORY_ROOT / ".github" / "workflows" / "prepare-release.yml"
        ).read_text()
        publish = (
            REPOSITORY_ROOT / ".github" / "workflows" / "release.yml"
        ).read_text()

        self.assertIn(".github/release-base-sha", prepare)
        self.assertIn('branch="release/$tag-${base:0:12}"', prepare)
        self.assertIn('if: steps.prepare.outputs.release == \'true\'', prepare)
        self.assertIn('merge_parent="$(git rev-parse "${RELEASE_SHA}^1")"', publish)
        self.assertIn('[ "$merge_parent" != "$prepared_base" ]', publish)
        self.assertNotIn("expected_head", publish)


if __name__ == "__main__":
    unittest.main()
