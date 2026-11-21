"""Portrait name plates (graphics.md G15): raw 32x16 2bpp images under the dialogue portraits.

Each plate is 0x80 bytes, 8 tiles in VRAM order (top row tiles 0-3, bottom row 4-7). C5:1C6B queues plate n
(portrait table C1:E78A byte 0) from C7:A1FF + n * 0x80 to BG3 tiles $340 or $348 (two buffers); the map is 4x2
tiles under the 32-px portrait, so a plate cannot grow. The original: paper colour 2, kanji and frame colour 3
(columns 0 and 31, row 15). English (decision D17): the narrow 8-px font (fonts/en_narrow.png) in the 30x15 inner
area, one centred line, or two lines split where NAMES has a "|" when one line would pass 30 px (a blank row
between the two lines when the 15 rows allow it).

    python -X utf8 tools/plates.py sheet ROM START COUNT OUT.png [--zoom 3]   plates START.. side by side
    python -X utf8 tools/plates.py preview OUT.png                           the English plates as built
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import font_en  # noqa: E402

PLATE = 0x80
BASE = 0x7A1FF          # C7:A1FF, plate 0
PAPER, INK = 2, 3
INNER_W = 30
# English per plate, in ROM order (= name ids 054-09C with gaps; generic speakers after 一条/花山). The Japanese
# plate is the short form, so the English is too (glossary.md). "|" marks the line break of a two-line plate.
NAMES = [
    "Kagura", "Seimei", "Hiro|yuki", "Mori|taka", "Jogu", "Momiji", "Semi|maru", "Uzuki",              # 神楽..卯月
    "Tota", "Kikyo", "Kaede", "Aoi", "Kongo", "Koku", "Kuho", "Enho",                                   # 蘆太..猿法
    "Natsume", "Haruna", "Hida", "Suzume", "Kijime", "Hazuki", "Aizen", "Chinnen",                      # 夷..珍念
    "Joun", "Shama", "Fudo", "Fugen", "Horen", "Shoun", "Tamon", "Rokkaku",                             # 如雲..六角
    "Genshin", "Ninku", "Moro|hide", "Yori|mitsu", "Tsuna", "Kage|toki", "Masa|hide", "Kintoki",        # 源信..公時
    "Sada|mitsu", "Tame|yuki", "Yasu|masa", "Kotono", "Yori|nobu", "Sugi|maru", "Takato", "Suetake",    # 貞光..季武
    "Masa|kado", "Sumi|tomo", "Akoya", "Doma", "Tenkai", "Chobu|kumaru", "Bandit", "Sagami",            # 将門..相模
    "Kuji", "Kusaka", "Masa|mitsu", "Shin|shada", "Kainki", "Isomeki", "Ichijo", "Kazan",               # 久慈..花山
    "Usagino", "Kuzu|noha", "Akana", "Aona", "Mido|rina", "Boke", "Yama", "Futa|kami",                  # 兎乃..二上
    "Isogami", "Moriya", "Guard", "Princess", "Monk", "Old Man", "Elder", "Miko",                       # 石上..巫女
    "Priest", "Boatman", "Noble", "Mer|chant", "Villager", "Man", "Girl", "Villager",                   # 宮司..里男
    "Woman", "Child", "Acolyte", "Samurai", "Yama|waro", "Michi|naga",                                  # 女..道長
]


def tile_px(b):
    """16 bytes of 2bpp -> 8 rows of 8 colour indices."""
    return [[((b[2 * y] >> (7 - x)) & 1) | (((b[2 * y + 1] >> (7 - x)) & 1) << 1) for x in range(8)]
            for y in range(8)]


def plate_px(b):
    """0x80 bytes -> 16 rows of 32 colour indices."""
    px = [[0] * 32 for _ in range(16)]
    for t in range(8):
        tp = tile_px(b[16 * t:16 * t + 16])
        ox, oy = 8 * (t % 4), 8 * (t // 4)
        for y in range(8):
            px[oy + y][ox:ox + 8] = tp[y]
    return px


def pack_plate(px):
    """16 rows of 32 colour indices -> 0x80 bytes."""
    out = bytearray()
    for t in range(8):
        ox, oy = 8 * (t % 4), 8 * (t // 4)
        for y in range(8):
            row = px[oy + y][ox:ox + 8]
            out += bytes([sum((c & 1) << (7 - x) for x, c in enumerate(row)),
                          sum(((c >> 1) & 1) << (7 - x) for x, c in enumerate(row))])
    return bytes(out)


def line_px(text):
    """(width, {(x, y): ink}) of one line in the narrow font, glyph row 0 at y 0."""
    gl = font_en.glyphs("narrow")
    ink, x = set(), 0
    for c in text:
        rows, adv = gl[ord(c) - font_en.FIRST]
        for y, m in enumerate(rows):
            for dx in range(8):
                if m & (0x80 >> dx):
                    ink.add((x + dx, y))
        x += adv
    return x - 1, ink


def render(name):
    """16 rows of 32 colour indices: the framed plate with `name` (see NAMES) in it."""
    px = [[INK if x in (0, 31) or y == 15 else PAPER for x in range(32)] for y in range(16)]
    lines = [line_px(name.replace("|", ""))]
    if lines[0][0] > INNER_W:
        lines = [line_px(t) for t in name.split("|")]
    for w, _ in lines:
        if w > INNER_W:
            raise ValueError("plate %r: %d px > %d" % (name, w, INNER_W))
    if len(lines) == 1:
        tops = [4]                       # caps on rows 4-10 of the 15 inner rows
    else:       # two lines, ink rows not shared (a blank row between when there is room), above the frame row
        lo1 = max(y for _, y in lines[0][1])
        lo2, hi2 = min(y for _, y in lines[1][1]), max(y for _, y in lines[1][1])
        tops = next(([a, b] for a, b in ((0, 8), (1, 8), (0, 7))
                     if b + lo2 >= a + lo1 + 1 and b + hi2 <= 14), None)
        if tops is None:
            raise ValueError("plate %r: the two lines do not fit 15 rows" % name)
    for (w, ink), top in zip(lines, tops):
        x0 = 1 + (INNER_W - w) // 2
        for x, y in ink:
            px[top + y][x0 + x] = INK
    return px


def writes():
    """[(file offset, bytes)] for every plate (raw, same size: written in place)."""
    assert len(NAMES) == 94, len(NAMES)
    return [(BASE + k * PLATE, pack_plate(render(n))) for k, n in enumerate(NAMES)]


def preview(out, zoom=3):
    rom = bytearray(BASE + len(NAMES) * PLATE)
    for off, data in writes():
        rom[off:off + PLATE] = data
    sheet(bytes(rom), BASE, len(NAMES), out, zoom)


def sheet(rom, start, count, out, zoom=3, cols=8):
    from PIL import Image, ImageDraw
    grey = [(0, 0, 0), (90, 90, 90), (170, 170, 170), (255, 255, 255)]
    rows = (count + cols - 1) // cols
    img = Image.new("RGB", (cols * 40, rows * 28), (80, 0, 0))
    d = ImageDraw.Draw(img)
    for k in range(count):
        off = start + k * PLATE
        px = plate_px(rom[off:off + PLATE])
        x0, y0 = (k % cols) * 40 + 4, (k // cols) * 28 + 10
        d.text((x0, y0 - 10), "%X" % off, fill=(255, 255, 0))
        for y in range(16):
            for x in range(32):
                img.putpixel((x0 + x, y0 + y), grey[px[y][x]])
    img.resize((img.width * zoom, img.height * zoom), Image.NEAREST).save(out)
    print("wrote", out)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("sheet")
    s.add_argument("rom")
    s.add_argument("start", type=lambda v: int(v, 16))
    s.add_argument("count", type=int)
    s.add_argument("out")
    s.add_argument("--zoom", type=int, default=3)
    p = sub.add_parser("preview")
    p.add_argument("out")
    p.add_argument("--zoom", type=int, default=3)
    a = ap.parse_args()
    if a.cmd == "preview":
        preview(a.out, a.zoom)
    else:
        sheet(Path(a.rom).read_bytes(), a.start, a.count, a.out, a.zoom)


if __name__ == "__main__":
    sys.exit(main())
