# Arabic 🇸🇦: method notes

## 1. Target variant & register
- **Correct toward:** Modern Standard Arabic (MSA / الفصحى), neutral written register.
- **Tolerate without comment (diglossia + chat norms):**
  - dialect words/forms (*3ayez, biddi, mish, leh, izzay*); never "upgrade" them to MSA
  - Arabizi / romanized input (3=ع, 7=ح, 2=ء, 5=خ, 9=ق or ص by region); never correct the script choice
  - missing short vowels/shadda, hamza seat variation (ان/أن/إن), ة vs ه, ى vs ي
  - **case endings (i'rab)**: unwritten in chat; never correct them
  - English tech nouns/verbs in Arabic text (*push, commit, API*)
- **RTL:** put the Arabic fragment in the footer as-is (the terminal handles bidi). Keep English hints outside the Arabic run, in parentheses.

## 2. Error priorities for English speakers
1. `definite`: *ملف لا يعمل* (meaning "the file doesn't work") → ***الملف** لا يعمل*; a bare noun means "a file". (A1+)
2. `idafa`: *الملف البرنامج* → ***ملف** البرنامج* ("the program's file"; no ال on the first noun, and no possessive like *الملف من البرنامج* at A-levels). (A2+)
3. `gender-agree`: *هي يعمل* → *هي **تعمل***; *الشاشة كبير* → *الشاشة كبير**ة***. ة-nouns are feminine; be lenient with loanwords. (A1+)
4. `verb-agree`: *أنا يعمل* → *أنا **أعمل*** (A1+). VSO: *كتبوا المطورون* → ***كتب** المطورون* (verb before subject stays singular; B1+).
5. `adj-agree`: *الكود جديد* (meant "the new code") → *الكود **الجديد*** (adjective copies ال). Note: without ال it's a full sentence "the code is new", so only fix if meaning is clearly a phrase. (A2+)
6. `pronoun-suffix`: *كتاب أنا* → ***كتابي***; *ساعد أنا* → ***ساعدني*** (A1+)
7. `prep`: *أبحث الخطأ* → *أبحث **عن** الخطأ*; *يعتمد في* → *يعتمد **على*** (A2+, item-learned: give the form, no rule)
8. `nonhuman-plural`: *الملفات كبيرون* → *الملفات **كبيرة***; *هذه* not *هؤلاء* for things (B1+)
9. `dual`: *اثنان ملفات* → ***ملفان*** (two files; B2+, low priority)
10. `false-friend`: see §4
11. `vocab`: a missing or wrong word

Never tag at any level below C1: number–noun reverse polarity (*ثلاثة ملفات*, not *ثلاث ملفات*), broken-plural pattern slips, i'rab.

## 3. Readiness / acquisition order
- **Agreement follows Processability Theory:** lexical morphology (plural/fem. forms on a single word) → phrasal agreement (noun–adjective, within NP) → interphrasal subject–verb agreement. Phrasal agreement emerges well before S–V agreement; correct only the current or next stage (Nielsen 1997; Mansouri 2000, 2005; Alsubhi 2026).
- **Gender:** English speakers overuse the masculine default; feminine marking on adjectives lags (Alhawary 2009). Give the right form directly (item learning).
- **Non-human plural = fem. sg.** and **VSO singular verb** are late (form–function mismatch with English); ignore below B1.
- **Case endings, dual, number polarity** are late and mostly invisible in unvowelled text; ignore at A/B levels.
- **Error taxonomy:** ALC/AALETA groups learner errors into orthography, morphology, syntax, semantics, punctuation; only morphosyntax and semantics matter here, because orthography in chat is noise (Alfaifi & Atwell 2014).

## 4. False friends & tech-talk
| Learner writes | Issue | Say instead |
|---|---|---|
| ملف for "folder" | ملف = file | مجلد (folder) |
| برنامج for "app" | برنامج = program/software | تطبيق (app) |
| خطأ for "bug" | fine for error; "bug" specifically | خلل / علة (or just "bug") |
| باگ / بق | loanword, often with Persian گ | tolerate; MSA خلل |
| كمبيوتر | loanword, fine | حاسوب (formal) |
| نسخة | = version *and* copy | نسخة (version), نسخ (copying) |
| تحديث vs ترقية | update vs upgrade | pick by meaning |
| مسح vs حذف | erase/clear vs delete | حذف for "delete a file" |

## 5. Micro-lesson chunks (A0–A2)
1. هل يمكنك …؟ (hal yumkinuka …?) = Can you …?
2. أحتاج … (aḥtāju …) = I need …
3. لا يعمل. (lā yaʿmal) = It doesn't work.
4. ما المشكلة؟ (mā al-mushkila?) = What's the problem?
5. من فضلك / شكرًا! (min faḍlak / shukran) = Please / Thanks!
6. كيف أفعل …؟ (kayfa afʿalu …?) = How do I …?
7. لماذا …؟ (limādhā …?) = Why …?
8. أريد … (urīdu …) = I want …
9. مرة أخرى، من فضلك. (marra ukhrā, min faḍlak) = Once more, please.
10. هذا صحيح / هذا خطأ. (hādhā ṣaḥīḥ / hādhā khaṭaʾ) = That's right / wrong.

## 6. Sources
- Nielsen (1997), "On acquisition order of agreement procedures in Arabic learner language," *Al-ʿArabiyya* 30:49–94.
- Mansouri (2000), *Grammatical Markedness and Information Processing in the Acquisition of Arabic as a Second Language*, Lincom Europa.
- Mansouri (2005), "Agreement morphology in Arabic as a second language," in Pienemann (ed.), *Cross-Linguistic Aspects of Processability Theory*. https://www.fethimansouri.com/s/2005_Cross-Linguistic-Aspects-of-Processability-Theory-Agreement-morphology-in-Arabic-as-a-second-la.pdf
- Alsubhi (2026), "The Emergence of Agreement in Arabic as an L2," *TPLS* 16(1). https://tpls.academypublication.com/index.php/tpls/article/view/11591
- Alhawary (2009), *Arabic Second Language Acquisition of Morphosyntax*, Yale UP. https://yalebooks.yale.edu/book/9780300141290/arabic-second-language-acquisition-of-morphosyntax/
- Alfaifi & Atwell (2014), Arabic Learner Corpus v2 / AALETA error tagset. https://catalog.ldc.upenn.edu/docs/LDC2015S10/ALFAIFI_LCSAW2014.pdf
- Arabic chat alphabet (Arabizi). https://en.wikipedia.org/wiki/Arabic_chat_alphabet
- Full research notes: `docs/research/sla-methods.md`
