"""kanjisheet.py: review sheets for building tbl/jp.tbl by eye (phase 4 helper).

    python -X utf8 tools/kanjisheet.py GUESS.tsv OUTDIR [--first 0x58] [--count 0x35F] [--per 64] [--cols 8]

GUESS.tsv: `code<TAB>char[<TAB>...]` (fontmatch.py output, or a draft table as code<TAB>char). Each cell shows the
code, the game glyph (dialogue font, 2bpp 16x16 at C9:0000, zoomed x3) and the guessed characters drawn in MS Gothic
at the same size, so look-alike mistakes stand out. One PNG per `--per` glyphs.
"""
import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from fontview import glyph_snes2

ROOT = Path(__file__).resolve().parents[1]
ROM = ROOT / "rom" / "Heian Fuuunden (Japan).sfc"
FONT_OFF = 0x90000
Z = 3
CELL_W, CELL_H = 16 * Z * 3 + 20, 16 * Z + 18


def load_guess(path):
    out = {}
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        f = line.split("\t")
        if len(f) < 2 or f[0] == "code":
            continue
        out[int(f[0], 16)] = [f[i] for i in range(1, len(f), 2) if f[i]][:2] if len(f) > 3 else [f[1]]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("guess")
    ap.add_argument("outdir")
    ap.add_argument("--first", type=lambda s: int(s, 0), default=0x58)
    ap.add_argument("--count", type=lambda s: int(s, 0), default=0x35F)
    ap.add_argument("--per", type=int, default=64)
    ap.add_argument("--cols", type=int, default=8)
    a = ap.parse_args()
    data = ROM.read_bytes()
    guess = load_guess(a.guess)
    font = ImageFont.truetype("C:/Windows/Fonts/msgothic.ttc", 16 * Z)
    lab = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 14)
    out = Path(a.outdir)
    out.mkdir(parents=True, exist_ok=True)
    for page in range(0, a.count, a.per):
        n = min(a.per, a.count - page)
        rows = (n + a.cols - 1) // a.cols
        img = Image.new("RGB", (a.cols * CELL_W, rows * CELL_H), (255, 255, 255))
        dr = ImageDraw.Draw(img)
        for i in range(n):
            code = a.first + page + i
            cx, cy = (i % a.cols) * CELL_W, (i // a.cols) * CELL_H
            dr.rectangle([cx, cy, cx + CELL_W - 1, cy + CELL_H - 1], outline=(200, 200, 200))
            dr.text((cx + 2, cy + 1), "%03X" % code, fill=(200, 0, 0), font=lab)
            g = glyph_snes2(data[FONT_OFF + code * 64: FONT_OFF + code * 64 + 64])
            for y in range(16):
                for x in range(16):
                    if g[y][x] == 3:
                        dr.rectangle([cx + 4 + x * Z, cy + 16 + y * Z, cx + 4 + x * Z + Z - 1,
                                      cy + 16 + y * Z + Z - 1], fill=(0, 0, 0))
            for k, ch in enumerate(guess.get(code, [])):
                dr.text((cx + 10 + (k + 1) * 16 * Z, cy + 16), ch, fill=(0, 0, 160) if k == 0 else (120, 120, 120),
                        font=font)
        p = out / ("k%03X.png" % (a.first + page))
        img.save(p)
        print(p)


if __name__ == "__main__":
    main()
