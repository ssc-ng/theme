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

Open a pull request. CI tests it, and the PR gets a Cloudflare preview of the test sites. Merging to `main` moves the `v1` branch once CI passes, and each site picks the change up on its next build.

Renaming or removing a CSS variable can break a site, so CI also builds the sites that use the theme and fails if a variable they use is gone.

## Test locally

Needs Docker and Python 3:

```bash
bash script/build-test-sites.sh
python3 -I -m unittest discover -s tests -t .
```
