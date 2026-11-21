# Window data: measured text budgets (phase 5 width gate)

Measured on the marker build (`python -X utf8 build.py marker`, VWF fonts `fonts/en16.png` / `fonts/en8.png`) from
pixels in emulator shots, not from the Japanese length. px = English VWF pixels (`tools/font_en.py text_px`).
"measured" names the shot. Renderer-2 calls (caller, string id, VRAM slot) come from `tools/lua/r2log.lua`
(`work/qa/r2/<scene>/log.txt`).

| Variant | Renderer | Budget | Lines | State |
|---|---|---|---|---|
| Dialogue box (field, events, portrait or not) | dialogue `C1:7270` | 176 px per line | 3 per page | measured: `work/qa/torture2` f4700 (22 x `M` = 176 px shows whole; 185-px line loses its last glyphs) |
| Dialogue, the line before `{page}` | dialogue | 160 px | - | measured: torture f4100 (the ▼ arrow is a Japanese glyph drawn at x 160-175 of line 3 and erases text under it when it blinks off). Applies to line 3 only; lines 1-2 keep 176 |
| Battle turn message (`{name}のばんです`, id 205) | dialogue | 176 px | 1 | measured: `marker_warp/battle_turn_msg` (box is wider than the buffer; cut at 176 by the VWF) |
| Battle help prompt (id 0B8) | dialogue | 176 px | 1 | measured: `marker_warp/battle_help_prompt` (128-px marker shows whole); box ~200 px, buffer 176 |
| Menu popup (id 28B in items/shikigami, id 243 save message) | renderer 2 (`C0:A93A`, VRAM 7000) | 112 px (14 tiles); **243: 120 px** | 1 | measured: `marker_warp/menu_items`, `save_message` (`n` after "brow" cut at x 112). Phase 8: the save-menu window shows a 15th tile (the Japanese uploads 10 glyphs x 12 px); "Saved." padded to 109 px left it as a see-through hole, padded to 117 px it is filled (`work/qa/qa_pad`), so 243 is centred in 120 px and 243/244 are padded to 120 px (D21; 244 and 28B stay left-aligned: their Japanese fills the window from the left, inkbox 4/7 and 4/12) |
| Quit popup (id 244, save menu このままおわる) | renderer 2 `C0:AF62`, VRAM 7000 (as 243) | 120 px (as 243) | 1 | measured: `marker_warp/quit_nosave` ("[244] The quick brown" cut like 243); phase 8 as 243 |
| Item-menu two-line popup (1C8 inventory full over 1C9 can't equip, both drawn by step `$3A=12`, `C0:A8CB`) | renderer 2 `C0:A8DE`/`A8F5`, VRAM 7E00/7F00, window `C1:1699` #0D | **128 px** (16 tiles) per line | 2 (one id each) | measured: `marker_warp/item_full` (scene pokes `$3A=12` in the item menu; "[1C9] The quick brown f" whole = 125 px, the `o` at 126+ cut; ink x 66-190, frame at 196) |
| Squad confirm popup (28D これでいいですか？ over 28E はい/いいえ; event command 0 step $1F `C5:A4A2`, window #12 at step $20) | renderer 2 `C5:A4B5`/`A4CC`, VRAM 7800/7900 | **112 px** per line | 2 (one id each) | measured: `marker_warp/confirm_prompt` (scene `confirm_prompt`; "[28D] The quick brow" ink x 74-183, cut at 184; frame x 66-189 = window #12, 16 tiles). 28E is a choice line: the BG cursor (`C5:FB6E`, `$1228`) sits at about +8..16 px and +58..64 px from the line start; the Japanese puts はい at +24 and いいえ at +72 (original shot `work/qa/probe/p28jp`), so English keeps Yes at +24 and No at +72 px (row note) |
| Shop label 価値 (id FF) under both panels, value digits to its right | renderer 2 `C0:D938` (mode 0C sub 3), VRAM 6700 | **24 px** (3 tiles, x 64-88 / 168-192) | 1 big or 2 small | measured: `marker_warp/shop` (scene `shop`: `$122E=1` poked after sub 0 loads the shop; JP marker "[0FF" ink x 66-86, `]` cut at 88; small marker's 2nd line "he q" whole); digits start at x 113 |
| Battle music window title 音楽 (id 203; battle menu state `$1516=6`, also state 7) | renderer 2 `C5:183B`, `C5:1AE2`, VRAM 6D40 | **24 px** (3 tiles, x 144-168; window x 130-181) | 1 big or 2 small | measured: `marker_warp/battle_music` (scene pokes `$1516=6,$1518=0` at the command column; "[203" ink x 146-166, cut at 168) |
| Squad formation screen names (ids 054-083, 100 = empty slot; event command 0 steps $10-$18, `C1:5FBC`) | renderer 2 `C1:6011`, VRAM table `C1:E6CE` (slots $18 words apart: 7200/7218/7230/7248, 7400.., 7500..) | **24 px (3 tiles) of 16-px text** in the original; slot pitch 56 px on screen | 1 | measured: original `work/qa/probe/psqjp` (神楽 x 40-64 under its Lv); **English: 40 px narrow, one row** (D11 remedy, `PartyName` at `C1:6011`, table `C1:E6CE` = $7200/$7400/$7600 + n*$28, panel C8:9506 widened too). Verified 2026-11-22 with `--qa 054=Sadamitsu` (scene `squad_form`: "Sadamitsu" whole; the screen drew slots 0-11, a log of `C1:6011` showed; 12-19 not reached). Id 100 must translate to blank |
| Item grid (ids 001-053 + 000 blank) | renderer 2 `C1:2D13`, VRAM 7600/7650/7700.. | 48 px (6 tiles) | 1 big or 2 small | measured: `stress_small/menu_items` (`--qa 000=...`: "0123456" / "abcdefg" in 8 px show whole, 48 px) |
| Status screen class / name / equipment (0F3.., 0B9-0F2, items) | renderer 2 `C1:29D9`, VRAM 7000/7050/7100/7150 | 48 px (6 tiles) | 1 big or 2 small | measured: `marker_warp/menu_status` (small two-line markers whole) |
| Party list names under the portraits (ids 054-083) | renderer 2 via `PartyName` (callers `C1:2C04`, `C1:32AE`, `C1:3327`), VRAM table `C1:A3CB` (`C1:A3DB` = +$200 when `$10CC`) | **40 px (5 tiles), narrow 8-px font, always** | 1 | measured: `work/qa/party/menu_items`, `menu_squad`, `menu_status` (`build.py marker --qa 054=Sadamitsu --qa 100=Yasumasa`: all 8 slots whole). Room per slot: x 32-71 (own portrait ends x 32, next starts x 72). Original: 3 tiles (24 px) of 16-px text; widened in the engine (D11, hooks.md §Party list) |
| Battle jutsu list (ids 13C-181) | renderer 2 `C5:0D03`.. (5 rows), VRAM 6D40/6E00/6E40.. (8 tiles each) | 48 px | 1 big or 2 small | measured: `marker_warp/battle_jutsu_list` (small lines whole; the cost digit sits at x 48) |
| Status-screen jutsu page (ids 13C-181; A in the status screen, `$1294=0`) | renderer 2 `C1:2E0E` (`C1:2DA1`, from `C0:AC99`), VRAM table `C1:A3EB` (7C00/7C50/7D00/7D50/7E00) | **48 px** | 1 big or 2 small | measured: `work/qa/probe/pjls/pjl_a` (stress `--qa 16E={small}0123456789..`, `--qa 146=ABCDEFGHIJKL`: ink x 136-182, cut at 184; cost digits from x 201). A string wider than the field spills into a neighbour slot's tiles (stress shot): the lint must hold 48 |
| Status-screen shikigami page (ids 182-1B2; A twice) | renderer 2 `C1:57C0`, VRAM table `C1:A3EB` | **48 px** | 1 big or 2 small | measured: `pjls/pjl_aa` (ink x 152-198, cut at 200; count digit from x 217) |
| Battle shikigami list (ids 182-1B2) | renderer 2 `C5:226F`.. | 48 px | 1 big or 2 small | measured: `marker_small/battle_shikigami_list` (same layout as the jutsu list) |
| Overworld squad label (ids 1B3-1B8) | renderer 2 `C1:4FF3`, VRAM 6B00 | 48 px (6 tiles) | 1 big or 2 small | measured: `marker_small/overworld` |
| Overworld province label (ids 24A-288) | renderer 2 `C1:5018`, VRAM 6B30 | 48 px (6 tiles) | 1 big or 2 small | measured: `marker_small/overworld` ("[26C] The" cut at 48; a wider string spills into the squad label's bottom row at 6B80) |
| Title slot list: place (101-111), port (1BD-1C4) or province (24A-288) per slot | renderer 2 `C0:93CA`/`9432`/`949A` (`C0:9377`: place `$100+map`, ports +$AB, else province), VRAM 6C00/6D00/6E00 | 48 px (6 tiles) | 1 big or 2 small | measured: `work/qa/r2/title_slots` f3100 (scene `title_slots`; "[102] The" ink x 154-199, `q` at 200 cut) |
| Place / port banner on entering a place (101-111, 1BF-1C4) | renderer 2 `C1:3667` (overworld sub 0E, `C0:D2F0`), VRAM 6910 + 8 x `C1:364D[$1088-1]` | 72 px (9 tiles, x 88-160; window inner 84-163); the 48-px slot list is the smaller | 1 big or 2 small | measured: `work/qa/r2/place_07`, `place_m` (scene `place_banner` + `tools/lua/execpoke.lua AT=0xC136C0 POKES='7E1088=07'`); JP glyphs 12 px, offsets centre them |
| Map-exit banner (115-12C) | renderer 2 `C1:687F` (field sub 06, `C0:9B2F`), id $117 + `C1:E708[(map-1)*4+$10E4]`, VRAM 6910 + 8 x `C1:6869[i]` | **72 px** (9 tiles) | 1 big or 2 small | measured: `work/qa/r2/exit_banner` (offset 0: "[12C] The quic" whole, ink x 90-159), `exit_m` (two small 72-px lines whole) |

Banner centring: `insert.banner_offsets` rewrites `C1:364D` / `C1:6869` for every entry whose string the build
replaces (tile offset = round((72 - px) / 16), never past x 160); Japanese entries keep theirs
(`tests/test_insert.py::test_banner_offsets`; verified `place_m`: a 48-px small marker sits at offset 2).

## Small mode (two 8-px lines in one 16-px field)
`tools/insert.py fit_field`: a name wider than its field in the 16-px font goes in as `{small}line 1{sbr}line 2`
(Pixel Operator 8, advance = ink + 1, space 3 px), split at the space that balances the lines; each line <= the
field. Then the same one or two lines in the narrow 8-px font (`{narrow}`, 3-px letters: "Sadamitsu" is 52 px
big, 61 small, 35 narrow). None fits = build error. Field budgets per id range: `insert.FIELDS`. The dialogue ignores `{small}` and
draws `{sbr}` as a space, so `{name}` in dialogue reads normally (verified: `marker_warp/battle_turn_msg`).

## Measured last (2026-11-22); only the ending/credits are left, as graphics (phase 8)
- Squad exchange screen (`C0:B9A5` -> `C1:32C8`, `C0:EF6F` -> `C1:3267`: two panels, panel B = tiles $280-$2BF,
  VRAM $7400): **measured 40 px narrow** (2026-11-22): mode 0E (`C0:835B` -> `C0:EC48`) asks 部隊へんせいしますか？,
  Yes draws both panels (scene `squad_xchg`); a 10-name `--qa` stress build shows every name whole in both panels.
- Province card `{name}の闘い` (id 1B9): **measured 176 px** (2026-11-22, marker `card_p00` with hold 420 and
  `SHOTS_AFTER=10`, `work/qa/card_cmp3.png`): one dialogue line in the top box (x 26-229, text x 41-217), the same
  box as the save prompt 229 that follows; the full 176-px marker line ([1B9] filler + {name} marker) ends inside the
  frame. The card shows ~f2260-2390 after the `card_p*` warp, past the scene's 180-frame hold.
- Palace scene, ids 297-2A5 (+ 2A6 "...長保二年 紀州熊野"): a speaker line + up to 3 lines per page. **Unreferenced
  (cut scene), 2026-11-22**: no `LDA/LDX/LDY/CMP/CPX/CPY/ADC #id` in the ROM, no event-script entry (3-byte
  `id, byte` records as at `C1:E4DC`, flag bit 15) in the ROM or in any unpacked block; the title demo loops 290-296
  only (`C0:8D59` stops at 297; idle 20000 frames logged at `C1:7233`), New Game goes scrolling prologue
  (tilemap text) -> banner 101 -> 2A7. Forced into the real box (execpoke `$1416=29B` at `C1:7233`,
  `work/qa/palace29B_b`): the box shows 3 rows of 176 px and drops the 4th line. Translated anyway, linted as
  speaker line + 3 lines of 176/160 (`lint.SPEAKER`).
- Renderer-2 callers, resolved from the code before each `JSL $C1753B`, each now shot (no "(guess)" left in the
  `max` column). Budgets live in `insert.FIELDS` / `tools/lint.py POPUPS`.
  | Caller | id | VRAM | Budget |
  |---|---|---|---|
  | `C1:6011` | `$101E` + $54 (party names) | table `C1:E6CE` | squad formation screen: D11 remedy applied (`PartyName`, 40 px narrow, one row; slots 0-3 panel C8:939E, 4-11 C8:9450, 12-19 C8:9506) |
  | `C1:2E0E` / `C1:57C0` | + $13F jutsu / + $181 shikigami | table `C1:A3EB` | 48 field (measured, status pages above) |
  | `C5:1281` / `C5:206A` | `$09EE,x` + $C2 or $12D / + $53 | 6E00 / 6D40 | ids in 001-0FE: 48 field |
  | `C5:12FF`, `C5:132A` | `C1:8785` + $1A7 (shikigami) | 6E40 / 6F00 | 48 field |
  | `C5:0064` / `0093` | fixed 101 / 102-103 | 6D40 / 6E00 | place names: 48 field |
  | `C5:A4B5` / `A4CC` | fixed 28D / 28E (confirm, yes/no) | 7800 / 7900 | 112 popup (measured, table above) |
  | `C0:D938` / `C5:183B`,`1AE2` | fixed FF (価値) / 203 (音楽) | 6700 / 6D40 | 24 field each (measured, table above) |

  Triggers (2026-11-22, probes in `work/qa/probe/`; `tools/lua/steplog.lua` logs `$1244`/`$129E`/`$12A6`):
  - Event interpreter `C5:99E4` runs only from **mode 0A sub $0D** (`C0:E9B5`; mode table `C0:833F` entry 0B is a
    bare RTS, so poking `$34=0B` freezes). Command `$1244` (table `C5:9A07`); command 0 = `C5:9C29`, script at
    `[$12A6]` in bank C1 (set by `C0:EBFB`), step `$129E` (table `C5:9C31`; steps 4-$0F read the script and show
    dialogue, $10-$17 build the squad formation screen, $18 = pick, Start -> $1F confirm, $20 window #12).
    Poking `$34=0A,$36=0D,$1244=0,$129E=10` from the field reaches it (scenes `squad_form`, `confirm_prompt`).
  - FF 価値: mode 0C (`C0:D7A7`, sub table `C0:D7AE`) is the **shop**. Sub 0 copies the shop record from SRAM
    `$30:608A` (`C5:8CEE`), so a poked `$1446` is overwritten: poke `$122E` (shop type; 0 = medicine seller 28C)
    one frame after `$34=0C,$36=0` instead (scene `shop`). Sub 3 (`C0:D8ED`) draws 価値.
  - 203 音楽: battle menu state `$1516` (jump table `C5:000A`): 6 = `C5:1801`, 7 = `C5:1AAA` both draw it; poke
    `$1516=6,$1518=0` at the command column (scene `battle_music`). Which unit's command opens it is not mapped.
  - Mode 2 (`C0:8B34`, title idle ~f3380) is the history demo: ids 290-296, two lines over the city; the marker
    fills each line to the Japanese 14 glyphs so no cut is visible (dialogue renderer, linted at 176).
    Palace ids 297-2A5 are not in the demo, nor in New Game (mode 0A goes prologue -> 2A7 town).
  | `C0:921E` | 0 (blank slot) | 6C00+ | slot list, 48 |

## Not table text (stays Japanese in the marker build)
- Battle command labels こうげき / じゅつ (`marker_warp/battle_cmd_attack`, `battle_jutsu_list`): not in the table;
  look for tilemap words or `LDA #tile` chains (graphics survey G-list).
- Status labels 攻 防 技 術 速 体力 経験 装備, help/controls screen, captions: graphics (`graphics.md`).
