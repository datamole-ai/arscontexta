from __future__ import annotations

import shutil
from pathlib import Path

import pytest
import yaml

from asserts import (
    assert_git_initial,
    assert_pinned_vocabulary,
    assert_process_outcome,
    assert_schema_contract,
    assert_skills_verbatim,
    assert_vault_structure,
    run_validate_all,
    snapshot_notes,
)
from conftest import REPO_ROOT
from driver import run_process

pytestmark = pytest.mark.skipif(
    shutil.which("claude") is None,
    reason="claude CLI not found; skipping e2e tests",
)


def test_setup(generated_vault):
    scenario, setup_result, run_dir, env = generated_vault
    vault = setup_result.vault
    vocab = setup_result.vocabulary

    schema = yaml.safe_load((vault / "ops" / "schema.yaml").read_text(encoding="utf-8"))

    assert_vault_structure(vault, vocab)
    assert_schema_contract(vault)
    assert_skills_verbatim(vault, REPO_ROOT)
    assert_pinned_vocabulary(
        vocab,
        scenario.expect_vocabulary,
        schema=schema,
        content_type_includes=scenario.expect_content_type_includes,
    )
    assert_git_initial(vault)
    run_validate_all(vault, env)


def test_process(generated_vault):
    scenario, setup_result, run_dir, env = generated_vault
    vault = setup_result.vault
    vocab = setup_result.vocabulary

    for run_cfg in scenario.process_runs:
        (vault / ".obsidian").mkdir(exist_ok=True)

        fixture_src = Path(__file__).parent / "scenarios" / scenario.name / run_cfg["fixture"]
        dest = vault / vocab["inbox"] / fixture_src.name
        shutil.copy(fixture_src, dest)

        before = snapshot_notes(vault, vocab)
        rel_source = f"{vocab['inbox']}/{dest.name}"
        turn = run_process(
            vault=vault,
            rel_source=rel_source,
            mode=run_cfg["mode"],
            env=env,
            run_dir=run_dir,
        )

        assert not turn.is_error, f"/process turn failed: {turn.text}"
        assert_process_outcome(vault, vocab, run_cfg, before, env)
