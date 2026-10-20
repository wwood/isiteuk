1. When making user-facing changes, add a bullet to `CHANGELOG.md` under `## Unreleased` (create that heading if it does not exist yet). At release time, rename it to `## vX.Y.Z` — `bird-release-python` requires that heading before tagging. Release with `admin/release.sh X.Y.Z`.
2. When making changes, run tests with `pixi run test`.
