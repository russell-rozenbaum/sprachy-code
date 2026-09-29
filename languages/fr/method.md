# French 🇫🇷: method notes

## 1. Target variant & register
- **Correct toward:** Standard (metropolitan) French. In tech chat, informal *tu* is the norm (flag *tu*/*vous* only in formal external text, e.g. a client email).
- **Tolerate without comment:**
  - missing or wrong accents (*e/a/c* for *é/è/à/ç*, *ca* for *ça*); keyboards make them costly, and they rarely hide meaning
  - dropped *ne* (*je sais pas*, *c'est pas grave*); natives drop it in most casual speech and chat
  - *on* for *nous* (*on a fini*)
  - spoken forms: *y a*, *t'as*, *chais pas*, *ouais*
  - English tech nouns (*le build, la PR, le commit*)
  - franglais tech verbs (*pusher, merger, débugger, commiter, déployer, forker*) and their participles (*j'ai pushé*)

## 2. Error priorities for English speakers
1. `aux-etre`: *j'ai allé* → *je **suis** allé*; reflexives too: *je me **suis** trompé* (A2+). Hides tense/meaning and recurs.
2. `avoir-expr`: *je suis 25 ans* → *j'**ai** 25 ans*; *je suis faim* → *j'**ai** faim*; *je besoin* → *j'**ai besoin de*** (A1+)
3. `gender`: *le fonction* → ***la** fonction*. Tips: -tion/-sion/-té → la; -ment/-age → le. Be lenient with loanwords (le/la commit). Correct only nouns the user repeats (A2+).
4. `pronoun-order`: *je teste le* → *je **le** teste*; *donne à moi* → *donne-**moi*** (A2+)
5. `negation`: *je pas comprends* → *je **ne** comprends **pas*** (the missing *ne* is fine, the misplaced *pas* is not); *je n'ai pas du temps* → *pas **de** temps* (A2+)
6. `prep`: *dans France* → ***en** France*; *à Paris*; *je code pour 3 ans* (still coding) → ***depuis** 3 ans* (A2+)
7. `past-aspect`: *il a planté quand je codé* → *…quand je **codais*** (B1+). Background = imparfait, event = passé composé.
8. `subjunctive`: *il faut que tu fais* → *…que tu **fasses*** (B1+, only high-frequency verbs: faire, être, avoir, aller, pouvoir)
9. `adj-agree`: *une solution simple* ✓, *une grand erreur* → *une **grande** erreur*; most adjectives go after the noun (B1+, low priority)
10. `c-est`: *il est un bon outil* → ***c'est** un bon outil* (B1+)
11. `false-friend`: see §4
12. `vocab`: a missing or wrong word

## 3. Readiness / acquisition order
- **Developmental stages** (Bartning & Schlyter 2004, six stages from Swedish-L1 corpora, largely confirmed for English L1 in FLLOC data):
  - Stages 1–2 (≈A1–A2): bare/infinitive verb forms, *pas* before or without the verb, object pronouns after the verb (*je vois le*). Correct only `avoir-expr`, `aux-etre` on very common verbs, and vocab.
  - Stage 3 (≈A2–B1): preverbal object clitics emerge; passé composé/imparfait contrast begins. Start `pronoun-order`, `negation`, `prep`.
  - Stage 4 (≈B1): subordination grows; first subjunctives; agreement improves. Start `past-aspect`, `c-est`.
  - Stages 5–6 (≈B2–C1): subjunctive and adjective/participle agreement become systematic. Now `subjunctive` and `adj-agree` are worth flagging.
- **Object pronouns:** English speakers pass through a post-verbal phase (*je vois le*) before placing clitics correctly; correcting before stage 3 wastes the fix (Myles 2005).
- **Aspect:** PC/imparfait follows lexical aspect (states → imparfait first, events → PC). Anglophones over-use PC for states. Ignore below B1 (Ayoun 2005).
- **Gender** is item-learned, errors persist even in advanced speakers, especially on adjectives and vowel-initial nouns (*l'erreur*: gender invisible). Give the right form, not a rule (Dewaele & Véronique 2001).
- **Dropping *ne*** is native-like; advanced L2 speakers learn to drop it (Dewaele 2004). Never correct it.

## 4. False friends & tech-talk
| Looks like | Actually means | Say instead |
|---|---|---|
| actuellement | currently | (for "actually": en fait) |
| éventuellement | possibly | (for "eventually": finalement) |
| librairie | bookshop | (for a code library: bibliothèque; *librairie* is common dev jargon, flag only once) |
| supporter | tolerate / put up with | (for "support a feature": prendre en charge, gérer) |
| assister à | attend | (for "assist": aider) |
| demander | ask | (for "demand": exiger) |
| réaliser | carry out / build | (for "realize": se rendre compte) |
| sensible | sensitive | (for "sensible": raisonnable) |
| résumer | summarize | (for "resume": reprendre) |
| contrôler | check | (for "control": maîtriser, piloter) |

## 5. Micro-lesson chunks (A0–A2)
1. Tu peux …? = Can you …?
2. J'ai besoin de … = I need …
3. Ça (ne) marche pas. = It doesn't work.
4. Quel est le problème ? = What's the problem?
5. S'il te plaît / Merci ! = Please / Thanks!
6. Comment je fais pour …? = How do I …?
7. Pourquoi …? = Why …?
8. Je voudrais … = I would like …
9. Encore une fois, s'il te plaît. = Once more, please.
10. C'est bon / C'est faux. = That's good / wrong.

## 6. Sources
- Bartning & Schlyter (2004), *Itinéraires acquisitionnels et stades de développement en français L2*, JFLS 14. https://www.cambridge.org/core/journals/journal-of-french-language-studies/article/abs/itineraires-acquisitionnels-et-stades-de-developpement-en-francais-l2/E51B5BDB4ABEE63E6CFF9566870472BB
- Myles (2005), *French second language acquisition research: Setting the scene*, JFLS 15. https://www.researchgate.net/publication/231872662_French_second_language_acquisition_research_Setting_the_scene
- Myles & Mitchell, French Learner Language Oral Corpora (FLLOC), English L1 learners. http://www.flloc.soton.ac.uk/
- Ayoun (2005), tense and aspect in L2 French (PC vs imparfait, English L1). https://www.researchgate.net/publication/290257697_The_acquisition_of_tense_and_aspect_in_L2_French_from_a_Universal_Grammar_perspective
- Dewaele & Véronique (2001), gender assignment and agreement in advanced French interlanguage, *Bilingualism: Language and Cognition* 4(3). https://doi.org/10.1017/S136672890100044X
- Dewaele (2004), retention or omission of *ne* in advanced French interlanguage, *Journal of Sociolinguistics* 8(3).
- Full research notes: `docs/research/sla-methods.md`
