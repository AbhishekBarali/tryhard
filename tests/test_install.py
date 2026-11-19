"""Tests for install.sh, run against a throwaway CODEX_HOME."""

import glob
import os
import shutil
import subprocess
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
START = "<!-- donedone:start -->"
END = "<!-- donedone:end -->"
SNIPPET = "## Done Done\n\nDefine what done means before you start.\n"


@unittest.skipIf(shutil.which("bash") is None, "needs bash")
class InstallTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="dd-install-")
        self.repo = os.path.join(self.tmp, "repo")
        os.makedirs(os.path.join(self.repo, "agents-md"))
        shutil.copy(os.path.join(ROOT, "install.sh"), self.repo)
        self.snippet = os.path.join(self.repo, "agents-md", "AGENTS.snippet.md")
        self.write(self.snippet, SNIPPET)
        self.home = os.path.join(self.tmp, "codex-home")
        self.agents = os.path.join(self.home, "AGENTS.md")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def write(self, path, text):
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(text)

    def read(self, path):
        with open(path, encoding="utf-8") as handle:
            return handle.read()

    def run_install(self, *args):
        env = dict(os.environ, CODEX_HOME=self.home, HOME=self.tmp)
        return subprocess.run(
            ["bash", os.path.join(self.repo, "install.sh")] + list(args),
            capture_output=True,
            text=True,
            env=env,
            stdin=subprocess.DEVNULL,
            timeout=60,
        )

    def backups(self):
        return glob.glob(self.agents + ".bak-donedone-*")

    def test_creates_the_file_and_prints_the_steps(self):
        result = self.run_install()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.read(self.agents), START + "\n" + SNIPPET + END + "\n")
        self.assertEqual(self.backups(), [])
        self.assertIn("codex plugin marketplace add AbhishekBarali/donedone", result.stdout)
        self.assertIn("codex plugin add donedone@donedone", result.stdout)
        self.assertIn("/hooks", result.stdout)
        self.assertIn("DONEDONE_HOOK=off", result.stdout)
        # Nothing else is created in CODEX_HOME.
        self.assertEqual(os.listdir(self.home), ["AGENTS.md"])

    def test_second_run_changes_nothing(self):
        self.run_install()
        first = self.read(self.agents)
        result = self.run_install()
        self.assertEqual(result.returncode, 0)
        self.assertEqual(self.read(self.agents), first)
        self.assertEqual(self.backups(), [])
        self.assertIn("Nothing changed", result.stdout)

    def test_existing_text_is_kept_and_backed_up(self):
        os.makedirs(self.home)
        self.write(self.agents, "# My rules\n\nUse tabs.")
        result = self.run_install()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.read(self.agents), "# My rules\n\nUse tabs.\n\n" + START + "\n" + SNIPPET + END + "\n")
        backups = self.backups()
        self.assertEqual(len(backups), 1)
        self.assertEqual(self.read(backups[0]), "# My rules\n\nUse tabs.")

    def test_update_replaces_only_the_block(self):
        os.makedirs(self.home)
        self.write(self.agents, "Before.\n\n" + START + "\nold text\n" + END + "\n\nAfter.\n")
        result = self.run_install()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.read(self.agents), "Before.\n\n" + START + "\n" + SNIPPET + END + "\n\nAfter.\n")
        self.assertEqual(len(self.backups()), 1)

    def test_markers_inside_the_snippet_are_not_doubled(self):
        self.write(self.snippet, START + "\n" + SNIPPET + END + "\n")
        self.run_install()
        text = self.read(self.agents)
        self.assertEqual(text.count(START), 1)
        self.assertEqual(text.count(END), 1)

    def test_remove(self):
        os.makedirs(self.home)
        self.write(self.agents, "Before.\n")
        self.run_install()
        result = self.run_install("--remove")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.read(self.agents), "Before.\n")
        self.assertIn("codex plugin remove donedone@donedone", result.stdout)
        again = self.run_install("--remove")
        self.assertIn("Nothing changed", again.stdout)

    def test_install_then_remove_gives_back_the_original(self):
        os.makedirs(self.home)
        original = "# My rules\n\nUse tabs.\n"
        self.write(self.agents, original)
        for _ in range(3):
            self.run_install()
            self.run_install("--remove")
        self.assertEqual(self.read(self.agents), original)

    def test_remove_from_the_middle_keeps_the_text_around_it(self):
        os.makedirs(self.home)
        self.write(self.agents, "Before.\n\n" + START + "\nold text\n" + END + "\n\nAfter.\n")
        result = self.run_install("--remove")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.read(self.agents), "Before.\n\nAfter.\n")

    def test_missing_snippet_is_reported_and_nothing_is_written(self):
        os.remove(self.snippet)
        result = self.run_install()
        self.assertEqual(result.returncode, 1)
        self.assertIn("AGENTS.snippet.md is missing", result.stderr)
        self.assertIn("codex plugin add donedone@donedone", result.stdout)
        self.assertFalse(os.path.exists(self.home))

    def test_broken_markers_stop_the_script(self):
        os.makedirs(self.home)
        self.write(self.agents, START + "\nno end marker\n")
        result = self.run_install()
        self.assertEqual(result.returncode, 1)
        self.assertIn("no end marker", result.stderr)
        self.assertEqual(self.read(self.agents), START + "\nno end marker\n")

    def test_override_file_warning(self):
        os.makedirs(self.home)
        self.write(os.path.join(self.home, "AGENTS.override.md"), "override rules\n")
        result = self.run_install()
        self.assertEqual(result.returncode, 0)
        self.assertIn("AGENTS.override.md", result.stderr)

    def test_unknown_option(self):
        result = self.run_install("--bogus")
        self.assertEqual(result.returncode, 2)
        self.assertFalse(os.path.exists(self.home))

    def test_help(self):
        result = self.run_install("--help")
        self.assertEqual(result.returncode, 0)
        self.assertIn("--remove", result.stdout)
        self.assertFalse(os.path.exists(self.home))


if __name__ == "__main__":
    unittest.main()
