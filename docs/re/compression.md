# Graphics compression and load tables (verified)

## Codec: `C1:05CF` (JSL), source `[$00]` 24-bit, destination `[$04]` 24-bit (direct page)
Block = type byte, 16-bit LE output size, payload. `tools/kss_comp.py` decodes all three types (checked on every
block the game loaded in `work/qa/dec_*`: each decoded block ends exactly where the next begins).

| type | routine | format |
|---|---|---|
| 0 | `C1:0724` | raw copy of `size` bytes |
| 1 | `C1:05E6` | LZ. 16-bit flag words, LSB first; flag word 0 with ≥16 bytes left = 16 literals. Bit 0 = literal byte; bit 1 = word `w`: copy `(w>>11)+3` bytes from `out[pos-(w&0x7FF)-1]` |
| 2 | `C1:074F` | word RLE (tilemaps). Odd size: one extra byte follows the header (last output byte). Command byte `c`: `c>>6` 0 = `n+1` literal words, 1 = one word `n+2` times, 2 = incrementing word `n+2` times, 3 = decrementing `n+2` times (`n = c&0x3F`) |

An encoder is not written yet (phase 3/5). Blocks are packed back to back; a re-encoded block that grows must move
to free space and have its pointer changed in the load tables below (or the code that names it).

## Where blocks live (`tools/kss_blocks.py`, list in `work/re/blocks.tsv`)
- C8 (file 0x80000-0x8DF9E): title, file select, menus, small font, battle UI, ending/credits art, tilemaps. All
  graphics text is here.
- C4 0x49F08-0x4DE54: non-tile data (map data), loaded to `7F:4000`.
- C7 0x70000-0x7779F: field tiles + other formats; CB 0xB0000-0xBBA3C: field tiles; D1, D4, D5 (whole banks):
  character/enemy sprites; D7 0x170000-0x174B55 backgrounds, rest map data.
- Raw (uncompressed) graphics: CA portraits, CC-CD sprites, CE-CF effect art, D0 sprites + damage digits, D3
  sprites, D6 spell effects. D2 and C2 are not tile data.

## Load tables (bank C1)
- **Table B** `C1:EFA1`, 45 records × 10 bytes: src24, WRAM dest24, VRAM word address, length. Loaded by id with
  `JSL C101D7` / `C101DD` (`A` = id; routine `C1:01E3`). Text-bearing ids: 8 (`C8:B282`), 12 (`C8:C2F8`, called
  from bank CB code), 33-36 (`C8:ABF2`), 43 (`C8:D140`), 6 (`C8:3E4F`, file select), 15 (`C8:8954`, small font; id = (record - 0x1EFA1) / 10).
- **Table A** `C1:EDFD`, 42 records × 10 bytes, to WRAM `$7E`, then DMA (`C1:0196`; `JSL C10190` / `C1018A`).
  Mostly type-2 tilemaps.
- Many other callers set `$00-$06` themselves (40+ `JSL C105CF` sites).
- Logged at run time with `tools/lua/declog.lua` (one line per distinct source/destination).
