# SSC-NG theme

The shared look of the SSC-NG websites: brand colors, code font and logo. It is a Jekyll plugin used alongside a site's real theme, so Just the Docs is not forked. See the [design](docs/superpowers/specs/2026-11-04-shared-theme-design.md).

## Use it in a site

```ruby
# Gemfile
gem "just-the-docs", "~> 0.10"
gem "ssc-ng-theme", github: "ssc-ng/theme", branch: "v1"
```

```yaml
# _config.yml
theme: just-the-docs
plugins:
  - ssc-ng-theme
```

In the site's workflow, replace the `ruby/setup-ruby` step with the following, which takes the newest theme on every build:

```yaml
- uses: ssc-ng/theme/.github/actions/setup@v1
  with:
    working-directory: site
```

The plugin sets `color_scheme` and `logo`, replacing any local value. Page-specific styles stay in the site's `_sass/custom/custom.scss`, and should use the CSS variables in [`_sass/ssc-ng/_brand.scss`](_sass/ssc-ng/_brand.scss) rather than fixed colors or fonts.

## Change the theme

Open a pull request. CI tests it, and the PR gets a Cloudflare preview of the test sites. Merging to `main` does not reach any site. That takes a release.

Renaming or removing a CSS variable can break a site, so CI also builds the sites that use the theme and fails if a variable they use is gone.

## Versions

Sites choose how closely to follow the theme, in their `Gemfile`:

| Gemfile | Follows | Gets |
| --- | --- | --- |
| `branch: "v1"` | The highest `v1.x.y` | Every release in `v1`. This is the normal choice. |
| `branch: "v1.0"` | The highest `v1.0.x` | Fixes only |
| `tag: "v1.0.3"` | That release | Nothing new, until the site changes the line |

Choosing the next version:

- **Patch, `v1.0.1`:** a fix that doesn't change the intended look.
- **Minor, `v1.1.0`:** a change to the look, or a new style or variable, that needs no change in the sites.
- **Major, `v2.0.0`:** a site has to change to keep working, as when a CSS variable is renamed or removed. Sites on `v1` stay there until they move.

## Release a version

1. Set the new version in `ssc-ng-theme.gemspec` by pull request, and merge it.
2. Tag that commit and push the tag:

   ```bash
   git tag -a v1.1.0 -m "v1.1.0" && git push origin v1.1.0
   ```

CI runs its tests on the tag. If they pass, it moves `v1` and `v1.1` to the release, and each site picks it up on its next build. If they fail, or the tag differs from the gemspec's version, no branch moves.

A branch only moves to the highest release it covers, so `v1.0.4` moves `v1.0` but not `v1` once `v1.1.0` exists. To fix an older minor, branch from its `v1.0` branch, set the version there, and tag the fix. Branches never move backward: to undo a bad release, release a fix with a higher version.

## Test locally

Needs Docker and Python 3:

```bash
bash script/build-test-sites.sh
python3 -I -m unittest discover -s tests -t .
```
