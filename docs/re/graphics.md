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
| G6 | Battle command buttons with kana labels (こうげき, どうぐ, にげる …) | `C8:B282` LZ 2bpp 0x480, table B id 8 (loaded at `C0:62CA`) | scenes `battle_cmd_*` (Y in battle: こうげき じゅつ しきがみ たいき; どうぐ hidden without items) | Redraw labels; buttons are fixed width |
| G7 | Help-panel tiles: SNES pad drawing, PUSH KEY, small kana for the panel text | `C8:ABF2` LZ 2bpp 0x10C0, table B ids 33-36 (0x21 loaded at `C0:6A1B`, 0x22 at `C0:A21F`; 0x23/0x24 have no immediate loader, likely unused) | scenes `battle_help` (せんとうシーン), `help_menu` (ステータスがめん) | English labels and panel text (T8) |
| G8 | 8×16 two-tile font with kana and kanji (いまむかし …, 今は昔) | `C8:D140` LZ 2bpp 0xF00, table B id 43 (code `C1:E747`); its map is `C8:D861` (type 2) | *phase 2* | English font in the same cells |
| G9 | Ending / credits kanji panel (staff kanji on grey, TEAM SD, 1995 KSS) | `C8:C2F8` LZ 2bpp 0x1800, table B id 12 (bank CB code) | scenes `credits`, `credits_end` (real path: win the final battle) | English credits (D3) |
| G10 | Dialogue-font credit kanji 0x380-0x3B6 and logo cells 0x3C0-0x3CF | font bank C9 | ending | English credits (D3) |
| G11 | Tiny kanji strip in the last portrait slot | raw `CA:FE00`-ish (`work/qa/caend2.png`) | not seen in game | Probably unused; check if any portrait id reaches it (phase 2) |
| G12 | Map screen (field menu icon 3) | - | `menu_tour.txt` | Shows no Japanese in the tour shot; re-check once place names are known |
| G13 | Game-over 終 card (32×32-ish brush kanji over the burnt capital) | `C8:9BAF` LZ 4bpp 0x300 (24 tiles; decoded at mode 8 start, `work/qa/exp/m8dec`) | scene `game_over` | Redraw ("The End" / "Game Over"; decide in phase 5) |
| G15 | Portrait name plates (神楽 … 道長, generic 男 娘 僧 …) under dialogue portraits | raw 2bpp, 94 × 0x80 at `C7:A1FF` (C5:1C6B: plate = table `C1:E78A` byte 0; BG3 tiles $340/$348) | scene `title_slots` | **Done**: `tools/plates.py` (D17) |
| G14 | Ending 終 card after the staff roll (white kanji on black) | not traced yet (bank CB ending code; check G9/G10 cells) | scene `credits_end` | Same wording as G13 |

## Small-font tilemap text (text work, not art)

BG3 words `0x20xx`/`0x24xx`, tile = small-font cell (`tools/smallfont.py` decodes them).

| # | Text | Source | Screen |
|---|---|---|---|
| T1 | 6 field-menu captions (どうぐを　つかいます …) | ROM table `C1:9E7F` → `C1:9E8B`, 2 rows × 18 words each | field menu |
| T2 | Save menu: きろくしておわる / きろくしてつづける / このままおわる / まえのきろくにもどる | `C8:71C2` LZ tilemap | menu → save |
| T3 | Options: もじのはやさ / あるくはやさ / おんがく (+ value tiles 0x12A-0x14E) | `C8:723A` LZ tilemap | menu → settings |
| T4 | おつかれさまでした | `C8:72B5` RLE tilemap | scene `quit_nosave` (save menu option 3 このままおわる) |
| T5 | きろくしました　おつかれさまでした | `C8:72E0` LZ tilemap | scene `save_message` |
| T6 | Status labels 攻 防 体力 経験 装備 (16×16 kanji cells) | tilemaps `C8:92E4`, `C8:9DD6`, `C8:A13B` (type 2) | scene `menu_status`; the two variants not placed yet (Y on a unit in battle shows no status: check X/A screens in phase 8) |
| T7 | Grid-layout tilemaps (not a name entry: there is none) | `C8:AA6E` battle help panel, `C8:D861` prologue (G8), `C8:746F` decoded at game-over start | scenes `battle_help`, `prologue`, `game_over` |
| T8 | Help-panel text: せんとうシーン / ステータスがめん titles, Y… けってい, X… フィールド, B… キャンセル, 3-4 lines of ※ notes | G7 cells in the T7 map (battle) and the id-0x22 panel map (field menu; map source not traced) | scenes `battle_help`, `help_menu` |

Everything else in the menus (names, items, equipment, numbers on BG1/BG2) is drawn at run time from the dialogue
table and the dialogue font (`text.md`).

## Swept with no Japanese
D1/D4/D5 sprites, CB/C7/D7 field and background tiles, CA portraits (except G11), CC-D0/D3 raw sprites, CE-CF and
D6 effects, D0 damage digits (0-9, English as is). Not tile data (skipped, listed by `gfx_sweep.py`): C4 map data,
C7:1053/57A6/73D9, D2, D7:6C5D+, all type-2 blocks except those decoded above.

## Dialogue-font text found on the warp tour (text work, listed so phase 4 checks the table covers it)
- Battle title card "<province>の闘い" (message 0xB9 + name id 0x1A0+province): scenes `card_p00`..`card_p3E`.
- Overworld labels (紀伊の国 top right, 神楽部隊 bottom left): scene `overworld`; drawn with the dialogue font, source
  not traced yet (phase 4: confirm they come from the table).

## Phase 8 progress
- **Done (English in a zoomed cold-boot shot):** G5 small font (kana cells -> English letters, `tools/smallfont_en.py`),
  T1 captions, T2 save menu, T3 options, T4/T5 maps (the quit/saved popups seen in `quit_nosave`/`save_message` are
  dialogue rows 243/244), T6 status labels in all three status maps (D16), G15 name plates (D17), the はい/いいえ box
  after 229 (small-font map `C8:BBEE`, named by code `C5:265A`: `tilemaps.tsv` row yesno0; scenes
  `battle_save_prompt`, `battle_save_no`).
- **Done 2026-11-22 (worker 3), `tools/gfx_en.py`:** G6 command labels (5 buttons of 5x2 tiles in `C8:B282`, tiles
  read from the BG3 map in the `battle_cmd_*` scenes; D18), G13 game-over card (`C8:9BAF` = four 16x16 OBJ at
  (112,111), OAM base $4000; "GAME / OVER"), G9/G14 credits: the staff roll is not sprites or the dialogue font but
  BG3 pages cut from the 32x64 map `C8:CD4E` (decoded to $7E:2000) with 16x16 kanji tiles from `C8:C2F8`; page
  table `C1:8265` (src lo16, rows, columns, VRAM), title = map rows 32-33, end card = rows 40-49 cols 0-23 (終 at
  rows 44-49 cols 16-21). All rebuilt in English (D19). G10 (dialogue-font credit kanji 0x380-0x3B6) is not drawn
  by the roll: unused. `warp.lua --var DUMP_PPU=1` dumps VRAM/CGRAM/OAM with the scene shot.
- **Left:** G3/G4 file select scroll, G7/T8 help panels (own small kana in `C8:ABF2`), G8/T7 prologue font + map.

## Still open
- The T6 variants' screens; the field-menu help panel's map source (T8).
