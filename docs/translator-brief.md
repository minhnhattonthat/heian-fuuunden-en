# Translator brief - Heian Fuuunden (SNES, KSS 1995)

You translate part of the Japanese script of Heian Fuuunden into English for a fan patch. A strategy RPG set in
Heian-era Japan: the young onmyoji Kagura (a boy of 16: he/him), raised by Priest Tenkai at Kumano, gathers allies across the provinces
while Seimei and Hiroyuki face Doma's plot to raise Taira no Masakado and the Yamawaro's rite to wipe out Kyoto.
Work only on the batches named in your dispatch, one at a time in the order given, each to a passing check before
the next. Do all translation yourself; do not dispatch subagents.

## Read first (read long files with offset/limit: whole-file reads above ~4 KB come back as a stub)
1. `docs/style-reference.md` - character voices and approved example pairs. Match this voice.
2. `build/terms_<batch>.txt` - binding glossary rows for this batch (full table in `glossary.md`, Style rules too).
3. `docs/synopsis.md` - who is who. Don't give a reveal away early.

## Input: `work/tl/<batch>.tsv`
`id<TAB>speaker<TAB>form<TAB>limit<TAB>Japanese`. Speaker is empty (the game shows a portrait, not a name): infer it
from content and neighbours. `{br}` = line break in the box, `{page}` = next box. Limit `176/160 x3` = each line at
most 176 px (about 30 characters), 160 px on the 3rd line of a box that continues to another page, at most 3 lines
per page; add `{page}`s freely. `48 field` etc. = a name field (the build fits it). Rows are in ROM order, which is
mostly story order: use neighbours for context.

## Output: `work/tl/<batch>.out.tsv`, written with your file-write tool (not a shell heredoc)
`id<TAB>English`, every input id exactly once, same order. Plain ASCII: straight quotes, `...`; no tabs inside the
English, no Japanese or fullwidth characters. Breaks are written as `{br}` and `{page}`, never `\n`.

## Validate
`python -X utf8 tools/batches.py check <batch>` from the repo root; fix every reported id until it prints OK.
`python -X utf8 tools/batches.py fit ID "English"` dry-runs one line (pixel widths, glossary, codes).

## Style
- Faithful: keep the information and order of ideas; adapt idiom, not meaning. Don't add or summarise.
- Keep the speaker audible: Seimei (old, おる/そなた/〜ぬ) formal and wry ("I had thought...", "Is that not so?");
  Tenkai (old priest, わし/じゃ/のう) warm and gruff ("eh?", "my boy"); Kagura young, direct, lively; bandits and
  rough men clipped ("ya", "ain't"); court nobles stiff and polite. A line any speaker could have said is a mistake.
- Names and terms exactly as in the glossary. Never abbreviate to fit: rephrase, or add a `{page}`.
- Honorifics kept: 〜殿 -dono, 〜様 -sama (Seimei-sama), 〜姫 -hime. Western name order.
- `{name}` (a name the game draws, up to ~119 px) and `{num}` (a number): copy exactly; no a/an before `{name}`,
  never `{num}th`. Battle and system messages are ONE line of 176 px including the name: keep them terse
  ("{name} dodged!"). `{end2}` stays at the very end where the Japanese has it.
- Last line of a page never under 6 characters.

## Consistency
Never edit `glossary.md`. For a recurring name or term not in it, pick a form, use it consistently, and report it.

## Report (reply with only this)
Files written and entry count; then any lines: `NEW TERM: jp -> en`, `UNSURE: id - note`, `LONG: id - note`.
