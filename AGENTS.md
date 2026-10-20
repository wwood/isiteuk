1. When making user-facing changes, add a bullet to `CHANGELOG.md` under `## Unreleased` (create that heading if it does not exist yet). `admin/release.sh X.Y.Z` renames that heading to `## vX.Y.Z` and tags the release.
2. When making changes, run tests with `pixi run test`.
