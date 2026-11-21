# Engine hooks (asm/main.asm)

Assembled by `build.py` with `tools/asar/asar.exe` (asar 1.91, github.com/RPGHacker/asar, gitignored; `--fix-checksum=off
--no-title-check`, the title is half-width katakana). Code, font and widths live in `$DF:0000-7FFF`; strings and
`PTRS` in `$D8-$DE` (`tools/insert.py`). All hooks enter with M=16, X=16 and leave DB alone. Checked by
`tests/test_insert.py::test_hooks_assembled`.

| Hook | Original | New | Why |
|---|---|---|---|
| `C1:7270` | `LDA $C30000,x` + C3/C6 bank pick by id | `TextPtr`: `PTRS[id]` -> `$00/$02`, back to `C1:728F` | dialogue reader, 24-bit pointers |
| `C1:74F1` | `LDA $C30000,x` / `LDA #$C3` | `NamePtr` -> `$04/$06`, back to `C1:74FC` | `{name}` reader |
| `C1:754D` | `LDA $C30000,x` / `LDA #$C3` | `MenuPtr` -> `$0E/$10`, zero `$1426`, back to `C1:7558` | renderer 2 (menu strings) |
| `C1:7537` | `ADC #$02E1` | `ADC #$0430` | `{num}` digits as English codes |
| `C1:73A5` | `LDA $C1F2F4,x` (glyph address) | `VwfMain`: code >= $400 -> VWF into `$7F:A000`, then the original upload at `C1:7491` | dialogue VWF |
| `C1:75B8` | `LDA $C1F2F4,x` | `VwfMenu`: code >= $400 -> VWF into `[$20]`, back to `C1:7558`; `{small}` ($401) / `{sbr}` ($40A) switch to two 8-px lines | renderer 2 VWF |
| `C1:7564` | upload size = glyph count x 12 px | `MenuEnd`: size from the VWF pixel width (small mode: the wider line; Japanese strings keep the old formula) | renderer 2 |

## Party list (verified: `work/qa/party/menu_items`, `menu_squad`, `menu_status`)
| Site | Original | New |
|---|---|---|
| `C1:2C04`, `C1:32AE`, `C1:3327` | `JSL $C1753B` (one name slot) | `JSL PartyName` |
| `C1:2C0D`, `C1:32B7`, `C1:3360` | buffer step `ADC #$0030` | `$0050` (5 tiles) |
| `C1:A3CB` / `C1:A3DB` | slot VRAM $7200 + 3 tiles per slot (2 rows of 16) | $7200 + n * $28 (5 tiles; panel B +$200) |
| `C8:939E`, `C8:9450` (compressed tilemaps) | 3 tiles per slot, two rows | 5 tiles in one row (`tools/gfx_edits.py`, applied by build.py) |
- `PartyName` papers the slot's 5 buffer tiles, sets `PARTY` (`$7E:1CF0`), calls the renderer, clears it. With
  `PARTY` set, `VwfMenu` draws every English glyph in the narrow font into the top half-row and drops glyphs past
  40 px; control codes (`{small}` `{narrow}` `{sbr}`) draw nothing; `MenuEnd` queues one DMA of the 5 top tiles
  (the original's bottom half-row DMA would land on another slot's tiles). A Japanese name (an untranslated build)
  shows only its top half.
- Free WRAM: `$7E:1B25-1CFF` was never written non-zero in 18 warp scenes (`tools/lua/wramuse.lua`); `PARTY` at
  `$1CF0`, `NARROWF` at `$1CF2`.

## Small mode (renderer 2, verified: `work/qa/stress_small`, `marker_warp/menu_status`)
- `{small}` clears both half-rows of `[$20]` (16 tiles each) to paper and sets `$1426 = $8000`; glyphs then come
  from `FONT8` (8 rows, `VwfDraw8`) into the top half-row; `{sbr}` keeps line 1's width in bits 8-13 and sets bit
  14, so line 2 goes into the bottom half-row (`+$400`). `MenuEnd` uploads max(line 1, line 2) tiles.
- `{narrow}` ($402) starts the same mode with `NARROWF` set: glyphs from `FONTN` / `WIDTHSN` (`Width8`,
  `VwfDraw8`); `MenuPtr` clears `NARROWF` at every string start.
- The dialogue (`VwfMain`) skips `{small}` and `{narrow}` and draws `{sbr}` as a space (GlyphIndex maps codes < $420
  to glyph 0).

## VWF (verified in-game: marker build, `work/qa/marker_newgame`)
- English code = `0x400 + ASCII` (`tbl/en.tbl`); font `fonts/en16.png` (8x16 cells, 1bpp, advance = ink + 1 px,
  space 4 px; `tools/font_en.py`), ink colour 3 on the game's colour-2 paper (bp1 = `FF` in every row).
- Dialogue line buffer: 22 tiles (176 px) per line, top half-row at line base, bottom half-row +`0x160`; lines at
  `$1422` = 0, `0x2C0`, `0x580`; the page-wait arrow is a Japanese glyph drawn at `0x6C0` (line 3, x 160-175).
  `$1426` now holds the pixel x in the line (the original kept a glyph count there for its 12-px pairs; every line
  start zeroes it). `$1422` = line base + tile of x.
- Renderer 2 (one call draws a whole string into `[$20]`, bottom half-row +`0x400`, then two DMAs, the bottom one
  0x100 bytes after the top in VRAM): at most 16 tiles (128 px) before the bottom row is overwritten.
- A glyph whose end passes the line end is dropped, not drawn (no wrap in the engine; the lint keeps lines inside).
- Japanese codes (< $400) still take the original 12-px path, so untranslated lines keep working.
