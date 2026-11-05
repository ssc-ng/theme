#!/usr/bin/env python3
"""Check that the setup action moved the theme, and only the theme.

Usage: check_lock_float.py LOCK_BEFORE LOCK_AFTER EXPECTED_REVISION
"""
import re
import sys
from pathlib import Path

REVISION = re.compile(r"(remote: \S*/ssc-ng/theme\.git\n\s+revision: )(\S+)")
THEME_VERSION = re.compile(r"ssc-ng-theme \(\S+\)")


def main():
    before, after = (Path(p).read_text() for p in sys.argv[1:3])
    expected = sys.argv[3]
    problems = []

    found = REVISION.search(after)
    if not found or found.group(2) != expected:
        problems.append(f"theme is at {found and found.group(2)}, expected {expected}")

    strip = lambda text: THEME_VERSION.sub("ssc-ng-theme", REVISION.sub(r"\1", text)).splitlines()
    for old, new in zip(strip(before), strip(after)):
        if old != new:
            problems.append(f"other line changed: {old.strip()} -> {new.strip()}")
    if len(strip(before)) != len(strip(after)):
        problems.append("the lock file gained or lost lines")

    for problem in problems:
        print(problem)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
