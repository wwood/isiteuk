1. When making user-facing changes, add a bullet to `CHANGELOG.md` under a `## vX.Y.Z` heading for the next release (create the heading if it does not exist yet). The release script (`pixi run -e dev bird-release-python --version X.Y.Z`) requires that section before tagging.
2. When making changes, run tests with `pixi run test`.
