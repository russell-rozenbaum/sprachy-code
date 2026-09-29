import io
import json
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import denglisch as dg  # noqa: E402

NOW = datetime(2026, 9, 29, 12, tzinfo=timezone.utc)


def event(kind, tag="v2", days_ago=0, **extra):
    return {"ts": (NOW - timedelta(days=days_ago)).isoformat(), "kind": kind, "tag": tag, "example": "Dann **habe ich**", **extra}


class ParseLevelTest(unittest.TestCase):
    def test_reads_level_line(self):
        self.assertEqual(dg.parse_level("# Profile\n\nlevel: b1\n"), "B1")

    def test_missing_or_invalid(self):
        self.assertIsNone(dg.parse_level(""))
        self.assertIsNone(dg.parse_level("level: D9"))


class ParseFooterTest(unittest.TestCase):
    def test_error_footer(self):
        reply = "Done, tests pass.\n\n🇩🇪 Dann **habe ich** den Bug gefixt — if you mean 'Then I fixed the bug' [v2]"
        [parsed] = dg.parse_footer_events(reply, NOW)
        self.assertEqual((parsed["kind"], parsed["tag"]), ("error", "v2"))
        self.assertIn("habe ich", parsed["example"])

    def test_correct_use_footer(self):
        [parsed] = dg.parse_footer_events("🇩🇪 ✓ weil es kaputt ist [verb-final]", NOW)
        self.assertEqual((parsed["kind"], parsed["tag"]), ("ok", "verb-final"))

    def test_multi_tags_with_trailing_text(self):
        reply = "🇩🇪 Ich habe **den** Code gepusht, dann **habe ich** — if you mean 'x' [v2, gender] · Neu hier?"
        self.assertEqual([e["tag"] for e in dg.parse_footer_events(reply, NOW)], ["v2", "gender"])

    def test_ignores_untagged_and_mid_text_flags(self):
        self.assertEqual(dg.parse_footer_events("I like 🇩🇪 flags [v2]\n🇩🇪 no tag here", NOW), [])


class GermanDetectionTest(unittest.TestCase):
    def test_counts_german(self):
        self.assertGreater(dg.german_word_count("Kannst du mir bitte helfen, weil der Test nicht läuft?"), 5)

    def test_denglisch_counts(self):
        self.assertGreater(dg.german_word_count("fix the bug und push es bitte"), 0)

    def test_english_lookalikes_do_not_count(self):
        self.assertEqual(dg.german_word_count("I will die if this was broken"), 0)
        self.assertEqual(dg.german_word_count("Refactor the auth module"), 0)

    def test_xp_is_capped(self):
        wall_of_german = " ".join(["ich und der die das nicht"] * 20)
        self.assertEqual(dg.xp_for_prompt(wall_of_german, NOW)["xp"], dg.XP_PROMPT_CAP)
        self.assertIsNone(dg.xp_for_prompt("english only please", NOW))


class XpTest(unittest.TestCase):
    def test_total_xp_mixes_sources(self):
        events = [{"ts": NOW.isoformat(), "kind": "xp", "xp": 7}, event("error"), event("ok")]
        self.assertEqual(dg.total_xp(events), 7 + dg.XP_PER_ERROR + dg.XP_PER_FIX)

    def test_rank_thresholds_grow(self):
        self.assertEqual(dg.xp_rank(0), (1, 0, 100))
        self.assertEqual(dg.xp_rank(100), (2, 0, 200))
        self.assertEqual(dg.xp_rank(350), (3, 50, 300))

    def test_statusline(self):
        self.assertEqual(dg.format_statusline(True, "B1", 250), "🇩🇪 ✓ B1 · Lv2 ▰▰▰▱▱ 250xp")
        self.assertEqual(dg.format_statusline(False, "B1", 250), "🇩🇪 ✗ off")
        self.assertIn("??", dg.format_statusline(True, None, 0))


class ReviewScheduleTest(unittest.TestCase):
    def test_due_after_first_gap(self):
        stats = dg.summarize_tags([event("error", days_ago=2)])
        self.assertEqual([d["tag"] for d in dg.due_reviews(stats, NOW)], ["v2"])

    def test_not_due_too_soon(self):
        self.assertEqual(dg.due_reviews(dg.summarize_tags([event("error", days_ago=0)]), NOW), [])

    def test_gap_expands_with_correct_uses(self):
        # One correct use -> 3-day gap; last seen 2 days ago -> not due yet.
        stats = dg.summarize_tags([event("error", days_ago=10), event("ok", days_ago=2)])
        self.assertEqual(dg.due_reviews(stats, NOW), [])

    def test_retired_after_three_correct(self):
        events = [event("error", days_ago=60)] + [event("ok", days_ago=50)] * dg.RETIRE_AFTER_CORRECT
        self.assertEqual(dg.due_reviews(dg.summarize_tags(events), NOW), [])

    def test_most_frequent_first(self):
        events = [event("error", "gender", 5), event("error", "v2", 5), event("error", "v2", 4)]
        self.assertEqual(dg.due_reviews(dg.summarize_tags(events), NOW)[0]["tag"], "v2")

    def test_xp_events_ignored_in_tag_stats(self):
        self.assertEqual(dg.summarize_tags([{"ts": NOW.isoformat(), "kind": "xp", "xp": 3}]), {})


class ReminderTest(unittest.TestCase):
    def test_unknown_level_offers_test(self):
        text = dg.build_reminder(None, [])
        self.assertIn("assume A1", text)
        self.assertIn("/denglisch test", text)

    def test_due_review_included(self):
        text = dg.build_reminder("B1", [{"tag": "v2", "errors": 3, "example": "x"}])
        self.assertIn("Review due [v2]", text)
        self.assertNotIn("/denglisch test", text)

    def test_quiet_reminder_is_one_line(self):
        self.assertEqual(dg.build_reminder("B1", [], quiet=True).count("\n"), 0)

    def test_reminder_stays_small(self):
        # Paid on every prompt: guard against prompt bloat (~4 chars/token).
        self.assertLess(len(dg.build_reminder(None, [{"tag": "v2", "errors": 1, "example": "x" * 200}])) / 4, 400)


class TranscriptTest(unittest.TestCase):
    def test_last_assistant_text(self):
        lines = [
            json.dumps({"type": "user", "message": {"role": "user", "content": "hi"}}),
            json.dumps({"type": "assistant", "message": {"role": "assistant", "content": [{"type": "text", "text": "first"}]}}),
            json.dumps({"type": "assistant", "message": {"role": "assistant", "content": [{"type": "tool_use", "name": "Bash"}]}}),
            json.dumps({"type": "assistant", "message": {"role": "assistant", "content": [{"type": "text", "text": "🇩🇪 x [v2]"}]}}),
            "not json",
        ]
        self.assertEqual(dg.last_assistant_text(lines), "🇩🇪 x [v2]")


class StoreAndHooksTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.store = dg.LearnerStore(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_prompt_hook_logs_xp_and_returns_reminder(self):
        out = dg.run_prompt_hook(self.store, {"prompt": "Kannst du bitte den Test fixen?"}, NOW)
        self.assertIn("denglisch tutor", out)
        self.assertGreater(dg.total_xp(self.store.events()), 0)

    def test_cooldown_after_feedback(self):
        prompt = {"prompt": "fix it"}
        self.assertNotIn("quiet", dg.run_prompt_hook(self.store, prompt, NOW))  # fresh learner: feedback allowed
        dg.run_stop_hook(self.store, {"last_assistant_message": "🇩🇪 …weil es kaputt **ist** [verb-final]"}, NOW)
        for _ in range(dg.QUIET_TURNS_AFTER_FEEDBACK):
            self.assertIn("quiet turn", dg.run_prompt_hook(self.store, prompt, NOW))
        self.assertNotIn("quiet", dg.run_prompt_hook(self.store, prompt, NOW))

    def test_reply_without_footer_keeps_counting(self):
        dg.run_stop_hook(self.store, {"last_assistant_message": "done"}, NOW)
        self.assertNotIn("quiet", dg.run_prompt_hook(self.store, {"prompt": "x"}, NOW))

    def test_off_silences_everything(self):
        self.store.set_enabled(False)
        self.assertEqual(dg.run_prompt_hook(self.store, {"prompt": "ich bin und der"}, NOW), "")
        dg.run_stop_hook(self.store, {"last_assistant_message": "🇩🇪 x [v2]"}, NOW)
        self.assertEqual(self.store.events(), [])
        self.store.set_enabled(True)
        self.assertTrue(self.store.enabled)

    def test_stop_hook_reads_transcript_fallback(self):
        transcript = Path(self.tmp.name) / "t.jsonl"
        transcript.write_text(json.dumps({"type": "assistant", "message": {"content": [{"type": "text", "text": "ok\n🇩🇪 ✓ gut [v2]"}]}}) + "\n")
        dg.run_stop_hook(self.store, {"transcript_path": str(transcript)}, NOW)
        self.assertEqual([e["kind"] for e in self.store.events()], ["ok"])

    def test_set_level_creates_and_updates_profile(self):
        self.store.set_level("A2")
        self.store.set_level("B1")
        self.assertEqual(self.store.level(), "B1")
        self.assertEqual(self.store.profile.read_text().count("level:"), 1)

    def test_corrupt_log_line_skipped(self):
        self.store.append_events([event("error")])
        with self.store.log.open("a") as handle:
            handle.write("{broken\n")
        self.assertEqual(len(self.store.events()), 1)

    def test_cli_statusline(self):
        with mock.patch.dict("os.environ", {"DENGLISCH_HOME": self.tmp.name}), mock.patch("sys.stdout", new=io.StringIO()) as out:
            self.assertEqual(dg.main(["denglisch.py", "statusline"]), 0)
        self.assertTrue(out.getvalue().startswith("🇩🇪 ✓"))

    def test_cli_rejects_bad_level(self):
        with mock.patch.dict("os.environ", {"DENGLISCH_HOME": self.tmp.name}), mock.patch("sys.stderr", new=io.StringIO()):
            self.assertEqual(dg.main(["denglisch.py", "level", "Z9"]), 2)


if __name__ == "__main__":
    unittest.main()
