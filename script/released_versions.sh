#!/usr/bin/env bash
# Print the version on each release branch, such as v1.2.0, for release_targets.py.
# Branches rather than tags, as a branch only moves once a release has passed CI,
# while a tag can be a typo or a release that failed.
set -euo pipefail

git for-each-ref --format='%(refname:short)' 'refs/remotes/origin/v*' |
  grep -E '^origin/v[0-9]+(\.[0-9]+)?$' |
  while read -r branch; do
    version=$(git show "$branch:ssc-ng-theme.gemspec" | sed -n 's/.*spec\.version *= *"\(.*\)".*/\1/p')
    echo "v$version"
  done || true
