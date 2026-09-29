#!/usr/bin/env python3
"""claude-denglisch hook + CLI.

Functional core (pure functions) + thin I/O shell. Stdlib only, Python 3.8+.

Subcommands:
  prompt   UserPromptSubmit hook -> prints per-turn tutor reminder (stdout = context)
  stop     Stop hook -> logs 🇩🇪 footer lines from Claude's last reply
  status   human-readable progress summary
  on|off   toggle the tutor
  level X  set CEFR level (A0, A1, A2, B1, B2, C1, C2)
  statusline  one-line badge for Claude Code's statusLine: 🇩🇪 ✓ B1 · Lv3 ▰▰▰▱▱
"""
from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Optional

LEVELS = ("A0", "A1", "A2", "B1", "B2", "C1", "C2")
# Expanding review gaps (days), indexed by how many times the learner has since
# used the form correctly — spaced retrieval per Cepeda et al. 2006 / Kim & Webb 2022.
REVIEW_INTERVALS_DAYS = (1, 3, 7, 21)
# Replies that stay silent after each correction: caps feedback at ~1 in 3 prompts
# so it never nags (focused WCF, Sheen 2007; affective filter, Krashen 1982).
QUIET_TURNS_AFTER_FEEDBACK = 2
# Three correct spontaneous uses = treat the pattern as acquired.
RETIRE_AFTER_CORRECT = 3

# Footer contract shared with the prompt reminder + SKILL.md:
#   🇩🇪 <correction text> [tag]      -> error event
#   🇩🇪 ✓ <snippet> [tag]            -> correct-use event
FOOTER_RE = re.compile(r"^\s*🇩🇪\s*(?P<ok>✓)?\s*(?P<body>.*)$")
# Tags may be anywhere on the line and comma-separated: [v2] or [v2, gender]
TAGS_RE = re.compile(r"\[(?P<tags>[a-z0-9][a-z0-9:-]{0,40}(?:\s*,\s*[a-z0-9][a-z0-9:-]{0,40})*)\]")
# XP rewards: writing German at all (output hypothesis, Swain 1985) and fixing a
# past mistake (the real learning signal). Errors earn a little: trying > silence.
XP_PER_GERMAN_WORD = 1
XP_PROMPT_CAP = 15
XP_PER_ERROR = 2
XP_PER_FIX = 10
XP_RANK_STEP = 100  # rank n -> n+1 costs n * 100 XP, so growth slows over time
BAR_WIDTH = 5
# High-frequency German function words: cheap, dependency-free "is this German?" signal.
GERMAN_MARKERS = frozenset(
    "ich du er sie es wir ihr und oder aber nicht kein keine der die das den dem des ein eine einen einem "
    "ist sind bin bist war habe hast hat haben kann kannst mit für auf von zu im ins bitte danke wie was "
    "warum wo wann weil dass wenn ob noch schon auch nur sehr mal jetzt hier dann mir mich dir dich uns".split()
)
# Markers that are also common English words; they only count alongside an unambiguous one.
ENGLISH_LOOKALIKES = frozenset("die was bin hat also so an in am war will".split())
WORD_RE = re.compile(r"[a-zäöüß]+")
LEVEL_RE = re.compile(r"^\s*level:\s*(?P<level>[A-C][0-2])\b", re.IGNORECASE | re.MULTILINE)


# ---------- functional core ----------

def parse_level(profile_text: str) -> Optional[str]:
    match = LEVEL_RE.search(profile_text or "")
    level = match.group("level").upper() if match else None
    return level if level in LEVELS else None


def parse_footer_events(reply_text: str, now: datetime) -> List[Dict]:
    """Extract logged feedback events from an assistant reply."""
    events = []
    for line in (reply_text or "").splitlines():
        match = FOOTER_RE.match(line)
        tag_groups = TAGS_RE.findall(match.group("body")) if match else []
        for tag in (tag.strip() for group in tag_groups for tag in group.split(",")):
            events.append({
                "ts": now.isoformat(),
                "kind": "ok" if match.group("ok") else "error",
                "tag": tag,
                "example": TAGS_RE.sub("", match.group("body")).split(" · ")[0].strip()[:200],
            })
    return events


def german_word_count(prompt: str) -> int:
    """German-looking words in a prompt, or 0 if it doesn't read as German/Denglisch.

    Needs >=2 marker hits, at least one unambiguous, so "I will die if this was broken" scores 0.
    """
    words = WORD_RE.findall((prompt or "").lower())
    hits = [word for word in words if word in GERMAN_MARKERS]
    if len(hits) < 2 or all(word in ENGLISH_LOOKALIKES for word in hits):
        return 0
    return sum(word in GERMAN_MARKERS or any(ch in word for ch in "äöüß") for word in words)


def xp_for_prompt(prompt: str, now: datetime) -> Optional[Dict]:
    gained = min(german_word_count(prompt) * XP_PER_GERMAN_WORD, XP_PROMPT_CAP)
    return {"ts": now.isoformat(), "kind": "xp", "xp": gained} if gained else None


def total_xp(events: Iterable[Dict]) -> int:
    rewards = {"error": XP_PER_ERROR, "ok": XP_PER_FIX}
    return sum(event.get("xp", 0) if event["kind"] == "xp" else rewards.get(event["kind"], 0) for event in events)


def xp_rank(xp: int) -> tuple:
    """(rank, xp into rank, xp needed for next rank). Rank n needs n*STEP more XP."""
    rank, floor = 1, 0
    while xp >= floor + rank * XP_RANK_STEP:
        floor += rank * XP_RANK_STEP
        rank += 1
    return rank, xp - floor, rank * XP_RANK_STEP


def format_statusline(enabled: bool, level: Optional[str], xp: int) -> str:
    if not enabled:
        return "🇩🇪 ✗ off"
    rank, into, needed = xp_rank(xp)
    filled = into * BAR_WIDTH // needed
    return f"🇩🇪 ✓ {level or '??'} · Lv{rank} {'▰' * filled}{'▱' * (BAR_WIDTH - filled)} {xp}xp"


def summarize_tags(events: Iterable[Dict]) -> Dict[str, Dict]:
    """Fold the event log into per-tag stats: errors, oks, last seen, last error example."""
    stats: Dict[str, Dict] = {}
    for event in events:
        if event["kind"] not in ("error", "ok"):
            continue
        tag_stats = stats.setdefault(event["tag"], {"errors": 0, "oks": 0, "last": event["ts"], "example": ""})
        if event["kind"] == "ok":
            tag_stats["oks"] += 1
        else:
            tag_stats["errors"] += 1
            tag_stats["example"] = event.get("example", "")
        tag_stats["last"] = max(tag_stats["last"], event["ts"])
    return stats


def due_reviews(stats: Dict[str, Dict], now: datetime, limit: int = 1) -> List[Dict]:
    """Tags whose review gap has elapsed, most-frequent errors first."""
    due = []
    for tag, tag_stats in stats.items():
        if tag_stats["errors"] == 0 or tag_stats["oks"] >= RETIRE_AFTER_CORRECT:
            continue
        gap_days = REVIEW_INTERVALS_DAYS[min(tag_stats["oks"], len(REVIEW_INTERVALS_DAYS) - 1)]
        if now - datetime.fromisoformat(tag_stats["last"]) >= timedelta(days=gap_days):
            due.append({"tag": tag, **tag_stats})
    due.sort(key=lambda item: (-item["errors"], item["last"]))
    return due[:limit]


def is_quiet_turn(turns_since_feedback: int) -> bool:
    return turns_since_feedback < QUIET_TURNS_AFTER_FEEDBACK


def build_reminder(level: Optional[str], due: List[Dict], quiet: bool = False) -> str:
    """Per-turn context. Kept tiny: it's paid on every prompt."""
    if quiet:
        # Cooldown turn: one line, ~30 tokens. Asking about truly ambiguous German is task work, not a correction.
        return "[denglisch · quiet turn] No 🇩🇪 footer this reply. Just do the task (ask only if unclear German changes what to do)."
    lines = [
        f"[denglisch tutor · level {level or 'unknown → assume A1'}]",
        "Do the task first, fully, in the user's language. Then OPTIONALLY one footer line, max ~12 words:",
        "  🇩🇪 …<fragment with the ONE fix in **bold**> (≤5-word hint) [tag]",
        "Pick only the single most important fix: one that hides meaning, or a pattern they keep repeating. "
        "Ignore everything else — typos, umlauts, capitals, style, small slips, English words mixed in, tech verbs (gepusht, deployt). "
        "Show only the fixed fragment, never the whole sentence. Add \"— if you mean '…'\" only when meaning was unclear. "
        "Below B1 skip case/adjective endings; hints in English below B2. No footer if nothing clears that bar, or user is busy/stressed. "
        "English-only message → at most a tiny tip: 🇩🇪 try: \"ich brauche\" = I need [vocab]. "
        "Past mistake now right → 🇩🇪 ✓ <snippet> [tag]. "
        "Tags: v2, verb-final, gender, case-acc, case-dat, sep-verb, perfekt-aux, false-friend, vocab. Details: denglisch skill.",
    ]
    if level is None:
        lines.append("No learner profile → once per session append to the footer: · `/denglisch test` sets your level (2 min).")
    for item in due:
        lines.append(f"Review due [{item['tag']}] e.g. \"{item['example']}\": if natural, footer may be a quick recall cue instead.")
    return "\n".join(lines)


def format_status(level: Optional[str], stats: Dict[str, Dict], enabled: bool, now: datetime) -> str:
    lines = [f"denglisch: {'ON' if enabled else 'OFF'} · level {level or 'unassessed (run /denglisch test)'}"]
    if not stats:
        return "\n".join(lines + ["No feedback logged yet."])
    lines.append(f"{'tag':<16}{'errors':>7}{'✓':>4}  status")
    for tag, tag_stats in sorted(stats.items(), key=lambda kv: -kv[1]["errors"]):
        if tag_stats["oks"] >= RETIRE_AFTER_CORRECT:
            status = "acquired"
        elif due_reviews({tag: tag_stats}, now):
            status = "review due"
        else:
            status = "learning"
        lines.append(f"{tag:<16}{tag_stats['errors']:>7}{tag_stats['oks']:>4}  {status}")
    return "\n".join(lines)


def last_assistant_text(transcript_lines: Iterable[str]) -> str:
    """Text of the final assistant message in a Claude Code JSONL transcript."""
    last = ""
    for raw in transcript_lines:
        try:
            entry = json.loads(raw)
        except ValueError:
            continue
        message = entry.get("message") or {}
        if entry.get("type") != "assistant" and message.get("role") != "assistant":
            continue
        content = message.get("content")
        texts = [content] if isinstance(content, str) else [
            block.get("text", "") for block in content or [] if isinstance(block, dict) and block.get("type") == "text"
        ]
        joined = "\n".join(t for t in texts if t)
        if joined:
            last = joined
    return last


# ---------- imperative shell ----------

class LearnerStore:
    """Owns the learner folder (~/.denglisch by default, override with DENGLISCH_HOME)."""

    def __init__(self, home: Optional[str] = None):
        self.root = Path(home or os.environ.get("DENGLISCH_HOME") or Path.home() / ".denglisch").expanduser()
        self.profile = self.root / "profile.md"
        self.log = self.root / "log.jsonl"
        self.off_flag = self.root / "off"
        self.cooldown = self.root / "cooldown"

    @property
    def enabled(self) -> bool:
        return not self.off_flag.exists()

    def level(self) -> Optional[str]:
        return parse_level(self.profile.read_text(encoding="utf-8")) if self.profile.exists() else None

    def events(self) -> List[Dict]:
        if not self.log.exists():
            return []
        events = []
        for raw in self.log.read_text(encoding="utf-8").splitlines():
            try:
                events.append(json.loads(raw))
            except ValueError:
                continue  # a corrupt line must never break the user's session
        return events

    def append_events(self, events: List[Dict]) -> None:
        if not events:
            return
        self.root.mkdir(parents=True, exist_ok=True)
        with self.log.open("a", encoding="utf-8") as handle:
            handle.writelines(json.dumps(event, ensure_ascii=False) + "\n" for event in events)

    def turns_since_feedback(self) -> int:
        try:
            return int(self.cooldown.read_text().strip())
        except (OSError, ValueError):
            return QUIET_TURNS_AFTER_FEEDBACK  # no record -> feedback allowed

    def set_turns_since_feedback(self, turns: int) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        self.cooldown.write_text(str(turns))

    def set_enabled(self, enabled: bool) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        if enabled:
            if self.off_flag.exists():
                self.off_flag.unlink()
        else:
            self.off_flag.touch()

    def set_level(self, level: str) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        existing = self.profile.read_text(encoding="utf-8") if self.profile.exists() else "# Denglisch learner profile\n\nlevel: A1\n"
        updated = LEVEL_RE.sub(f"level: {level}", existing, count=1) if LEVEL_RE.search(existing) else f"level: {level}\n{existing}"
        self.profile.write_text(updated, encoding="utf-8")


def read_hook_input() -> Dict:
    try:
        return json.loads(sys.stdin.read() or "{}")
    except ValueError:
        return {}


def run_prompt_hook(store: LearnerStore, hook_input: Dict, now: datetime) -> str:
    if not store.enabled:
        return ""
    xp_event = xp_for_prompt(hook_input.get("prompt", ""), now)
    store.append_events([xp_event] if xp_event else [])
    turns = store.turns_since_feedback()
    store.set_turns_since_feedback(turns + 1)
    if is_quiet_turn(turns):
        return build_reminder(store.level(), [], quiet=True)
    return build_reminder(store.level(), due_reviews(summarize_tags(store.events()), now))


def run_stop_hook(store: LearnerStore, hook_input: Dict, now: datetime) -> None:
    if not store.enabled:
        return
    reply = hook_input.get("last_assistant_message") or ""
    transcript = hook_input.get("transcript_path")
    if not reply and transcript and Path(transcript).exists():
        reply = last_assistant_text(Path(transcript).read_text(encoding="utf-8").splitlines())
    events = parse_footer_events(reply, now)
    store.append_events(events)
    if events:
        store.set_turns_since_feedback(0)  # start the cooldown


def main(argv: List[str]) -> int:
    store = LearnerStore()
    now = datetime.now(timezone.utc)
    command = argv[1] if len(argv) > 1 else "status"
    try:
        if command == "prompt":
            print(run_prompt_hook(store, read_hook_input(), now))
        elif command == "stop":
            run_stop_hook(store, read_hook_input(), now)
        elif command in ("on", "off"):
            store.set_enabled(command == "on")
            print(f"denglisch {command.upper()}")
        elif command == "level":
            level = argv[2].upper() if len(argv) > 2 else ""
            if level not in LEVELS:
                print(f"usage: level {{{'|'.join(LEVELS)}}}", file=sys.stderr)
                return 2
            store.set_level(level)
            print(f"level set: {level}")
        elif command == "statusline":
            print(format_statusline(store.enabled, store.level(), total_xp(store.events())))
        elif command == "status":
            print(format_status(store.level(), summarize_tags(store.events()), store.enabled, now))
        else:
            print(__doc__, file=sys.stderr)
            return 2
    except OSError as error:
        # Hooks must never block the user's real work; degrade silently-ish.
        print(f"denglisch: {error}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
