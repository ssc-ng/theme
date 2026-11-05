#!/usr/bin/env bash
# Build every test site with the gem from this checkout, twice: under a base
# path (_preview/<name>/, as on project Pages) and with an empty one
# (_preview-root/<name>/, as on a Cloudflare preview).
set -euo pipefail
cd "$(dirname "$0")/.."

docker run --rm -v "$PWD:/w" -v ssc-theme-bundle:/usr/local/bundle -w /w \
  -e JEKYLL_ENV=production -e HOST_IDS="$(id -u):$(id -g)" ruby:3.3 bash -c '
    set -euo pipefail
    status=0
    rm -rf _preview _preview-root
    for dir in test-sites/*/; do
      name=$(basename "$dir")
      (
        cd "$dir"
        bundle install --quiet
        bundle exec jekyll build --quiet --baseurl "/$name" --destination "/w/_preview/$name"
        bundle exec jekyll build --quiet --baseurl "" --destination "/w/_preview-root/$name"
      ) || status=$?
    done
    chown -R "$HOST_IDS" _preview _preview-root test-sites 2>/dev/null || true
    exit "$status"
  '
