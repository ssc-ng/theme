"""Tests for script/released_versions.sh, with release_targets.py after it."""
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENV = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.org",
       "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@example.org"}


class Repo:
    """A git repository whose remote branches and tags hold given versions."""

    def __init__(self, path):
        self.path = path
        self.git("init", "-q")

    def git(self, *args):
        return subprocess.run(["git", "-c", "commit.gpgsign=false", "-c", "tag.gpgsign=false", *args],
                              cwd=self.path, env=ENV, check=True, capture_output=True, text=True).stdout.strip()

    def commit(self, version):
        Path(self.path, "ssc-ng-theme.gemspec").write_text(f'  spec.version = "{version}"\n')
        self.git("add", ".")
        self.git("commit", "-q", "--allow-empty", "-m", version)
        return self.git("rev-parse", "HEAD")

    def released(self):
        return subprocess.run(["bash", ROOT / "script/released_versions.sh"], cwd=self.path,
                              check=True, capture_output=True, text=True).stdout.split()

    def targets(self, tag):
        versions = "\n".join(self.released()) + "\n"
        r = subprocess.run([sys.executable, "-I", ROOT / "script/release_targets.py", tag, "ssc-ng-theme.gemspec"],
                           cwd=self.path, input=versions, capture_output=True, text=True)
        return r.stdout.split()


class ReleasedVersions(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.repo = Repo(tmp.name)

    def release(self, version, *branches):
        sha = self.repo.commit(version)
        for branch in branches:
            self.repo.git("update-ref", f"refs/remotes/origin/{branch}", sha)

    def test_reads_the_version_on_each_release_branch(self):
        self.release("1.0.0", "v1.0")
        self.release("1.2.0", "v1", "v1.2")
        self.assertEqual(sorted(self.repo.released()), ["v1.0.0", "v1.2.0", "v1.2.0"])

    def test_other_branches_do_not_count(self):
        self.release("1.0.0", "v1")
        self.release("9.0.0", "main", "v1-experiment", "v1.2.3")
        self.assertEqual(self.repo.released(), ["v1.0.0"])

    def test_a_typo_tag_does_not_stop_v1_moving(self):
        self.release("1.1.0", "v1", "v1.1")
        self.repo.git("tag", "v1.20.0")
        self.repo.commit("1.2.0")
        self.assertEqual(self.repo.targets("v1.2.0"), ["v1", "v1.2"])

    def test_a_failed_higher_release_does_not_stop_v1_moving(self):
        self.release("1.2.0", "v1", "v1.2")
        self.repo.commit("1.3.0")
        self.repo.git("tag", "v1.3.0")
        self.repo.commit("1.2.1")
        self.assertEqual(self.repo.targets("v1.2.1"), ["v1", "v1.2"])

    def test_a_patch_to_an_older_minor_still_leaves_v1_alone(self):
        self.release("1.0.0", "v1.0")
        self.release("1.1.0", "v1", "v1.1")
        self.repo.commit("1.0.1")
        self.assertEqual(self.repo.targets("v1.0.1"), ["v1.0"])


class Workflow(unittest.TestCase):
    def test_release_and_gate_use_released_versions_not_tags(self):
        ci = (ROOT / ".github/workflows/ci.yml").read_text()
        self.assertNotIn("git tag --list", ci)
        self.assertEqual(ci.count("script/released_versions.sh"), 2)

    def test_gate_checks_it_built_the_candidate(self):
        self.assertIn("bundle info ssc-ng-theme --path", (ROOT / ".github/workflows/ci.yml").read_text())


if __name__ == "__main__":
    unittest.main()
