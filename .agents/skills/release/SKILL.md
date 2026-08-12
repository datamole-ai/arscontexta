---
name: release
description: Prepare, merge, publish, and verify the next Second Brain release. Use only when the user explicitly asks to release this repository.
---

# Release

Operate on `datamole-ai/arscontexta` with `gh`. Do not edit the working tree.

1. Resume an active release workflow or open `release/*` pull request instead of creating a duplicate.
2. If neither exists, dispatch `prepare-release.yml` on `main`, capture its run URL, and watch it with `--exit-status`. If it creates no pull request because there are no releasable commits, report that and stop.
3. Resolve exactly one open `release/*` pull request targeting `main`. Watch its checks, read its current `headRefOid`, squash-merge it with `--match-head-commit`, and wait until GitHub reports `MERGED`.
4. Dispatch `release.yml` on `main` with `release_pr=<number>`. Capture and watch that run with `--exit-status`.
5. Verify the latest release matches the prepared version and contains `second-brain.zip` and `second-brain.zip.sha256`. Download both through `/releases/latest/download/`, check the SHA-256 file, test the ZIP, and report the pull request, workflow, and release URLs.
