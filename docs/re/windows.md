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
| Party list names under the portraits (ids 054-083) | renderer 2 `C1:2C04`, VRAM table `C1:A3CB` (and `C1:A3DB` when `$10CC`) | **24 px (3 tiles)** | 1 | measured: `stress_small/menu_items` (`--qa 054=0123456789..`: "012" whole, the rest spills into the next slot's tiles). Tilemap: BG3, tiles 240-24E / 250-25E per row pair, columns 5-7, 12-14, 19-21, 26-28 (compressed block `C8:939E`, gfx/blocks.tsv). Visual room per slot: 4 tiles (x 40-71, the next portrait starts at x 72) |
| Battle jutsu list (ids 13C-181) | renderer 2 `C5:0D03`.. (5 rows), VRAM 6D40/6E00/6E40.. (8 tiles each) | 48 px | 1 big or 2 small | measured: `marker_warp/battle_jutsu_list` (small lines whole; the cost digit sits at x 48) |
| Battle shikigami list (ids 182-1B2) | renderer 2 `C5:226F`.. | 48 px | 1 big or 2 small | measured: `marker_small/battle_shikigami_list` (same layout as the jutsu list) |
| Overworld squad label (ids 1B3-1B8) | renderer 2 `C1:4FF3`, VRAM 6B00 | 48 px (6 tiles) | 1 big or 2 small | measured: `marker_small/overworld` |
| Overworld province label (ids 24A-288) | renderer 2 `C1:5018`, VRAM 6B30 | 48 px (6 tiles) | 1 big or 2 small | measured: `marker_small/overworld` ("[26C] The" cut at 48; a wider string spills into the squad label's bottom row at 6B80) |

## Small mode (two 8-px lines in one 16-px field)
`tools/insert.py fit_field`: a name wider than its field in the 16-px font goes in as `{small}line 1{sbr}line 2`
(Pixel Operator 8, advance = ink + 1, space 3 px), split at the space that balances the lines; each line <= the
field. Neither fits = build error. Field budgets per id range: `insert.FIELDS`. The dialogue ignores `{small}` and
draws `{sbr}` as a space, so `{name}` in dialogue reads normally (verified: `marker_warp/battle_turn_msg`).

## Not measured yet (next session)
- Squad list (`menu_squad` shows the same party panel; the squad screen proper was not reached), province card
  `{name}の闘い` (`card_p*`: dialogue path, so 176 px; confirm in a later shot), ports 1BD-1C4 and places
  101-12C (field-map labels? not in any warp scene's r2 log), ending/credits (graphics, phase 8).
- The party list (24 px) is too narrow for English names (Kagura 36 px big / 42 px small). Engine options, in
  order: (1) 4 tiles per slot: 8 x 4 = 32 tiles = exactly VRAM rows 7200 + 7300; change the slot table `C1:A3CB`
  (+ `A3DB`, also read at `C1:3292`, `C1:330B`), the buffer step `ADC #$0030` at `C1:2C0C`, and the tilemap block
  `C8:939E` (4 tiles per slot); (2) a narrower 8-px font (3-px letters, 4-px advance) for this field so 8 letters
  fit 32 px. Both are needed for names like Hiroyuki / Moritaka.

## Not table text (stays Japanese in the marker build)
- Battle command labels こうげき / じゅつ (`marker_warp/battle_cmd_attack`, `battle_jutsu_list`): not in the table;
  look for tilemap words or `LDA #tile` chains (graphics survey G-list).
- Status labels 攻 防 技 術 速 体力 経験 装備, help/controls screen, captions: graphics (`graphics.md`).
