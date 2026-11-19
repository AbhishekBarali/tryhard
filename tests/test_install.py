"""Tests for install.sh, run against a throwaway CODEX_HOME."""

import glob
import os
import shutil
import subprocess
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
START = "<!-- tryhard:start -->"
END = "<!-- tryhard:end -->"
SNIPPET = "## Tryhard\n\nDefine what done means before you start.\n"


@unittest.skipIf(shutil.which("bash") is None, "needs bash")
class InstallTests(unittest.TestCase):
    def setUp(self):
        # Spaces in every path, as on many macOS and Windows home folders.
        self.tmp = tempfile.mkdtemp(prefix="tryhard install ")
        self.repo = os.path.join(self.tmp, "my repo")
        os.makedirs(os.path.join(self.repo, "agents-md"))
        shutil.copy(os.path.join(ROOT, "install.sh"), self.repo)
        self.snippet = os.path.join(self.repo, "agents-md", "AGENTS.snippet.md")
        self.write(self.snippet, SNIPPET)
        self.home = os.path.join(self.tmp, "codex home")
        self.agents = os.path.join(self.home, "AGENTS.md")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def write(self, path, text):
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(text)

    def read(self, path):
        with open(path, encoding="utf-8") as handle:
            return handle.read()

    def run_install(self, *args, **options):
        env = dict(os.environ, CODEX_HOME=self.home, HOME=self.tmp)
        env.pop("CDPATH", None)
        env.update(options.get("env", {}))
        for name in options.get("unset", ()):
            env.pop(name, None)
        script = options.get("script", os.path.join(self.repo, "install.sh"))
        return subprocess.run(
            ["bash", script] + list(args),
            capture_output=True,
            text=True,
            env=env,
            cwd=options.get("cwd"),
            stdin=subprocess.DEVNULL,
            timeout=60,
        )

    def read_bytes(self, path):
        with open(path, "rb") as handle:
            return handle.read()

    def backups(self):
        return glob.glob(self.agents + ".bak-tryhard-*")

    def test_creates_the_file_and_prints_the_steps(self):
        result = self.run_install()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.read(self.agents), START + "\n" + SNIPPET + END + "\n")
        self.assertEqual(self.backups(), [])
        self.assertIn("codex plugin marketplace add AbhishekBarali/tryhard", result.stdout)
        self.assertIn("codex plugin add tryhard@tryhard", result.stdout)
        self.assertIn("/hooks", result.stdout)
        self.assertIn("TRYHARD_HOOK=off", result.stdout)
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
        self.assertIn("codex plugin remove tryhard@tryhard", result.stdout)
        again = self.run_install("--remove")
        self.assertIn("Nothing changed", again.stdout)

    def test_remove_takes_away_a_file_the_installer_created(self):
        self.run_install()
        result = self.run_install("--remove")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(os.path.exists(self.agents))
        self.assertIn("held only the Tryhard block", result.stdout)
        backups = self.backups()
        self.assertEqual(len(backups), 1)
        self.assertEqual(self.read(backups[0]), START + "\n" + SNIPPET + END + "\n")
        again = self.run_install("--remove")
        self.assertEqual(again.returncode, 0, again.stderr)
        self.assertIn("Nothing changed", again.stdout)
        self.assertFalse(os.path.exists(self.agents))

    @unittest.skipUnless(hasattr(os, "symlink"), "needs symlinks")
    def test_remove_keeps_a_symlink_even_when_nothing_is_left(self):
        os.makedirs(self.home)
        target = os.path.join(self.tmp, "dotfiles AGENTS.md")
        self.write(target, "")
        os.symlink(target, self.agents)
        self.run_install()
        self.assertEqual(self.run_install("--remove").returncode, 0)
        self.assertTrue(os.path.islink(self.agents))
        self.assertEqual(self.read(target), "")

    def test_missing_final_newline_is_added(self):
        # Install has to end the last line before the block, and remove can't
        # tell afterwards whether the newline was there before.
        os.makedirs(self.home)
        self.write(self.agents, "# My rules\n- Use tabs.")
        self.run_install()
        self.assertEqual(self.run_install("--remove").returncode, 0)
        self.assertEqual(self.read(self.agents), "# My rules\n- Use tabs.\n")

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
        self.assertIn("codex plugin add tryhard@tryhard", result.stdout)
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

    def test_relative_path_with_cdpath_exported(self):
        # With CDPATH exported, a bare cd prints the folder, which used to end
        # up inside the script's own path.
        result = self.run_install(
            script=os.path.join("my repo", "install.sh"), cwd=self.tmp, env={"CDPATH": ".:" + self.tmp}
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.read(self.agents), START + "\n" + SNIPPET + END + "\n")
        self.assertIn('codex plugin marketplace add "%s"' % os.path.realpath(self.repo), result.stdout)

    def test_codex_home_unset_uses_home(self):
        result = self.run_install(unset=["CODEX_HOME"])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(os.path.isfile(os.path.join(self.tmp, ".codex", "AGENTS.md")))
        self.assertFalse(os.path.exists(self.home))
        empty = self.run_install(env={"CODEX_HOME": ""})
        self.assertEqual(empty.returncode, 0, empty.stderr)
        self.assertIn("already has the current Tryhard block", empty.stdout)

    def test_no_home_at_all_is_a_clear_error(self):
        result = self.run_install(unset=["CODEX_HOME", "HOME"])
        self.assertEqual(result.returncode, 1)
        self.assertIn("Neither CODEX_HOME nor HOME is set", result.stderr)
        self.assertNotIn("unbound variable", result.stderr)

    def test_crlf_file_is_updated_and_removed_without_duplicates(self):
        os.makedirs(self.home)
        original = b"# Mine\r\n\r\nUse tabs.\r\n"
        with open(self.agents, "wb") as handle:
            handle.write(original + b"\r\n" + START.encode() + b"\r\nold\r\n" + END.encode() + b"\r\n")
        self.assertEqual(self.run_install().returncode, 0)
        text = self.read_bytes(self.agents)
        self.assertEqual(text.count(START.encode()), 1)
        self.assertIn(SNIPPET.encode(), text)
        self.assertNotIn(b"old", text)
        self.assertEqual(self.run_install("--remove").returncode, 0)
        self.assertEqual(self.read_bytes(self.agents), original)

    def test_crlf_snippet_is_normalised(self):
        with open(self.snippet, "wb") as handle:
            handle.write((START + "\r\n" + SNIPPET.replace("\n", "\r\n") + END + "\r\n").encode())
        self.assertEqual(self.run_install().returncode, 0)
        self.assertEqual(self.read_bytes(self.agents), (START + "\n" + SNIPPET + END + "\n").encode())

    @unittest.skipUnless(hasattr(os, "symlink"), "needs symlinks")
    def test_symlinked_agents_file_stays_a_symlink(self):
        os.makedirs(self.home)
        target = os.path.join(self.tmp, "dotfiles AGENTS.md")
        self.write(target, "# Dotfiles\n")
        os.symlink(target, self.agents)
        self.assertEqual(self.run_install().returncode, 0)
        self.assertTrue(os.path.islink(self.agents))
        self.assertIn(START, self.read(target))


if __name__ == "__main__":
    unittest.main()
