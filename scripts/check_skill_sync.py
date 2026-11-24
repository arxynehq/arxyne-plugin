#!/usr/bin/env python3
"""Fail when the skill bundled in this plugin is not the one published on ClawHub.

Why this exists: this repository and ClawHub both ship a file called SKILL.md, and
nothing compared them. The copy here stayed at the first 40-line draft while the
published skill grew to 180 lines, so a plugin user and a ClawHub user were told
different things by the same product.

The published skill is the reference. Copy it here when it changes; never edit
this copy alone.
"""

from __future__ import annotations

import difflib
import shutil
import subprocess
import sys
from pathlib import Path

PUBLISHED = "@arxyne/arxyne"
LOCAL = Path("skills/arxyne/SKILL.md")


def main() -> int:
    if not LOCAL.is_file():
        print(f"FAIL: {LOCAL} is missing")
        return 1
    if not shutil.which("clawhub"):
        print("FAIL: clawhub is not on PATH; npm install -g clawhub")
        return 1

    fetched = subprocess.run(
        ["clawhub", "inspect", PUBLISHED, "--file", "SKILL.md"],
        capture_output=True,
        text=True,
    )
    if fetched.returncode != 0 or not fetched.stdout.strip():
        print(f"FAIL: could not read the published skill: {fetched.stderr.strip()[:400]}")
        return 1

    here = LOCAL.read_text(encoding="utf-8")
    there = fetched.stdout
    if here == there:
        print(f"PASS: {LOCAL} is the published {PUBLISHED} skill, byte for byte")
        return 0

    diff = list(
        difflib.unified_diff(
            there.splitlines(keepends=True),
            here.splitlines(keepends=True),
            fromfile=f"published {PUBLISHED}",
            tofile=str(LOCAL),
            n=2,
        )
    )
    print("FAIL: the bundled skill has drifted from the published one")
    print("".join(diff[:60]))
    if len(diff) > 60:
        print(f"... {len(diff) - 60} more diff lines")
    print()
    print("Fix: copy the published text over this copy, or publish a new version first.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
