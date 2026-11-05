"""Checks on the test sites built by script/build-test-sites.sh."""
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class JustTheDocsChecks:
    """Shared checks; subclasses choose the build to inspect."""

    output = None
    base = None

    @property
    def site(self):
        return ROOT / self.output / "just-the-docs"

    @property
    def css_path(self):
        return self.site / "assets/css/just-the-docs-default.css"

    def css(self):
        return self.css_path.read_text()

    def test_color_scheme_comes_from_the_gem(self):
        self.assertIn("#0e6480", self.css().lower())

    def test_site_custom_scss_loads_after_the_brand(self):
        css = self.css()
        self.assertIn(".fixture-site-rule", css)
        self.assertIn("--brand-primary:", css)
        self.assertLess(css.index("--brand-primary:"), css.index(".fixture-site-rule"))

    def test_logo_reaches_the_output(self):
        self.assertTrue((self.site / "assets/ssc-ng-theme/logo-400.png").exists())

    def test_brand_overrides_local_settings(self):
        self.assertIn(f"{self.base}/assets/ssc-ng-theme/logo-400.png", self.css())
        self.assertNotIn("/wrong.png", self.css())

    def test_other_sass_options_survive(self):
        self.assertLess(self.css().count("\n"), 50)

    def test_every_color_is_defined(self):
        for value in ("#0e6480", "#e3f1f5", "#0b6e8e", "#c9e3ea", "#6fa9bc",
                      "#f4f8f9", "#ddf0f5", "#8fd3e6"):
            self.assertIn(value, self.css().lower())

    def test_every_brand_variable_is_defined(self):
        for name in ("--brand-primary", "--brand-soft", "--brand-hover",
                     "--brand-partial", "--brand-accent", "--brand-primary-rgb",
                     "--brand-bar-ink", "--brand-mono", "--ink", "--muted", "--line",
                     "--console-bg", "--console-ink", "--console-dim",
                     "--console-good", "--console-err", "--console-keyword"):
            self.assertIn(name + ":", self.css())

    def test_old_brand_values_are_gone(self):
        for value in ("#123a63", "18,58,99", "18, 58, 99"):
            self.assertNotIn(value, self.css())

    def test_code_is_bold(self):
        self.assertRegex(self.css(), r"code[^{]*\{[^}]*font-weight:\s*(700|bold)")

    def test_font_stack_has_fallbacks(self):
        self.assertRegex(self.css(), r'"JetBrains Mono",\s*ui-monospace')

    def test_both_font_weights_are_declared(self):
        faces = re.findall(r"@font-face\s*\{[^}]*\}", self.css())
        weights = {m for f in faces for m in re.findall(r"font-weight:\s*(\d+)", f)}
        self.assertEqual(weights, {"400", "700"})

    def test_font_urls_resolve_on_disk(self):
        urls = re.findall(r'url\("?([^")]+\.woff2)', self.css())
        self.assertTrue(urls)
        for url in urls:
            self.assertTrue((self.css_path.parent / url).resolve().exists(), url)

    def test_font_license_ships_with_the_fonts(self):
        self.assertTrue((self.site / "assets/ssc-ng-theme/OFL.txt").exists())

    def test_sidebar_shows_the_site_title_beside_the_logo(self):
        html = (self.site / "index.html").read_text()
        link = re.search(r'<a [^>]*class="site-title[^"]*"[^>]*>(.*?)</a>', html, re.S).group(1)
        self.assertIn('class="site-logo"', link)
        visible = re.sub(r"<[^>]+>", "", link).strip()
        self.assertEqual(visible, "Theme test site")

    def test_logo_leaves_room_for_the_title(self):
        logo = re.findall(r"\.site-logo\s*\{([^}]*)\}", self.css())[-1]
        self.assertNotIn("width:100%", logo.replace(" ", ""))

    def test_sidebar_footer_links_back_to_the_main_site(self):
        html = (self.site / "index.html").read_text()
        footer = re.search(r'<div class="d-md-block d-none site-footer">(.*?)</div>', html, re.S).group(1)
        self.assertIn('href="https://ssc-ng.net/"', footer)
        self.assertLess(footer.index("ssc-ng.net"), footer.index("This site uses"))

    def test_phone_footer_links_back_to_the_main_site(self):
        html = (self.site / "index.html").read_text()
        footer = re.search(r'<div class="d-md-none mt-4 fs-2">(.*?)</div>', html, re.S).group(1)
        self.assertIn('href="https://ssc-ng.net/"', footer)
        self.assertIn("This site uses", footer)

    def test_back_link_says_where_it_goes(self):
        html = (self.site / "index.html").read_text()
        link = re.search(r'<a class="site-back-link"[^>]*>(.*?)</a>', html, re.S).group(1)
        self.assertIn("SSC-NG main site", link)

    def test_back_link_is_the_size_of_the_nav_items(self):
        def sizes(selector):
            found = re.findall(re.escape(selector) + r"\s*\{[^}]*?font-size:\s*([^;}]+)", self.css())
            self.assertTrue(found, selector)
            return found
        self.assertEqual(sizes(".site-back-link"), sizes(".nav-list .nav-list-item"))

    def test_text_box_styles_leave_the_search_box_alone(self):
        rule = re.search(r"([^{}]*input\[type=text\][^{}]*)\{[^}]*--brand-mono", self.css())
        self.assertIn(":not(.search-input)", rule.group(1))

    def test_icon_links_use_the_base_path(self):
        html = (self.site / "index.html").read_text()
        self.assertIn(f'href="{self.base}/assets/ssc-ng-theme/logo-64.png"', html)
        self.assertIn(f'href="{self.base}/assets/ssc-ng-theme/logo-180.png"', html)

    def test_icon_files_exist(self):
        for name in ("logo-64.png", "logo-180.png"):
            self.assertTrue((self.site / "assets/ssc-ng-theme" / name).exists(), name)

    def test_shared_site_rules_are_present(self):
        for selector in (".kicker", ".lede", "fieldset", "legend", ".hint", ".row", ".check",
                         ".results", ".results-bar", ".results pre", ".cursor", "#stats"):
            self.assertRegex(self.css(), r"(^|[},\s])" + re.escape(selector) + r"\s*[{,]")

    def test_results_window_extras_are_present(self):
        for selector in (".results+.results", ".results pre .kw", ".results-bar .ttl",
                         ".results-bar a", ".results-bar .barbtns button",
                         ".results-bar button:disabled"):
            self.assertIn(selector, self.css())

    def test_shared_rules_use_brand_variables(self):
        shared = (ROOT / "_sass/ssc-ng/_shared.scss").read_text()
        for value in ("ui-monospace", "--navy", "--accent:", "#dce7f2", "#8fc1ec"):
            self.assertNotIn(value, shared)

    def test_results_window_stays_regular_weight(self):
        self.assertRegex(self.css(), r"\.results pre\{[^}]*font:\s*\.88rem/1\.65\s+var\(--brand-mono\)")

    def test_root_absolute_links_carry_the_base_path(self):
        html = (self.site / "index.html").read_text()
        for link in re.findall(r'(?:href|src)="(/[^/"][^"]*)"', html):
            self.assertTrue(link.startswith(self.base + "/"), link)


class PreviewIndex(unittest.TestCase):
    index = ROOT / "_preview/index.html"

    def test_index_links_to_every_test_site(self):
        html = self.index.read_text()
        for site in (ROOT / "test-sites").iterdir():
            if site.is_dir():
                self.assertIn(f'href="{site.name}/"', html)

    def test_linked_sites_were_built(self):
        for link in re.findall(r'href="([^"]+)/"', self.index.read_text()):
            self.assertTrue((self.index.parent / link / "index.html").exists(), link)


class Components(unittest.TestCase):
    """The preview must show real components, or it can't reveal a bad change."""

    def test_home_page_shows_each_component(self):
        html = (ROOT / "_preview/just-the-docs/index.html").read_text()
        for marker in ("<table", 'class="btn', "<kbd>", "highlighter-rouge", "<blockquote"):
            self.assertIn(marker, html)


class MinimalMistakesChecks:
    """Shared checks; subclasses choose the build to inspect."""

    output = None
    base = None

    @property
    def site(self):
        return ROOT / self.output / "minimal-mistakes"

    def css(self):
        return (self.site / "assets/css/main.css").read_text()

    def html(self):
        return (self.site / "index.html").read_text()

    def test_brand_colors_reach_the_theme(self):
        css = self.css().lower()
        self.assertIn("#0b6e8e", css)  # links
        self.assertIn("#0e6480", css)  # primary
        self.assertNotIn("#6f777d", css)  # the theme's own primary

    def test_brand_variables_are_defined(self):
        self.assertIn("--brand-primary:", self.css())

    def test_code_is_bold_in_the_brand_font(self):
        self.assertRegex(self.css(), r"code[^{}]*\{[^}]*font-weight:\s*(700|bold)")
        self.assertRegex(self.css(), r"code[^{}]*\{[^}]*font-family:[^;}]*JetBrains Mono")

    def test_code_rule_outranks_the_theme_rules(self):
        self.assertIn("html body code", self.css())

    def test_font_urls_resolve_on_disk(self):
        urls = re.findall(r'url\("?(\.\./ssc-ng-theme/[^")]+)', self.css())
        self.assertEqual(len(set(urls)), 2)
        for url in set(urls):
            self.assertTrue((self.site / "assets/css" / url).resolve().exists(), url)

    def test_logo_replaces_local_setting(self):
        self.assertIn(f'src="{self.base}/assets/ssc-ng-theme/logo-400.png"', self.html())
        self.assertNotIn("wrong.png", self.html())
        self.assertTrue((self.site / "assets/ssc-ng-theme/logo-400.png").exists())

    def test_other_sass_options_survive(self):
        self.assertLess(self.css().count("\n"), 20)

    def test_every_variable_is_defined(self):
        out = subprocess.run([sys.executable, "-I", ROOT / "script/check_css_vars.py",
                              self.site / "assets/css/main.css"], capture_output=True, text=True)
        self.assertEqual(out.returncode, 0, out.stdout)


class TokensAreTheOnlySource(unittest.TestCase):
    def test_font_stack_keeps_its_quotes(self):
        for path in ("just-the-docs/assets/css/just-the-docs-default.css", "minimal-mistakes/assets/css/main.css"):
            self.assertIn('--brand-mono: "JetBrains Mono"', (ROOT / "_preview" / path).read_text(), path)

    def test_brand_colors_are_written_once(self):
        for name in ("_sass/ssc-ng/_brand.scss", "_sass/minimal-mistakes/skins/_ssc-ng.scss",
                     "_sass/color_schemes/ssc-ng.scss"):
            text = (ROOT / name).read_text().lower()
            for value in ("#0e6480", "#0b6e8e", "#e3f1f5"):
                self.assertNotIn(value, text, name)


class MinimalMistakesUnderBasePath(MinimalMistakesChecks, unittest.TestCase):
    output, base = "_preview", "/minimal-mistakes"


class MinimalMistakesWithEmptyBasePath(MinimalMistakesChecks, unittest.TestCase):
    output, base = "_preview-root", ""


class BuiltUnderBasePath(JustTheDocsChecks, unittest.TestCase):
    output = "_preview"
    base = "/just-the-docs"


class BuiltWithEmptyBasePath(JustTheDocsChecks, unittest.TestCase):
    output = "_preview-root"
    base = ""


if __name__ == "__main__":
    unittest.main()
