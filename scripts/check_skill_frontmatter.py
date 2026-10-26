#!/usr/bin/env python3
"""check_skill_frontmatter.py — validate a SKILL.md's frontmatter shape.

Checks the hard requirements the Hermes skill validator enforces, plus the
soft fields every peer skill carries. Used by CI so a malformed SKILL.md fails
the build instead of failing silently at load time.

Usage:
    python3 check_skill_frontmatter.py path/to/SKILL.md
"""
from __future__ import annotations

import sys

MAX_DESCRIPTION_LENGTH = 1024
MAX_NAME_LENGTH = 64
MAX_CONTENT_CHARS = 100_000

REQUIRED_FIELDS = ("name", "description", "version", "author", "license")
SOFT_FIELDS = ("version", "author", "license")


def check(path: str) -> list:
    """Return a list of error strings. Empty list means the file is valid."""
    errors: list = []

    with open(path, encoding="utf-8") as fh:
        text = fh.read()

    if not text.startswith("---"):
        errors.append("frontmatter must start at byte 0 with '---'")
        return errors

    parts = text.split("---", 2)
    if len(parts) < 3:
        errors.append("frontmatter block is not closed")
        return errors

    frontmatter, body = parts[1], parts[2]

    if not body.strip():
        errors.append("body is empty")

    for field in REQUIRED_FIELDS:
        if field not in frontmatter:
            errors.append(f"missing frontmatter field '{field}'")

    name = description = None
    for line in frontmatter.splitlines():
        if line.startswith("name:") and name is None:
            name = line.split(":", 1)[1].strip().strip("'\"")
        if line.startswith("description:") and description is None:
            description = line.split(":", 1)[1].strip().strip("'\"")

    if name is not None:
        if len(name) > MAX_NAME_LENGTH:
            errors.append(f"name is {len(name)} chars (max {MAX_NAME_LENGTH})")
        if name != name.lower() or " " in name:
            errors.append(f"name '{name}' should be lowercase and hyphen-separated")

    if description is not None:
        if len(description) > MAX_DESCRIPTION_LENGTH:
            errors.append(
                f"description is {len(description)} chars (max {MAX_DESCRIPTION_LENGTH})"
            )
        if not description.lower().startswith("use when"):
            errors.append("description should start with 'Use when'")

    if len(text) > MAX_CONTENT_CHARS:
        errors.append(f"file is {len(text)} chars (max {MAX_CONTENT_CHARS})")

    return errors


def main(argv: list) -> int:
    if len(argv) != 2:
        print(f"usage: {argv[0]} <SKILL.md>", file=sys.stderr)
        return 2

    path = argv[1]
    errors = check(path)
    if errors:
        for err in errors:
            print(f"::error file={path}::{err}")
        return 1

    with open(path, encoding="utf-8") as fh:
        size = len(fh.read())
    print(f"OK {path} ({size} chars)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
