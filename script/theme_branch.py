#!/usr/bin/env python3
"""Print the theme branch a site's Gemfile follows, or nothing if it pins a tag.

Fails if the Gemfile is missing or doesn't use the theme, because CI must not
take either for a site it has no need to test.

Usage: theme_branch.py GEMFILE
"""
import re
import sys
from pathlib import Path

LINE = re.compile(r"""^\s*gem\s+['"]ssc-ng-theme['"](.*)$""", re.M)
BRANCH = re.compile(r"""branch:\s*['"]([^'"]+)['"]""")


def main():
    path = Path(sys.argv[1])
    if not path.exists():
        sys.exit(f"{path} does not exist")
    line = LINE.search(path.read_text())
    if not line:
        sys.exit(f"{path} does not use ssc-ng-theme")
    branch = BRANCH.search(line.group(1))
    print(branch.group(1) if branch else "")


if __name__ == "__main__":
    main()
