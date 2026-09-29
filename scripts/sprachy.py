#!/usr/bin/env python3
"""sprachy-code hook + CLI: learn a language while you code with Claude.

Functional core (pure functions) + thin I/O shell. Stdlib only, Python 3.8+.
Language specifics live in languages/<code>/pack.json (see docs/plans/language-pack-contract.md).

Subcommands:
  prompt              UserPromptSubmit hook -> per-turn tutor reminder (stdout = context)
  stop                Stop hook -> logs <flag> footer lines from Claude's last reply
  statusline          one-line badge: 🇩🇪 ✓ B1 · Lv3 ▰▰▰▱▱ 340xp
  status              progress summary (active language in detail + the others)
  languages           list available language packs
  use <code>          switch the active language (e.g. use ru)
  level <A0-C2>       set the active language's CEFR level
  on | off            toggle the tutor
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
PACKS_DIR = Path(__file__).resolve().parent.parent / "languages"
# Expanding review gaps (days), indexed by how many times the learner has since
# used the form correctly — spaced retrieval per Cepeda et al. 2006 / Kim & Webb 2022.
REVIEW_INTERVALS_DAYS = (1, 3, 7, 21)
# Replies that stay silent after each correction: caps feedback at ~1 in 3 prompts
# so it never nags (focused WCF, Sheen 2007; affective filter, Krashen 1982).
QUIET_TURNS_AFTER_FEEDBACK = 2
# Three correct spontaneous uses = treat the pattern as acquired.
RETIRE_AFTER_CORRECT = 3
# XP rewards: writing the target language at all (output hypothesis, Swain 1985) and
# fixing a past mistake (the real learning signal). Errors earn a little: trying > silence.
XP_PER_TARGET_WORD = 1
XP_PROMPT_CAP = 15
XP_PER_ERROR = 2
XP_PER_FIX = 10
XP_RANK_STEP = 100  # rank n -> n+1 costs n * 100 XP, so growth slows over time
BAR_WIDTH = 5
# Non-Latin scripts are self-identifying: a couple of words in them is enough signal.
SCRIPT_RANGES = {"cyrillic": ("Ѐ", "ӿ"), "arabic": ("؀", "ۿ")}

# Tags may be anywhere on the footer line and comma-separated: [v2] or [v2, gender]
TAGS_RE = re.compile(r"\[(?P<tags>[a-z0-9][a-z0-9:-]{0,40}(?:\s*,\s*[a-z0-9][a-z0-9:-]{0,40})*)\]")
WORD_RE = re.compile(r"\w+")
LEVEL_RE = re.compile(r"^\s*level:\s*(?P<level>[A-C][0-2])\b", re.IGNORECASE | re.MULTILINE)


# ---------- functional core ----------

def parse_level(profile_text: str) -> Optional[str]:
    match = LEVEL_RE.search(profile_text or "")
    level = match.group("level").upper() if match else None
    return level if level in LEVELS else None


def parse_footer_events(reply_text: str, flag: str, now: datetime) -> List[Dict]:
    """Extract feedback events from footer lines: `<flag> [✓] <body> [tag, …]`."""
    events = []
    for line in (reply_text or "").splitlines():
        stripped = line.strip()
        if not stripped.startswith(flag):
            continue
        body = stripped[len(flag):].strip()
        is_ok = body.startswith("✓")
        tag_groups = TAGS_RE.findall(body)
        example = TAGS_RE.sub("", body.lstrip("✓")).split(" · ")[0].strip()[:200]
        for tag in (tag.strip() for group in tag_groups for tag in group.split(",")):
            events.append({"ts": now.isoformat(), "kind": "ok" if is_ok else "error", "tag": tag, "example": example})
    return events


def in_script(word: str, script: str) -> bool:
    low, high = SCRIPT_RANGES.get(script, ("", ""))
    return bool(low) and any(low <= ch <= high for ch in word)


def target_word_count(prompt: str, pack: Dict) -> int:
    """Target-language words in a prompt, or 0 if it doesn't read as that language.

    Latin scripts need >=2 marker hits, at least one not an English lookalike, so
    "I will die if this was broken" scores 0 for German.
    """
    words = WORD_RE.findall((prompt or "").lower())
    markers = set(pack.get("markers", [])) | set(pack.get("romanized_markers", []))
    lookalikes = set(pack.get("english_lookalikes", []))
    hits = [word for word in words if word in markers]
    script_words = [word for word in words if in_script(word, pack.get("script", "latin"))]
    if len(script_words) >= 2:
        return len(script_words) + sum(1 for word in hits if not in_script(word, pack["script"]))
    if len(hits) < 2 or all(word in lookalikes for word in hits):
        return 0
    # Non-ASCII Latin words (ä, é, ç…) are near-certain target-language words.
    return sum(word in markers or not word.isascii() for word in words)


def xp_for_prompt(prompt: str, pack: Dict, now: datetime) -> Optional[Dict]:
    gained = min(target_word_count(prompt, pack) * XP_PER_TARGET_WORD, XP_PROMPT_CAP)
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


def xp_bar(xp: int) -> str:
    rank, into, needed = xp_rank(xp)
    filled = into * BAR_WIDTH // needed
    return f"Lv{rank} {'▰' * filled}{'▱' * (BAR_WIDTH - filled)} {xp}xp"


def format_statusline(pack: Optional[Dict], enabled: bool, level: Optional[str], xp: int) -> str:
    flag = pack["flag"] if pack else "🌐"
    if not enabled:
        return f"{flag} ✗ off"
    if not pack:
        return "🌐 sprachy · /sprachy language"
    return f"{flag} ✓ {level or '??'} · {xp_bar(xp)}"


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


def build_reminder(pack: Dict, level: Optional[str], due: List[Dict], quiet: bool = False) -> str:
    """Per-turn context. Kept tiny: it's paid on every prompt."""
    flag, name = pack["flag"], pack["name"]
    if quiet:
        # Cooldown turn: one line, ~30 tokens. Asking about truly ambiguous input is task work, not a correction.
        return f"[sprachy {flag} · quiet turn] No {flag} footer this reply. Just do the task (ask only if unclear {name} changes what to do)."
    lines = [
        f"[sprachy {flag} {name} tutor · learner level {level or 'unknown → assume A1'} · source language English]",
        "Do the task first, fully, in the user's language. Then OPTIONALLY one footer line, max ~12 words:",
        f"  {flag} …<fragment with the ONE fix in **bold**> (≤5-word hint) [tag]   e.g. {pack['example_fix']}",
        "Pick only the single most important fix: one that hides meaning, or a pattern they keep repeating. "
        "Ignore everything else — typos, accents/diacritics, capitals, style, small slips, English words mixed in. "
        "Show only the fixed fragment, never the whole sentence, in the user's script (translit/Arabizi in → same out). Add \"— if you mean '…'\" only when meaning was unclear. "
        f"Hints in English below B2. No footer if nothing clears that bar, or user is busy/stressed. "
        f"Skip below B1: {', '.join(pack.get('skip_below_b1', [])) or 'nothing'}. "
        f"English-only message → at most a tiny tip: {pack['example_tip']}. "
        f"Past mistake now right → {flag} ✓ <snippet> [tag]. "
        f"{pack.get('reminder_note', '')} "
        f"Tags: {', '.join(pack['tags'])}. Details: sprachy skill.",
    ]
    if level is None:
        lines.append("No level yet → once per session append to the footer: · `/sprachy test` sets your level (2 min).")
    for item in due:
        lines.append(f"Review due [{item['tag']}] e.g. \"{item['example']}\": if natural, footer may be a quick recall cue instead.")
    return "\n".join(lines)


def no_language_reminder() -> str:
    return "[sprachy] No language picked yet. Once per session, end your reply with: 🌐 Learn a language while you code: `/sprachy language`"


def format_status(pack: Dict, level: Optional[str], stats: Dict[str, Dict], xp: int, enabled: bool, now: datetime) -> str:
    lines = [
        f"{pack['flag']} {pack['name']} · {'ON' if enabled else 'OFF'} · level {level or 'unassessed (/sprachy test)'} · {xp_bar(xp)}"
    ]
    if not stats:
        return "\n".join(lines + ["No corrections logged yet."])
    lines.append(f"{'pattern':<16}{'missed':>7}{'✓':>4}  status")
    for tag, tag_stats in sorted(stats.items(), key=lambda kv: -kv[1]["errors"]):
        if tag_stats["oks"] >= RETIRE_AFTER_CORRECT:
            status = "✅ learned"
        elif due_reviews({tag: tag_stats}, now):
            status = "🔁 review due"
        else:
            status = "📈 learning"
        lines.append(f"{tag:<16}{tag_stats['errors']:>7}{tag_stats['oks']:>4}  {status}")
    return "\n".join(lines)


def format_language_list(packs: List[Dict], active: Optional[str], summaries: Dict[str, str]) -> str:
    return "\n".join(
        f"{'▶' if pack['code'] == active else ' '} {pack['flag']} {pack['code']}  {pack['name']} ({pack['native_name']})"
        f"{'  · ' + summaries[pack['code']] if summaries.get(pack['code']) else ''}"
        for pack in packs
    )


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

def load_packs(packs_dir: Path = PACKS_DIR) -> Dict[str, Dict]:
    packs = {}
    for pack_file in sorted(packs_dir.glob("*/pack.json")):
        try:
            pack = json.loads(pack_file.read_text(encoding="utf-8"))
        except ValueError:
            continue  # one broken pack must not take down the others
        packs[pack["code"]] = pack
    return packs


class LearnerStore:
    """Owns one language's learner folder: profile.md, log.jsonl, cooldown."""

    def __init__(self, root: Path):
        self.root = root
        self.profile = root / "profile.md"
        self.log = root / "log.jsonl"
        self.cooldown = root / "cooldown"

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

    def set_level(self, level: str) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        existing = self.profile.read_text(encoding="utf-8") if self.profile.exists() else "# Sprachy learner profile\n\nlevel: A1\n"
        updated = LEVEL_RE.sub(f"level: {level}", existing, count=1) if LEVEL_RE.search(existing) else f"level: {level}\n{existing}"
        self.profile.write_text(updated, encoding="utf-8")

    def summary(self) -> str:
        level, xp = self.level(), total_xp(self.events())
        return f"{level or '??'} · {xp_bar(xp)}" if (level or xp) else ""


class Sprachy:
    """Owns ~/.sprachy-code (override: SPRACHY_HOME): global on/off, active language, per-language stores."""

    def __init__(self, home: Optional[str] = None, packs: Optional[Dict[str, Dict]] = None):
        self.root = Path(home or os.environ.get("SPRACHY_HOME") or Path.home() / ".sprachy-code").expanduser()
        self.config_file = self.root / "config.json"
        self.off_flag = self.root / "off"
        self.packs = load_packs() if packs is None else packs

    @property
    def enabled(self) -> bool:
        return not self.off_flag.exists()

    def set_enabled(self, enabled: bool) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        if enabled:
            if self.off_flag.exists():
                self.off_flag.unlink()
        else:
            self.off_flag.touch()

    def active_code(self) -> Optional[str]:
        try:
            code = json.loads(self.config_file.read_text(encoding="utf-8")).get("active")
        except (OSError, ValueError):
            return None
        return code if code in self.packs else None

    def set_active(self, code: str) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        self.config_file.write_text(json.dumps({"active": code}) + "\n", encoding="utf-8")

    def active_pack(self) -> Optional[Dict]:
        code = self.active_code()
        return self.packs.get(code) if code else None

    def learner(self, code: str) -> LearnerStore:
        return LearnerStore(self.root / code)


def read_hook_input() -> Dict:
    try:
        return json.loads(sys.stdin.read() or "{}")
    except ValueError:
        return {}


def run_prompt_hook(app: Sprachy, hook_input: Dict, now: datetime) -> str:
    if not app.enabled:
        return ""
    pack = app.active_pack()
    if not pack:
        return no_language_reminder()
    learner = app.learner(pack["code"])
    xp_event = xp_for_prompt(hook_input.get("prompt", ""), pack, now)
    learner.append_events([xp_event] if xp_event else [])
    turns = learner.turns_since_feedback()
    learner.set_turns_since_feedback(turns + 1)
    if is_quiet_turn(turns):
        return build_reminder(pack, learner.level(), [], quiet=True)
    return build_reminder(pack, learner.level(), due_reviews(summarize_tags(learner.events()), now))


def run_stop_hook(app: Sprachy, hook_input: Dict, now: datetime) -> None:
    pack = app.active_pack()
    if not app.enabled or not pack:
        return
    reply = hook_input.get("last_assistant_message") or ""
    transcript = hook_input.get("transcript_path")
    if not reply and transcript and Path(transcript).exists():
        reply = last_assistant_text(Path(transcript).read_text(encoding="utf-8").splitlines())
    learner = app.learner(pack["code"])
    events = parse_footer_events(reply, pack["flag"], now)
    learner.append_events(events)
    if events:
        learner.set_turns_since_feedback(0)  # start the cooldown


def run_status(app: Sprachy, now: datetime) -> str:
    pack = app.active_pack()
    others = {code: app.learner(code).summary() for code in app.packs if code != app.active_code()}
    other_lines = [f"  {app.packs[code]['flag']} {app.packs[code]['name']}: {s}" for code, s in others.items() if s]
    if not pack:
        return "\n".join(["No active language. Pick one: /sprachy language"] + other_lines)
    learner = app.learner(pack["code"])
    events = learner.events()
    detail = format_status(pack, learner.level(), summarize_tags(events), total_xp(events), app.enabled, now)
    tail = ["", "Other languages:"] + other_lines if other_lines else []
    return "\n".join([detail, f"(pack notes: {PACKS_DIR / pack['code']})"] + tail)


def main(argv: List[str]) -> int:
    app = Sprachy()
    now = datetime.now(timezone.utc)
    command = argv[1] if len(argv) > 1 else "status"
    arg = argv[2] if len(argv) > 2 else ""
    try:
        if command == "prompt":
            print(run_prompt_hook(app, read_hook_input(), now))
        elif command == "stop":
            run_stop_hook(app, read_hook_input(), now)
        elif command == "statusline":
            pack = app.active_pack()
            learner = app.learner(pack["code"]) if pack else None
            print(format_statusline(pack, app.enabled, learner.level() if learner else None, total_xp(learner.events()) if learner else 0))
        elif command == "status":
            print(run_status(app, now))
        elif command == "languages":
            summaries = {code: app.learner(code).summary() for code in app.packs}
            print(format_language_list(list(app.packs.values()), app.active_code(), summaries))
        elif command == "use":
            if arg.lower() not in app.packs:
                print(f"unknown language '{arg}'. available: {', '.join(app.packs)}", file=sys.stderr)
                return 2
            app.set_active(arg.lower())
            pack = app.packs[arg.lower()]
            print(f"{pack['flag']} now learning {pack['name']} · {app.learner(pack['code']).summary() or 'new — try /sprachy test'}")
        elif command == "level":
            pack = app.active_pack()
            if not pack or arg.upper() not in LEVELS:
                print(f"usage: level {{{'|'.join(LEVELS)}}} (needs an active language)", file=sys.stderr)
                return 2
            app.learner(pack["code"]).set_level(arg.upper())
            print(f"{pack['flag']} level set: {arg.upper()}")
        elif command in ("on", "off"):
            app.set_enabled(command == "on")
            print(f"sprachy {command.upper()}")
        else:
            print(__doc__, file=sys.stderr)
            return 2
    except OSError as error:
        # Hooks must never block the user's real work.
        print(f"sprachy: {error}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
