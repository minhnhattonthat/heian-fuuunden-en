"""English VWF fonts: 16-px for dialogue and menus, 8-px for two-line names in menu fields (phase 5).

    python -X utf8 tools/font_en.py render TTF [--small]   TTF -> fonts/en16.png (Pixel Operator, 16 px) or
                                                            fonts/en8.png (--small: Pixel Operator 8, 8 px)
    python -X utf8 tools/font_en.py build          sheets -> build/gen/font_en.bin + widths (used by build.py)
    python -X utf8 tools/font_en.py preview TEXT OUT.png [--small]   draw TEXT with the VWF metrics (x3)

Sheet layout: 16 columns x 6 rows of 8xH cells (H = 16 or 8) for ASCII 0x20-0x7F (0x7F unused). Black = ink,
white = paper. The advance of a glyph is its rightmost ink column + 2 (1 px gap); the space is 4 px (3 px small);
a red pixel in row 0 of a cell overrides the advance (its x + 1). Game code = 0x400 + ASCII (`tbl/en.tbl`). Ink
is colour 3 on the game's colour-2 paper (`docs/re/hooks.md` §VWF).

build/gen: font_en.bin (16 bytes per glyph) + font_en_w.bin (0x60 widths), font_en8.bin (8 bytes per glyph) +
font_en8_w.bin, font_enn.bin + font_enn_w.bin (narrow 8 px, fonts/en_narrow.png from tools/font_narrow.py);
asm/main.asm places FONT8 and FONTN right after FONT (VwfDraw8 indexes them as FONT + $600 / + $900).
`preview ... --narrow` draws with the narrow font.
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
SHEET = ROOT / "fonts" / "en16.png"
SHEET8 = ROOT / "fonts" / "en8.png"
SHEETN = ROOT / "fonts" / "en_narrow.png"
GEN = ROOT / "build" / "gen"
FIRST, COUNT = 0x20, 0x60
CELL_W = 8


def _spec(small):
    """small: False = 16 px, True = 8 px (Pixel Operator 8), "narrow" = 8 px with 3-px letters
    (fonts/en_narrow.png, drawn by tools/font_narrow.py). Returns sheet, cell height, space width."""
    if small == "narrow":
        return SHEETN, 8, 3
    return (SHEET8, 8, 3) if small else (SHEET, 16, 4)


def render(ttf, small=False):
    sheet, cell_h, _ = _spec(small)
    font = ImageFont.truetype(ttf, cell_h)
    img = Image.new("RGB", (16 * CELL_W, 6 * cell_h), "white")
    for i in range(COUNT - 1):
        ch = chr(FIRST + i)
        cell = Image.new("L", (16, 24), 255)
        ImageDraw.Draw(cell).text((-1, -1) if not small else (0, 0), ch, font=font, fill=0)
        cell = cell.point(lambda v: 0 if v < 128 else 255)
        x0, y0 = (i % 16) * CELL_W, (i // 16) * cell_h
        for y in range(cell_h):
            for x in range(CELL_W):
                if cell.getpixel((x, y)) == 0:
                    img.putpixel((x0 + x, y0 + y), (0, 0, 0))
        if any(cell.getpixel((x, y)) == 0 for x in range(CELL_W, 16) for y in range(24)) or \
                any(cell.getpixel((x, y)) == 0 for x in range(16) for y in range(cell_h, 24)):
            print("warning: %r does not fit the %dx%d cell" % (ch, CELL_W, cell_h))
    sheet.parent.mkdir(exist_ok=True)
    img.save(sheet)
    print("wrote", sheet)


def glyphs(small=False):
    """[(rows[H] as ints, bit 7 = leftmost px), advance)] for codes 0x20.."""
    sheet, cell_h, space = _spec(small)
    img = Image.open(sheet).convert("RGB")
    out = []
    for i in range(COUNT):
        x0, y0 = (i % 16) * CELL_W, (i // 16) * cell_h
        rows, right, adv = [], -1, None
        for y in range(cell_h):
            v = 0
            for x in range(CELL_W):
                p = img.getpixel((x0 + x, y0 + y))
                if p == (255, 0, 0) and y == 0:
                    adv = x + 1
                    continue
                if sum(p) < 384:
                    v |= 0x80 >> x
                    right = max(right, x)
            rows.append(v)
        if adv is None:
            adv = space if right < 0 else right + 2
        out.append((rows, adv))
    return out


def widths(small=False):
    return {chr(FIRST + i): adv for i, (_, adv) in enumerate(glyphs(small))}


_W = {}


def text_px(text, small=False):
    if small not in _W:
        _W[small] = widths(small)
    return sum(_W[small].get(c, 0) for c in text)


def build(gen=GEN):
    gen.mkdir(parents=True, exist_ok=True)
    big, small, narrow = glyphs(), glyphs(True), glyphs("narrow")
    out = []
    for name, gl in (("font_en", big), ("font_en8", small), ("font_enn", narrow)):
        (gen / (name + ".bin")).write_bytes(bytes(b for rows, _ in gl for b in rows))
        (gen / (name + "_w.bin")).write_bytes(bytes(adv for _, adv in gl))
        out += [gen / (name + ".bin"), gen / (name + "_w.bin")]
    return out


def preview(text, out, small=False):
    gl = glyphs(small)
    cell_h = _spec(small)[1]
    w = sum(gl[ord(c) - FIRST][1] for c in text) + 8
    img = Image.new("RGB", (w, cell_h), (200, 190, 150))
    x = 0
    for c in text:
        rows, adv = gl[ord(c) - FIRST]
        for y, v in enumerate(rows):
            for b in range(8):
                if v & (0x80 >> b):
                    img.putpixel((x + b, y), (40, 30, 20))
        x += adv
    img.resize((w * 3, cell_h * 3), Image.NEAREST).save(out)
    print("%s: %d px" % (out, x))


if __name__ == "__main__":
    cmd, small = sys.argv[1], "narrow" if "--narrow" in sys.argv else "--small" in sys.argv
    args = [a for a in sys.argv[2:] if a not in ("--small", "--narrow")]
    if cmd == "render":
        render(args[0], small)
    elif cmd == "build":
        print(build())
    elif cmd == "preview":
        preview(args[0], args[1], small)
