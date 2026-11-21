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

## Small mode (two 8-px lines in one 16-px field)
`tools/insert.py fit_field`: a name wider than its field in the 16-px font goes in as `{small}line 1{sbr}line 2`
(Pixel Operator 8, advance = ink + 1, space 3 px), split at the space that balances the lines; each line <= the
field. Then the same one or two lines in the narrow 8-px font (`{narrow}`, 3-px letters: "Sadamitsu" is 52 px
big, 61 small, 35 narrow). None fits = build error. Field budgets per id range: `insert.FIELDS`. The dialogue ignores `{small}` and
draws `{sbr}` as a space, so `{name}` in dialogue reads normally (verified: `marker_warp/battle_turn_msg`).

## Not measured yet (next session)
- Squad exchange screen (`C0:B9A5` -> `C1:32C8`, `C0:EF6F` -> `C1:3267`: two panels, panel B = tiles $280-$2BF,
  VRAM $7400): same `PartyName` slots, so 40 px; not reached by any warp scene (needs two squads), panel B's
  tilemap checked by `tests/test_insert.py::test_party_tilemaps` only. Province card `{name}の闘い` (`card_p*`:
  dialogue path, so 176 px; confirm in a later shot), ending/credits (graphics, phase 8).
- Renderer-2 callers never seen in a warp scene's r2 log (`JSL $C1753B` sites; id and VRAM from the code before the
  call). Each needs a scene and a shot before its strings get a budget:
  | Caller | id | VRAM | Guess |
  |---|---|---|---|
  | `C1:363A` | `$1088` + $100 (101-111 places) | 6110 | place name in a field/travel screen |
  | `C1:6910` | table `C1:E7..` + $117 (115-12C exits) | 6910 + 1 tile per index | map-exit direction labels |
  | `C1:6011` | `$101E` + $54 (party names) | table `C1:E6CE` | a second party-name screen (unit placement?) |
  | `C1:2E0E` | + $13F (jutsu) | - | jutsu list outside battle |
  | `C1:57C0` | + $181 (shikigami) | - | shikigami list outside battle |
  | `C1:36E6` | + $AB | 6910.. | ? |
  | `C5:1281` / `C5:206A` | + $C2 / + $53 | 6E00 / 6D40 | battle-side windows |
  | `C5:12FF`, `C5:132A` | + $1A7 | 6E40 / 6F00 | battle-side windows |
  | `C0:921E`, `C0:A8DE`/`A8F5`, `C0:AEED`/`B06C`, `C0:AF62`, `C0:D938`, `C5:0064`/`0093`, `C5:183B`/`1AE2`, `C5:A4B5`/`A4CC` | fixed ids 28F, 1C8/1C9, 243, 244, FF, 101-103, 203, 28D/28E | various | popups / one-off labels |
  Ports 1BD-1C4 are not reached through any of these (no immediate $1BD); look for a table-driven caller.

## Not table text (stays Japanese in the marker build)
- Battle command labels こうげき / じゅつ (`marker_warp/battle_cmd_attack`, `battle_jutsu_list`): not in the table;
  look for tilemap words or `LDA #tile` chains (graphics survey G-list).
- Status labels 攻 防 技 術 速 体力 経験 装備, help/controls screen, captions: graphics (`graphics.md`).
