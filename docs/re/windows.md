# Window data: measured text budgets (phase 5 width gate)

Measured on the marker build (`python -X utf8 build.py marker`, VWF font `fonts/en16.png`) from pixels in emulator
shots, not from the Japanese length. px = English VWF pixels (`tools/font_en.py text_px`). "measured" names the shot.

| Variant | Renderer | Budget | Lines | State |
|---|---|---|---|---|
| Dialogue box (field, events, portrait or not) | dialogue `C1:7270` | 176 px per line | 3 per page | measured: `work/qa/torture2` f4700 (22 x `M` = 176 px shows whole; 185-px line loses its last glyphs) |
| Dialogue, the line before `{page}` | dialogue | 160 px | - | measured: torture f4100 (the ▼ arrow is a Japanese glyph drawn at x 160-175 of line 3 and erases text under it when it blinks off). Applies to line 3 only; lines 1-2 keep 176 |
| Battle turn message (`{name}のばんです`, id 205) | dialogue | 176 px | 1 | measured: `marker_warp/battle_turn_msg` (box is wider than the buffer; cut at 176 by the VWF) |
| Battle help prompt (id 0B8) | dialogue | 176 px | 1 | measured: `marker_warp/battle_help_prompt` (128-px marker shows whole); box ~200 px, buffer 176 |
| Menu popup (id 28B in items/shikigami, id 243 save message) | ? (cut at a tile edge) | 112 px (14 tiles) | 1 | measured: `marker_warp/menu_items`, `save_message` (`n` after "brow" cut at x 112) |
| Item / jutsu / shikigami names in menu grids and the battle jutsu list | renderer 2 `C1:753B` | 48 px (6 tiles) | 1 | measured: `marker_warp/menu_items` z_field (the `e` of "[000] The" cut at x 48). Longer names overflow into the next field's tiles (garbled rows in the shot) |
| Status screen equipment / name fields | renderer 2 | 48 px (6 tiles) | 1 | measured: `marker_warp/menu_status` ("[0B9] The" cut like the item grid) |

## Not measured yet (next session)
- Squad list (`menu_squad`), name plates under portraits and in the party list, province card `{name}の闘い`
  (`card_p*`, the shot came before the card showed), overworld labels, ending/credits (graphics, phase 8).
- Renderer-2 fields at 48 px fit ~7 letters: engine work (D4) before translation: a narrow second font for renderer 2
  (e.g. Pixel Operator 8 / a 4-px-advance font), and/or wider fields (tilemap layout and tile reserve per field).
  Find the tile reserve per field (caller of `C1:753B`: VRAM `$0C`, tilemap) before choosing.

## Not table text (stays Japanese in the marker build)
- Battle command labels こうげき / じゅつ (`marker_warp/battle_cmd_attack`, `battle_jutsu_list`): not in the table;
  look for tilemap words or `LDA #tile` chains (graphics survey G-list).
- Status labels 攻 防 技 術 速 体力 経験 装備, help/controls screen, captions: graphics (`graphics.md`).
