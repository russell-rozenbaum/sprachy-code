# Language pack contract (locked)

Every language is one folder, `languages/<iso-639-1>/`, containing exactly 4 files. The core code has no knowledge of any specific language beyond what these files provide.

```
languages/<code>/
  pack.json      machine-readable: detection + tags + reminder snippets
  method.md      language-specific teaching notes (loaded on demand, ≤ ~120 lines)
  placement.json 30-item multiple-choice bank for the adaptive placement test
  placement.md   short notes on what the test covers
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

Superseded in v0.3 by `placement.json` (adaptive and all multiple choice). `placement.md` now holds only short notes: what the items cover, and which skills predict level best. It is ≤25 lines, for humans and `/sprachy why`.

## placement.json (adaptive test item bank), added in v0.3

The placement test is **adaptive** (Rasch/Elo-style). `scripts/sprachy.py placement` runs **5 rounds of 3 items** (15 total). Each round picks the 3 unused items closest to the learner's current ability estimate, preferring different skills, and the estimate updates after every round. The file lives at `languages/<code>/placement.json`, next to `placement.md`.

```jsonc
{
  "items": [
    {
      "id": "de-a1-1",                 // unique: <code>-<level lowercase>-<n>
      "level": "A1",                   // A1 | A2 | B1 | B2 | C1
      "prompt": "\"Hello, my name is Sam\" → Hallo, ___ heiße Sam.",
      "choices": ["ich", "mich", "mein"],  // EXACTLY 3 options, each ≤40 chars, all plausible
      "answer": "ich",                 // must equal one of choices exactly; the CLI grades deterministically
      "skill": "pronoun"               // what it tests (a pack tag where possible), used for profile notes
    }
  ]
}
```

Rules:
- **6 items per level, A1–C1 (30 total).** Spread the skills; don't test the same thing twice at one level.
- **A1 items must be doable by someone who can't read the script yet:** give transliteration for non-Latin scripts, and accept translit or Arabizi answers.
- **Prompts must fit on one line** (≤120 chars) and be answerable in about 10 seconds.
- **All multiple choice, no free text.** Items are shown in Claude's picker (AskUserQuestion). The skill adds an "I don't know" option, and the CLI shuffles the choice order.
- **Distractors must be real learner errors** (e.g. the wrong case or aspect), not nonsense. Exactly one choice is correct.
- For translation items, the choices are full short phrases (e.g. "Ich brauche Kaffee" / "Ich brauche den Kaffee zu" / "Ich Kaffee brauche").
