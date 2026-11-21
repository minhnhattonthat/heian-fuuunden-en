"""fontview.py: render a run of 16x16 1bpp glyphs from the ROM as a labelled sheet (recon helper).

    python -X utf8 tools/fontview.py OFFSET COUNT OUT.png [--first CODE] [--layout rows|tiles] [--cols 16] [--zoom 2]

layout rows:  32 bytes per glyph, 16 rows of 2 bytes (left byte, right byte).
layout tiles: four 8x8 1bpp tiles (TL, TR, BL, BR), 8 bytes each.
Each cell is labelled with its code (first + index) in hex.
"""
import argparse
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
ROM = ROOT / "rom" / "Heian Fuuunden (Japan).sfc"


def glyph_rows(b):
    """16 rows of 16 bools."""
    return [[bool((b[r * 2 + (x >> 3)] >> (7 - (x & 7))) & 1) for x in range(16)] for r in range(16)]


def glyph_tiles(b):
    rows = []
    for r in range(16):
        row = []
        for x in range(16):
            t = (r >> 3) * 2 + (x >> 3)
            byte = b[t * 8 + (r & 7)]
            row.append(bool((byte >> (7 - (x & 7))) & 1))
        rows.append(row)
    return rows


def glyph_snes2(b):
    """64 bytes: four 2bpp 8x8 tiles TL, TR, BL, BR (the game's dialogue font in bank C9). Returns colour index 0-3."""
    rows = []
    for r in range(16):
        row = []
        for x in range(16):
            t = (r >> 3) * 2 + (x >> 3)
            p0 = b[t * 16 + (r & 7) * 2]
            p1 = b[t * 16 + (r & 7) * 2 + 1]
            bit = 7 - (x & 7)
            row.append(((p0 >> bit) & 1) | (((p1 >> bit) & 1) << 1))
        rows.append(row)
    return rows


GREYS = [(0, 0, 0), (255, 255, 255), (90, 90, 90), (170, 170, 170)]

LAYOUTS = {"rows": (glyph_rows, 32), "tiles": (glyph_tiles, 32), "snes2": (glyph_snes2, 64)}


def render(data, off, count, first, layout, cols, zoom):
    cell_w, cell_h = 16 * zoom + 4, 16 * zoom + 14
    rows_n = (count + cols - 1) // cols
    img = Image.new("RGB", (cols * cell_w, rows_n * cell_h), (40, 40, 60))
    dr = ImageDraw.Draw(img)
    fn, size = LAYOUTS[layout]
    for i in range(count):
        b = data[off + i * size: off + i * size + size]
        if len(b) < size:
            break
        cx, cy = (i % cols) * cell_w, (i // cols) * cell_h
        dr.text((cx + 1, cy), f"{first + i:03X}", fill=(255, 220, 0))
        g = fn(b)
        for y in range(16):
            for x in range(16):
                v = int(g[y][x])
                col = (255, 255, 255) if v is True or v == 1 and layout != "snes2" else GREYS[v]
                dr.rectangle([cx + 2 + x * zoom, cy + 12 + y * zoom, cx + 2 + x * zoom + zoom - 1,
                              cy + 12 + y * zoom + zoom - 1], fill=col)
    return img


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("offset", type=lambda s: int(s, 0))
    ap.add_argument("count", type=int)
    ap.add_argument("out")
    ap.add_argument("--first", type=lambda s: int(s, 0), default=0)
    ap.add_argument("--layout", choices=sorted(LAYOUTS), default="snes2")
    ap.add_argument("--cols", type=int, default=16)
    ap.add_argument("--zoom", type=int, default=2)
    a = ap.parse_args()
    data = ROM.read_bytes()
    render(data, a.offset, a.count, a.first, a.layout, a.cols, a.zoom).save(a.out)
    print(a.out)


if __name__ == "__main__":
    main()
