import io
import json
import re
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import sprachy as sp  # noqa: E402

NOW = datetime(2026, 9, 29, 12, tzinfo=timezone.utc)
PACKS = sp.load_packs()
DE = PACKS["de"]
# Minimal non-Latin pack so core tests don't depend on in-progress language packs.
RU_FIXTURE = {
    "code": "ru", "name": "Russian", "native_name": "Русский", "flag": "🇷🇺", "script": "cyrillic",
    "markers": ["и", "в", "не", "я", "что"], "romanized_markers": ["privet", "spasibo", "ya", "ne"],
    "english_lookalikes": [], "tags": {"case": "cases", "vocab": "words", "false-friend": "ff"},
    "skip_below_b1": [], "reminder_note": "Translit is fine.",
    "example_fix": "🇷🇺 …в **Москве** [case]", "example_tip": "🇷🇺 try: \"мне нужно\" = I need [vocab]",
}


def event(kind, tag="v2", days_ago=0, **extra):
    return {"ts": (NOW - timedelta(days=days_ago)).isoformat(), "kind": kind, "tag": tag, "example": "Dann **habe ich**", **extra}


class PackContractTest(unittest.TestCase):
    """Every shipped pack must satisfy docs/plans/language-pack-contract.md."""

    REQUIRED = ("code", "name", "native_name", "flag", "variant", "script", "markers", "romanized_markers",
                "english_lookalikes", "tags", "skip_below_b1", "reminder_note", "example_fix", "example_tip")

    def test_all_packs(self):
        self.assertIn("de", PACKS)
        for code, pack in PACKS.items():
            with self.subTest(pack=code):
                pack_dir = ROOT / "languages" / code
                self.assertEqual(sorted(p.name for p in pack_dir.iterdir()), ["method.md", "pack.json", "placement.md"])
                for key in self.REQUIRED:
                    self.assertIn(key, pack)
                self.assertIn(pack["script"], ("latin", "cyrillic", "arabic"))
                self.assertGreaterEqual(len(pack["markers"]), 40)
                self.assertTrue(all(m == m.lower() for m in pack["markers"] + pack["romanized_markers"]))
                self.assertTrue(set(pack["english_lookalikes"]) <= set(pack["markers"] + pack["romanized_markers"]))
                for tag in pack["tags"]:
                    self.assertRegex(tag, r"^[a-z0-9][a-z0-9-]*$")
                self.assertTrue({"vocab", "false-friend"} <= set(pack["tags"]))
                self.assertTrue(set(pack["skip_below_b1"]) <= set(pack["tags"]))
                self.assertLessEqual(len(pack["reminder_note"].split()), 35)
                for example in (pack["example_fix"], pack["example_tip"]):
                    self.assertTrue(example.startswith(pack["flag"]))
                    [parsed] = sp.parse_footer_events(example, pack["flag"], NOW)
                    self.assertIn(parsed["tag"], pack["tags"])

    def test_reminder_stays_small_for_every_pack(self):
        # Paid on every prompt: guard against prompt bloat (~4 chars/token, ≤ ~450 tokens worst case).
        for code, pack in PACKS.items():
            with self.subTest(pack=code):
                text = sp.build_reminder(pack, None, [{"tag": "v2", "errors": 1, "example": "x" * 200}])
                self.assertLess(len(text) / 4, 450)


class ParseTest(unittest.TestCase):
    def test_level(self):
        self.assertEqual(sp.parse_level("# Profile\n\nlevel: b1\n"), "B1")
        self.assertIsNone(sp.parse_level("level: D9"))

    def test_error_footer(self):
        [parsed] = sp.parse_footer_events("Done.\n\n🇩🇪 …**habe ich** gefixt — if you mean 'x' [v2]", "🇩🇪", NOW)
        self.assertEqual((parsed["kind"], parsed["tag"]), ("error", "v2"))

    def test_ok_footer(self):
        [parsed] = sp.parse_footer_events("🇩🇪 ✓ weil es kaputt ist [verb-final]", "🇩🇪", NOW)
        self.assertEqual(parsed["kind"], "ok")

    def test_multi_tags_and_trailing_text(self):
        reply = "🇩🇪 …**den** Code, dann **habe ich** [v2, gender] · /sprachy test sets your level"
        self.assertEqual([e["tag"] for e in sp.parse_footer_events(reply, "🇩🇪", NOW)], ["v2", "gender"])

    def test_other_flag_ignored(self):
        self.assertEqual(sp.parse_footer_events("🇷🇺 …в **Москве** [case]", "🇩🇪", NOW), [])
        self.assertEqual(sp.parse_footer_events("I like 🇩🇪 flags [v2]", "🇩🇪", NOW), [])


class DetectionTest(unittest.TestCase):
    def test_german(self):
        self.assertGreater(sp.target_word_count("Kannst du mir bitte helfen, weil der Test nicht läuft?", DE), 5)
        self.assertGreater(sp.target_word_count("fix the bug und push es bitte", DE), 0)

    def test_english_lookalikes_do_not_count(self):
        self.assertEqual(sp.target_word_count("I will die if this was broken", DE), 0)
        self.assertEqual(sp.target_word_count("Refactor the auth module", DE), 0)

    def test_cyrillic_script_is_enough(self):
        self.assertEqual(sp.target_word_count("почини этот тест пожалуйста", RU_FIXTURE), 4)

    def test_translit(self):
        self.assertGreater(sp.target_word_count("privet, ya ne ponimayu this error", RU_FIXTURE), 0)
        self.assertEqual(sp.target_word_count("fix the flaky test", RU_FIXTURE), 0)

    def test_xp_is_capped(self):
        wall = " ".join(["ich und der die das nicht"] * 20)
        self.assertEqual(sp.xp_for_prompt(wall, DE, NOW)["xp"], sp.XP_PROMPT_CAP)
        self.assertIsNone(sp.xp_for_prompt("english only please", DE, NOW))


class XpTest(unittest.TestCase):
    def test_total_xp_mixes_sources(self):
        events = [{"ts": NOW.isoformat(), "kind": "xp", "xp": 7}, event("error"), event("ok")]
        self.assertEqual(sp.total_xp(events), 7 + sp.XP_PER_ERROR + sp.XP_PER_FIX)

    def test_rank_thresholds_grow(self):
        self.assertEqual(sp.xp_rank(0), (1, 0, 100))
        self.assertEqual(sp.xp_rank(100), (2, 0, 200))
        self.assertEqual(sp.xp_rank(350), (3, 50, 300))

    def test_statusline(self):
        self.assertEqual(sp.format_statusline(DE, True, "B1", 250), "🇩🇪 ✓ B1 · Lv2 ▰▰▰▱▱ 250xp")
        self.assertEqual(sp.format_statusline(DE, False, "B1", 250), "🇩🇪 ✗ off")
        self.assertIn("/sprachy language", sp.format_statusline(None, True, None, 0))


class ReviewScheduleTest(unittest.TestCase):
    def test_due_after_first_gap(self):
        self.assertEqual([d["tag"] for d in sp.due_reviews(sp.summarize_tags([event("error", days_ago=2)]), NOW)], ["v2"])

    def test_not_due_too_soon(self):
        self.assertEqual(sp.due_reviews(sp.summarize_tags([event("error")]), NOW), [])

    def test_gap_expands_with_correct_uses(self):
        stats = sp.summarize_tags([event("error", days_ago=10), event("ok", days_ago=2)])
        self.assertEqual(sp.due_reviews(stats, NOW), [])

    def test_retired_after_three_correct(self):
        events = [event("error", days_ago=60)] + [event("ok", days_ago=50)] * sp.RETIRE_AFTER_CORRECT
        self.assertEqual(sp.due_reviews(sp.summarize_tags(events), NOW), [])

    def test_most_frequent_first(self):
        events = [event("error", "gender", 5), event("error", "v2", 5), event("error", "v2", 4)]
        self.assertEqual(sp.due_reviews(sp.summarize_tags(events), NOW)[0]["tag"], "v2")


class ReminderTest(unittest.TestCase):
    def test_unknown_level_offers_test(self):
        text = sp.build_reminder(DE, None, [])
        self.assertIn("assume A1", text)
        self.assertIn("/sprachy test", text)
        self.assertIn(DE["example_fix"], text)

    def test_due_review_included(self):
        self.assertIn("Review due [v2]", sp.build_reminder(DE, "B1", [{"tag": "v2", "errors": 3, "example": "x"}]))

    def test_quiet_reminder_is_one_line(self):
        self.assertEqual(sp.build_reminder(DE, "B1", [], quiet=True).count("\n"), 0)

    def test_transcript_parsing(self):
        lines = [
            json.dumps({"type": "user", "message": {"role": "user", "content": "hi"}}),
            json.dumps({"type": "assistant", "message": {"content": [{"type": "text", "text": "first"}]}}),
            json.dumps({"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "Bash"}]}}),
            json.dumps({"type": "assistant", "message": {"content": [{"type": "text", "text": "🇩🇪 x [v2]"}]}}),
            "not json",
        ]
        self.assertEqual(sp.last_assistant_text(lines), "🇩🇪 x [v2]")


class AppTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.app = sp.Sprachy(self.tmp.name, packs={"de": DE, "ru": RU_FIXTURE})

    def tearDown(self):
        self.tmp.cleanup()

    def test_no_language_offers_menu(self):
        self.assertIn("/sprachy language", sp.run_prompt_hook(self.app, {"prompt": "hi"}, NOW))

    def test_prompt_hook_logs_xp(self):
        self.app.set_active("de")
        self.assertIn("German tutor", sp.run_prompt_hook(self.app, {"prompt": "Kannst du bitte den Test fixen?"}, NOW))
        self.assertGreater(sp.total_xp(self.app.learner("de").events()), 0)

    def test_cooldown_after_feedback(self):
        self.app.set_active("de")
        prompt = {"prompt": "fix it"}
        self.assertNotIn("quiet", sp.run_prompt_hook(self.app, prompt, NOW))
        sp.run_stop_hook(self.app, {"last_assistant_message": "🇩🇪 …weil es kaputt **ist** [verb-final]"}, NOW)
        for _ in range(sp.QUIET_TURNS_AFTER_FEEDBACK):
            self.assertIn("quiet turn", sp.run_prompt_hook(self.app, prompt, NOW))
        self.assertNotIn("quiet", sp.run_prompt_hook(self.app, prompt, NOW))

    def test_progress_is_per_language(self):
        self.app.set_active("de")
        self.app.learner("de").set_level("B1")
        sp.run_stop_hook(self.app, {"last_assistant_message": "🇩🇪 …x [v2]"}, NOW)
        self.app.set_active("ru")
        self.assertIsNone(self.app.learner("ru").level())
        sp.run_stop_hook(self.app, {"last_assistant_message": "🇩🇪 …x [v2]"}, NOW)  # wrong flag for ru
        self.assertEqual(self.app.learner("ru").events(), [])
        self.assertEqual(self.app.learner("de").level(), "B1")
        self.assertIn("German", sp.run_status(self.app, NOW))  # others listed

    def test_off_silences_everything(self):
        self.app.set_active("de")
        self.app.set_enabled(False)
        self.assertEqual(sp.run_prompt_hook(self.app, {"prompt": "ich bin und der"}, NOW), "")
        sp.run_stop_hook(self.app, {"last_assistant_message": "🇩🇪 x [v2]"}, NOW)
        self.assertEqual(self.app.learner("de").events(), [])
        self.app.set_enabled(True)
        self.assertTrue(self.app.enabled)

    def test_unknown_active_code_is_ignored(self):
        self.app.config_file.parent.mkdir(parents=True, exist_ok=True)
        self.app.config_file.write_text('{"active": "xx"}')
        self.assertIsNone(self.app.active_pack())

    def test_stop_hook_transcript_fallback(self):
        self.app.set_active("de")
        transcript = Path(self.tmp.name) / "t.jsonl"
        transcript.write_text(json.dumps({"type": "assistant", "message": {"content": [{"type": "text", "text": "ok\n🇩🇪 ✓ gut [v2]"}]}}) + "\n")
        sp.run_stop_hook(self.app, {"transcript_path": str(transcript)}, NOW)
        self.assertEqual([e["kind"] for e in self.app.learner("de").events()], ["ok"])

    def test_corrupt_log_line_skipped(self):
        learner = self.app.learner("de")
        learner.append_events([event("error")])
        with learner.log.open("a") as handle:
            handle.write("{broken\n")
        self.assertEqual(len(learner.events()), 1)

    def test_set_level_updates_in_place(self):
        learner = self.app.learner("de")
        learner.set_level("A2")
        learner.set_level("B1")
        self.assertEqual(learner.level(), "B1")
        self.assertEqual(learner.profile.read_text().count("level:"), 1)


class CliTest(unittest.TestCase):
    def run_cli(self, *args):
        with tempfile.TemporaryDirectory() as home, mock.patch.dict("os.environ", {"SPRACHY_HOME": home}):
            outputs = []
            for argv in args:
                with mock.patch("sys.stdout", new=io.StringIO()) as out, mock.patch("sys.stderr", new=io.StringIO()):
                    code = sp.main(["sprachy.py", *argv])
                outputs.append((code, out.getvalue()))
            return outputs

    def test_use_level_statusline(self):
        (_, used), (_, _), (_, badge) = self.run_cli(["use", "de"], ["level", "B1"], ["statusline"])
        self.assertIn("German", used)
        self.assertTrue(badge.startswith("🇩🇪 ✓ B1"))

    def test_languages_lists_active(self):
        _, (_, listing) = self.run_cli(["use", "de"], ["languages"])
        self.assertRegex(listing, re.compile(r"^▶ 🇩🇪 de", re.MULTILINE))

    def test_rejects_bad_input(self):
        [(code_lang, _), (code_level, _)] = self.run_cli(["use", "xx"], ["level", "B1"])
        self.assertEqual((code_lang, code_level), (2, 2))  # unknown language; level without active language


if __name__ == "__main__":
    unittest.main()
