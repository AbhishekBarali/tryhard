"""Runs every case in fixtures/final_messages.txt through the Stop hook.

Good cases must pass untouched and bad cases must trip exactly the checks they
name. Run this file directly to print how often each check fires per group:

    PYTHONDONTWRITEBYTECODE=1 python3 tests/test_corpus.py --report
"""

import importlib.util
import json
import os
import shutil
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOK_PATH = os.path.join(ROOT, "plugins", "tryhard", "hooks", "tryhard_stop.py")
CORPUS = os.path.join(ROOT, "tests", "fixtures", "final_messages.txt")

sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location("tryhard_stop_corpus", HOOK_PATH)
hook = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hook)


def load_corpus(path=CORPUS):
    """Return a list of dicts with id, group, expect, users and message."""
    with open(path, encoding="utf-8") as handle:
        text = handle.read()
    cases = []
    for chunk in text.split("\n=== ")[1:]:
        header, _, message = chunk.partition("\n---\n")
        lines = header.splitlines()
        case = {"id": lines[0].strip(), "expect": set(), "users": [], "message": message.rstrip("\n")}
        for line in lines[1:]:
            key, _, value = line.partition(":")
            value = value.strip()
            if key == "expect":
                case["expect"] = {part.strip() for part in value.split(",") if part.strip() and part.strip() != "none"}
            elif key == "user":
                case["users"].append(value)
        case["group"] = case["id"].split("-", 1)[0]
        cases.append(case)
    return cases


def fired_checks(case, data_dir):
    """Run one case through evaluate() with a fresh state dir; return the set of checks that fired."""
    transcript = hook.Transcript()
    transcript.user_texts = list(case["users"])
    payload = {
        "session_id": "corpus-" + case["id"],
        "turn_id": "turn-1",
        "transcript_path": "/unused",
        "cwd": "/tmp",
        "hook_event_name": "Stop",
        "model": "gpt-6.2-astra",
        "permission_mode": "default",
        "stop_hook_active": False,
        "last_assistant_message": case["message"],
    }
    output = hook.evaluate(payload, {"PLUGIN_DATA": data_dir}, transcript_reader=lambda path: transcript)
    if not output:
        return set()
    reason = json.loads(output)["reason"]
    markers = {
        "handback": hook.handback_reason("x").split("(")[0],
        "own-work": "never appear in their messages",
        "readability": "hard to follow",
    }
    return {name for name, marker in markers.items() if marker in reason}


def report(cases, data_dir):
    lines = []
    for group in ("good", "bad"):
        members = [case for case in cases if case["group"] == group]
        lines.append("%s: %d messages" % (group, len(members)))
        results = {case["id"]: fired_checks(case, data_dir) for case in members}
        for name in hook.CHECKS:
            hits = [cid for cid, fired in results.items() if name in fired]
            lines.append("  %-12s fires on %2d/%d" % (name, len(hits), len(members)))
        blocked = [cid for cid, fired in results.items() if fired]
        lines.append("  any check    fires on %2d/%d" % (len(blocked), len(members)))
        wrong = [
            "%s (expected %s, got %s)" % (case["id"], sorted(case["expect"]) or "none", sorted(results[case["id"]]) or "none")
            for case in members
            if results[case["id"]] != case["expect"]
        ]
        lines.extend("  MISMATCH " + item for item in wrong)
    return "\n".join(lines)


class CorpusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = load_corpus()

    def setUp(self):
        self.data = tempfile.mkdtemp(prefix="tryhard-corpus-")

    def tearDown(self):
        shutil.rmtree(self.data, ignore_errors=True)

    def test_corpus_size(self):
        groups = [case["group"] for case in self.cases]
        self.assertGreaterEqual(groups.count("good"), 40)
        self.assertGreaterEqual(groups.count("bad"), 20)
        self.assertEqual(len({case["id"] for case in self.cases}), len(self.cases))

    def test_good_messages_pass(self):
        for case in self.cases:
            if case["group"] == "good":
                with self.subTest(case["id"]):
                    self.assertEqual(fired_checks(case, self.data), case["expect"])

    def test_bad_messages_are_caught(self):
        for case in self.cases:
            if case["group"] == "bad":
                with self.subTest(case["id"]):
                    self.assertTrue(case["expect"], "bad cases must name a check")
                    self.assertEqual(fired_checks(case, self.data), case["expect"])


if __name__ == "__main__":
    if "--report" in sys.argv:
        directory = tempfile.mkdtemp(prefix="tryhard-corpus-")
        try:
            print(report(load_corpus(), directory))
        finally:
            shutil.rmtree(directory, ignore_errors=True)
    else:
        unittest.main()
