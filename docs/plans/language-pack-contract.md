# Language pack contract (locked)

Every language is one folder, `languages/<iso-639-1>/`, containing exactly 3 files. The core code has no knowledge of any specific language beyond what these files provide.

```
languages/<code>/
  pack.json      machine-readable: detection + tags + reminder snippets
  method.md      language-specific teaching notes (loaded on demand, ≤ ~120 lines)
  placement.md   10-question placement test, answer key, scoring
```

## pack.json schema

```jsonc
{
  "code": "de",                       // ISO 639-1, same as folder name
  "name": "German",                   // English name shown in the menu
  "native_name": "Deutsch",
  "flag": "🇩🇪",                      // one emoji, used in footer + status line
  "nickname": "Denglisch",            // optional fun name for mixed input
  "variant": "Standard German",       // what we correct TOWARD (e.g. "Modern Standard Arabic")
  "script": "latin",                  // "latin" | "cyrillic" | "arabic"
  "markers": ["ich", "und", "..."],   // 60–100 lowercase high-frequency function words, native script
  "romanized_markers": [],            // Latin-letter forms learners type (translit/Arabizi), e.g. "privet", "ya3ni"
  "english_lookalikes": ["die", "was"], // markers that are also common English words
  "tags": {                           // ordered by teaching priority (most important first), 6–12 entries
    "v2": "verb second in main clauses"
  },
  "skip_below_b1": ["case-acc", "adj-ending"], // tags too advanced to correct at A-levels
  "reminder_note": "≤30 words, the most important language-specific instruction for the per-turn reminder",
  "example_fix": "🇩🇪 …weil es kaputt **ist** (verb last) [verb-final]",
  "example_tip": "🇩🇪 try: \"ich brauche\" = I need [vocab]"
}
```

Rules:
- Tags must be kebab-case `[a-z0-9-]` and always include `vocab` and `false-friend`.
- `example_fix` and `example_tip` must start with the pack's flag and end with a `[tag]` from `tags`.
- Accept romanized input and never correct the script choice itself. Correct only the language.

## method.md outline (same headings in every pack)

1. **Target variant & register**: what we correct toward, and what we tolerate (dialect, informal, romanized input).
2. **Error priorities for English speakers**: a numbered list matching `tags`, each with a wrong → **right** fragment example and the level at which to start correcting it.
3. **Readiness / acquisition order**: what to ignore at each CEFR band, with citations.
4. **False friends & tech-talk**: 6–10 items relevant to developers.
5. **Micro-lesson chunks (A0–A2)**: 10 high-value reusable chunks for English-only prompts ("Can you…", "I need…", "It doesn't work", "Thanks").
6. **Sources**: author + year + URL.

## placement.md outline

10 questions, A1 → C1, all shown in one message, answerable in about 2 minutes, "?" allowed. Then an answer key, a score → level table (0 → A0 … 10 → C1), and a note on which items predict level best. The "After scoring" steps come from the shared SKILL.md and must not be repeated here.
