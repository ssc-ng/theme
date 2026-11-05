"""Tests for script/compare_css.py."""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "script/compare_css.py"


def run_compare(before, after):
    with tempfile.TemporaryDirectory() as d:
        a, b = Path(d, "a.css"), Path(d, "b.css")
        a.write_text(before)
        b.write_text(after)
        r = subprocess.run([sys.executable, "-I", SCRIPT, a, b], capture_output=True, text=True)
    return r.returncode, r.stdout


class CompareCss(unittest.TestCase):
    def test_lost_selector_fails_and_is_named(self):
        code, out = run_compare(".a{color:red}.b{color:red}", ".a{color:blue}")
        self.assertEqual(code, 1)
        self.assertIn("lost: .b", out)

    def test_added_selector_passes_and_is_named(self):
        code, out = run_compare(".a{color:red}", ".a{color:red}.b{color:red}")
        self.assertEqual(code, 0)
        self.assertIn("added: .b", out)

    def test_selector_list_order_does_not_matter(self):
        self.assertEqual(run_compare(".a,.b{x:y}", ".b{x:y}.a{x:y}")[0], 0)

    def test_comma_inside_not_does_not_split(self):
        code, out = run_compare(":not(pre, figure) > code{x:y}", ":not(pre,figure)>code{x:y}")
        self.assertEqual(code, 0)
        self.assertNotIn("lost", out)

    def test_selector_inside_media_is_seen(self):
        code, out = run_compare("@media print{.a{x:y}}", "")
        self.assertEqual(code, 1)
        self.assertIn("lost: .a", out)

    def test_comments_are_ignored(self):
        self.assertEqual(run_compare("/* .gone{x:y} */.a{x:y}", ".a{x:y}")[0], 0)


if __name__ == "__main__":
    unittest.main()
