"""Tests for script/release_targets.py."""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "script/release_targets.py"


def run(tag, existing, gem_version=None):
    gem_version = gem_version or tag.lstrip("v")
    with tempfile.TemporaryDirectory() as d:
        gemspec = Path(d, "x.gemspec")
        gemspec.write_text(f'Gem::Specification.new do |spec|\n  spec.version = "{gem_version}"\nend\n')
        r = subprocess.run([sys.executable, "-I", SCRIPT, tag, gemspec],
                           input="\n".join(existing + [tag]) + "\n",
                           capture_output=True, text=True)
    return r.returncode, r.stdout.split(), r.stderr


class ReleaseTargets(unittest.TestCase):
    def test_first_release_moves_major_and_minor(self):
        self.assertEqual(run("v1.0.0", [])[:2], (0, ["v1", "v1.0"]))

    def test_new_patch_moves_major_and_minor(self):
        self.assertEqual(run("v1.0.1", ["v1.0.0"])[:2], (0, ["v1", "v1.0"]))

    def test_new_minor_moves_major_and_its_own_minor(self):
        self.assertEqual(run("v1.1.0", ["v1.0.0", "v1.0.1"])[:2], (0, ["v1", "v1.1"]))

    def test_patch_to_an_older_minor_leaves_major_alone(self):
        self.assertEqual(run("v1.0.2", ["v1.0.1", "v1.1.0"])[:2], (0, ["v1.0"]))

    def test_older_patch_moves_nothing(self):
        self.assertEqual(run("v1.0.1", ["v1.0.0", "v1.0.2"])[:2], (0, []))

    def test_versions_compare_as_numbers(self):
        self.assertEqual(run("v1.10.0", ["v1.9.0"])[:2], (0, ["v1", "v1.10"]))
        self.assertEqual(run("v1.9.1", ["v1.10.0", "v1.9.0"])[:2], (0, ["v1.9"]))

    def test_other_majors_do_not_count(self):
        self.assertEqual(run("v1.2.0", ["v2.0.0", "v1.1.0"])[:2], (0, ["v1", "v1.2"]))
        self.assertEqual(run("v2.0.0", ["v1.9.0"])[:2], (0, ["v2", "v2.0"]))

    def test_other_tags_are_ignored(self):
        self.assertEqual(run("v1.0.0", ["v1.5.0-rc1", "old", "v9"])[:2], (0, ["v1", "v1.0"]))

    def test_tag_that_is_not_a_full_version_fails(self):
        self.assertEqual(run("v1.0", [], "1.0")[0], 1)

    def test_tag_that_differs_from_the_gem_version_fails(self):
        code, out, err = run("v1.1.0", ["v1.0.0"], "1.0.0")
        self.assertEqual((code, out), (1, []))
        self.assertIn("1.0.0", err)


if __name__ == "__main__":
    unittest.main()
