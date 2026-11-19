"""Checks that the marketplace, manifest, hooks file and profile match what Codex reads."""

import json
import os
import re
import shutil
import subprocess
import tempfile
import unittest
import xml.dom.minidom

try:
    import tomllib
except ImportError:  # Python < 3.11
    tomllib = None

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLUGIN = os.path.join(ROOT, "plugins", "tryhard")


def load(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as handle:
        return json.load(handle)


class MarketplaceTests(unittest.TestCase):
    def test_lists_the_plugin_with_a_local_source(self):
        market = load(".agents", "plugins", "marketplace.json")
        self.assertEqual(market["name"], "tryhard")
        self.assertEqual(len(market["plugins"]), 1)
        entry = market["plugins"][0]
        self.assertEqual(entry["name"], "tryhard")
        self.assertEqual(entry["source"], {"source": "local", "path": "./plugins/tryhard"})
        self.assertEqual(entry["policy"], {"installation": "AVAILABLE", "authentication": "ON_INSTALL"})
        self.assertTrue(os.path.isfile(os.path.join(ROOT, entry["source"]["path"], ".codex-plugin", "plugin.json")))


class ManifestTests(unittest.TestCase):
    def setUp(self):
        self.manifest = load("plugins", "tryhard", ".codex-plugin", "plugin.json")

    def test_core_fields(self):
        manifest = self.manifest
        self.assertEqual(manifest["name"], "tryhard")
        self.assertRegex(manifest["name"], r"^[a-z0-9][a-z0-9.-]{0,63}$")
        self.assertEqual(manifest["version"], "0.2.0")
        self.assertEqual(manifest["license"], "MIT")
        self.assertEqual(manifest["author"]["name"], "Abhishek Barali")
        self.assertEqual(manifest["skills"], "./skills/")
        self.assertTrue(manifest["description"])
        self.assertTrue(manifest["keywords"])

    def test_no_hooks_key_so_codex_finds_hooks_json(self):
        # A "hooks" entry in the manifest replaces hooks/hooks.json instead of adding to it.
        self.assertNotIn("hooks", self.manifest)
        self.assertNotIn("hooks", self.manifest.get("extensions", {}).get("com.openai", {}))

    def test_interface(self):
        interface = self.manifest["interface"]
        for key in ("displayName", "shortDescription", "longDescription", "category", "capabilities", "brandColor"):
            self.assertTrue(interface.get(key), key)
        self.assertRegex(interface["brandColor"], r"^#[0-9A-Fa-f]{6}$")
        prompts = interface["defaultPrompt"]
        self.assertLessEqual(len(prompts), 3)
        for prompt in prompts:
            self.assertTrue(0 < len(prompt) <= 512, prompt)
            self.assertRegex(prompt, r"^\$tryhard:(raise-the-bar|set-a-goal) ")

    def test_paths_stay_inside_the_plugin(self):
        interface = self.manifest["interface"]
        for key in ("composerIcon", "logo"):
            path = interface[key]
            self.assertTrue(path.startswith("./"), path)
            self.assertTrue(os.path.isfile(os.path.normpath(os.path.join(PLUGIN, path))), path)
        self.assertTrue(self.manifest["skills"].startswith("./"))

    def test_icon_is_valid_svg(self):
        document = xml.dom.minidom.parse(os.path.join(PLUGIN, "assets", "icon.svg"))
        self.assertEqual(document.documentElement.tagName, "svg")


def stop_handler():
    hooks = load("plugins", "tryhard", "hooks", "hooks.json")["hooks"]
    return hooks["Stop"][0]["hooks"][0]


class HooksFileTests(unittest.TestCase):
    def test_one_stop_hook_pointing_at_the_script(self):
        hooks = load("plugins", "tryhard", "hooks", "hooks.json")
        self.assertEqual(list(hooks), ["hooks"])  # HooksFile rejects unknown top-level keys
        hooks = hooks["hooks"]
        self.assertEqual(list(hooks), ["Stop"])
        self.assertEqual(len(hooks["Stop"]), 1)
        handlers = hooks["Stop"][0]["hooks"]
        self.assertEqual(len(handlers), 1)
        handler = handlers[0]
        self.assertEqual(set(handler), {"type", "command", "commandWindows", "timeout", "statusMessage"})
        self.assertEqual(handler["type"], "command")
        self.assertIsInstance(handler["timeout"], int)
        self.assertFalse(handler.get("async", False))  # async hooks can't block
        match = re.search(r"\$\{PLUGIN_ROOT\}/(\S+?)\"", handler["command"])
        self.assertIsNotNone(match)
        self.assertTrue(os.path.isfile(os.path.join(PLUGIN, match.group(1))))
        windows = re.search(r"\$\{PLUGIN_ROOT\}\\(\S+?)\"", handler["commandWindows"])
        self.assertEqual(windows.group(1).replace("\\", "/"), match.group(1))

    def test_commands_work_in_every_shell_codex_uses(self):
        # Codex replaces ${PLUGIN_ROOT} itself before running the command with
        # the session's shell: zsh, bash or sh -c on Unix, and on Windows
        # PowerShell -Command or cmd /c. PowerShell never expands %VAR%.
        handler = stop_handler()
        for key in ("command", "commandWindows"):
            self.assertNotRegex(handler[key], r"%\w+%")
            self.assertNotRegex(handler[key].replace("${PLUGIN_ROOT}", ""), r"\$")
            self.assertIn(" -I ", handler[key])  # PYTHONPATH and the cwd can't shadow the stdlib


class HookCommandRunTests(unittest.TestCase):
    """Run the Unix command the way Codex does, from a plugin path with spaces."""

    PAYLOAD = {
        "session_id": "packaging-test",
        "turn_id": "turn-1",
        "transcript_path": None,
        "cwd": "/tmp",
        "hook_event_name": "Stop",
        "model": "gpt-6.2-astra",
        "permission_mode": "default",
        "stop_hook_active": False,
        "last_assistant_message": "Done. Want me to add tests for the parser?",
    }

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="tryhard plugin ")
        self.root = os.path.join(self.tmp, "plugins cache", "tryhard")
        shutil.copytree(os.path.join(PLUGIN, "hooks"), os.path.join(self.root, "hooks"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def run_in(self, argv):
        # A fresh state folder each time: the hook blocks a given turn only once.
        data = tempfile.mkdtemp(dir=self.tmp)
        env = dict(os.environ, PLUGIN_ROOT=self.root, PLUGIN_DATA=data)
        for name in ("TRYHARD_HOOK", "TRYHARD_CHECKS", "PYTHONDONTWRITEBYTECODE"):
            env.pop(name, None)
        return subprocess.run(
            argv,
            input=json.dumps(self.PAYLOAD),
            capture_output=True,
            text=True,
            env=env,
            cwd=self.tmp,
            timeout=60,
        )

    @unittest.skipIf(shutil.which("python3") is None, "needs python3 on PATH")
    def test_unix_command(self):
        command = stop_handler()["command"].replace("${PLUGIN_ROOT}", self.root)
        shells = [[shell, "-c"] for shell in ("sh", "bash", "dash", "zsh") if shutil.which(shell)]
        if shutil.which("pwsh"):
            shells.append(["pwsh", "-NoProfile", "-Command"])
        self.assertTrue(shells)
        for shell in shells:
            with self.subTest(shell[0]):
                result = self.run_in(shell + [command])
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(json.loads(result.stdout)["decision"], "block")
                self.assertFalse(os.path.exists(os.path.join(self.root, "hooks", "__pycache__")))


class ProfileTests(unittest.TestCase):
    @unittest.skipIf(tomllib is None, "tomllib needs Python 3.11+")
    def test_profile_parses_and_uses_known_values(self):
        with open(os.path.join(ROOT, "profiles", "tryhard.config.toml"), "rb") as handle:
            profile = tomllib.load(handle)
        efforts = {"low", "medium", "high", "xhigh", "max", "ultra"}
        self.assertIn(profile["model_reasoning_effort"], efforts)
        self.assertIn(profile["plan_mode_reasoning_effort"], efforts)
        self.assertIn(profile["model_verbosity"], {"low", "medium", "high"})
        self.assertIn(profile["agents"]["default_subagent_reasoning_effort"], efforts)


if __name__ == "__main__":
    unittest.main()
