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


class BuiltUnderBasePath(JustTheDocsChecks, unittest.TestCase):
    output = "_preview"
    base = "/just-the-docs"


class BuiltWithEmptyBasePath(JustTheDocsChecks, unittest.TestCase):
    output = "_preview-root"
    base = ""


if __name__ == "__main__":
    unittest.main()
