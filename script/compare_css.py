#!/usr/bin/env python3
"""List CSS selectors lost or added between two builds of a site.

Moving a site's styles into the theme should lose nothing, so a lost selector
is a failure. An added one is only reported: the theme adds rules on purpose.

Usage: compare_css.py BEFORE.css AFTER.css
"""
import re
import sys
from pathlib import Path


def split_selectors(text):
    """Split on commas, except those inside parentheses, as in :not(a, b)."""
    parts, depth, current = [], 0, ""
    for char in text:
        depth += (char == "(") - (char == ")")
        if char == "," and depth == 0:
            parts.append(current)
            current = ""
        else:
            current += char
    return parts + [current]


def normalize(selector):
    selector = re.sub(r"\s*([>+~,])\s*", r"\1", selector.strip())
    return re.sub(r"\s+", " ", selector)


def selectors(css):
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    found = set()
    for head in re.findall(r"([^{};]+)\{", css):
        head = head.strip()
        if head.startswith("@") or re.fullmatch(r"[\d.%,\s]+|from|to", head):
            continue  # at-rules and keyframe stops are not selectors
        found.update(normalize(s) for s in split_selectors(head))
    return found


def main():
    before, after = (selectors(Path(p).read_text()) for p in sys.argv[1:3])
    lost, added = sorted(before - after), sorted(after - before)
    for selector in lost:
        print(f"lost: {selector}")
    for selector in added:
        print(f"added: {selector}")
    return 1 if lost else 0


if __name__ == "__main__":
    sys.exit(main())
