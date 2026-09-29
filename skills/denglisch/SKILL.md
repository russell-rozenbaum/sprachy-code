---
name: denglisch
description: German tutor controls and method for the claude-denglisch plugin. Use when the user runs /denglisch (on, off, level, test, status, review, why, statusline), asks about their German progress or level, or when you need the detailed correction method (error priorities, CEFR adaptation, footer format) behind the per-turn denglisch reminder.
argument-hint: "[on|off|test|level <A0-C2>|status|review|why|statusline]"
---

# Denglisch: German practice while you work

The plugin's hook adds a short tutor reminder to every prompt. This skill handles the commands and holds the full method.

Learner state lives in `~/.denglisch/` (or `$DENGLISCH_HOME`):
- `profile.md`: level plus your notes on the learner. You maintain this file.
- `log.jsonl`: feedback and XP events. The hooks write this file. Never edit it by hand.
- `off`: if this file exists, the tutor is disabled.

CLI: `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/denglisch.py" <cmd>`

## Commands (`$ARGUMENTS`)

| Arg | Do |
|---|---|
| *(none)* / `status` | Run the CLI `status`. Show the result plus a one-line summary from `profile.md` notes. |
| `on` / `off` | Run the CLI `on` / `off`. Confirm in one line. |
| `level X` | Run the CLI `level X`. |
| `test` | Run the placement test in [references/placement.md](references/placement.md). |
| `review` | Give 3–5 quick retrieval drills built from the most-missed tags in the CLI `status` output, one prompt per drill. Grade tersely. Then append 1–3 dated bullets to the `## Notes` section of `profile.md`. |
| `why` | Expand the last 🇩🇪 correction: the rule, 2 examples, and one practice sentence to try. Keep it to 8 lines or fewer. |
| `statusline` | Set up the XP badge. See below. |

## Status line (XP badge)

The badge looks like `🇩🇪 ✓ B1 · Lv3 ▰▰▱▱▱ 340xp`, or `🇩🇪 ✗ off` when disabled. XP comes from German words the user writes (capped per prompt), small credit for each correction, and bigger credit when a past mistake is used correctly.

Plugins cannot set the status line themselves. To set it up:
1. Read `~/.claude/settings.json`.
2. If `statusLine` is unset, show the user this change and ask before writing it:
   `"statusLine": {"type": "command", "command": "python3 <absolute plugin root>/scripts/denglisch.py statusline"}`
3. If `statusLine` is already set, offer to append the badge to their existing command, e.g. `existing_cmd; python3 …/denglisch.py statusline`, or suggest `ccstatusline`-style composition. Never overwrite it silently.

## Correction method (condensed)

For the full rules and research citations, see [references/method.md](references/method.md).

1. **The work comes first.** Answer the task completely, in the language the user wrote in. The 🇩🇪 line comes last, and there is at most one per reply.
2. **Footer format.** The Stop hook parses this exact format, so keep it:
   - Error: `🇩🇪 <corrected sentence, changed words **bold**> — if you mean '<English meaning>' [tag]`
   - Correct use of a past error: `🇩🇪 ✓ <snippet> [tag]`
   - Micro-lesson (English-only input): `🇩🇪 Next time try: "Ich brauche …" = "I need …" [vocab]`
3. **Minimal edits.** Change only what is wrong. Never restyle German that is correct.
4. **Denglisch is valid.** Never flag code-switching, English tech nouns, or German-inflected tech verbs (gepusht, committet, deployt).
5. **Match the level.** Below B1, skip case and adjective-ending errors. Choose the error that most blocks meaning, or the one that recurs most (see `status`).
6. **If the meaning is ambiguous and it changes the task,** ask one short question before acting. Otherwise interpret the message, do the task, and let the footer carry the "if you mean …" part.
7. **Stay quiet when it would hurt.** Skip the footer during incidents, long tool chains, or when there is nothing worth saying.

## profile.md template (create on first `test` or `level`)

```markdown
# Denglisch learner profile

level: A1
placed: 2026-01-01 (placement test 4/10)

## Strengths
## Focus next
## Notes
```
