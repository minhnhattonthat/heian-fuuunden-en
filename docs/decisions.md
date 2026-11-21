# Decisions

The user's rulings on scope, style and trade-offs, newest last. Read before asking the user anything; if a later
decision replaces one, mark the old one "replaced by D<n>" instead of deleting it. Binding term spellings live in
`glossary.md`; this file holds the why.

| # | Date | Question | Options offered | Decision and reason |
|---|---|---|---|---|
| D1 | 2026-11-21 | Honorifics and name order | keep (-san), drop; JP or Western order | Keep honorifics; Western order (given name first). Owner's standing answer for one-shot runs. |
| D2 | 2026-11-21 | Romanization source for names | official art, earlier patch, Hepburn | Official English names where they exist, else an earlier fan patch, else Hepburn without macrons. Owner's standing answer. |
| D3 | 2026-11-21 | Credits | stay Japanese, translate | English. Owner's standing answer. |
| D4 | 2026-11-21 | Abbreviations | engine work first (default), abbreviate | Engine work first (skill default; not overridden). |
| D5 | 2026-11-21 | Graphics text left in Japanese | none (default), list | Translate all of it (titles, menus, banners, cards); leave the Japanese logo only if no official English version exists. |
| D6 | 2026-11-21 | Specs and plans | need approval, pre-approved | Pre-approved: keep going through every checkpoint without asking, report at the end. |
| D7 | 2026-11-21 | Existing saves / savestates | user supplies, none | None provided; build the debug tool as usual. |
| D8 | 2026-11-21 | Publishing | user publishes, agent publishes | Agent never runs `gh release create` and never changes repo visibility; the run ends at a built and verified release zip. |
| D9 | 2026-11-22 | Dialogue font path (agent call under D6) | 8x16 half-width fixed; VWF; tiny 2-per-tile | VWF with Pixel Operator (CC0) on both glyph paths: 176 px per line fits ~30 letters vs 22 half-width (D4, engine first). |
| D10 | 2026-11-22 | Names wider than a 48-px menu field (agent call under D4/D6) | abbreviate; narrower 16-px font; two 8-px lines in the same field | Two 8-px lines (Pixel Operator 8, CC0), chosen per string by the build (`{small}`/`{sbr}`, `insert.fit_field`): full names, no layout change, dialogue unaffected. Fields under 48 px (party list, 24 px) get engine widening first. |
