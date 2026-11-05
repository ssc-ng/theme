#!/usr/bin/env python3
"""Print the branches a release should move: vX and vX.Y.

Each follows the highest release it covers, so a patch to an older minor moves
only that minor's branch. Fails if the tag is not a full version or differs
from the version in the gemspec.

Usage: git tag --list | release_targets.py TAG GEMSPEC
"""
import re
import sys
from pathlib import Path

VERSION = re.compile(r"v(\d+)\.(\d+)\.(\d+)")
GEM_VERSION = re.compile(r'spec\.version\s*=\s*"([^"]+)"')


def main():
    tag, gemspec = sys.argv[1:3]
    found = VERSION.fullmatch(tag)
    if not found:
        sys.exit(f"{tag} is not a full version, such as v1.2.3")

    gem_version = GEM_VERSION.search(Path(gemspec).read_text()).group(1)
    if gem_version != tag[1:]:
        sys.exit(f"tag {tag} differs from the gemspec's version {gem_version}")

    release = tuple(int(n) for n in found.groups())
    tags = (VERSION.fullmatch(line.strip()) for line in sys.stdin)
    versions = {tuple(int(n) for n in t.groups()) for t in tags if t} | {release}
    major, minor, _ = release

    if release == max(v for v in versions if v[0] == major):
        print(f"v{major}")
    if release == max(v for v in versions if v[:2] == (major, minor)):
        print(f"v{major}.{minor}")


if __name__ == "__main__":
    main()
