#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
    echo "Usage: admin/release.sh <version>  e.g. 0.0.3" >&2
    exit 1
fi

version=$1

pixi run -e dev bird-release-python --version "$version"

cat <<EOF

Next steps:
  git push && git push --tags

  GitHub Actions will publish to PyPI and open a draft GitHub release
  filled from CHANGELOG.md. Review that draft and publish it.

  Once on PyPI, submit to bioconda: update sha256 in conda.recipe/meta.yaml
  and open a PR to bioconda-recipes.

  If a new metapackage was uploaded to Zenodo: update DATA_DOI in
  isiteuk/metapackage.py, then release again.
EOF
