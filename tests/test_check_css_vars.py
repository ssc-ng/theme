"""Tests for script/check_css_vars.py."""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "script/check_css_vars.py"


def run_check(css):
    with tempfile.NamedTemporaryFile("w", suffix=".css") as f:
        f.write(css)
        f.flush()
        r = subprocess.run([sys.executable, "-I", SCRIPT, f.name],
                           capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


class CheckCssVars(unittest.TestCase):
    def test_undefined_variable_is_reported(self):
        code, out = run_check(":root{--a:1} p{color:var(--gone)}")
        self.assertEqual(code, 1)
        self.assertIn("--gone", out)

    def test_defined_variable_passes(self):
        self.assertEqual(run_check(":root{--a:1} p{color:var(--a)}")[0], 0)

    def test_variable_with_a_fallback_passes(self):
        self.assertEqual(run_check("p{color:var(--gone,red)}")[0], 0)

    def test_undefined_variable_inside_a_fallback_is_reported(self):
        code, out = run_check(":root{--a:1} p{color:var(--a,var(--gone))}")
        self.assertEqual(code, 1)
        self.assertIn("--gone", out)

    def test_defined_only_by_prefix_is_reported(self):
        code, out = run_check(":root{--brand-primary-rgb:1} p{color:var(--brand-primary)}")
        self.assertEqual(code, 1)
        self.assertIn("--brand-primary", out)


if __name__ == "__main__":
    unittest.main()
