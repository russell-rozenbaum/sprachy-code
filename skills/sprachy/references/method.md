# Sprachy correction method (shared, language-agnostic)

This file distils the research in `docs/research/sla-methods.md`. It is shared by all languages. For language-specific error priorities, false friends and chunks, see `languages/<code>/method.md`.

## 0. Annoyance budget (overrides everything below)
- At most **one** correction every ~3 prompts. The hook enforces this with 2 quiet turns after each correction.
- A correction must earn its place. It either blocks the meaning, or it is a repeat offender. With rough Denglisch, most messages get **no** correction.
- Keep it to one line of about 12 words, **fragment only**, and after the work. If you have to explain for more than 5 words, it isn't worth doing now; `/sprachy why` exists for that.

## 1. Pick at most one target per reply
Written corrective feedback works best when it is **focused**: 1–2 targets, not every error (Sheen 2007; Bitchener & Knoch 2010). Choose in this order:
1. An error that obscures meaning.
2. A recurring tag. Check `status`; an error seen 3 or more times beats a new one.
3. The highest-priority error below that the learner is ready for (§3).

Skip typos, umlaut substitutes (ae/oe/ue/ss), missing capitals on nouns in casual chat, and punctuation.

## 2. Choose the feedback type by error type
| Error type | Examples | Feedback |
|---|---|---|
| Rule-based | V2, verb-final, verb bracket, case after a preposition | Give the correction with a ≤5-word rule tag, e.g. `(weil → verb last)`. From B1 up, sometimes **prompt** instead: `🇩🇪 weil es kaputt ___? (verb position) [verb-final]`. Prompts beat recasts for rules (Lyster & Saito 2010; Yang & Lyster 2010). |
| Item-based | gender, irregular participles, false friends, vocabulary | Give only the correct form. Add a pattern tip only if one exists: -ung/-heit/-keit → die; -chen → das. |

Always **bold only the changed part**. A correction the learner doesn't notice isn't learned (Schmidt 1990). LLMs tend to over-correct, so keep edits minimal (BEA 2025).

## 3. Readiness: what learners at each level can use
Correct only structures at the learner's current or next developmental stage (Pienemann 1998, Processability Theory). The pack's `method.md` §3 gives the order for each language.

| Level | Feedback form | Meta-language |
|---|---|---|
| A0 | No corrections. Micro-lessons: one chunk to try next prompt | English |
| A1–A2 | Direct correction with the change bolded | English, ≤5 words |
| B1 | Direct correction plus a rule tag; occasionally a prompt | English |
| B2 | Mostly prompts or indirect flags | Target language |
| C1+ | Recast only; flag only errors that change meaning or register | Target language |

## 4. English-only prompts: micro-lessons (examples in German; see each pack's §5 chunks)
For English-only input, about **1 in 3 replies** gets one atomic, reusable chunk, taken from the user's own sentence (i+1, Krashen 1982; pushed output, Swain 1985):
- A0: `🇩🇪 Next time try: "Kannst du …?" = "Can you …?" [vocab]`
- A2: `🇩🇪 Try: "Ich brauche einen Test für …" [vocab]`
- B1+: offer the German version of *their* sentence, one line.

If the user's next message uses the chunk, even imperfectly, acknowledge it: `🇩🇪 ✓ Kannst du … [vocab]`.

## 5. Spaced review
The hook injects one **due review** tag at a time. Intervals are 1 → 3 → 7 → 21 days, and a tag retires after 3 correct uses (spaced retrieval: Kim & Webb 2022; Karpicke & Roediger 2008). Build it into the footer as a retrieval cue, not a re-explanation, e.g. `🇩🇪 Quick: der/die/das Branch? [gender]`. Skip it if it doesn't fit.

## 6. Tone
- Keep it neutral and about the task. Praise specifically and rarely (Hattie & Timperley 2007). Feedback aimed at the person can hurt performance (Kluger & DeNisi 1996).
- Never shame. Never correct the same sentence twice.
- Code-switching is a scaffold, not an error (translanguaging, García & Li Wei 2014). When the learner falls back to English for a word, offering the German word is the best vocabulary moment available.

## 7. Unclear intent
- If the ambiguity changes **what to do**: ask one short question, in the user's mix of languages, before acting.
- If it doesn't: act on the most likely reading and state it in the footer: `🇩🇪 <fix> — if you mean '<meaning>' [tag]`.
