# Releasing

The `Prepare release` action computes the next generator version from pull request labels:

- `breaking` bumps the major version.
- `enhancement` bumps the minor version.
- `bug` and unclassified changes bump the patch version.
- `internal`, `ci`, `testing`, and `automations` do not enter the release calculation.

The first release is `1.0.0`. Its changelog is bootstrapped without inherited repository
history. Later releases use Rooster to inspect merged pull requests since the latest tag.

Run `Prepare release` from GitHub Actions. It opens a `release/X.Y.Z-BASE` pull request using
the repository's `GITHUB_TOKEN`. Approve its workflows, review the changelog and version,
then merge it through the usual branch protection. Require release branches to be up to date
with main before merging. The preparation commit records the main commit used for version
calculation. If main advances first, do not update the release branch: close the stale pull
request and run `Prepare release` again. The recorded base suffix gives the replacement a new
branch name.

Run `Publish release archive` and enter the merged preparation pull request number. The
action checks out that pull request's merge commit, runs the tests, builds the archive, and
verifies that it was merged onto the recorded base before creating the tag and GitHub release
in its final step. Commits merged afterward remain unreleased until the next version.
