"""Tests for script/theme_branch.py."""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "script/theme_branch.py"


def run(gemfile):
    with tempfile.TemporaryDirectory() as d:
        path = Path(d, "Gemfile")
        if gemfile is not None:
            path.write_text(gemfile)
        r = subprocess.run([sys.executable, "-I", SCRIPT, path], capture_output=True, text=True)
    return r.returncode, r.stdout.strip()


class ThemeBranch(unittest.TestCase):
    def test_branch_is_printed(self):
        self.assertEqual(run('gem "ssc-ng-theme", github: "ssc-ng/theme", branch: "v1"\n'), (0, "v1"))

    def test_minor_branch_is_printed(self):
        self.assertEqual(run('gem "ssc-ng-theme", github: "ssc-ng/theme", branch: "v1.2"\n'), (0, "v1.2"))

    def test_single_quotes_and_a_group_are_understood(self):
        gemfile = "group :jekyll_plugins do\n  gem 'ssc-ng-theme', github: 'ssc-ng/theme', branch: 'v2'\nend\n"
        self.assertEqual(run(gemfile), (0, "v2"))

    def test_a_pinned_tag_follows_no_branch(self):
        self.assertEqual(run('gem "ssc-ng-theme", github: "ssc-ng/theme", tag: "v1.0.3"\n'), (0, ""))

    def test_a_missing_gemfile_fails(self):
        self.assertEqual(run(None)[0], 1)

    def test_a_gemfile_without_the_theme_fails(self):
        self.assertEqual(run('gem "jekyll"\n')[0], 1)

    def test_a_comment_does_not_count_as_the_theme(self):
        self.assertEqual(run('# gem "ssc-ng-theme", branch: "v1"\n')[0], 1)


if __name__ == "__main__":
    unittest.main()
