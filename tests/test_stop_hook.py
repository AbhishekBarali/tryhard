"""Tests for plugins/tryhard/hooks/tryhard_stop.py (stdlib unittest only)."""

import importlib.util
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOK_PATH = os.path.join(ROOT, "plugins", "tryhard", "hooks", "tryhard_stop.py")
FIXTURES = os.path.join(ROOT, "tests", "fixtures")

# Keep __pycache__ out of the plugin folder that gets installed.
sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location("tryhard_stop", HOOK_PATH)
hook = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hook)


def fixture(name):
    return os.path.join(FIXTURES, name)


REPORT_TAIL = (
    "\n\nI changed the cache key so it includes the locale, which stops French pages from being "
    "served to English visitors. The fix is in the page cache module and nowhere else.\n\n"
    "I checked it by running the full test suite, which passes, and by loading the home page in "
    "both languages on the local server. I did not test the CDN layer because it is not running "
    "here.\n\n"
    "Nothing else is open. I kept the old cache entries because they expire on their own within "
    "an hour, so no manual purge is needed."
)

DENSE_SSD_OPENING = (
    "Root cause is store-side, not git: `worktree add` is ~0.4 s; the tail is pnpm's per-tree link "
    "phase, with `node-linker=isolated` and the CAS under `~/.local/share/pnpm/store/v10`, the "
    "~212k-inode hardlink fan-out falls back to copy since wt-3 is on a different mount (EXDEV), so "
    "reflink is ineligible; compounded by side-effects-cache misses from the postinstall hash drift "
    "seen in r7."
)

PLAIN_SSD_OPENING = (
    "Worktrees are slow on this machine because its SSD is slow. Git creates the worktree in under "
    "a second. The rest of the time is the package install, which writes about 200,000 small files, "
    "and this disk writes small files about 8 times slower than your laptop."
)


class HookTestCase(unittest.TestCase):
    def setUp(self):
        self.data = tempfile.mkdtemp(prefix="tryhard-test-")
        self.env = {"PLUGIN_DATA": self.data}
        self.turn = 0

    def tearDown(self):
        shutil.rmtree(self.data, ignore_errors=True)

    def payload(self, message, **overrides):
        self.turn += 1
        data = {
            "session_id": "019a96c1-5a2e-7d31-9f0e-2b8d41c7e5a0",
            "turn_id": "turn-%d" % self.turn,
            "transcript_path": None,
            "cwd": "/home/dev/projects/landing",
            "hook_event_name": "Stop",
            "model": "gpt-6.2-astra",
            "permission_mode": "default",
            "stop_hook_active": False,
            "last_assistant_message": message,
        }
        data.update(overrides)
        return data

    def run_hook(self, message, env=None, **overrides):
        output = hook.evaluate(self.payload(message, **overrides), env if env is not None else self.env)
        return json.loads(output) if output else None


# ---------------------------------------------------------------------------


class SettingsTests(unittest.TestCase):
    def test_off_values_disable_the_hook(self):
        for value in ("0", "off", "OFF", "false", "no", "disabled", " off "):
            self.assertTrue(hook.hook_disabled({"TRYHARD_HOOK": value}), value)
        for value in ("", "1", "on", "yes"):
            self.assertFalse(hook.hook_disabled({"TRYHARD_HOOK": value}), value)
        self.assertFalse(hook.hook_disabled({}))

    def test_check_selection(self):
        self.assertEqual(hook.enabled_checks({}), list(hook.CHECKS))
        self.assertEqual(hook.enabled_checks({"TRYHARD_CHECKS": ""}), list(hook.CHECKS))
        self.assertEqual(hook.enabled_checks({"TRYHARD_CHECKS": "all"}), list(hook.CHECKS))
        self.assertEqual(hook.enabled_checks({"TRYHARD_CHECKS": "none"}), [])
        self.assertEqual(
            hook.enabled_checks({"TRYHARD_CHECKS": "readability, handback"}),
            ["handback", "readability"],
        )
        self.assertEqual(hook.enabled_checks({"TRYHARD_CHECKS": "own_work"}), ["own-work"])
        self.assertEqual(hook.enabled_checks({"TRYHARD_CHECKS": "hand-back own-files"}), ["handback", "own-work"])
        self.assertEqual(hook.enabled_checks({"TRYHARD_CHECKS": "typo"}), [])


# ---------------------------------------------------------------------------


class HandbackTests(unittest.TestCase):
    POSITIVE = [
        "Fixed the parser and added a regression test. All 42 tests pass.\n\nWant me to also add a CLI flag for verbose output?",
        "The migration is written and tested locally. Shall I run it against the staging copy too?",
        "Done with the refactor. Would you like me to update the docs to match?",
        "Everything builds. Do you want me to wire the new endpoint into the router?",
        "The script works on the sample files. Let me know if you want me to run it on the full set.",
        "I can also add retries for the upload step if you'd like.",
        "If you'd like, I can convert the remaining three pages the same way.",
        "Tests pass. Should I go ahead and fix the two lint warnings as well?",
        "The fix is in. **Want me to add a test for the empty-input case?**",
        "Report is ready. Happy to add charts for the weekly numbers if you want.",
        "So, should we also cover the Windows paths?",
        "Tests pass. Should I also look at the two slow tests, or leave it here?",
        "Retries are in. Want me to tackle the docs or the dashboard next?",
        "Rate limits are live.\n\nIf you'd like, I can also:\n\n- add per-route limits\n- document the headers",
        "Want me to:\n\n- add tests\n- update the docs?",
        # Destructive words used as names, not as the action.
        "The list works. Want me to add a delete button to each row?",
        "If you'd like, I can add a purge command for the cache.",
    ]
    NEGATIVE = [
        "Fixed the parser and added a regression test. All 42 tests pass.",
        "Done. Let me know if you'd like me to change anything.",
        "That's everything. Let me know if you need anything else.",
        "If you want to run it yourself, use `npm test`.",
        "I rendered two clips. Should I use 24_g521.mp4 or 24_p11.mp4?",
        "Should I use Postgres or SQLite for this?",
        "Want me to add tests? I did that too, and they all pass. The build is green.",
        "Here is the change:\n\n```python\n# Want me to?\nprint('hi')\n```\n\nIt is merged into the work branch and the tests pass.",
        "You can also add retries if you'd like, by setting `RETRIES=3`.",
        "Everything is merged into the work branch. Let me know if anything looks off.",
        "The next step would be moving the cron job, which is outside this task.",
        "",
        # A choice about how to do the asked work.
        "Do you want me to use your personal account or the company one for the release?",
        "The teaser is ready. Should I put it in public/video/intro.mp4 or next to it?",
        # Really the user's call.
        "Should I delete the backups in /var/backups/app that are older than 90 days?",
        "The hotfix is ready. Should I deploy it to production?",
        "Want me to send the invoice emails to the 40 customers now?",
        "Shall I publish the package?",
    ]

    def test_offers_at_the_end_are_found(self):
        for message in self.POSITIVE:
            self.assertIsNotNone(hook.check_handback(message), message)

    def test_other_endings_are_left_alone(self):
        for message in self.NEGATIVE:
            self.assertIsNone(hook.check_handback(message), message)

    def test_returns_the_offering_sentence(self):
        sentence = hook.check_handback("All done.\n\nWant me to open a pull request for this?")
        self.assertEqual(sentence, "Want me to open a pull request for this?")


class AnswerOnlyTests(unittest.TestCase):
    def test_questions_plans_and_reviews(self):
        for text in (
            "Why is the build slow on CI?",
            "What does the retry decorator do",
            "Make a plan for moving auth to the new service.",
            "Review this diff and tell me what you think.",
            "Look at the logs but don't change anything.",
            "Ask me before you change the schema.",
        ):
            self.assertTrue(hook.wants_answer_only(text), text)

    def test_tasks(self):
        for text in (
            "Fix the login timeout.",
            "Can you fix the flaky upload test?",
            "QA the checkout flow on mobile.",
            "Why does the export crash? Fix it.",
            "",
        ):
            self.assertFalse(hook.wants_answer_only(text), text)


# ---------------------------------------------------------------------------


class IdentifierTests(unittest.TestCase):
    def test_finds_files_paths_and_ids(self):
        text = (
            "Compare `out/run-3/metrics.json` with clips/24_g521.mp4, the file report_final.csv, "
            "commit 4be91c0d, worktree wt-3 and /tmp/scratch/a.log at https://example.com/x/y.png."
        )
        names = hook.extract_identifiers(text)
        for expected in ("out/run-3/metrics.json", "clips/24_g521.mp4", "report_final.csv", "4be91c0d", "wt-3", "/tmp/scratch/a.log"):
            self.assertIn(expected, names)
        self.assertFalse(any("example.com" in name for name in names), names)
        self.assertNotIn("24_g521", names)  # already covered by the path that contains it

    def test_ignores_prose_and_tool_names(self):
        text = "Should I upgrade Node.js and React for e.g. the and/or case in 24/7 mode at 3.14 speed?"
        self.assertEqual(hook.extract_identifiers(text), [])

    def test_known_names_match_by_basename_and_spelling(self):
        user = "export it to public/video/intro.mp4 and keep run 3"
        squashed = hook._squash(user)
        self.assertTrue(hook.known_to_user("intro.mp4", user, squashed))
        self.assertTrue(hook.known_to_user("/abs/public/video/intro.mp4", user, squashed))
        self.assertTrue(hook.known_to_user("run-3", user, squashed))
        self.assertFalse(hook.known_to_user("teaser_v2.mp4", user, squashed))


class OwnWorkTests(unittest.TestCase):
    USER = ["Make a 6 second teaser cut of the intro and put it next to public/video/intro.mp4."]

    def test_question_about_own_files(self):
        names = hook.check_own_work("I exported two teaser cuts. Should I use 24_g521.mp4 or 24_p11.mp4?", self.USER)
        self.assertEqual(names, ["24_g521.mp4", "24_p11.mp4"])

    def test_choice_question_refers_to_the_sentence_before(self):
        message = "I made two cuts, teaser_a.mp4 and teaser_b.mp4, both 6 seconds long. Which one should I keep?"
        self.assertEqual(hook.check_own_work(message, self.USER), ["teaser_a.mp4", "teaser_b.mp4"])

    def test_options_listed_after_the_question(self):
        message = "Both cuts are ready. Which should go on the page?\n\n- `out/teaser_fast.mp4`\n- `out/teaser_slow.mp4`"
        self.assertEqual(hook.check_own_work(message, self.USER), ["out/teaser_fast.mp4", "out/teaser_slow.mp4"])

    def test_names_the_user_used_are_fine(self):
        message = "The teaser is done. Should I overwrite public/video/intro.mp4 with it?"
        self.assertEqual(hook.check_own_work(message, self.USER), [])

    def test_non_choice_question_ignores_earlier_sentences(self):
        message = "The new cut is in out/teaser_fast.mp4. Want me to open a pull request?"
        self.assertEqual(hook.check_own_work(message, self.USER), [])

    def test_no_question_no_finding(self):
        self.assertEqual(hook.check_own_work("I used 24_g521.mp4 because it is shorter.", self.USER), [])

    def test_no_user_messages_means_no_finding(self):
        self.assertEqual(hook.check_own_work("Should I use 24_g521.mp4 or 24_p11.mp4?", []), [])

    def test_at_most_three_names(self):
        message = "Which one: a1.mp4, b1.mp4, c1.mp4 or d1.mp4?"
        self.assertEqual(len(hook.check_own_work(message, self.USER)), 3)

    def test_asking_the_user_to_act_is_fine(self):
        for message in (
            "The deploy is blocked. Can you add the key in ~/.ssh/id_ed25519.pub to the server?",
            "Could you add your Stripe key as STRIPE_SECRET_KEY in config/.env.local?",
            "Would you run scripts/rotate.sh from a machine with production access?",
        ):
            self.assertEqual(hook.check_own_work(message, self.USER), [], message)

    def test_asking_the_user_to_confirm_own_files_still_counts(self):
        message = "Can you confirm whether teaser_a.mp4 is the final cut?"
        self.assertEqual(hook.check_own_work(message, self.USER), ["teaser_a.mp4"])

    def test_destructive_and_taste_questions_are_fine(self):
        for message in (
            "Two old archives are left. Should I delete backup_2023.tar.gz or keep both?",
            "Should I overwrite out/teaser_final.mp4 with the new cut?",
            "Does the tone in docs/launch-email.md fit how you talk to your customers?",
        ):
            self.assertEqual(hook.check_own_work(message, self.USER), [], message)


# ---------------------------------------------------------------------------


class ReadabilityTests(unittest.TestCase):
    def test_short_messages_are_skipped(self):
        self.assertIsNone(hook.check_readability(DENSE_SSD_OPENING))

    def test_dense_opening_with_semicolons(self):
        detail = hook.check_readability(DENSE_SSD_OPENING + REPORT_TAIL)
        self.assertIsNotNone(detail)
        self.assertIn("semicolons", detail)

    def test_plain_report_passes(self):
        self.assertIsNone(hook.check_readability(PLAIN_SSD_OPENING + REPORT_TAIL))

    def test_heading_is_not_the_opening(self):
        self.assertIsNone(hook.check_readability("## Summary\n\n" + PLAIN_SSD_OPENING + REPORT_TAIL))

    def test_opening_packed_with_code_names(self):
        opening = (
            "Updated `src/auth/session.ts`, `src/auth/token.ts`, `refreshToken()`, `SESSION_TTL_MS`, "
            "`lib/clock.ts`, `tests/session.test.ts` and `scripts/seed_users.py` so that the session "
            "refresh path uses one clock source everywhere in the app, which stops the early logouts "
            "people saw after the clocks changed last week."
        )
        detail = hook.check_readability(opening + REPORT_TAIL)
        self.assertIsNotNone(detail)
        self.assertIn("code names", detail)

    def test_stacked_semicolons_later_in_the_message(self):
        middle = "\n\nThe cache was stale; the key ignored the locale; the purge job was off; nobody noticed."
        detail = hook.check_readability(PLAIN_SSD_OPENING + middle + REPORT_TAIL)
        self.assertIsNotNone(detail)
        self.assertIn("4 clauses", detail)

    def test_semicolons_in_code_do_not_count(self):
        code = "\n\n```js\nlet a = 1; let b = 2; let c = 3; let d = 4;\n```"
        span = "\n\nThe config line is `a=1; b=2; c=3; d=4` and it is unchanged."
        self.assertIsNone(hook.check_readability(PLAIN_SSD_OPENING + code + span + REPORT_TAIL))

    def test_ordinary_technical_report_passes(self):
        message = (
            "The login timeout is fixed. Sessions were expiring early because `refreshToken()` compared "
            "seconds with milliseconds, so a one hour session ended after about four seconds of idle time.\n\n"
            "What changed:\n\n"
            "- `src/auth/session.ts` now converts both values to milliseconds before comparing.\n"
            "- `src/auth/session.test.ts` has a new test that idles for five seconds and stays logged in.\n"
            "- `docs/auth.md` explains the unit the setting uses.\n\n"
            "I ran the whole test suite, which passes, and logged in on the local server and waited ten "
            "minutes without being logged out. The admin panel uses the same session code, and I checked "
            "that it now behaves the same way. I did not test the mobile app because it uses a separate "
            "login service that this change does not touch.\n\n"
            "Nothing is left open. I kept the setting name the same so existing config files still work."
        )
        self.assertGreater(len(message), hook.LONG_MESSAGE_CHARS)
        self.assertIsNone(hook.check_readability(message))

    def test_separate_lines_are_not_one_long_paragraph(self):
        line = "Every service now starts with the shared config loader and reads the same settings file.  "
        opening = "\n".join([line] * 10)
        self.assertIsNone(hook.check_readability(opening + REPORT_TAIL))

    def test_very_long_opening(self):
        opening = " ".join(["The build now passes on every platform we support."] * 18)
        detail = hook.check_readability(opening + REPORT_TAIL)
        self.assertIsNotNone(detail)
        self.assertIn("words", detail)

    def test_medium_length_dense_message(self):
        message = DENSE_SSD_OPENING + "\n\nI moved the store onto the same disk, so installs take 14 seconds now."
        self.assertLess(len(message), 800)
        self.assertIn("semicolons", hook.check_readability(message))

    def test_summary_heading_and_file_list_is_not_an_opening_paragraph(self):
        message = (
            "**Summary**\n"
            "- Renamed `Workspace` to `Project` in `api/models.py`, `api/serializers.py`, `api/views.py` "
            "and `api/urls.py`.\n"
            "- Old `/workspaces/` routes redirect to `/projects/`, so existing clients keep working.\n"
            "- Added `api/migrations/0042_rename_workspace.py`, which renames the table in place.\n\n"
            "**Testing**\n"
            "- `pytest api` passes (318 tests).\n"
            "- Ran the migration on a copy of the dev database and compared row counts."
        )
        self.assertGreater(len(message), hook.LONG_MESSAGE_CHARS)
        self.assertIsNone(hook.check_readability(message))
        self.assertEqual(hook.opening_unit(hook.paragraphs(message)), "")

    def test_greek_question_marks_are_not_semicolons(self):
        self.assertEqual(hook.semicolons("Θέλετε κεφαλαία; Και στους τίτλους; Ή μόνο στο μενού;"), 0)
        self.assertEqual(hook.semicolons("one; two; three"), 2)


# ---------------------------------------------------------------------------


class TranscriptTests(unittest.TestCase):
    def test_paginated_rollout(self):
        transcript = hook.read_transcript(fixture("rollout_paginated.jsonl"))
        self.assertFalse(transcript.plan_mode)
        self.assertEqual(
            transcript.user_texts,
            [
                "The intro video on the landing page is too long. Cut it to under 20 seconds and export it to public/video/intro.mp4.",
                "Looks good. Now make a 6 second teaser cut as well and put it next to the intro.",
            ],
        )
        joined = "\n".join(transcript.user_texts)
        self.assertNotIn("environment_context", joined)
        self.assertNotIn("hook_only_name.py", joined)

    def test_legacy_rollout(self):
        transcript = hook.read_transcript(fixture("rollout_legacy.jsonl"))
        self.assertEqual(
            transcript.user_texts,
            ["QA the invoice export in src/export/invoice_csv.py. Totals look off for multi-currency accounts."],
        )
        self.assertFalse(transcript.plan_mode)

    def test_plan_mode_is_detected(self):
        transcript = hook.read_transcript(fixture("rollout_plan_mode.jsonl"))
        self.assertTrue(transcript.plan_mode)

    def test_raw_response_items_use_provenance_and_skip_harness_text(self):
        transcript = hook.read_transcript(fixture("rollout_raw_only.jsonl"))
        self.assertEqual(transcript.user_texts, ["Speed up the nightly report job in jobs/nightly_report.py."])

    def test_claude_code_transcript(self):
        transcript = hook.read_transcript(fixture("claude_transcript.jsonl"))
        self.assertEqual(
            transcript.user_texts,
            ["Make the pricing page match the new design in designs/pricing-v3.fig.", "Also keep the FAQ section."],
        )

    def test_malformed_lines_are_skipped(self):
        transcript = hook.read_transcript(fixture("rollout_malformed.jsonl"))
        self.assertIn("Rename the config loader in lib/config_loader.rb.", transcript.user_texts)
        self.assertFalse(transcript.plan_mode)

    def test_unusable_paths(self):
        empty = tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False)
        empty.close()
        try:
            for path in (None, "", 42, "/no/such/rollout.jsonl", FIXTURES, empty.name, fixture("rollout_paginated.jsonl") + ".zst"):
                self.assertIsNone(hook.read_transcript(path), path)
        finally:
            os.unlink(empty.name)

    def test_oversized_transcript_is_skipped(self):
        with mock.patch.object(hook, "MAX_TRANSCRIPT_BYTES", 100):
            self.assertIsNone(hook.read_transcript(fixture("rollout_paginated.jsonl")))

    def test_slow_transcript_is_given_up(self):
        with mock.patch.object(hook, "TRANSCRIPT_SECONDS", -1):
            self.assertIsNone(hook.read_transcript(fixture("rollout_paginated.jsonl")))

    @unittest.skipUnless(os.path.exists(os.devnull) and os.name == "posix", "needs /dev")
    def test_special_files_are_not_read(self):
        for path in (os.devnull, "/dev/zero", "/dev/stdin"):
            self.assertIsNone(hook.read_transcript(path), path)

    def test_binary_and_huge_lines_are_tolerated(self):
        handle = tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False)
        try:
            handle.write(os.urandom(4096) + b"\n")
            handle.write(b'{"type":"user","message":"' + b"x" * 2000000 + b'"}\n')
            handle.write(b"\xff\xfe user \x00\x00\n")
            record = {"type": "event_msg", "payload": {"type": "user_message", "message": "Fix café.py — now"}}
            handle.write(json.dumps(record, ensure_ascii=False).encode("utf-8") + b"\n")
            handle.close()
            transcript = hook.read_transcript(handle.name)
            self.assertEqual(transcript.user_texts, ["Fix café.py — now"])
        finally:
            os.unlink(handle.name)


class ProseTests(unittest.TestCase):
    def test_long_tokens_are_shortened_but_keep_the_question_mark(self):
        blob = "A" * 5000
        self.assertNotIn(blob, hook.prose_of("Here is the key " + blob))
        self.assertTrue(hook.prose_of("Is this the key " + blob + "?").endswith("?"))
        self.assertEqual(hook.check_handback("Encoded: " + blob + "\n\nWant me to decode it too?"), "Want me to decode it too?")

    def test_only_the_relevant_end_of_a_huge_message_is_examined(self):
        filler = "This line is filler for the long report.\n" * 5000
        tail = hook.prose_of(filler + "Want me to add tests?", end=True)
        self.assertLessEqual(len(tail), hook.MAX_ANALYSED_CHARS)
        self.assertTrue(tail.endswith("Want me to add tests?"))
        head = hook.prose_of("Opening line.\n" + filler)
        self.assertLessEqual(len(head), hook.MAX_ANALYSED_CHARS)
        self.assertTrue(head.startswith("Opening line."))

    def test_hostile_messages_finish_quickly(self):
        messages = [
            ("+a" * 100 + " ") * 5000 + "?",
            ("a." * 99 + "py ") * 5000 + "?",
            ("x" * 200 + " ") * 20000 + "?",
            "`" + "a/" * 140 + "` " * 30000 + "?",
            "\n" * 2000000 + "Want me to?",
            "a.a.a." * 50000 + "py ?",
        ]
        started = time.time()
        for message in messages:
            hook.check_handback(message)
            hook.own_work_candidates(message)
            hook.check_readability(message)
        # The old code needed over a minute for these; the hook timeout is 15 s.
        self.assertLess(time.time() - started, 6)


# ---------------------------------------------------------------------------


class EvaluateTests(HookTestCase):
    OFFER = "The intro is 18.4 seconds now and exported. Want me to make a shorter teaser too?"
    OWN = "I exported two teaser cuts. Should I use 24_g521.mp4 or 24_p11.mp4?"

    def test_blocks_a_handback(self):
        result = self.run_hook(self.OFFER)
        self.assertEqual(result["decision"], "block")
        self.assertIn("Want me to make a shorter teaser too?", result["reason"])
        self.assertIn("do it now", result["reason"])
        self.assertTrue(result["reason"].endswith(hook.FOOTER))
        self.assertEqual(set(result), {"decision", "reason"})

    def test_clean_message_passes(self):
        self.assertIsNone(self.run_hook("The intro is 18.4 seconds now and exported to public/video/intro.mp4."))

    def test_one_push_per_turn(self):
        self.assertIsNone(self.run_hook(self.OFFER, stop_hook_active=True))
        payload = self.payload(self.OFFER)
        del payload["stop_hook_active"]
        self.assertIsNone(hook.evaluate(payload, self.env))
        payload = self.payload(self.OFFER, turn_id="same-turn")
        self.assertIsNotNone(hook.evaluate(payload, self.env))
        self.assertIsNone(hook.evaluate(dict(payload), self.env))

    def test_ignores_other_events_and_bad_fields(self):
        self.assertIsNone(self.run_hook(self.OFFER, hook_event_name="SubagentStop"))
        self.assertIsNone(self.run_hook(None))
        self.assertIsNone(self.run_hook("   "))
        self.assertIsNone(self.run_hook(["Want me to?"]))
        self.assertIsNone(self.run_hook(self.OFFER, session_id=""))
        self.assertIsNone(self.run_hook(self.OFFER, session_id=None))
        self.assertIsNone(hook.evaluate(["not", "a", "dict"], self.env))
        self.assertIsNone(hook.evaluate(None, self.env))

    def test_plan_mode_is_left_alone(self):
        self.assertIsNone(self.run_hook(self.OFFER, permission_mode="plan"))
        self.assertIsNone(self.run_hook(self.OFFER, transcript_path=fixture("rollout_plan_mode.jsonl")))
        plan = "<proposed_plan>\n1. Add the table.\n</proposed_plan>\n\n" + self.OFFER
        self.assertIsNone(self.run_hook(plan))

    def test_handback_skipped_when_user_only_asked(self):
        transcript = hook.Transcript()
        transcript.user_texts = ["Why is the teaser export so slow?"]
        output = hook.evaluate(self.payload(self.OFFER), self.env, transcript_reader=lambda path: transcript)
        self.assertIsNone(output)

    def test_own_work_needs_the_transcript(self):
        self.assertIsNone(self.run_hook(self.OWN))
        result = self.run_hook(self.OWN, transcript_path=fixture("rollout_paginated.jsonl"))
        self.assertIn("`24_g521.mp4` and `24_p11.mp4`", result["reason"])
        self.assertIn("never appear in their messages", result["reason"])

    def test_own_work_with_known_name_passes(self):
        message = "The teaser is ready. Should I put it in public/video/intro.mp4 or next to it?"
        self.assertIsNone(self.run_hook(message, transcript_path=fixture("rollout_paginated.jsonl")))

    def test_readability_block(self):
        result = self.run_hook(DENSE_SSD_OPENING + REPORT_TAIL)
        self.assertIn("hard to follow", result["reason"])
        self.assertIn("without redoing any work", result["reason"])

    def test_reasons_combine_in_fixed_order(self):
        message = DENSE_SSD_OPENING + REPORT_TAIL + "\n\nWant me to add a regression test for the locale key?"
        result = self.run_hook(message)
        reason = result["reason"]
        self.assertLess(reason.index("offering more work"), reason.index("hard to follow"))

    def test_env_switches(self):
        self.assertIsNone(self.run_hook(self.OFFER, env=dict(self.env, TRYHARD_HOOK="off")))
        self.assertIsNone(self.run_hook(self.OFFER, env=dict(self.env, TRYHARD_CHECKS="readability")))
        self.assertIsNone(self.run_hook(self.OFFER, env=dict(self.env, TRYHARD_CHECKS="none")))
        self.assertIsNotNone(self.run_hook(self.OFFER, env=dict(self.env, TRYHARD_CHECKS="handback")))

    def test_check_goes_quiet_after_three_in_a_row(self):
        for _ in range(3):
            self.assertIsNotNone(self.run_hook(self.OFFER))
        self.assertIsNone(self.run_hook(self.OFFER))
        self.assertIsNone(self.run_hook(self.OFFER))
        # Other checks keep working in the same session.
        self.assertIsNotNone(self.run_hook(DENSE_SSD_OPENING + REPORT_TAIL))
        # A new session starts fresh.
        self.assertIsNotNone(self.run_hook(self.OFFER, session_id="another-session"))

    def test_a_clean_turn_resets_the_streak(self):
        self.assertIsNotNone(self.run_hook(self.OFFER))
        self.assertIsNotNone(self.run_hook(self.OFFER))
        self.assertIsNone(self.run_hook("All done and checked."))
        for _ in range(3):
            self.assertIsNotNone(self.run_hook(self.OFFER))
        self.assertIsNone(self.run_hook(self.OFFER))

    def test_streak_is_per_check(self):
        dense = DENSE_SSD_OPENING + REPORT_TAIL
        self.assertIsNotNone(self.run_hook(self.OFFER))
        self.assertIsNotNone(self.run_hook(dense))  # handback streak resets here
        self.assertIsNotNone(self.run_hook(self.OFFER))
        self.assertIsNotNone(self.run_hook(dense))
        self.assertIsNotNone(self.run_hook(self.OFFER))
        self.assertIsNotNone(self.run_hook(self.OFFER))

    def test_state_file_location_and_fallbacks(self):
        self.run_hook(self.OFFER)
        files = os.listdir(os.path.join(self.data, "stop-hook"))
        self.assertEqual(files, ["019a96c1-5a2e-7d31-9f0e-2b8d41c7e5a0.json"])
        self.assertEqual(hook.state_dir({"CLAUDE_PLUGIN_DATA": "/x"}), os.path.join("/x", "stop-hook"))
        self.assertEqual(hook.state_dir({"PLUGIN_DATA": "/a", "CLAUDE_PLUGIN_DATA": "/b"}), os.path.join("/a", "stop-hook"))
        with mock.patch.object(hook.tempfile, "gettempdir", return_value=self.data):
            self.assertTrue(hook.state_dir({}).startswith(os.path.join(self.data, "tryhard-")))
        self.assertNotIn("/", os.path.basename(hook.state_path("/d", "../../etc/passwd")))

    def test_corrupt_state_is_ignored(self):
        path = hook.state_path(hook.state_dir(self.env), "019a96c1-5a2e-7d31-9f0e-2b8d41c7e5a0")
        os.makedirs(os.path.dirname(path))
        with open(path, "w") as handle:
            handle.write("{not json")
        self.assertIsNotNone(self.run_hook(self.OFFER))
        with open(path, "w") as handle:
            handle.write('["a list"]')
        self.assertIsNotNone(self.run_hook(self.OFFER))

    def test_unwritable_state_means_no_block(self):
        blocker = os.path.join(self.data, "file")
        with open(blocker, "w") as handle:
            handle.write("x")
        env = {"PLUGIN_DATA": blocker}
        with self.assertRaises(OSError):
            hook.evaluate(self.payload(self.OFFER), env)
        out = io.StringIO()
        self.assertEqual(hook.main(io.StringIO(json.dumps(self.payload(self.OFFER))), out, env), 0)
        self.assertEqual(out.getvalue(), "")

    def test_old_state_files_are_pruned(self):
        with mock.patch.object(hook, "MAX_STATE_FILES", 3):
            for index in range(6):
                self.run_hook(self.OFFER, session_id="s%d" % index)
        self.assertEqual(len(os.listdir(os.path.join(self.data, "stop-hook"))), 3)

    def test_leftover_temp_files_are_removed(self):
        directory = os.path.join(self.data, "stop-hook")
        os.makedirs(directory)
        stale = os.path.join(directory, ".state-killed")
        fresh = os.path.join(directory, ".state-running")
        for path in (stale, fresh):
            with open(path, "w") as handle:
                handle.write("{")
        old = time.time() - 2 * hook.STALE_TEMP_SECONDS
        os.utime(stale, (old, old))
        self.run_hook(self.OFFER)
        self.assertFalse(os.path.exists(stale))
        self.assertTrue(os.path.exists(fresh))

    def test_state_holds_no_message_text(self):
        self.run_hook(self.OFFER + " The API key is sk-test-123.")
        directory = os.path.join(self.data, "stop-hook")
        with open(os.path.join(directory, os.listdir(directory)[0]), encoding="utf-8") as handle:
            state = json.load(handle)
        self.assertEqual(set(state), {"session_id", "streak", "quiet", "last_block_turn", "updated"})
        self.assertNotIn("sk-test", json.dumps(state))

    @unittest.skipUnless(hasattr(os, "getuid") and hasattr(os, "symlink"), "POSIX only")
    def test_fallback_state_folder_must_be_private(self):
        good = os.path.join(self.data, "tryhard-me", "stop-hook")
        self.assertTrue(hook.private_dir_ok(good))
        elsewhere = os.path.join(self.data, "elsewhere")
        os.makedirs(elsewhere)
        link = os.path.join(self.data, "tryhard-link")
        os.symlink(elsewhere, link)
        self.assertFalse(hook.private_dir_ok(os.path.join(link, "stop-hook")))
        with mock.patch.object(hook.tempfile, "gettempdir", return_value=self.data), mock.patch.object(
            hook, "private_dir_ok", return_value=False
        ):
            self.assertIsNone(hook.evaluate(self.payload(self.OFFER), {}))
        with mock.patch.object(hook.tempfile, "gettempdir", return_value=self.data):
            self.assertIsNotNone(hook.evaluate(self.payload(self.OFFER), {}))


# ---------------------------------------------------------------------------


class MainTests(HookTestCase):
    def call(self, text, env=None):
        out = io.StringIO()
        code = hook.main(io.StringIO(text), out, env if env is not None else self.env)
        return code, out.getvalue()

    def test_malformed_input_is_silent(self):
        for text in ("", "   ", "not json", "{", "[1, 2]", "null", '"Want me to?"', "42", '{"stop_hook_active": "no"}'):
            self.assertEqual(self.call(text), (0, ""), text)

    def test_oversized_input_is_silent(self):
        with mock.patch.object(hook, "MAX_STDIN_BYTES", 10):
            self.assertEqual(self.call(json.dumps(self.payload("Want me to add tests?"))), (0, ""))

    def test_unexpected_error_is_silent(self):
        with mock.patch.object(hook, "evaluate", side_effect=RuntimeError("boom")):
            self.assertEqual(self.call(json.dumps(self.payload("Want me to add tests?"))), (0, ""))

    def test_input_is_read_as_utf8_whatever_the_locale(self):
        # Windows pipes decode stdin with the ANSI code page unless told otherwise.
        payload = json.dumps(self.payload("Done — café page fixed. If you’d like, I can add retries."), ensure_ascii=False)
        stdin = io.TextIOWrapper(io.BytesIO(b"\xef\xbb\xbf" + payload.encode("utf-8")), encoding="cp1252")
        out = io.StringIO()
        self.assertEqual(hook.main(stdin, out, self.env), 0)
        self.assertEqual(json.loads(out.getvalue())["decision"], "block")

    def test_block_output_is_one_json_object(self):
        code, output = self.call(json.dumps(self.payload("Done. Want me to add tests for the parser?")))
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(output)["decision"], "block")
        self.assertEqual(output.count("\n"), 1)

    def test_runs_as_a_script(self):
        env = dict(os.environ, PLUGIN_DATA=self.data)
        env.pop("TRYHARD_HOOK", None)
        env.pop("TRYHARD_CHECKS", None)
        block = subprocess.run(
            [sys.executable, HOOK_PATH],
            input=json.dumps(self.payload("Done. Want me to add tests for the parser?")),
            capture_output=True,
            text=True,
            env=env,
            timeout=30,
        )
        self.assertEqual(block.returncode, 0)
        self.assertEqual(json.loads(block.stdout)["decision"], "block")
        self.assertEqual(block.stderr, "")
        quiet = subprocess.run(
            [sys.executable, HOOK_PATH], input="garbage", capture_output=True, text=True, env=env, timeout=30
        )
        self.assertEqual((quiet.returncode, quiet.stdout, quiet.stderr), (0, "", ""))

    def test_script_reads_utf8_with_a_legacy_locale(self):
        env = dict(os.environ, PLUGIN_DATA=self.data, PYTHONIOENCODING="cp1252", LC_ALL="C")
        env.pop("TRYHARD_HOOK", None)
        env.pop("TRYHARD_CHECKS", None)
        message = "Le cache est corrigé — tout passe. If you’d like, I can add a purge command."
        result = subprocess.run(
            [sys.executable, HOOK_PATH],
            input=json.dumps(self.payload(message), ensure_ascii=False).encode("utf-8"),
            capture_output=True,
            env=env,
            timeout=30,
        )
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stderr, b"")
        reason = json.loads(result.stdout.decode("ascii"))["reason"]
        self.assertIn("If you’d like, I can add a purge command.", reason)


if __name__ == "__main__":
    unittest.main()
