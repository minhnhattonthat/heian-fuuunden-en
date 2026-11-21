"""English VWF font for the 16-px dialogue and menu text (phase 5).

    python -X utf8 tools/font_en.py render TTF     TTF (Pixel Operator, CC0) -> fonts/en16.png (the editable source)
    python -X utf8 tools/font_en.py build          fonts/en16.png -> build/gen/font_en.bin + widths (used by build.py)
    python -X utf8 tools/font_en.py preview TEXT OUT.png   draw TEXT with the VWF metrics (x3), for checking

Sheet layout: 16 columns x 6 rows of 8x16 cells for ASCII 0x20-0x7F (0x7F unused). Black = ink, white = paper.
The advance width of a glyph is its rightmost ink column + 2 (1 px gap), the space is 4 px; a red pixel in row 0
of a cell overrides the advance (its x + 1). Game code = 0x400 + ASCII (`tbl/en.tbl`). Ink is colour 3 on the
game's colour-2 paper (`docs/re/text.md` §VWF).
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
SHEET = ROOT / "fonts" / "en16.png"
GEN = ROOT / "build" / "gen"
FIRST, COUNT = 0x20, 0x60
CELL_W, CELL_H = 8, 16
SPACE_W = 4


def render(ttf):
    font = ImageFont.truetype(ttf, 16)
    img = Image.new("RGB", (16 * CELL_W, 6 * CELL_H), "white")
    for i in range(COUNT - 1):
        ch = chr(FIRST + i)
        cell = Image.new("L", (16, 24), 255)
        ImageDraw.Draw(cell).text((-1, -1), ch, font=font, fill=0)
        cell = cell.point(lambda v: 0 if v < 128 else 255)
        x0, y0 = (i % 16) * CELL_W, (i // 16) * CELL_H
        for y in range(CELL_H):
            for x in range(CELL_W):
                if cell.getpixel((x, y)) == 0:
                    img.putpixel((x0 + x, y0 + y), (0, 0, 0))
        if any(cell.getpixel((x, y)) == 0 for x in range(CELL_W, 16) for y in range(24)):
            print("warning: %r is wider than %d px" % (ch, CELL_W))
    SHEET.parent.mkdir(exist_ok=True)
    img.save(SHEET)
    print("wrote", SHEET)


def glyphs(sheet=SHEET):
    """[(rows[16] as ints, bit 7 = leftmost px), advance)] for codes 0x20.."""
    img = Image.open(sheet).convert("RGB")
    out = []
    for i in range(COUNT):
        x0, y0 = (i % 16) * CELL_W, (i // 16) * CELL_H
        rows, right, adv = [], -1, None
        for y in range(CELL_H):
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
            adv = SPACE_W if right < 0 else right + 2
        out.append((rows, adv))
    return out


def widths(sheet=SHEET):
    return {chr(FIRST + i): adv for i, (_, adv) in enumerate(glyphs(sheet))}


def text_px(text, sheet=SHEET, _w={}):
    if not _w:
        _w.update(widths(sheet))
    return sum(_w.get(c, 0) for c in text)


def build(gen=GEN):
    gen.mkdir(parents=True, exist_ok=True)
    gl = glyphs()
    (gen / "font_en.bin").write_bytes(bytes(b for rows, _ in gl for b in rows))
    (gen / "font_en_w.bin").write_bytes(bytes(adv for _, adv in gl))
    return gen / "font_en.bin", gen / "font_en_w.bin"


def preview(text, out):
    gl = glyphs()
    w = sum(gl[ord(c) - FIRST][1] for c in text) + 8
    img = Image.new("RGB", (w, CELL_H), (200, 190, 150))
    x = 0
    for c in text:
        rows, adv = gl[ord(c) - FIRST]
        for y, v in enumerate(rows):
            for b in range(8):
                if v & (0x80 >> b):
                    img.putpixel((x + b, y), (40, 30, 20))
        x += adv
    img.resize((w * 3, CELL_H * 3), Image.NEAREST).save(out)
    print("%s: %d px" % (out, x))


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "render":
        render(sys.argv[2])
    elif cmd == "build":
        print(build())
    elif cmd == "preview":
        preview(sys.argv[2], sys.argv[3])
