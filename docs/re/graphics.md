# Graphics-text survey (phase 1, in progress)

Every Japanese element drawn as tiles rather than through the dialogue table. Columns: screen, how reached, layer,
source guess, plan. "Kept" rows follow D5 (logo stays Japanese only when no official English logo exists).

| # | Screen / element | Reached by | Layer | Source (guess unless marked) | Plan |
|---|---|---|---|---|---|
| G1 | Title logo 平安風雲伝 (red brush kanji) | cold boot, no input, frame ~2400 (`work/qa/title2`) | BG | compressed graphics | **Kept Japanese** (D5: no official English logo). Optional English subtitle later if room. |
| G2 | Title "PUSH START", "©1995 KSS", KSS logo | cold boot | BG | - | Already English, no work. |
| G3 | File select scrolls はじめから / つづきから | `tools/routes/boot.txt` (final frame) | BG (scroll art) | big kana baked into scroll art; source not traced | Redraw: "New Game" / "Continue". |
| G4 | File select scrolls 記録1 / 記録2 / 記録3 | same | BG | as G3 | Redraw: "Save 1..3" (or "Record"). |
| G5 | Field menu captions (X menu), e.g. なかまの　のうりょくを　みます | field state `work/states/play3_end.mss` + X | BG3 | **verified**: tilemap words at `C1:9E7F` table (`text.md` §Other text); 8×16 small font tiles compressed or built at run time | Text-like: extract the 6 captions as tilemap text, give the small font English glyphs. |
| G6 | Field menu sub-boxes (party list, items, settings: Lv labels, 体力-style stat labels, list rows) | `tools/routes/menu_tour.txt` from `play3_end.mss` | BG1/BG3 | mix: names from the table; labels probably tilemap text like G5 | Trace each label in phase 1 follow-up. |
| G7 | Map screen (X menu icon 3) | `menu_tour.txt` | BG | graphics | Check for place-name kanji. |
| G8 | Dialogue font cells 0x380-0x3B6 (credit kanji) and 0x3C0-0x3CF (logo) | `tools/fontview.py 0x90000+0x380*64` | font | font bank C9 | Credits are English (D3): rebuild with the English font. |

## Still to survey (next session)
- Battle screen: command menu, status window, damage/victory banners. Needs an encounter (none reached yet).
- Shops, inn, item/equipment screens, save confirmation, name entry if any, option screen labels.
- Chapter or area title cards, game over, ending, credits: reach with the debug tool (phase 2), add rows here.
- Static sweep: render every graphics region (compressed blocks once the codec is known) and list Japanese cells
  (`references/graphics.md` §Survey). The 8×16 small font and the scroll-art kana are the first things to locate.
