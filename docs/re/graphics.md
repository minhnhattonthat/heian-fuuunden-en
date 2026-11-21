# Graphics-text survey (phase 1)

Every Japanese element drawn as tiles or tilemap words rather than through the dialogue table. Sources: the menu
tour (`tools/routes/menu_tour.txt`), DMA/decompression logs (`work/qa/dma_tour`, `work/qa/dec_*`), and a static
sweep of every compressed chain and raw bank (`tools/gfx_sweep.py`, sheets `work/qa/sweep4`, `sweep2_c8`,
`sweep_raw4`; codec in `compression.md`). "Kept" rows follow D5. Screens marked *phase 2* are known from the sweep
and still need an in-game shot via the debug tool.

## Tile art (redraw)

| # | Element | Source (verified unless marked) | Reached by | Plan |
|---|---|---|---|---|
| G1 | Title logo 平安風雲伝 | `C8:0000` LZ 4bpp (title BG) and a 2bpp copy `C8:31F3` | cold boot ~f2400 | **Kept Japanese** (D5); optional English subtitle |
| G2 | PUSH START / ©1995 KSS, KSS logo, NATSUME logo | `C8:3B1E`, `C8:DAF9`, `C8:77CA` | cold boot | English already |
| G3 | File select scroll kana はじめから / つづきから (vertical) | `C8:3E4F` LZ 2bpp, 0xF20 bytes, table B id 6 | `boot.txt` final frame | Redraw "New Game" / "Continue" (vertical scroll: likely horizontal lettering rotated or stacked; decide in phase 5) |
| G4 | File select 記録 1 2 3 | same block | same | Redraw "Save 1-3" |
| G5 | Small 8×16 font (kana, digits, X Y A B L R) + 16×16 stat kanji 体力 経験 装備 攻 防, `LV`, 宮 | `C8:8954` LZ 2bpp 0x1600 → BG3 VRAM `$6000`, table B id 15 | field menu | Replace kana cells with English glyphs; redraw the kanji labels as English ("HP", "EXP", "Equip", "Atk", "Def") |
| G6 | Battle command buttons with kana labels (こうげき, どうぐ, にげる …) | `C8:B282` LZ 2bpp 0x480, table B id 8 (loaded at `C0:62CA`) | *phase 2* (battle) | Redraw labels; buttons are fixed width |
| G7 | Vertical kana grid + PUSH L/R bar (probably name entry or a kana list) | `C8:ABF2` LZ 2bpp 0x10C0, table B ids 33-36 | *phase 2* | Redraw as A-Z grid |
| G8 | 8×16 two-tile font with kana and kanji (いまむかし …, 今は昔) | `C8:D140` LZ 2bpp 0xF00, table B id 43 (code `C1:E747`); its map is `C8:D861` (type 2) | *phase 2* | English font in the same cells |
| G9 | Ending / credits kanji panel (staff kanji on grey, TEAM SD, 1995 KSS) | `C8:C2F8` LZ 2bpp 0x1800, table B id 12 (bank CB code) | *phase 2* (ending) | English credits (D3) |
| G10 | Dialogue-font credit kanji 0x380-0x3B6 and logo cells 0x3C0-0x3CF | font bank C9 | ending | English credits (D3) |
| G11 | Tiny kanji strip in the last portrait slot | raw `CA:FE00`-ish (`work/qa/caend2.png`) | not seen in game | Probably unused; check if any portrait id reaches it (phase 2) |
| G12 | Map screen (field menu icon 3) | - | `menu_tour.txt` | Shows no Japanese in the tour shot; re-check once place names are known |

## Small-font tilemap text (text work, not art)

BG3 words `0x20xx`/`0x24xx`, tile = small-font cell (`tools/smallfont.py` decodes them).

| # | Text | Source | Screen |
|---|---|---|---|
| T1 | 6 field-menu captions (どうぐを　つかいます …) | ROM table `C1:9E7F` → `C1:9E8B`, 2 rows × 18 words each | field menu |
| T2 | Save menu: きろくしておわる / きろくしてつづける / このままおわる / まえのきろくにもどる | `C8:71C2` LZ tilemap | menu → save |
| T3 | Options: もじのはやさ / あるくはやさ / おんがく (+ value tiles 0x12A-0x14E) | `C8:723A` LZ tilemap | menu → settings |
| T4 | おつかれさまでした | `C8:72B5` RLE tilemap | quit after save (*phase 2*) |
| T5 | きろくしました　おつかれさまでした | `C8:72E0` LZ tilemap | after saving (*phase 2*) |
| T6 | Status labels 攻 防 体力 経験 装備 (16×16 kanji cells) | tilemaps `C8:92E4`, `C8:9DD6`, `C8:A13B` (type 2) | status screen and two variants (*phase 2*: battle status?) |
| T7 | Kana grid maps (あいうえお … in grid layouts) | `C8:746F`, `C8:AA6E`, `C8:D861` (with G7/G8 tiles) | name entry / kana list (*phase 2*) |

Everything else in the menus (names, items, equipment, numbers on BG1/BG2) is drawn at run time from the dialogue
table and the dialogue font (`text.md`).

## Swept with no Japanese
D1/D4/D5 sprites, CB/C7/D7 field and background tiles, CA portraits (except G11), CC-D0/D3 raw sprites, CE-CF and
D6 effects, D0 damage digits (0-9, English as is). Not tile data (skipped, listed by `gfx_sweep.py`): C4 map data,
C7:1053/57A6/73D9, D2, D7:6C5D+, all type-2 blocks except those decoded above.

## Still open (phase 2, with the debug tool)
- In-game shots for every *phase 2* row: battle (G6), the G7/G8 screens, ending/credits (G9/G10), save messages.
- Chapter or area title cards and game over, if any: none found in the sweep; confirm on the warp tour.
