# Releasing

The `Prepare release` action uses Convco and `.github/versionrc` to compute the next
generator version from conventional commits since the latest numeric tag:

- A breaking change bumps the major version.
- `feat` bumps the minor version.
- `fix` and every other commit type bump the patch version.

Squash merge pull requests so the checked conventional PR title becomes the commit on main.

To bootstrap a repository with no release tag, publish the merged pull request that introduced
the release files. It already carries version `1.0.0` and its recorded base commit. Run
`Publish release archive` with that pull request number; do not run `Prepare release` first.
If main advances before the pull request merges, rebase it onto current main and update
`.github/release-base-sha` to that main commit before squash merging.

Run `Prepare release` from GitHub Actions. It opens a `release/X.Y.Z-BASE` pull request using
the repository's `GITHUB_TOKEN`. Approve its workflows, review the version, then squash merge
it through the usual branch protection. Require release branches to be up to date with main
before merging. The preparation commit records the main commit used for version
calculation. If main advances first, do not update the release branch: close the stale pull
request and run `Prepare release` again. The recorded base suffix gives the replacement a new
branch name.

Run `Publish release archive` and enter the merged preparation pull request number. The
action checks out that pull request's merge commit, runs the tests, builds the archive, and
verifies that it was merged onto the recorded base before creating the tag and GitHub release
in its final step. Commits merged afterward remain unreleased until the next version.
