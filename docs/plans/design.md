# Design: sprachy-code (Sprachy Terminal)

> v0.1 shipped as German-only "claude-denglisch". v0.2 generalizes it to language packs; see `language-pack-contract.md`.

## Goal
Treat daily Claude Code use as low-friction German practice for English speakers at any level (A0–C2), without slowing down real work.

## Decisions
| Decision | Choice | Why |
|---|---|---|
| Delivery | Plugin = hook + skill | A skill loads only when its description matches, so it can't guarantee a correction every turn. A hook can. |
| Placement | One footer line after the work | The work comes first; the research found no learning loss from placing feedback like this (Kamelabad 2025). |
| Annoyance cap | Hook-enforced cooldown: 2 quiet turns after each correction; one fix, shown as a fragment of about 12 words; only fixes that hide the meaning or keep recurring | The user's hard requirement: never annoying. Research also supports focused feedback (Sheen 2007). |
| Logging | The Stop hook parses the 🇩🇪 footer | No extra tool calls or permission prompts, and no added latency. |
| State | `~/.sprachy-code/<lang>/` + `config.json` for the active language (`SPRACHY_HOME` overrides) | Visible to the user and survives uninstalling the plugin. `CLAUDE_PLUGIN_DATA` is deleted on uninstall. |
| Onboarding | Offer `/sprachy test` once per session until a profile exists | A forced test would block the user's first real task. |
| XP | German words + corrections + fixes; rank cost grows linearly | Motivation; shown in the status line so it costs 0 tokens. |
| Profile notes | Updated by Claude only during `test` / `review` | Writing notes every turn would add tool calls and permission prompts. |
| Multi-language | One repo; language packs in `languages/<code>/`; one language active at a time; progress kept per language | About 80% of the code is language-neutral. A contract test keeps every pack consistent. |
| Language menu | `/sprachy language` → the built-in AskUserQuestion picker | Native UI, no extra code. Its 4-option limit is handled with an "Other" entry for the rest. |
| Placement | Adaptive: 5 rounds × 3 multiple-choice items in Claude's picker. Rasch/Elo θ picks items near θ−s, θ, θ+s; the final level is the highest band with ≥60% correct | User wanted it quick and adaptive. The CLI grades deterministically. Simulated learners are placed exactly at every level in every pack; with 15% random slips, 80% are placed exactly. |
| Runtime | Python 3 stdlib, pure-function core | No dependencies; the core is fully unit-tested. |

## Footer contract (hook ↔ reminder ↔ SKILL.md)
- `🇩🇪 <fix, changed words **bold**> — if you mean '<meaning>' [tag]` → error event
- `🇩🇪 ✓ <snippet> [tag]` → correct-use event
- Tags are kebab-case and may be comma-separated: `[v2, gender]`

## Verified
- 33 unit tests pass, and `claude plugin validate .` passes.
- End-to-end with `claude -p --plugin-dir .`: correction footer rendered → `verb-final` logged → XP credited → `/denglisch:denglisch level B1` wrote the profile.

## Open / next
- Windows: `python3` may not be on PATH (`py` launcher). Consider a fallback.
- The German detector is a function-word heuristic; it misses German without function words.
- Measure uptake: does the error rate per tag fall over time? That tells us whether the tool actually works.
- 3-turn rough-Denglisch E2E: turn 1 → one fragment fix `[verb-final]`; turns 2–3 → silent despite many errors (cooldown worked).
