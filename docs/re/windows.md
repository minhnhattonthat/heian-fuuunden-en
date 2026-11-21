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
| Menu popup (id 28B in items/shikigami, id 243 save message) | renderer 2 (`C0:A93A`, VRAM 7000) | 112 px (14 tiles) | 1 | measured: `marker_warp/menu_items`, `save_message` (`n` after "brow" cut at x 112) |
| Item grid (ids 001-053 + 000 blank) | renderer 2 `C1:2D13`, VRAM 7600/7650/7700.. | 48 px (6 tiles) | 1 big or 2 small | measured: `stress_small/menu_items` (`--qa 000=...`: "0123456" / "abcdefg" in 8 px show whole, 48 px) |
| Status screen class / name / equipment (0F3.., 0B9-0F2, items) | renderer 2 `C1:29D9`, VRAM 7000/7050/7100/7150 | 48 px (6 tiles) | 1 big or 2 small | measured: `marker_warp/menu_status` (small two-line markers whole) |
| Party list names under the portraits (ids 054-083) | renderer 2 via `PartyName` (callers `C1:2C04`, `C1:32AE`, `C1:3327`), VRAM table `C1:A3CB` (`C1:A3DB` = +$200 when `$10CC`) | **40 px (5 tiles), narrow 8-px font, always** | 1 | measured: `work/qa/party/menu_items`, `menu_squad`, `menu_status` (`build.py marker --qa 054=Sadamitsu --qa 100=Yasumasa`: all 8 slots whole). Room per slot: x 32-71 (own portrait ends x 32, next starts x 72). Original: 3 tiles (24 px) of 16-px text; widened in the engine (D11, hooks.md §Party list) |
| Battle jutsu list (ids 13C-181) | renderer 2 `C5:0D03`.. (5 rows), VRAM 6D40/6E00/6E40.. (8 tiles each) | 48 px | 1 big or 2 small | measured: `marker_warp/battle_jutsu_list` (small lines whole; the cost digit sits at x 48) |
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

## Not measured yet (next session)
- Squad exchange screen (`C0:B9A5` -> `C1:32C8`, `C0:EF6F` -> `C1:3267`: two panels, panel B = tiles $280-$2BF,
  VRAM $7400): same `PartyName` slots, so 40 px; not reached by any warp scene (needs two squads), panel B's
  tilemap checked by `tests/test_insert.py::test_party_tilemaps` only. Province card `{name}の闘い` (id 1B9,
  dialogue path, linted at 176 px; the `card_p*` hold shot comes after the card is gone: shoot it mid-card with
  `SHOTS_AFTER`), ending/credits (graphics, phase 8).
- Opening palace scene, ids 29B-2A5: a speaker line + 3 lines per page (6 pages have 4 `{br}`-lines). Not reached by
  mashing from the prologue (scene `opening` goes prologue -> 2A7 town); find its trigger. Linted as dialogue
  (3 lines): the speaker line needs handling before phase 6 translates those rows.
- Renderer-2 callers resolved from the code before each `JSL $C1753B` (static, not shot). Budgets live in
  `insert.FIELDS` / `tools/lint.py POPUPS`; "(guess)" in the `max` column until shot.
  | Caller | id | VRAM | Budget |
  |---|---|---|---|
  | `C1:6011` | `$101E` + $54 (party names) | table `C1:E6CE` | 48 field (names fall back to `{narrow}`); screen unknown, shoot it |
  | `C1:2E0E` / `C1:57C0` | + $13F jutsu / + $181 shikigami | table `C1:A3EB` | 48 field (guess) |
  | `C5:1281` / `C5:206A` | `$09EE,x` + $C2 or $12D / + $53 | 6E00 / 6D40 | ids in 001-0FE: 48 field |
  | `C5:12FF`, `C5:132A` | `C1:8785` + $1A7 (shikigami) | 6E40 / 6F00 | 48 field |
  | `C5:0064` / `0093` | fixed 101 / 102-103 | 6D40 / 6E00 | place names: 48 field |
  | `C0:A8DE` / `A8F5` | fixed 1C8 / 1C9 (item full, can't equip) | 7E00 / 7F00 | 112 popup (guess) |
  | `C0:AF62` | fixed 244 (quit message) | 7000, as 243 | 112 popup (guess; scene `quit_nosave`) |
  | `C5:A4B5` / `A4CC` | fixed 28D / 28E (confirm, yes/no) | 7800 / 7900 | 112 popup (guess) |
  | `C0:D938` / `C5:183B`,`1AE2` | fixed FF (価値) / 203 (音楽) | 6700 / 6D40 | 48 (guess) |
  | `C0:921E` | 0 (blank slot) | 6C00+ | slot list, 48 |

## Not table text (stays Japanese in the marker build)
- Battle command labels こうげき / じゅつ (`marker_warp/battle_cmd_attack`, `battle_jutsu_list`): not in the table;
  look for tilemap words or `LDA #tile` chains (graphics survey G-list).
- Status labels 攻 防 技 術 速 体力 経験 装備, help/controls screen, captions: graphics (`graphics.md`).
