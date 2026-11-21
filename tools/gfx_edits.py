"""Edits to unpacked graphics/tilemap blocks, applied by build.py between unpack and repack.

Party list (docs/re/windows.md, party list row): the original gives each of the 8 name slots 3 tiles (24 px) of
16-px text: slots 0-4 in tiles base+0..14, slots 5-7 in base+$20.., bottom halves at + $10. English names are drawn
there in the narrow 8-px font on one tile row (asm/main.asm `PartyName`), 5 tiles (40 px) per slot: the room
between the slot's own portrait (ends x 32) and the next one (starts x 72). Both panels' tilemaps (C8:939E tiles
$240-$27F, C8:9450 tiles $280-$2BF; the game flips between them with $10CC) then place slot n at tiles base + 5n
.. + 4 in columns 4-8, 11-15, 18-22, 25-29 of tile row 4 (slots 0-3) or 8 (slots 4-7); the row under it is blank.
The slot table `C1:A3CB` (asm) gives the same VRAM addresses: $7200 + n * $28 (+ $200 for panel B).
The squad formation screen loads the same panels plus a third, C8:9506 (tiles $2C0-$2FF, same layout); its slot
table `C1:E6CE` (asm) is widened the same way: 0-3 at $7200.., 4-11 at $7400.., 12-19 at $7600 + n * $28.
"""
import struct
from pathlib import Path

PARTY_PANELS = {"08939E.bin": 0x240, "089450.bin": 0x280, "089506.bin": 0x2C0}
PARTY_ROWS = (4, 8)          # tile row of each slot row (the original's top half-row)
PARTY_COLS = (5, 12, 19, 26)  # the original name columns; the new slots start one column left
SLOT_TILES = 5


def party_slot_tiles(base, n):
    return [base + SLOT_TILES * n + k for k in range(SLOT_TILES)]


def widen_party(data, base):
    """Return the panel tilemap with 5-tile one-row name slots. Checks the original 3-tile layout first."""
    w = list(struct.unpack("<%dH" % (len(data) // 2), data))
    old = [(base + 3 * n) if n < 5 else (base + 0x20 + 3 * (n - 5)) for n in range(8)]
    for n in range(8):
        r, c = PARTY_ROWS[n // 4], PARTY_COLS[n % 4]
        top, bot = r * 32 + c, (r + 1) * 32 + c
        for i, want in ((top, old[n]), (bot, old[n] + 0x10)):
            got = [x & 0x3FF for x in w[i:i + 3]]
            if got != [want, want + 1, want + 2]:
                raise ValueError("party tilemap: word %d holds %s, expected %03X.." % (i, got, want))
            if (w[i - 1] & 0x3FF) or (w[i + 3] & 0x3FF):
                raise ValueError("party tilemap: the columns beside word %d are not blank" % i)
        attr = w[top] & 0xFC00
        for k, t in enumerate(party_slot_tiles(base, n)):
            w[top - 1 + k] = attr | t
        for k in range(3):
            w[bot + k] = w[bot + k] & 0xFC00          # tile 0: blank
    return struct.pack("<%dH" % len(w), *w)


def apply(gfxdir):
    gfxdir = Path(gfxdir)
    for name, base in PARTY_PANELS.items():
        p = gfxdir / name
        p.write_bytes(widen_party(p.read_bytes(), base))
