#!/usr/bin/env python3
"""Release script for isiteuk.

Usage:
    pixi run python admin/release.py 0.1.0
"""

import re
import subprocess
import sys
import os

ROOT = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')


def run(cmd):
    subprocess.run(cmd, shell=True, check=True)


def replace_in_file(path, pattern, replacement):
    with open(path) as f:
        content = f.read()
    new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
    if new_content == content:
        raise Exception(f"Pattern '{pattern}' not found in {path}")
    with open(path, 'w') as f:
        f.write(new_content)
    print(f"  Updated {path}")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: pixi run python admin/release.py <version>  e.g. 0.1.0")
        sys.exit(1)

    version = sys.argv[1]

    yes_no = input(
        "Did you run the expensive tests first? (y/n)\n\n"
        "  pixi run test-expensive\n\n"
    )
    if yes_no != 'y':
        raise Exception("Please run the expensive tests first")

    yes_no = input("Did you update CHANGELOG.md? (y/n) ")
    if yes_no != 'y':
        raise Exception("Please update CHANGELOG.md")

    print(f"\nUpdating version to {version} ...")

    replace_in_file(
        os.path.join(ROOT, 'isiteuk', '__init__.py'),
        r"__version__ = '[^']*'",
        f"__version__ = '{version}'",
    )
    replace_in_file(
        os.path.join(ROOT, 'pyproject.toml'),
        r'^version = "[^"]*"',
        f'version = "{version}"',
    )
    replace_in_file(
        os.path.join(ROOT, 'pixi.toml'),
        r'^version = "[^"]*"',
        f'version = "{version}"',
    )
    print("\nChecking git status ...")
    result = subprocess.run(
        'git diff --shortstat 2>/dev/null | tail -n1',
        shell=True, capture_output=True, text=True,
    )
    if result.stdout.strip():
        print(f'Committing version files')
        run(f'git commit -a -m "v{version}"')
    else:
        print("No uncommitted changes after version update — nothing to commit")

    print(f"Tagging release as v{version}")
    run(f'git tag v{version}')

    print(f"""
Release v{version} prepared. Next steps:

  git push && git push --tags
  → GitHub Actions will build and publish to PyPI automatically.

  Once the metapackage is on Zenodo:
  → Update DATA_DOI in isiteuk/metapackage.py, then release again.

  Once on PyPI, submit to bioconda:
  → Update sha256 in conda.recipe/meta.yaml and open a PR to bioconda-recipes.
""")
