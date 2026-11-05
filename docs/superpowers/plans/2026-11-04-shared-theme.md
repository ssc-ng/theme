# Shared SSC-NG Theme Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give `archive`, `ssc2`, `docker-stata` and then `ssc-ng.net` one brand source, through a Jekyll plugin gem that updates every site on its next build.

**Architecture:** `ssc-ng-theme` is a plugin gem used alongside the real theme. On `:site, :after_init` it adds its include and Sass folders to Jekyll's search paths, sets brand configuration, and a generator adds the logo and fonts to the output. Sites float on the `v1` branch through a composite action, and CI moves `v1` only after tests pass.

**Tech Stack:** Ruby 3.3, Jekyll 4.4, Just the Docs 0.12, Minimal Mistakes 4.28, Sass, Python `unittest` for checks on built sites, GitHub Actions, Cloudflare Pages.

**Spec:** `docs/superpowers/specs/2026-11-04-shared-theme-design.md`

## Global Constraints

- Ruby 3.3 everywhere. Never run `git config user.name` or `user.email`.
- Run Ruby tooling in containers (`ruby:3.3`), and Python with the standard library only. Install nothing globally.
- Page-specific styles stay in each site. Layout does not change.
- `stata-keyword-crosswalk` is out of scope.
- Colors: primary `#0E6480`, soft `#E3F1F5`, links and accent `#0B6E8E`, hover `#C9E3EA`, partial `#6FA9BC`, sidebar `#F4F8F9`, results-bar text `#DDF0F5`, console keyword `#8FD3E6`, primary RGB `14,100,128`.
- Unchanged variables: `--ink #20242a`, `--muted #5c6572`, `--line #d7dde4`, `--console-bg #171b21`, `--console-ink #e6e9ec`, `--console-dim #8a949f`, `--console-good #7fd08c`, `--console-err #e07a7a`.
- Fonts: self-hosted JetBrains Mono. Weight 700 on `code` and code blocks, 400 on other monospace text. Stack: `"JetBrains Mono", ui-monospace, "Cascadia Code", Consolas, Menlo, monospace`.
- All PRs on site repos need their Cloudflare preview checked before asking for review.

## Review Focus

- A Cloudflare preview builds with an empty base path, and production builds with `/archive`: every logo, font and favicon URL must resolve in both. Tested in Task 2.
- A site still has `color_scheme: light`, `logo:` or its own `sass:` options in `_config.yml`: the brand must win, and other `sass:` options must survive. This enforces the spec's no-drift anti-goal, so the plugin overwrites these keys rather than only filling blanks. Tested in Tasks 1 and 2.
- A theme change renames or drops a CSS variable that a site's `custom.scss` uses: the browser would silently ignore it. Candidates must not reach `v1`. Tested in Task 3.
- The site's committed `Gemfile.lock` predates the newest `v1`, or doesn't exist, as on `ssc-ng.net`: the build must still take the newest `v1`. Tested in Tasks 3 and 8.
- The web font fails to load: code stays readable through the fallback stack. Tested in Task 2.

---

## File structure in `ssc-ng/theme`

| Path | Responsibility |
| --- | --- |
| `ssc-ng-theme.gemspec` | Gem definition: Ruby `>= 3.3`, `jekyll >= 4.3, < 5`. Does not depend on either real theme. |
| `lib/ssc-ng-theme.rb` | Entry point Jekyll requires from `plugins:`. Hook and generator. |
| `_includes/css/custom.scss.liquid` | Just the Docs layer: loads brand, shared styles, then the site's `custom/custom`. |
| `_includes/favicon.html` | Just the Docs layer: icon links. |
| `_sass/color_schemes/ssc-ng.scss` | Just the Docs Sass variables. |
| `_sass/ssc-ng/_brand.scss` | CSS variables and `@font-face`. Theme-independent. |
| `_sass/ssc-ng/_just-the-docs.scss` | Code weight and font rules. |
| `_sass/ssc-ng/_shared.scss` | Rules shared by the three sites. |
| `assets/ssc-ng-theme/` | Logo sizes, fonts, OFL license. Output at `/assets/ssc-ng-theme/`. |
| `.github/actions/setup/action.yml` | Composite action that sites call. |
| `.github/workflows/ci.yml` | Tests and promotion to `v1`. |
| `.github/workflows/preview.yml` | Cloudflare previews. |
| `test-sites/just-the-docs/` | Test site, using the gem by local path. |
| `script/build-test-sites.sh` | Builds all test sites into `_preview/` in a `ruby:3.3` container. |
| `script/compare_css.py` | Lists CSS selectors lost or added between two builds. |
| `tests/test_built_sites.py` | Checks on built output. |

---

### Task 1: Prove the plugin (gate)

If this fails, stop, and take the spec's fallback to Lars before doing any more work.

**Files:**
- Create: `ssc-ng-theme.gemspec`, `lib/ssc-ng-theme.rb`, `_sass/color_schemes/ssc-ng.scss`, `_includes/css/custom.scss.liquid`, `assets/ssc-ng-theme/logo-400.png`, `test-sites/just-the-docs/{Gemfile,_config.yml,index.md,_sass/custom/custom.scss}`, `script/build-test-sites.sh`, `tests/test_built_sites.py`
- Modify: `.gitignore` (add `_preview/`, `.jekyll-cache/`, `test-sites/*/_site/`, `test-sites/*/Gemfile.lock`, `test-sites/*/.bundle/`)

**Interfaces:**
- Produces: `script/build-test-sites.sh` writes `_preview/just-the-docs/` built with base path `/just-the-docs`, and `_preview-root/just-the-docs/` built with an empty base path. `tests/test_built_sites.py` reads both.
- Produces: `SscNgTheme::ASSET_DIR = "assets/ssc-ng-theme"`, used for every logo and font URL.
- Produces: `SscNgTheme.configure(site)`, `SscNgTheme::AssetGenerator < Jekyll::Generator`.

- [ ] **Step 1: Write the failing tests** in `tests/test_built_sites.py`, for both output folders.

```python
def test_color_scheme_comes_from_the_gem(self):
    self.assertIn("#0e6480", self.css().lower())

def test_site_custom_scss_loads_after_the_brand(self):
    self.assertIn(".fixture-site-rule", self.css())

def test_logo_reaches_the_output(self):
    self.assertTrue((self.site / "assets/ssc-ng-theme/logo-400.png").exists())

def test_brand_overrides_local_settings(self):
    # test site sets color_scheme: light and logo: /wrong.png
    self.assertIn("ssc-ng-theme/logo-400.png", self.css())
    self.assertNotIn("/wrong.png", self.css())

def test_other_sass_options_survive(self):
    # test site sets sass: {style: compressed}
    self.assertLess(self.css().count("\n"), 50)
```

- [ ] **Step 2: Run them and confirm they fail**

Run: `bash script/build-test-sites.sh; python3 -I -m unittest discover -s tests -v`
Expected: FAIL, with the build failing or brand values absent.

- [ ] **Step 3: Implement `SscNgTheme.configure(site) -> nil` and `AssetGenerator#generate(site) -> nil`**

Register with `Jekyll::Hooks.register :site, :after_init`.

- Set `site.config["sass"]["load_paths"] = ["_sass", <gem>/_sass, *existing]`. `sass_load_paths` puts user paths first, so listing `_sass` first keeps the site's own files ahead of the gem. Mutate the existing hash so other `sass` options survive, and create it if absent.
- `site.includes_load_paths.insert(1, <gem>/_includes)`, which puts the gem after the site and before the theme.
- If `site.theme&.name == "just-the-docs"`, set `config["color_scheme"] = "ssc-ng"` and `config["logo"] = "/#{ASSET_DIR}/logo-400.png"`. For any other theme, log a warning with `Jekyll.logger.warn` and change nothing else.
- The generator adds each file under `<gem>/assets/ssc-ng-theme/` with `Jekyll::StaticFile.new(site, gem_root, "assets/ssc-ng-theme", name)`.

- [ ] **Step 4: Run the tests and confirm they pass**

Run: the Step 2 command.
Expected: all PASS, with both output folders built.

- [ ] **Step 5: Try it on real `archive`, on a throwaway copy**

Copy `archive/site` from `origin/main` to the scratchpad, add the gem by local path, build in `ruby:3.3`, and run `archive/tests/test_site.py` against the output. Expected: the build and tests pass, and `index.html` shows the logo. Commit nothing to `archive`.

- [ ] **Step 6: Report to Lars.** State plainly whether the plugin works, then commit on a branch and open a PR.

```bash
git add .
git commit -m "Add the plugin gem skeleton and test site"
```

---

### Task 2: Brand and Just the Docs layers

**Files:**
- Create: `_sass/ssc-ng/_brand.scss`, `_sass/ssc-ng/_just-the-docs.scss`, `_sass/ssc-ng/_shared.scss`, `_includes/favicon.html`, `assets/ssc-ng-theme/{logo-180.png,logo-64.png,JetBrainsMono-Regular.woff2,JetBrainsMono-Bold.woff2,OFL.txt}`
- Modify: `_sass/color_schemes/ssc-ng.scss`, `_includes/css/custom.scss.liquid`, `test-sites/just-the-docs/index.md`, `tests/test_built_sites.py`

**Interfaces:**
- Consumes: `SscNgTheme::ASSET_DIR`, `_preview/`, `_preview-root/`.
- Produces these CSS variables for sites and for Task 3's contract check: `--brand-primary`, `--brand-soft`, `--brand-hover`, `--brand-partial`, `--brand-accent`, `--brand-primary-rgb`, `--brand-bar-ink`, `--brand-mono`, `--ink`, `--muted`, `--line`, `--console-bg`, `--console-ink`, `--console-dim`, `--console-good`, `--console-err`, `--console-keyword`.

- [ ] **Step 1: Write the failing tests**

```python
def test_every_color_is_defined(self):
    for value in ("#0e6480", "#e3f1f5", "#0b6e8e", "#c9e3ea", "#6fa9bc", "#ddf0f5", "#8fd3e6"):
        self.assertIn(value, self.css().lower())

def test_old_brand_values_are_gone(self):
    for value in ("#123a63", "18,58,99", "18, 58, 99"):
        self.assertNotIn(value, self.css())

def test_code_is_bold(self):
    self.assertRegex(self.css(), r"code[^{]*\{[^}]*font-weight:\s*(700|bold)")

def test_font_stack_has_fallbacks(self):
    self.assertRegex(self.css(), r'"JetBrains Mono",\s*ui-monospace')

def test_font_urls_resolve_on_disk(self):
    for url in re.findall(r'url\("?([^")]+\.woff2)', self.css()):
        self.assertTrue((self.css_path.parent / url).resolve().exists(), url)

def test_icon_links_use_the_base_path(self):
    html = (self.site / "index.html").read_text()
    self.assertIn(f'href="{self.base}/assets/ssc-ng-theme/logo-64.png"', html)
    self.assertIn(f'href="{self.base}/assets/ssc-ng-theme/logo-180.png"', html)

def test_root_absolute_links_carry_the_base_path(self):
    # every href or src starting with / must start with self.base + "/",
    # the same rule as archive/tests/test_site.py
    for link in re.findall(r'(?:href|src)="(/[^/"][^"]*)"', (self.site / "index.html").read_text()):
        self.assertTrue(link.startswith(self.base + "/"), link)
```

- [ ] **Step 2: Run them and confirm they fail**

Run: the Task 1 command.
Expected: FAIL on missing colors and fonts.

- [ ] **Step 3: Add the assets.**

Take the logos from `ssc-ng.github.io/assets/images/ssc-ng-gears-v2-{400,180,64}.png` on PR #7, renamed. Take the fonts and `OFL.txt` from the JetBrains Mono release's `webfonts/` folder. Reference fonts with a relative `url("../ssc-ng-theme/...")`, because the stylesheet lives in `/assets/css/`.

- [ ] **Step 4: Write the layers**

- `color_schemes/ssc-ng.scss` sets `$link-color`, `$btn-primary-color`, `$body-heading-color`, `$sidebar-color`, `$mono-font-family` from the Global Constraints.
- `custom.scss.liquid` imports, in order: `./ssc-ng/brand`, `./ssc-ng/just-the-docs`, `./ssc-ng/shared`, `./custom/custom`.
- `_shared.scss` starts with an empty file and gets its rules in Task 5.

- [ ] **Step 5: Run the tests and confirm they pass**

Run: the Task 1 command.
Expected: all PASS for both base paths.

- [ ] **Step 6: Commit and open a PR**

```bash
git add .
git commit -m "Add brand and Just the Docs layers"
```

---

### Task 3: CI, promotion and the composite action

**Files:**
- Create: `.github/actions/setup/action.yml`, `.github/workflows/ci.yml`, `script/check_css_vars.py`
- Test: `tests/test_check_css_vars.py`

**Interfaces:**
- Produces: `uses: ssc-ng/theme/.github/actions/setup@v1` with inputs `working-directory` (required) and `ruby-version` (default `"3.3"`). After it runs, `bundle exec` works in that folder with the newest theme.
- Produces: `script/check_css_vars.py CSS_FILE`, which exits 1 and names each `var(--x)` with no definition and no fallback.

- [ ] **Step 1: Write the failing tests**

```python
def test_undefined_variable_is_reported(self):
    code, out = run_check(":root{--a:1} p{color:var(--gone)}")
    self.assertEqual(code, 1)
    self.assertIn("--gone", out)

def test_defined_variable_passes(self):
    self.assertEqual(run_check(":root{--a:1} p{color:var(--a)}")[0], 0)

def test_variable_with_a_fallback_passes(self):
    self.assertEqual(run_check("p{color:var(--gone,red)}")[0], 0)
```

- [ ] **Step 2: Run them and confirm they fail**

Run: `python3 -I -m unittest tests.test_check_css_vars -v`
Expected: FAIL, because the script doesn't exist.

- [ ] **Step 3: Implement `script/check_css_vars.py`, then confirm the tests pass**

- [ ] **Step 4: Write the action.** It has three steps, in this order:

1. `ruby/setup-ruby@v1` with `bundler-cache: false`.
2. `bundle lock --update ssc-ng-theme` in `working-directory`.
3. `ruby/setup-ruby@v1` again with `bundler-cache: true`, which installs and caches from the updated lock.

- [ ] **Step 5: Write `ci.yml`**

Trigger on pull requests and pushes to `main`.

- Job `test`: run `script/build-test-sites.sh` and the Python tests.
- Job `real-sites`: matrix of `archive`, `ssc2`, `docker-stata`. Check out each site's `main`. If its Gemfile lists the gem, point it at this checkout by local path and build, then run `check_css_vars.py` on the output CSS. Skip sites not yet migrated.
- Job `promote`: `if: github.ref == 'refs/heads/main' && github.event_name == 'push'`, `needs: [test, real-sites]`, `permissions: contents: write`. Run `git push origin HEAD:refs/heads/v1`, without force, so a non-fast-forward fails rather than overwriting.

- [ ] **Step 6: Verify on GitHub**

Open the PR, then merge. Expected: `test` passes on the PR, and after merging, `git ls-remote origin v1` matches `main`.

- [ ] **Step 7: Test that a site's lock floats.** On a throwaway `archive` branch, use the action with a lock pinned to an older `v1`. Expected: the build log shows the newest `v1` revision. Delete the branch afterward.

---

### Task 4: Theme previews

The `ssc-theme` Cloudflare project and org secrets already exist.

**Files:**
- Create: `.github/workflows/preview.yml`, `test-sites/index.html`
- Modify: `test-sites/just-the-docs/index.md`, `script/build-test-sites.sh`

**Interfaces:**
- Consumes: `script/build-test-sites.sh`, `_preview/`.

- [ ] **Step 1: Extend the test site** with real components: inline code, a code block, a table, buttons, links, and a page with `kbd`.

- [ ] **Step 2: Have the build script copy `test-sites/index.html` to `_preview/index.html`.** It links to each test site.

- [ ] **Step 3: Write `preview.yml`,** copying the `preview` job from `archive/.github/workflows/site.yml`, with `--project-name=ssc-theme`. Same fork guard. Keep it a separate workflow, so a preview failure doesn't block `promote`.

- [ ] **Step 4: Verify.** Open the PR. Expected: a `https://pr-N.ssc-theme.pages.dev` comment appears, the index page links work, and the logo and fonts load. This is the first use of the org token, so if it fails with an authentication error, tell Lars.

- [ ] **Step 5: Commit and open a PR**

```bash
git add .
git commit -m "Add Cloudflare previews for theme PRs"
```

---

### Task 5: Move `archive`

Work in `ssc-ng/archive`, on a branch from `origin/main`. Filling `_shared.scss` happens in `ssc-ng/theme`, in a PR merged first.

**Files:**
- Create in `theme`: `script/compare_css.py`, `tests/test_compare_css.py`
- Modify in `theme`: `_sass/ssc-ng/_shared.scss`
- Modify in `archive`: `site/Gemfile`, `site/Gemfile.lock`, `site/_config.yml`, `site/_sass/custom/custom.scss`, `.github/workflows/site.yml` (the step and, if needed, its header comment), `site/README-site.md`.

**Interfaces:**
- Consumes: `setup` action, `--brand-*` variables.
- Produces: `script/compare_css.py BEFORE.css AFTER.css`, which prints selectors lost and added, and exits 1 if any are lost.

- [ ] **Step 1: Save today's `archive` CSS as the baseline.** Build `origin/main` in `ruby:3.3`.

- [ ] **Step 2: Write and test `compare_css.py`,** with a test that a removed selector exits 1 and an added one exits 0.

- [ ] **Step 3: Fill `_shared.scss`,** moving only rules present in all three sites' `custom.scss`, replacing old values with brand variables. Merge this to `theme` and wait for `v1` to move.

- [ ] **Step 4: Update the site.**

- Add the gem and `plugins:`.
- Remove `color_scheme` and any `logo`.
- Reduce `custom.scss` to page-specific rules.
- Rename `--navy` to `--brand-primary`, `--navy-soft` to `--brand-soft`, `--accent` to `--brand-accent`.
- Replace `rgba(18,58,99,…)` with `rgba(var(--brand-primary-rgb),…)`, the old hover, partial and bar-text values with their variables, and monospace stacks with `var(--brand-mono)`.
- Replace the `ruby/setup-ruby` step with the action.

- [ ] **Step 5: Add a test to `archive/tests/test_site.py`** that `custom.scss` contains none of `#123a63`, `18,58,99`, `ui-monospace`, `--navy`.

- [ ] **Step 6: Verify locally**

Run: build in `ruby:3.3`, `python3 -m unittest discover -s tests -v`, `compare_css.py baseline.css new.css`, `check_css_vars.py new.css`.
Expected: all pass, and no selectors lost.

- [ ] **Step 7: Open the PR and check the preview.** Compare every page (About, Select packages, Compare, Package history, Availability) with the approved look, at desktop and phone widths. Expected: only colors, code font and logo differ. Then ask Lars to review.

---

### Task 6: Move `ssc2` and `docker-stata`

One PR per repo, the same way as Task 5 and in that order. Merge the first before starting the second.

**Files in each repo:** `site/Gemfile`, `site/Gemfile.lock`, `site/_config.yml`, `site/_sass/custom/custom.scss`, `.github/workflows/site.yml`, plus `tests/test_site.py` for the Task 5 check. `ssc2` is also called from `release.yml`, so check that path still works.

- [ ] **Step 1: Run Task 5 Steps 1, 4, 5 and 6 for `ssc2`.** Also confirm that `tools/serve_site.sh` still builds. Its image has `git`, which fetching a gem from GitHub requires. Expected: all pass, and no selectors lost.

- [ ] **Step 2: Open the PR and check the picker page and Reference page in the preview,** then ask Lars to review.

- [ ] **Step 3: Repeat for `docker-stata`.** Its `.results pre .kw` color changes to `var(--console-keyword)`. This wasn't in the approved builds, so point Lars to it in the PR. Check every tab on the image picker.

---

### Task 7: Prove the "Done when" list

- [ ] **Step 1: Test that a change reaches a site.** Merge a harmless visible change to `theme`, such as a one-shade hover change. Run `archive`'s `site` workflow by hand, with no commit to `archive`. Expected: the deployed CSS has the new value. Then revert it.

- [ ] **Step 2: Test that a broken change is blocked.** Open a PR that removes `--brand-primary`. Expected: `real-sites` fails, and because the PR isn't merged, `v1` doesn't move. Close the PR.

- [ ] **Step 3: Report results to Lars,** including which repo-level Cloudflare secrets could now be retired. Don't delete them without asking.

---

### Task 8: Phase 2, `ssc-ng.net` (gate, then PR)

Requires `ssc-ng.github.io` PRs #7 and #8 to be merged.

**Files:**
- Create in `theme`: `_sass/minimal-mistakes/skins/_ssc-ng.scss`, `test-sites/minimal-mistakes/`
- Modify in `theme`: `lib/ssc-ng-theme.rb`, `tests/test_built_sites.py`, `test-sites/index.html`
- Modify in `ssc-ng.github.io`: `Gemfile`, `_config.yml`, `index.md`, `_includes/head/custom.html`, `.github/workflows/pages.yml`, `build/Dockerfile` if needed. Remove `assets/images/ssc-ng-gears-v2*.png`, once nothing refers to them.

**Interfaces:**
- Consumes: `_brand.scss`, `ASSET_DIR`.
- Produces: for `site.theme.name == "minimal-mistakes-jekyll"`, `configure` sets `config["minimal_mistakes_skin"] = "ssc-ng"` and `config["logo"]`.

- [ ] **Step 1: Write the failing test** that the Minimal Mistakes test site's `assets/css/main.css` contains `#0b6e8e`, the bold `code` rule and `@font-face`, and that its logo URL resolves.

- [ ] **Step 2: Run it and confirm it fails**

Run: the Task 1 command.
Expected: FAIL, because the site doesn't exist yet.

- [ ] **Step 3: Implement the skin.** Skins are imported before the theme's partials, so they can set `$link-color`, `$primary-color`, `$monospace` and similar. Import the brand file for `@font-face`. If a rule needs to come after the partials, override `assets/css/main.scss` from the gem or test a higher-specificity rule.

- [ ] **Step 4: Run the test and confirm it passes**

Run: the Task 1 command.
Expected: PASS.

- [ ] **Step 5: Show Lars before going further.** Build the real main site with the skin in the scratchpad and show screenshots. The approved look was only ever seen on Just the Docs. If it can't be done cleanly, the spec's fallback is a shared CSS file. Wait for Lars's decision.

- [ ] **Step 6: Merge the theme change, then open the `ssc-ng.github.io` PR.** That site has no `Gemfile.lock`, so confirm in the CI log that the action works without one and takes the newest `v1`. Keep its masthead dropdown, hero and tile rules. Expected: the preview matches what Lars approved, and CI passes.

---

## Done when

The spec's "Done when" list holds, as shown by Task 7 and Task 8.
