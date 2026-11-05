"""Checks on the test sites built by script/build-test-sites.sh."""
import re
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

    def test_icon_links_use_the_base_path(self):
        html = (self.site / "index.html").read_text()
        self.assertIn(f'href="{self.base}/assets/ssc-ng-theme/logo-64.png"', html)
        self.assertIn(f'href="{self.base}/assets/ssc-ng-theme/logo-180.png"', html)

    def test_icon_files_exist(self):
        for name in ("logo-64.png", "logo-180.png"):
            self.assertTrue((self.site / "assets/ssc-ng-theme" / name).exists(), name)

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


class BuiltUnderBasePath(JustTheDocsChecks, unittest.TestCase):
    output = "_preview"
    base = "/just-the-docs"


class BuiltWithEmptyBasePath(JustTheDocsChecks, unittest.TestCase):
    output = "_preview-root"
    base = ""


if __name__ == "__main__":
    unittest.main()
