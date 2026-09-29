---
name: sprachy
description: Sprachy language-tutor controls and method for the sprachy-code plugin. Use when the user runs /sprachy (help, language, status, test, review, why, level, on, off, statusline), asks to switch or pick a language to learn, asks about their language-learning progress or level, or when you need the detailed correction method behind the per-turn sprachy reminder.
argument-hint: "[help|language|status|test|review|why|level <A0-C2>|on|off|statusline]"
allowed-tools: Bash(python3:*)
---

# Sprachy: learn a language while you code

Sprachy Terminal is the in-editor companion to the Sprachy app. The hook adds a short tutor reminder to each prompt. This skill runs the commands and holds the shared method. The source language is always English.

- **CLI:** `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/sprachy.py" <cmd>`
- **Language packs:** `${CLAUDE_PLUGIN_ROOT}/languages/<code>/`, each with `pack.json`, `method.md`, `placement.json` (question bank) and `placement.md`.
- **Learner state:** `~/.sprachy-code/` (or `$SPRACHY_HOME`), with `config.json` for the active language, a global `off` flag, and a `<code>/` folder per language holding `profile.md` (which you maintain), `log.jsonl` (hooks only) and `cooldown`.

## Live state (already loaded, so don't re-run these)

Languages (▶ = active):
!`python3 "${CLAUDE_PLUGIN_ROOT}/scripts/sprachy.py" languages`

Status:
!`python3 "${CLAUDE_PLUGIN_ROOT}/scripts/sprachy.py" status`

**Speed rule:** `help`, `language` and `status` need **no tool calls** before their first visible output. Use the live state above.

## Commands (`$ARGUMENTS`)

| Arg | Do |
|---|---|
| *(none)* / `help` | Print the **help card** below as-is, then the first line of the live status. |
| `language` / `lang` | Open the **language menu** (see below). |
| `status` | Show the live status in a code block. That's all; no extra reads. |
| `test` | Run the **adaptive placement test** (see below). |
| `review` | Give 3–5 quick drills, one at a time, on the most-missed patterns in the CLI `status` output. Grade tersely, then append 1–3 dated bullets to the `## Notes` section of `profile.md`. |
| `why` | Expand the last flagged correction: the rule, 2 examples and 1 try-it sentence, in ≤8 lines. Use the active pack's `method.md`. |
| `level X` | Run the CLI `level X`. |
| `on` / `off` | Run the CLI `on` / `off` and confirm in one line. |
| `statusline` | Set up the XP badge (see below). |

### Help card
```
Sprachy Terminal: learn a language while you code
  /sprachy language   pick or switch the language you're learning
  /sprachy status     level, XP, and patterns you're learning vs. have learned
  /sprachy test       adaptive level test: 5 quick rounds of 3 clickable questions
  /sprachy review     3–5 quick drills on your most-missed patterns
  /sprachy why        explain the last correction in more depth
  /sprachy level B1   set your level manually (A0–C2)
  /sprachy on | off   pause or resume the tutor (off = zero tokens)
  /sprachy statusline add the XP badge to your status line
How it works: write in English, your target language, or a mix. Claude does the
task first. At most one tiny fix every ~3 prompts, and only the ones that matter.
```

### Language menu
1. Use the live language list above. It already shows each pack's flag, name, native name, progress, and `▶` on the active one.
2. Immediately call **AskUserQuestion** with a single question, "Which language do you want to practice?", header "Language". Make one option per pack: label `<flag> <Name>`, and description `<Native name> · <progress or "new">`. Add "(current)" to the label of the active pack. If there are more than 4 packs, show the active pack plus the 3 with the most XP; the built-in "Other" option covers the rest by name or code.
3. Run the CLI `use <code>` and echo its one-line result.
4. If that language has no level yet, offer in one line: "Find your level with 5 quick rounds of clickable questions? `/sprachy test`".

### Adaptive placement test (5 rounds × 3 questions, all multiple choice)
The CLI picks and grades every question, so never judge answers yourself and never reveal the answer before the user picks.
1. Run the CLI `placement start`. It prints `ROUND 1/5` and 3 items, e.g. `[de-b1-2] Ich fahre mit ___ Auto.` followed by `a) das  b) dem  c) den`.
2. Call **AskUserQuestion** once, with all 3 items as 3 questions:
   - `question`: the item prompt.
   - `header`: `R1 · Q1`, `R1 · Q2`, `R1 · Q3`.
   - `options`: the 3 choices in the printed order (label = the choice text exactly), plus a 4th option `🤷 I don't know`.
   - Don't add descriptions or hints.
3. Map each pick back to its letter (a/b/c). Treat "I don't know" or a free-text "Other" as `?`. Then run the CLI `placement answer <id>=<letter> <id>=<letter> <id>=<letter>`.
4. The output starts with ✓/✗ feedback lines. Show them as-is (a quick learning moment). Then:
   - If it prints the next `ROUND n/5`, repeat from step 2 with no other commentary.
   - If it prints `DONE`, the level is already saved. Write the language's `profile.md` from the template: record the `strengths` under "Strengths" and the `focus next` items under "Focus next". Then reply in ≤3 lines: the level, one strength, and a micro-goal for the next prompt, e.g. *Next prompt: start with "Kannst du …" instead of "Can you …"*.

### Status line (XP badge)
The badge looks like `🇩🇪 ✓ B1 · Lv3 ▰▰▱▱▱ 340xp`, or `🇩🇪 ✗ off`. Plugins can't set the status line themselves. Read `~/.claude/settings.json`:
- If `statusLine` is unset, show the change and ask before writing:
  `"statusLine": {"type": "command", "command": "python3 \"$(ls -d ~/.claude/plugins/cache/sprachy-code/sprachy-code/*/ | sort -V | tail -1)scripts/sprachy.py\" statusline"}`
- If it is already set, offer to append the badge to the existing command. Never overwrite it silently.

## Correction method (shared across languages)

For language-specific priorities, see the active pack's `method.md`. For the research behind all of this, see [references/method.md](references/method.md).

**Never annoying: this matters more than any single correction.** Mixed-language input will be rough. Correct almost nothing.

1. **Work first.** Answer the task completely, in the user's language. The flag line is optional, comes last, and is one line of about 12 words at most.
2. **Cooldown (enforced by the hook).** A `quiet turn` reminder means no footer on that reply.
3. **One fix, only if it matters:** either it hides the meaning, or the user keeps repeating it. Ignore typos, accents, capitals, style, small slips, script choice (translit or Arabizi), and mixed-in English.
4. **Fragment only.** Keep the exact format; the Stop hook parses it:
   - Fix: `<flag> …<fragment with **fix**> (≤5-word hint) [tag]`
   - Plus meaning, only if it was unclear: `… — if you mean '<English>' [tag]`
   - Correct use of a past error: `<flag> ✓ <snippet> [tag]`
   - Tip for an English-only message: `<flag> try: "<chunk>" = <English> [vocab]`
5. **Match the level.** Respect the pack's `skip_below_b1`. Give hints in English below B2.
6. **Ambiguous and it changes the task?** Ask one short question first. That counts as task work, so it's allowed on quiet turns too.
7. **When in doubt, leave it out.**

## profile.md template

```markdown
# Sprachy learner profile: <Name>

level: A1
placed: 2026-01-01 (placement 11/15)

## Strengths
## Focus next
## Notes
```
