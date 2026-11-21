"""English in the 8x16 small font (graphics.md G5) and the small-font tilemap text T1-T5 (script/tilemaps.tsv).

The font block C8:8954 (file 0x88954, BG3 VRAM $6000) draws one character as a top tile t and a bottom tile
t + 0x10 (tools/smallfont.py). The kana cells (CELLS) get English glyphs taken from the dialogue font
(fonts/en16.png, so menus and dialogue share letter shapes), centred in the 8-px cell and moved down SHIFT px so
the baseline sits near the original digits'. Paper is colour 2, ink colour 3, as in the original glyphs. Digits
(0x10-0x19), the cursor and X Y A B L R (0xB9-0xBF) and the stat kanji (0xD0+) are kept.

The tilemaps then spell the English with those cells: the 6 menu captions (raw words at C1:9E8B.., one 18-cell
line each), and the save menu, options, quit and saved maps (LZ/RLE blocks, tools/tilemap_text.BLOCKS). A row is
written over its first N cells, N from the row's `max` budget ("10 cells", "8 cells + values"); the rest of the row
(the option value arrows) is kept.

    python -X utf8 tools/smallfont_en.py preview OUT.png    every redrawn cell, x4
"""
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import font_en  # noqa: E402
import kss_script  # noqa: E402
import tilemap_text  # noqa: E402

FONT_BLOCK = "088954.bin"
CELLS = [*range(0x30, 0x40), *range(0x50, 0x60), *range(0x70, 0x80), *range(0x90, 0xA0), *range(0xB0, 0xB9)]
CHARSET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.,'!?-:()/&"
CELL = {**dict(zip(CHARSET, CELLS)), **{str(d): 0x10 + d for d in range(10)}}
BLANK = 0x2001                  # the maps' own blank word (tile 1 is empty)
MAP_BLANK = {"yesno": 0x200E}   # the Yes/No box's blank is its window fill, tile 0x0E
SHIFT = 2
PAPER, INK = 2, 3
CAPTION_PTRS, CAPTION_WIDTH = tilemap_text.CAPTIONS, 18
assert len(CHARSET) <= len(CELLS)


def glyph_rows(ch):
    """16 rows of 8 px (bit 7 = left) for `ch`, centred in the cell, SHIFT px down."""
    rows = font_en.glyphs()[ord(ch) - font_en.FIRST][0]
    ink = [x for x in range(8) if any(r & (0x80 >> x) for r in rows)]
    dx = (8 - (ink[-1] - ink[0] + 1)) // 2 - ink[0] if ink else 0
    rows = [(r >> dx if dx >= 0 else r << -dx) & 0xFF for r in rows]
    return [0] * SHIFT + rows[:16 - SHIFT]


def tile_2bpp(rows8):
    """8 rows of ink masks -> 16 bytes of 2bpp: paper colour 2, ink colour 3."""
    out = bytearray()
    for m in rows8:
        out += bytes([(m if INK & 1 else 0) | (~m & 0xFF if PAPER & 1 else 0),
                      (m if INK & 2 else 0) | (~m & 0xFF if PAPER & 2 else 0)])
    return bytes(out)


def redraw_font(data):
    """The font block with English glyphs in CELLS and the status labels in LABELS."""
    out = bytearray(data)
    for ch in CHARSET:
        t, rows = CELL[ch], glyph_rows(ch)
        out[t * 16:t * 16 + 16] = tile_2bpp(rows[:8])
        out[(t + 0x10) * 16:(t + 0x10) * 16 + 16] = tile_2bpp(rows[8:])
    for top, bottom, text in LABELS:
        px = label_pixels(text, 8 * len(top))
        for k, (t, b) in enumerate(zip(top, bottom)):
            out[t * 16:t * 16 + 16] = tile_4col([row[8 * k:8 * k + 8] for row in px[:8]])
            out[b * 16:b * 16 + 16] = tile_4col([row[8 * k:8 * k + 8] for row in px[8:]])
    return bytes(out)


# Status-screen labels (graphics.md T6, decision D16): 16x16 kanji cells, ink 3 with a colour-1 shadow on paper 2,
# as the kanji. (top tiles, bottom tiles, English). 体力 経験 装備 are two cells (32 px), the rest one (16 px).
def _pair(t, below):
    return [t, t + 1], [t + below, t + below + 1]


LABELS = [
    ([0xD0, 0xD1, 0xD2, 0xD3], [0xE0, 0xE1, 0xE2, 0xE3], "Vit."),   # 体力
    ([0xD4, 0xD5, 0xD6, 0xD7], [0xE4, 0xE5, 0xE6, 0xE7], "Exp."),   # 経験
    ([0xD8, 0xD9, 0xDA, 0xDB], [0xE8, 0xE9, 0xEA, 0xEB], "Equip"),  # 装備
    (*_pair(0xDC, 0x10), "Atk"),                                    # 攻
    (*_pair(0xDE, 0x10), "Def"),                                    # 防
    (*_pair(0xF0, 2), "Skl"),                                       # 技
    (*_pair(0xF4, 2), "Jut"),                                       # 術
    (*_pair(0xF8, 2), "Spd"),                                       # 速
]


def label_pixels(text, width):
    """16 rows x `width` colour indices: the dialogue-font text centred (letter gaps squeezed if it is too wide),
    ink 3, shadow 1 right and below, paper 2."""
    gl = [font_en.glyphs()[ord(c) - font_en.FIRST][0] for c in text]
    cols = []                       # per letter: list of 16-bit column masks (bit y = row y)
    for rows in gl:
        ink = [x for x in range(8) if any(r & (0x80 >> x) for r in rows)]
        cols.append([sum(1 << y for y in range(16) if rows[y] & (0x80 >> x)) for x in range(ink[0], ink[-1] + 1)]
                    if ink else [0, 0, 0])
    gaps = [1] * (len(cols) - 1)
    total = lambda: sum(map(len, cols)) + sum(gaps) + 1    # noqa: E731 - + 1 for the shadow
    k = 0
    while total() > width and k < len(gaps):
        gaps[k], k = 0, k + 1
    if total() > width:
        raise ValueError("label %r: %d px > %d" % (text, total(), width))
    x = (width - total()) // 2
    mask = [0] * width
    for i, c in enumerate(cols):
        for m in c:
            mask[x] = m
            x += 1
        x += gaps[i] if i < len(gaps) else 0
    px = [[PAPER] * width for _ in range(16)]
    for x in range(width):
        for y in range(16):
            yy = y - 1                       # one row down: capitals on rows 4-12, descenders to 14
            if 0 <= yy < 16 and mask[x] >> yy & 1:
                px[y][x] = INK
    for y in range(15, -1, -1):
        for x in range(width - 1, -1, -1):
            if px[y][x] == PAPER and ((x and px[y][x - 1] == INK) or (y and px[y - 1][x] == INK)):
                px[y][x] = 1
    return px


def tile_4col(rows8):
    """8 rows of 8 colour indices (0-3) -> 16 bytes of 2bpp."""
    out = bytearray()
    for row in rows8:
        lo = sum(((c & 1) << (7 - x)) for x, c in enumerate(row))
        hi = sum((((c >> 1) & 1) << (7 - x)) for x, c in enumerate(row))
        out += bytes([lo, hi])
    return bytes(out)


def cells_of(text):
    bad = sorted({c for c in text if c != " " and c not in CELL})
    if bad:
        raise ValueError("small font has no %s" % "".join(bad))
    return [CELL.get(c) for c in text]


def budget(row):
    return int(row["max"].split()[0].split("x")[0])


def write_row(words, width, r, text, n, col=0, blank=BLANK):
    """Spell `text` over n cells from column `col` of row pair r (top row r, bottom row r + 1) of a `width`-word
    map; cells past the text get `blank`."""
    cells = cells_of(text)
    if len(cells) > n:
        raise ValueError("%r: %d cells > %d" % (text, len(cells), n))
    attr = next(w & 0xFC00 for w in words[r * width:(r + 1) * width] if w & 0x3FF)
    for i in range(n):
        c = cells[i] if i < len(cells) else None
        words[r * width + col + i] = blank if c is None else attr | c
        words[(r + 1) * width + col + i] = blank if c is None else attr | (c + 0x10)


def rows_by_id(script_dir=None):
    return {r["id"]: r for r in kss_script.read_tsv(Path(script_dir or kss_script.SCRIPT) / "tilemaps.tsv")}


def apply_blocks(gfxdir, script_dir=None):
    """Redraw the font block and rewrite the T2-T5 maps in an unpacked gfx dir (build.py, after unpack)."""
    gfxdir, rows = Path(gfxdir), rows_by_id(script_dir)
    p = gfxdir / FONT_BLOCK
    p.write_bytes(redraw_font(p.read_bytes()))
    for prefix, off, width, _ in tilemap_text.BLOCKS:
        p = gfxdir / ("%06X.bin" % off)
        data = p.read_bytes()
        words = list(struct.unpack("<%dH" % (len(data) // 2), data))
        cols = tilemap_text.span(prefix, width)
        col = cols[0]
        for n, (r, _, _) in enumerate(list(tilemap_text.pairs(words, width, 0, cols))):
            row = rows["%s%d" % (prefix, n)]
            if row["en"]:
                write_row(words, width, r, row["en"], budget(row), col, MAP_BLANK.get(prefix, BLANK))
        p.write_bytes(struct.pack("<%dH" % len(words), *words))


def caption_writes(rom, script_dir=None):
    """[(file offset, bytes)] for the 6 field-menu captions (T1), raw words in bank C1."""
    rows, out = rows_by_id(script_dir), []
    for k, ptr in enumerate(struct.unpack_from("<6H", rom, CAPTION_PTRS)):
        row = rows["caption%d" % k]
        if not row["en"]:
            continue
        off = 0x10000 + ptr
        words = list(struct.unpack_from("<%dH" % (2 * CAPTION_WIDTH), rom, off))
        write_row(words, CAPTION_WIDTH, 0, row["en"], budget(row))
        out.append((off, struct.pack("<%dH" % len(words), *words)))
    return out


def preview(path):
    from PIL import Image
    img = Image.new("RGB", (len(CHARSET) * 9, 16), (60, 0, 0))
    for i, ch in enumerate(CHARSET):
        for y, m in enumerate(glyph_rows(ch)):
            for x in range(8):
                if m & (0x80 >> x):
                    img.putpixel((i * 9 + x, y), (255, 255, 255))
    img.resize((img.width * 4, img.height * 4), Image.NEAREST).save(path)
    print("wrote", path)


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "preview":
        preview(sys.argv[2])
    else:
        print(__doc__)
