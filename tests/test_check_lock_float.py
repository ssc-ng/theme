"""Tests for script/check_lock_float.py."""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "script/check_lock_float.py"
LOCK = """GIT
  remote: https://github.com/ssc-ng/theme.git
  revision: {rev}
  branch: v1
  specs:
    ssc-ng-theme (1.0.0)

GEM
  specs:
    csv ({csv})
"""


def run_check(before, after, expected):
    with tempfile.TemporaryDirectory() as d:
        a, b = Path(d, "before"), Path(d, "after")
        a.write_text(before)
        b.write_text(after)
        r = subprocess.run([sys.executable, "-I", SCRIPT, a, b, expected],
                           capture_output=True, text=True)
    return r.returncode, r.stdout


class CheckLockFloat(unittest.TestCase):
    def test_theme_moved_and_nothing_else_passes(self):
        before = LOCK.format(rev="old", csv="1.0")
        self.assertEqual(run_check(before, LOCK.format(rev="new", csv="1.0"), "new")[0], 0)

    def test_theme_not_moved_fails(self):
        before = LOCK.format(rev="old", csv="1.0")
        code, out = run_check(before, before, "new")
        self.assertEqual(code, 1)
        self.assertIn("old", out)

    def test_another_gem_changing_fails(self):
        before = LOCK.format(rev="old", csv="1.0")
        code, out = run_check(before, LOCK.format(rev="new", csv="2.0"), "new")
        self.assertEqual(code, 1)
        self.assertIn("csv", out)


if __name__ == "__main__":
    unittest.main()
