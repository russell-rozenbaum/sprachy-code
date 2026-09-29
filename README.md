# claude-denglisch 🇩🇪

**Learn German while you code.** You already spend hours a day talking to Claude, so this plugin turns that time into language practice without slowing your work down.

Write your prompts in English, German, or *Denglisch*. Claude does the task first, then sometimes adds **one** short line:

```
🇩🇪 weil es kaputt **ist** — if you mean 'because it's broken' [verb-final]
```

```
     ┌───────────── your status line ─────────────┐
     │ 🇩🇪 ✓ B1 · Lv3 ▰▰▱▱▱ 340xp                  │
     └────────────────────────────────────────────┘
```

## Install

```
/plugin marketplace add russell-rozenbaum/claude-denglisch
/plugin install denglisch@claude-denglisch
```

Requires `python3` (stdlib only). Then:

| Command | What it does |
|---|---|
| `/denglisch test` | Quick 10-question placement test, A0 → C1 (~2 min) |
| `/denglisch status` | Level, XP, and which mistakes you've learned vs. still practising |
| `/denglisch review` | 3–5 quick drills on your most-missed patterns |
| `/denglisch why` | Explains the last correction in more detail |
| `/denglisch level B1` | Sets your level manually |
| `/denglisch on` / `off` | Turns the tutor on or off (off = no tokens, no footers) |
| `/denglisch statusline` | Adds the XP badge to your status line (asks first) |

Depending on your Claude Code version, plugin commands may be namespaced as `/denglisch:denglisch …`.

## How it works

| Piece | Job | Cost |
|---|---|---|
| `UserPromptSubmit` hook | Adds a short tutor reminder to each prompt: your level, the rules, and one review item that's due. Also credits XP for German you wrote. | ~250–300 tokens/prompt; 0 when off |
| `Stop` hook | Reads the 🇩🇪 line in Claude's reply and logs it to `~/.denglisch/log.jsonl` | 0 tokens, no tool calls |
| `denglisch` skill | Commands, the placement test, and the full correction method | loads only when used |
| `statusline` | `🇩🇪 ✓ B1 · Lv3 ▰▰▱▱▱` badge | 0 tokens |

Your data lives in `~/.denglisch/` (change it with `DENGLISCH_HOME`): `profile.md` (level + notes), `log.jsonl` (events), and `off` (the off switch). Everything is plain text, stays local, and is yours.

**XP:** you earn +1 per German word you write (max 15 per prompt), +2 per correction (trying beats not trying), and +10 when you get a past mistake right. Each rank costs more XP than the last, so leveling up slows down over time.

## The method (research-backed)

- **One focused correction at most, at the end of the reply.** Focused written feedback beats correcting everything (Sheen 2007; Bitchener & Knoch 2010), and it doesn't get in the way of your work.
- **Only the changed words are bold.** You only learn a correction you actually notice (Schmidt 1990).
- **The type of correction depends on the mistake.** Rule mistakes like word order get a tiny rule, or a nudge to fix it yourself. One-off mistakes like der/die/das just get the right answer (Lyster & Saito 2010; Yang & Lyster 2010).
- **It only corrects what you're ready for.** Learners pick up German word order in a fixed sequence, and case comes late (Pienemann 1998; Diehl et al. 2000).
- **Mixing languages is welcome.** Denglisch is a learning scaffold, not a mistake (translanguaging; Wang & Zhang 2026).
- **Past mistakes come back on a schedule:** after 1, 3, 7, then 21 days. A mistake retires after you get it right 3 times (Kim & Webb 2022).

Full notes and citations: [`docs/research/sla-methods.md`](docs/research/sla-methods.md).

## Develop

```
claude --plugin-dir .                     # try it locally
python3 -m unittest discover -s tests     # run the tests
claude plugin validate .                  # check the plugin files
```

MIT licensed.
