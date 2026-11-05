# Shared SSC-NG theme: design

Status: proposed, 2026-11-04. "Decided" marks choices made by Lars Vilhuber. "Builder's call" marks defaults proposed by the author that can be changed.

## Why

The SSC-NG sites share a look that is coordinated by hand. `archive`, `ssc2` and `docker-stata` each carry an identical block of color settings and 83 identical lines of other styles, and changes must be copied between repos.

A single shared theme replaces this. A change made once reaches every site on its next build.

## Goals

1. **One source for the brand:** colors, fonts and logo live only in `ssc-ng/theme`.
2. **No fork:** Just the Docs stays an ordinary dependency and keeps receiving upstream updates.
3. **Automatic updates:** no per-site merge is needed for a theme change to reach a site. (Decided)
4. **Bad changes contained:** a broken theme change does not take a site down.
5. **`ssc-ng.net` included:** it shares the brand while keeping its own theme and layout. (Decided: desirable, and second in order)

## Non-goals

- **Layout:** the Just the Docs layout stays as it is. (Decided)
- **`stata-keyword-crosswalk`:** not included in this round. (Decided)
- **Replacing the main site's theme:** Just the Docs is not the right theme for `ssc-ng.net`. (Decided)
- **Rebuild triggers:** a theme change does not start site builds. Sites wait for their next build. (Decided: "on next build")
- **Dark mode:** not added. (Builder's call: the sites are light-only today)
- **RubyGems:** the gem is not published there. Sites load it from GitHub. (Builder's call)

## Anti-goals

This project has failed, even if it technically works, if:

- A site's brand colors, logo or font can still drift from the theme because they are set locally.
- The theme becomes a fork of Just the Docs, with copied layouts to maintain.
- Page-specific styles, such as the `archive` timeline or the `docker-stata` tabs, move into the theme.
- Moving to the theme changes how a page looks beyond the approved changes below.

## Approved look

Approved from real builds of the `archive` site.

### Colors: option A, Teal (Decided)

| Role | Value | Today's equivalent |
| --- | --- | --- |
| Primary: headings, primary buttons, selections | `#0E6480` | `--navy` `#123a63` |
| Soft background | `#E3F1F5` | `--navy-soft` `#e8eef5` |
| Links and accent | `#0B6E8E` | `--accent` `#1b6fae` |
| Hover | `#C9E3EA` | `#cfdcea` |
| Partial state (History timeline) | `#6FA9BC` | `#6f8fb3` |
| Sidebar background | `#F4F8F9` | Theme default |
| Results-bar text | `#DDF0F5` | `#dce7f2` |
| Console keyword (`docker-stata` only, not shown in the approved builds; builder's call, check in its preview) | `#8FD3E6` | `#8fc1ec` |
| Primary as RGB, for translucent shadows and fills | `14,100,128` | `18,58,99` |

The console and warning colors in the current color block, such as `--console-bg` and `--console-good`, stay as they are, and `--ink`, `--muted` and `--line` carry over unchanged.

### Code font (Decided)

- JetBrains Mono **bold** (700) on inline code and code blocks.
- JetBrains Mono regular (400) on other monospace text, such as package names and letter buttons, as in the approved builds. (Builder's call on the weight, based on what was approved)
- Font files ship with the gem and are self-hosted, so no visitor request goes to Google. Include the font's OFL license. (Builder's call)

### Logo (Decided)

- Use `ssc-ng-gears-v2-400.png`, `-180.png` and `-64.png` from [`ssc-ng.github.io` PR #7](https://github.com/ssc-ng/ssc-ng.github.io/pull/7). Build them into the gem, and also serve the small sizes as the favicon and Apple touch icon on the Just the Docs sites. (Builder's call on the favicon: the sites have no consistent icon today)
- On Just the Docs sites, the logo replaces the text site title in the sidebar header. This was visible in the approved builds.

## How it works

### Packaging

`ssc-ng/theme` is a Ruby gem named `ssc-ng-theme`, used as a Jekyll plugin alongside the real theme, because Jekyll allows only one theme and has no theme inheritance. Each site's configuration becomes:

```ruby
# Gemfile
gem "just-the-docs", "~> 0.10"
gem "ssc-ng-theme", github: "ssc-ng/theme", branch: "v1"
```

```yaml
# _config.yml
theme: just-the-docs
plugins: [ssc-ng-theme]
```

Sites remove their local `color_scheme` and `logo` settings, and the plugin supplies them.

The plugin does four things:

1. Adds the gem's Sass and include folders to Jekyll's search paths, with priority over the real theme and below the site's own files.
2. Sets defaults for `color_scheme` and `logo`.
3. Adds the logo and font files to the site's output.
4. Detects the real theme and applies the matching layer.

### Layers

- **Brand layer:** CSS variables for the colors above, plus fonts and logo. Independent of any theme. Replace `--navy` and related names with role-based ones, such as `--brand-primary`. (Builder's call on the names)
- **Just the Docs layer:**
  - A color scheme file, `_sass/color_schemes/ssc-ng.scss`.
  - An override of `css/custom.scss.liquid` that loads brand and shared styles, then the site's own `custom.scss`.
  - Rules for code weight and font.
- **Minimal Mistakes layer:** phase 2, below.

### Sites and their styles

- The styles shared by `archive`, `ssc2` and `docker-stata` move to the gem.
- Each site's `custom.scss` keeps only page-specific rules, and these use the brand variables.
- Hardcoded brand values must go, including `rgba(18,58,99,…)` and fixed monospace font stacks. A check in the sites' tests or the theme's CI should catch them returning. (Builder's call on the form)
- Asset URLs must work under a project path such as `/archive`, and under an empty base path on Cloudflare previews. Each site's `tests/test_site.py` already checks the first case for root-absolute links and must keep passing.

### How updates reach sites

- Sites follow the `v1` branch. A breaking redesign would use a new `v2` branch. (Builder's call)
- `Gemfile.lock` stays committed and pins everything else. A CI step runs `bundle lock --update ssc-ng-theme` before installing gems, so the theme alone floats. The changed lock file is never committed.
- A composite action in `ssc-ng/theme` holds this and the Ruby setup, and replaces the `ruby/setup-ruby` step in each site's workflow, so these steps are not copied between repos. All sites run Ruby 3.3, which requires merging `ssc-ng.github.io` PR #8.
- `ruby/setup-ruby` with `bundler-cache: true` installs gems straight away, so the step order and gem caching need care. How to resolve this is the builder's call.

Local previews, such as `ssc2`'s `tools/serve_site.sh`, use the theme version in the committed lock file unless the developer updates it. That is acceptable, since CI always takes the latest. Check that the existing Docker images can still fetch a gem from GitHub.

Expected time for a change to arrive:

| Site | Scheduled rebuild | Longest wait |
| --- | --- | --- |
| `archive` | Daily | About 1 day |
| `ssc-ng.net` | Daily | About 1 day |
| `ssc2` | Mondays | 7 days |
| `docker-stata` | Mondays | 7 days |

### Safety

- Changes land on `main`. CI builds a small test site for each supported theme and runs checks. If they pass, CI moves `v1` to that commit. (Decided: test before release. Builder's call: the move is automatic)
- Each site's deploy already depends on its build, so a failed build leaves the last good version live. This also covers GitHub being unavailable when a gem is fetched.
- The test sites should cover the logo, fonts, code styling and links under a base path.

### Theme previews

Every pull request on `ssc-ng/theme` gets a preview website, using the same Cloudflare Pages setup as the other sites, with the link posted as a PR comment. This lets a theme change be seen before it reaches any site. (Decided)

- **Content:** the test sites from the Safety section, under one preview address, with a small index page linking to each. Each test site sits under its own path, such as `/just-the-docs/`, which also exercises links under a base path. Include pages showing real components: code, tables, buttons, links, logo. (Builder's call)
- **Scope:** pull requests from branches of this repository only, because forks can't read the deploy secrets, as on the other sites. (Builder's call)
- **Setup:** one Cloudflare Pages project named `ssc-theme`, following the `ssc-` naming that `archive` uses, and the secrets `CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID` on this repository. These are repo-level secrets on `archive` and must be added here by Lars. `archive`'s `site/DEPLOY-PREVIEW.md` has the steps.
- **Reuse:** the workflow should match the other sites' `preview` job. It is separate from promotion to `v1`, and a preview failure should not count as a failed theme test. (Builder's call)

## Order of work

1. **Prove the plugin on `archive`, on a throwaway branch.** It must show that a plugin can add include and Sass paths with the right priority, set defaults, and output static files. Nothing else proceeds until this works. If it fails, fall back to having the composite action check out the theme and copy its files into the site before the build, and revisit this design with Lars.
2. **Build the gem and CI:** brand and Just the Docs layers, test site, and promotion to `v1`.
3. **Add theme previews** in their own PR, so that every later theme change can be seen before merging.
4. **Move `archive`** by PR. Compare its Cloudflare preview with the approved look.
5. **Move `ssc2` and `docker-stata`** by PR, one at a time.
6. **Phase 2: `ssc-ng.net`.** Try the Minimal Mistakes layer on a throwaway branch, using the same gem. Show Lars the result before opening a PR, since the approved look was only seen on Just the Docs. If the plugin can't restyle it cleanly, the fallback is for the main site to load a shared CSS file built from the brand layer. This depends on PRs #7 and #8.

## What's left to the builder

- Plugin hook points and internal file layout.
- How the composite action orders steps and caches gems.
- Which of the 83 shared lines, and other near-duplicates, are truly shared. The test is whether the rule applies regardless of page.
- CI details, and how to check rendering in the test sites.

## Done when

- `archive`, `ssc2` and `docker-stata` get colors, code font and logo only from the gem, and their previews match the approved look.
- A test change merged to `main` of `ssc-ng/theme` reaches a site on its next build, with no commit to that site.
- A deliberately broken theme change fails CI and does not reach `v1`.
- A pull request on `ssc-ng/theme` gets a working preview link, posted as a comment.
- For phase 2, `ssc-ng.net` carries the brand from the same source, keeping its layout.
