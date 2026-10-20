#!/usr/bin/env python3
import argparse
import pathlib
import re
import sys


def section(text: str, heading: str) -> str | None:
    match = re.search(
        rf"(?ms)^##\s+{heading}\s*$(.*?)(?=^##\s|\Z)",
        text,
    )
    if not match:
        return None
    body = match.group(1).strip()
    return body or None


def notes_for(version: str, text: str) -> str | None:
    return section(text, rf"\[?v?{re.escape(version)}\]?") or section(
        text, r"Unreleased"
    )


def roll_unreleased(version: str, text: str) -> str | None:
    if section(text, rf"\[?v?{re.escape(version)}\]?"):
        return None
    if section(text, r"Unreleased") is None and not re.search(
        r"(?m)^##\s+Unreleased\s*$", text
    ):
        raise SystemExit(
            f"CHANGELOG.md has no ## Unreleased or ## v{version} section"
        )
    new, n = re.subn(
        r"(?m)^##\s+Unreleased\s*$",
        f"## Unreleased\n\n## v{version}",
        text,
        count=1,
    )
    if n != 1:
        raise SystemExit("failed to roll CHANGELOG.md ## Unreleased")
    return new


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("version")
    parser.add_argument(
        "--roll",
        action="store_true",
        help="Rename ## Unreleased to ## vVERSION in CHANGELOG.md",
    )
    args = parser.parse_args()
    path = pathlib.Path("CHANGELOG.md")
    text = path.read_text()
    if args.roll:
        rolled = roll_unreleased(args.version, text)
        if rolled is not None:
            path.write_text(rolled)
            text = rolled
            print(f"Rolled CHANGELOG.md ## Unreleased -> ## v{args.version}", file=sys.stderr)
    notes = notes_for(args.version, text)
    if not notes:
        raise SystemExit(f"no changelog notes for {args.version}")
    print(notes)


if __name__ == "__main__":
    main()
