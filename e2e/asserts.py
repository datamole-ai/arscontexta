from __future__ import annotations

import datetime
import json
import subprocess
from pathlib import Path

import yaml


def assert_vault_structure(vault: Path, vocab: dict) -> None:
    assert (vault / ".second-brain").exists(), ".second-brain marker missing"

    derivation = vault / "ops" / "derivation.md"
    assert derivation.exists(), "ops/derivation.md missing"
    assert derivation.stat().st_size > 0, "ops/derivation.md is empty"

    assert (vault / "ops" / "schema.yaml").exists(), "ops/schema.yaml missing"
    assert (vault / "self" / "identity.md").exists(), "self/identity.md missing"

    identity_text = (vault / "self" / "identity.md").read_text(encoding="utf-8")
    assert "{DOMAIN:" not in identity_text, "self/identity.md contains unsubstituted {DOMAIN: placeholder"

    note_collection = vocab["note_collection"]
    inbox = vocab["inbox"]
    archive = vocab["archive"]

    assert (vault / note_collection).is_dir(), f"note_collection dir '{note_collection}' missing"
    assert (vault / inbox).is_dir(), f"inbox dir '{inbox}' missing"
    assert (vault / archive).is_dir(), f"archive dir '{archive}' missing"

    assert (vault / note_collection / "index.md").exists(), f"{note_collection}/index.md missing"
    assert (vault / "CLAUDE.md").exists(), "CLAUDE.md missing"

    assert (vault / "pyproject.toml").exists(), "pyproject.toml (copied tooling) missing"
    assert (vault / "src" / "vault").is_dir(), "src/vault/ (copied tooling) missing"
    assert (vault / "uv.lock").exists(), "uv.lock missing"


def assert_schema_contract(vault: Path) -> None:
    schema = yaml.safe_load((vault / "ops" / "schema.yaml").read_text(encoding="utf-8"))
    required = set(schema.get("required", []))
    assert required == {
        "content_type", "granularity", "description", "created_at", "tags"
    }, f"schema required fields mismatch: {required}"

    enums = schema.get("enums", {})
    granularity = set(enums.get("granularity", []))
    assert granularity == {"structure", "capture"}, f"granularity enum mismatch: {granularity}"

    content_types = enums.get("content_type", [])
    assert "moc" in content_types, f"'moc' not in content_type enum: {content_types}"


def assert_skills_verbatim(vault: Path, repo_root: Path) -> None:
    for skill in ("seed", "structure", "capture", "connect", "verify", "process", "health"):
        vault_skill = vault / ".claude" / "skills" / skill / "SKILL.md"
        source_skill = repo_root / "skill-sources" / skill / "SKILL.md"
        assert vault_skill.exists(), f".claude/skills/{skill}/SKILL.md missing in vault"
        assert source_skill.exists(), f"skill-sources/{skill}/SKILL.md missing in repo"
        assert vault_skill.read_bytes() == source_skill.read_bytes(), (
            f".claude/skills/{skill}/SKILL.md differs from skill-sources/{skill}/SKILL.md"
        )
    assert (vault / ".claude" / "skills" / "ask" / "SKILL.md").exists(), (
        ".claude/skills/ask/SKILL.md missing"
    )


def assert_pinned_vocabulary(vocab: dict, expected: dict, schema: dict | None = None, content_type_includes: list[str] | None = None) -> None:
    for key, value in expected.items():
        actual = vocab.get(key)
        assert actual == value, (
            f"VOCABULARY DRIFT: vocab[{key!r}] = {actual!r}, expected {value!r}"
        )
    if content_type_includes and schema is not None:
        content_types = schema.get("enums", {}).get("content_type", [])
        for ct in content_type_includes:
            assert ct in content_types, (
                f"VOCABULARY DRIFT: expected content_type '{ct}' in schema enum {content_types}"
            )


def assert_git_initial(vault: Path) -> None:
    count_result = subprocess.run(
        ["git", "-C", str(vault), "rev-list", "--count", "HEAD"],
        capture_output=True, text=True, check=True,
    )
    assert int(count_result.stdout.strip()) >= 1, "no commits in vault git repo"

    log_result = subprocess.run(
        ["git", "-C", str(vault), "log", "--format=%s"],
        capture_output=True, text=True, check=True,
    )
    subjects = log_result.stdout.strip().splitlines()
    assert any("Initial vault generation" in s for s in subjects), (
        f"no commit with 'Initial vault generation' in subjects: {subjects}"
    )

    status_result = subprocess.run(
        ["git", "-C", str(vault), "status", "--porcelain"],
        capture_output=True, text=True, check=True,
    )
    assert status_result.stdout.strip() == "", (
        f"git working tree is not clean after setup: {status_result.stdout}"
    )


def run_validate_all(vault: Path, env: dict) -> dict:
    result = subprocess.run(
        ["uv", "run", "vault", "validate", "--all"],
        cwd=str(vault),
        env=env,
        capture_output=True,
        text=True,
    )
    try:
        payload = json.loads(result.stdout.strip())
    except json.JSONDecodeError as exc:
        raise AssertionError(
            f"uv run vault validate --all produced non-JSON output:\n{result.stdout}\n{result.stderr}"
        ) from exc
    assert payload.get("ok") is True, f"vault validate --all failed: {payload}"
    return payload


def snapshot_notes(vault: Path, vocab: dict) -> set[str]:
    note_collection = vault / vocab["note_collection"]
    if not note_collection.exists():
        return set()
    return {
        str(p.relative_to(vault))
        for p in note_collection.rglob("*.md")
    }


def assert_process_outcome(
    vault: Path,
    vocab: dict,
    run_cfg: dict,
    before: set[str],
    env: dict,
) -> None:
    fixture_name = Path(run_cfg["fixture"]).name
    inbox_dir = vault / vocab["inbox"]
    assert not (inbox_dir / fixture_name).exists(), (
        f"fixture {fixture_name} still in inbox after processing"
    )

    batch = run_cfg["expect"]["batch"]
    today = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
    archive_dir = vault / vocab["archive"]
    expected_archive = archive_dir / f"{today}-{batch}.md"
    assert expected_archive.exists(), (
        f"expected archive file {expected_archive.relative_to(vault)} not found"
    )

    log_result = subprocess.run(
        ["git", "-C", str(vault), "log", "-1", "--format=%s"],
        capture_output=True, text=True, check=True,
    )
    last_subject = log_result.stdout.strip()
    assert last_subject == f"pipeline: {batch}", (
        f"last commit subject is {last_subject!r}, expected 'pipeline: {batch}'"
    )

    show_result = subprocess.run(
        ["git", "-C", str(vault), "show", "--name-only", "--format=", "HEAD"],
        capture_output=True, text=True, check=True,
    )
    changed_files = show_result.stdout.strip().splitlines()
    archive_rel = str(expected_archive.relative_to(vault))
    assert any(archive_rel in f for f in changed_files), (
        f"archive path {archive_rel} not in HEAD commit files: {changed_files}"
    )
    after = snapshot_notes(vault, vocab)
    new_notes = after - before

    min_new_notes = run_cfg["expect"]["min_new_notes"]
    assert len(new_notes) >= min_new_notes, (
        f"expected >= {min_new_notes} new notes, got {len(new_notes)}: {new_notes}"
    )
    assert new_notes.intersection(changed_files), (
        f"HEAD commit does not include any new note paths; "
        f"new notes: {sorted(new_notes)}, committed files: {changed_files}"
    )

    run_validate_all(vault, env)

    status_result = subprocess.run(
        ["git", "-C", str(vault), "status", "--porcelain"],
        capture_output=True, text=True, check=True,
    )
    assert status_result.stdout.strip() == "", (
        f"working tree not clean after process: {status_result.stdout}"
    )
