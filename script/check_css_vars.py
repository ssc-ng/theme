#!/usr/bin/env python3
"""Fail if a stylesheet uses a CSS variable that nothing defines.

Browsers silently ignore such a rule, so a theme change that renames a variable
would quietly remove color from a site. Uses with a fallback, var(--x, red),
are allowed.

Usage: check_css_vars.py CSS_FILE
"""
import re
import sys
from pathlib import Path


def undefined_vars(css):
    defined = set(re.findall(r"(--[\w-]+)\s*:", css))
    used = re.findall(r"var\(\s*(--[\w-]+)\s*([,)])", css)
    return sorted({name for name, end in used if end == ")" and name not in defined})


def main():
    missing = undefined_vars(Path(sys.argv[1]).read_text())
    for name in missing:
        print(f"undefined CSS variable: {name}")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
