"""fontmatch.py: first-guess character for each glyph of the dialogue font by matching against a system font.

    python -X utf8 tools/fontmatch.py OUT.tsv [--font C:/Windows/Fonts/msgothic.ttc] [--first 0] [--count 0x3B7]

Every JIS X 0208 character (kana, symbols, level-1 and level-2 kanji) is rendered large and antialiased,
cropped to its ink box and scaled to 24x24 greyscale, then blurred; each game glyph (ink = colour index 3,
background 2) gets the same treatment. Score = normalised cross-correlation. Writes code, best char, score,
then the next two. A first guess only: the table is confirmed against decoded script text and zoomed sheets
(docs/re/text.md).
"""
import argparse
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ROM = ROOT / "rom" / "Heian Fuuunden (Japan).sfc"
FONT_OFF = 0x90000
GLYPH = 64
N = 24


def game_image(data, code):
    b = data[FONT_OFF + code * GLYPH: FONT_OFF + code * GLYPH + GLYPH]
    img = Image.new("L", (16, 16), 0)
    px = img.load()
    for r in range(16):
        for x in range(16):
            t = (r >> 3) * 2 + (x >> 3)
            bit = 7 - (x & 7)
            v = ((b[t * 16 + (r & 7) * 2] >> bit) & 1) | (((b[t * 16 + (r & 7) * 2 + 1] >> bit) & 1) << 1)
            if v == 3:
                px[x, r] = 255
    return img


def jis_chars():
    out = []
    for hi in range(0x81, 0xF0):
        if 0xA0 <= hi <= 0xDF:
            continue
        for lo in range(0x40, 0xFD):
            if lo == 0x7F:
                continue
            try:
                c = bytes([hi, lo]).decode("shift_jis")
            except UnicodeDecodeError:
                continue
            if c.strip():
                out.append(c)
    return out


def vec(img):
    """Ink box -> NxN greyscale (aspect kept, centred), blurred, zero-mean unit vector; None if blank."""
    box = img.getbbox()
    if not box:
        return None, None
    c = img.crop(box)
    w, h = c.size
    k = N / max(w, h)
    nw, nh = max(1, round(w * k)), max(1, round(h * k))
    c = c.resize((nw, nh), Image.BILINEAR)
    out = Image.new("L", (N, N), 0)
    out.paste(c, ((N - nw) // 2, (N - nh) // 2))
    out = out.filter(ImageFilter.GaussianBlur(0.8))
    a = np.asarray(out, dtype=np.float32).ravel()
    a = a - a.mean()
    n = np.linalg.norm(a)
    return (a / n if n else None), (w / h)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--font", default="C:/Windows/Fonts/msgothic.ttc")
    ap.add_argument("--first", type=lambda s: int(s, 0), default=0)
    ap.add_argument("--count", type=lambda s: int(s, 0), default=0x3B7)
    a = ap.parse_args()
    data = ROM.read_bytes()
    font = ImageFont.truetype(a.font, 64)
    chars, vecs, aspects = [], [], []
    for ch in jis_chars():
        img = Image.new("L", (80, 80), 0)
        ImageDraw.Draw(img).text((8, 0), ch, font=font, fill=255)
        v, asp = vec(img)
        if v is not None:
            chars.append(ch)
            vecs.append(v)
            aspects.append(asp)
    M = np.stack(vecs)
    aspects = np.array(aspects)
    with open(a.out, "w", encoding="utf-8", newline="\n") as f:
        f.write("code\tchar\tscore\tchar2\tscore2\tchar3\tscore3\n")
        for code in range(a.first, a.first + a.count):
            v, asp = vec(game_image(data, code))
            if v is None:
                f.write(f"{code:03X}\t\t0\t\t0\t\t0\n")
                continue
            s = M @ v
            # penalise very different ink-box shapes (ー vs |, 一 vs 口)
            s = s - 0.15 * np.abs(np.log(aspects / asp))
            top = np.argsort(-s)[:3]
            f.write(f"{code:03X}\t" + "\t".join(f"{chars[i]}\t{s[i]:.3f}" for i in top) + "\n")
    print(a.out)


if __name__ == "__main__":
    main()
