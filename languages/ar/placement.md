# Arabic 🇸🇦 placement notes

The adaptive bank lives in `placement.json`: 30 multiple-choice items, 6 per level (A1–C1), with 6 different skills at each level. The target is MSA. Dialect forms never appear as wrong answers.

## What the items cover
- **A1:** survival vocab, tech words (مجلد vs ملف), `pronoun-suffix` (ملفي), verb person (أعمل), negation (لا يعمل), and basic `gender-agree` on adjectives. Every prompt has a transliteration, and the choices show Arabic plus translit, so the learner doesn't need to read the script.
- **A2:** `gender-agree` on verbs (هي تعمل), `definite` (الملف), `adj-agree` with ال, `prep` (يبحث عن), plural verb forms, and attached pronouns (إليّ).
- **B1:** `idafa` (ملف البرنامج), `nonhuman-plural` (الملفات كبيرة), VSO singular verb (كتب المطورون), pronoun suffixes on verbal nouns (مساعدتي), feminine verb agreement, and verbs that take a fixed preposition.
- **B2:** `dual`, adjectives after an idafa, the relative pronoun التي for non-human plurals, لم + jussive, feminine VSO agreement, and idafa with a possessive suffix.
- **C1:** 3–10 number agreement (ثلاثة ملفات), dropping the ن of the dual in idafa (ملفا البرنامج), adjective agreement with the head of an idafa, لأنه, the preposition after مسؤول, and ال on generic nouns.

## Distractor design
Every wrong option is a documented English-speaker error: ال on the idafa head, the masculine default, a plural verb in VSO, human agreement for non-human plurals, a separate pronoun instead of a suffix (ملف أنا), the English copula (ليس يعمل, الأمان هو), or an English-style preposition.

## Best level predictors
- **`idafa`, `nonhuman-plural`, VSO `verb-agree` (B1):** these separate A-level from B-level learners best, because agreement *within* a phrase comes before agreement *across* phrases (Nielsen 1997; Mansouri 2000/2005; see method.md §3).
- **`definite` + `adj-agree`:** the most frequent meaning-level errors, and a strong A2 signal.
- **Weak predictors:** vocab items (A1) and C1 number-noun agreement, which even advanced learners and many native writers get wrong.

Items avoid case endings, vowel marks and hamza-seat distinctions, which the pack never corrects.
