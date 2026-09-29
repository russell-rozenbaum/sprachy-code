# Russian 🇷🇺: method notes

## 1. Target variant & register
- **Correct toward:** Standard Russian. In tech chat *ты* is the norm (devs and AI alike); *вы* is fine too. Flag only mixed agreement: *вы можешь* → *вы мож**ете***.
- **Tolerate without comment:**
  - **Translit** (Latin letters: *privet, ya ne znayu, ne rabotaet*). Never correct the script or translit spelling (*sh/š, y/j, kh/h*, missing soft sign `'`). In translit, correct only grammar and vocabulary.
  - е for ё, missing punctuation, lowercase
  - word stress (invisible in writing, not correctable)
  - IT anglicisms and slang: *коммит, закоммитить, запушить, задеплоить, пофиксить, дебажить, баг, фича, прод, либа, комп, мейл*
  - free word order (Russian allows it; don't "fix" SVO)

## 2. Error priorities for English speakers
Evidence: in RULEC-GEC, noun case is the #1 grammar error (13.2% of all errors), then lexical choice (12.3%), missing words (8.4%), adjective case, prepositions, agreement, aspect (Rozovskaya & Roth 2019). Order below weights **meaning loss in tech chat** over raw frequency.
1. `reflexive`: *программа не запускает* → *программа не запускает**ся*** ("doesn't launch [something]" vs "doesn't start"). Hits every tech verb: *открывается, сохраняется, компилируется, устанавливается*. (A2+)
2. `aspect`: *я уже делал это* → *я уже **с**делал это* (done vs was doing); requests: ***с**делай* (do it once) vs *делай* (keep doing). Low levels overuse imperfective (Apresjan 2024). (A2+)
3. `no-est`: *это есть проблема* → *это проблема*; *где есть файл?* → *где файл?* (A1+)
4. `case-prep`: *в файл* (location) → *в файл**е***; *на сервер* → *на сервер**е***. (A1+)
5. `v-na`: *в сайте* → ***на** сайте*; *на коде* → ***в** коде*. Item-learned: *на сервере/сайте/GitHub/странице*, *в файле/коде/базе/папке*. (A2+)
6. `case-acc`: *я вижу ошибка* → *я вижу ошибк**у***. Fem. -а→-у first; masc. animate/neuter later (Kisselev et al. 2025). (A2+)
7. `gender`: *моя код* → *м**ой** код*; *функция работал* → *функция работал**а***. (A2+)
8. `case-gen`: *нет файл* → *нет файл**а***; *5 ошибки* → *5 ошиб**ок***; *у я* → *у **меня***. (B1+)
9. `case-dat-instr`: *я нужно* → ***мне** нужно*; *с код* → *с код**ом***. Exception: fix *я нужно* at A-levels as a chunk (`vocab`), no rule. (B1+)
10. `motion-verb`: *каждый день я иду в офис* → *…я **хожу** в офис*. Rare in coding prompts. (B1+)
11. `false-friend`: see §4
12. `vocab`: a missing or wrong word

## 3. Readiness / acquisition order
- **Case** order for L2 learners: nominative → prepositional (after в/на) & accusative → genitive → dative → instrumental. Prepositional/accusative stabilize within the first year; dative and instrumental stay shaky much longer (Kisselev et al. 2025); heritage and L2 speakers both weaken most on lexically assigned dat/instr (Vancelette 2026). Ignore gen/dat/instr at A-levels except in fixed chunks (*у меня, мне нужно, нет*).
- **Aspect** is a lifelong error source. A-levels: correct only clear completed-result cases (*сделал, исправил, починил*) and one-off requests (*сделай*). B2+: correct the reverse error, perfective where process/repetition is meant (Apresjan 2024).
- **Agreement/gender** is mostly predictable from endings (-а/-я fem., consonant masc., -о/-е neut.). Give the right form, not a rule; soft-sign nouns are item-learned (*модель* fem., *словарь* masc.) (Yang & Lyster 2010).
- **Heritage speakers** (fluent, casual, often translit, sometimes gaps in spelling): skip A-level basics, focus on case collapse (gen/dat/instr → nom/acc) and formal register. The RLC separates the two groups because their errors differ (Rakhilina et al. 2016).
- **Never correct:** stress, ё, translit spelling, word order choices, soft-sign omission in translit.

## 4. False friends & tech-talk
| Looks like | Actually means | Say instead |
|---|---|---|
| аккуратный | neat, careful | (for "accurate": точный) |
| актуальный | current, relevant | (for "actual": фактический, реальный) |
| фабрика | factory (the *Factory* pattern is fine) | (for "fabric": ткань) |
| артист | performer | (for "artist": художник) |
| магазин | shop | (for "magazine": журнал) |
| интеллигентный | cultured | (for "intelligent": умный) |
| претендовать | lay claim to | (for "pretend": притворяться) |
| декада | ten days | (for "decade": десятилетие) |
| симпатичный | cute, nice-looking | (for "sympathetic": сочувствующий) |
| коммит, баг, фича, пушить | standard IT slang | fine, never flag |

## 5. Micro-lesson chunks (A0–A2)
Always show Cyrillic + translit.
1. Можешь …? (*mozhesh …?*) = Can you …?
2. Мне нужно … (*mne nuzhno …*) = I need …
3. Не работает. (*ne rabotaet*) = It doesn't work.
4. В чём проблема? (*v chyom problema?*) = What's the problem?
5. Пожалуйста / Спасибо! (*pozhaluysta / spasibo*) = Please / Thanks!
6. Как сделать …? (*kak sdelat …?*) = How do I do …?
7. Почему …? (*pochemu …?*) = Why …?
8. Я хочу … (*ya khochu …*) = I want …
9. Исправь, пожалуйста. (*isprav, pozhaluysta*) = Please fix it.
10. Это правильно / неправильно. (*eto pravilno / nepravilno*) = That's right / wrong.

## 6. Sources
- Rozovskaya & Roth (2019), *Grammar Error Correction in Morphologically Rich Languages: The Case of Russian*, TACL (RULEC-GEC error distribution). https://aclanthology.org/Q19-1001/
- Rakhilina, Vyrenkova et al. (2016), *Building a learner corpus for Russian* (RLC; L2 vs heritage). https://aclanthology.org/W16-6509.pdf · corpus: http://www.web-corpora.net/RLC/
- Apresjan (2024), *Errors in foreign language acquisition as a multifaceted phenomenon: the case of Russian aspect*, Russian Linguistics 48. https://link.springer.com/article/10.1007/s11185-023-09287-8
- Kisselev, Rubina & McManus (2025), *Russian nominative-accusative case distinction*, Pedagogical Linguistics. https://benjamins.com/catalog/pl.24010.kis
- Vancelette (2026), *Russian Case Across L1, Heritage, and L2 Speakers*, CUNY dissertation. https://academicworks.cuny.edu/gc_etds/6851/
- Yang & Lyster (2010). https://eric.ed.gov/?id=EJ892625
- Full research notes: `docs/research/sla-methods.md`
