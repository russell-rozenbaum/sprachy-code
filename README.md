# sprachy-code 🌐 (Sprachy Terminal)

**Learn a language while you code.** You already spend hours a day talking to Claude, so Sprachy Terminal turns that time into practice without getting in your way. It's the in-editor companion to [Sprachy](https://github.com/russell-rozenbaum), *the translator that teaches*.

Write your prompts in English, in the language you're learning, or a mix (*Denglisch*, *Franglais*, translit, Arabizi, all fine). Claude does the task first. Every few prompts, and only when it matters, it adds **one** tiny fix:

```
🇩🇪 …weil es kaputt **ist** (verb last) [verb-final]
```

```
 ┌──────── your status line ────────┐
 │ 🇩🇪 ✓ B1 · Lv3 ▰▰▱▱▱ 340xp        │
 └──────────────────────────────────┘
```

| Language | Mixed-input nickname | Notes |
|---|---|---|
| 🇩🇪 German | Denglisch | Focus on word order first; umlauts typed as ae/oe/ue are fine |
| 🇷🇺 Russian | — | Translit (e.g. `privet`) is fine |
| 🇫🇷 French | Franglais | Missing accents are fine |
| 🇸🇦 Arabic (MSA) | — | Arabizi (e.g. `shukran`, `3`) is fine; dialect words are tolerated |

The source language is always English. Adding a language means adding one folder; see [the language pack contract](docs/plans/language-pack-contract.md).

## Install

```
/plugin marketplace add russell-rozenbaum/sprachy-code
/plugin install sprachy-code@sprachy-code
```
Requires `python3` (standard library only). Then run `/sprachy language` to pick a language, and `/sprachy test` to set your level.

## Commands

| Command | What it does |
|---|---|
| `/sprachy` · `/sprachy help` | Shows all commands |
| `/sprachy language` | Menu to pick or switch languages (progress is saved separately for each) |
| `/sprachy status` | Level, XP, and which patterns you're still learning vs. have learned |
| `/sprachy test` | Adaptive level test: 5 rounds of 3 clickable questions, each round adjusted to your answers so far (A0 → C1) |
| `/sprachy review` | 3–5 quick drills on your most-missed patterns |
| `/sprachy why` | Explains the last correction in more depth |
| `/sprachy level B1` | Sets your level manually |
| `/sprachy on` / `off` | Pauses the tutor (off = zero tokens) |
| `/sprachy statusline` | Adds the XP badge to your status line |

Depending on your Claude Code version, the command may be namespaced as `/sprachy-code:sprachy …`.

## Never annoying, by design

- **Cooldown:** after a correction, the next 2 replies are silent. The hook enforces this; Claude doesn't have to remember.
- **One fix per correction, as a short fragment only**, and only if the mistake hides your meaning or keeps recurring. Typos, accents, and mixed-in English are ignored.
- **Level-aware:** it never corrects things you aren't ready to learn yet.
- **Zero overhead for logging:** a hook reads Claude's reply, so there are no extra tool calls or permission prompts.

## How it works

| Piece | Job | Cost |
|---|---|---|
| `UserPromptSubmit` hook | Adds the tutor reminder: level, rules, one review that's due, cooldown state. Also credits XP. | ~300 tokens on active turns, ~30 on quiet turns, 0 when off |
| `Stop` hook | Logs the flag line from Claude's reply to `~/.sprachy-code/<lang>/log.jsonl` | 0 tokens |
| `sprachy` skill | Commands, menu, placement test, method | Only loaded when used |
| `languages/<code>/` | `pack.json` (detection, tags), `method.md`, `placement.md` | Loaded on demand |

**XP:** you earn +1 per target-language word you write (max 15 per prompt), +2 per correction, and +10 when you fix a past mistake. Each rank costs more XP than the last.

**Spaced review:** past mistakes come back after 1, 3, 7, then 21 days, and retire after 3 correct uses.

Research notes and citations: [`docs/research/sla-methods.md`](docs/research/sla-methods.md).

## Develop

```
claude --plugin-dir .                   # try it locally
python3 -m unittest discover -s tests   # tests, including a contract check on every language pack
claude plugin validate .
```

MIT licensed.
