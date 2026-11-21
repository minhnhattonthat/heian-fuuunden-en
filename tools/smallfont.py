"""Decode BG3 tilemap text drawn with the 8x16 small font (block C8:8954, VRAM word $6000).

Glyph = top tile t, bottom tile t+0x10. Rows of top tiles (from work/qa/smallfont_top.png; X Y A B L R and
the small kana are approximate). Kanji pairs at 0xD0+ are 16x16 (two top tiles each).

    python -X utf8 tools/smallfont.py ROM OFFSET WORDS [ROWLEN]
"""
import sys

ROWS = {
    0x10: "0123456789",
    0x30: "あいうえおかきくけこさしすせそた",
    0x50: "ちつてとなにぬねのはひふへほまみ",
    0x70: "むめもやゆよわをんらりるれろがぎ",
    0x90: "ぐげござじずぜぞだぢづでどばびぶ",
    0xB0: "べぼぱぴぷぺぽぇぉ◀XYABLR",
}
KANJI = {0xD0: "体", 0xD2: "力", 0xD4: "経", 0xD6: "験", 0xD8: "装", 0xDA: "備", 0xDC: "攻", 0xDE: "防"}
CHARS = {}
for base, s in ROWS.items():
    for i, c in enumerate(s):
        CHARS[base + i] = c
CHARS.update(KANJI)


def text(words):
    out = []
    for w in words:
        t = w & 0x3FF
        if t in (0, 1):
            out.append("　")
        elif t in CHARS:
            out.append(CHARS[t])
        elif t - 1 in KANJI:
            continue
        elif t - 0x10 in CHARS or (t >= 0x20 and t - 0x10 in KANJI):
            out.append("_")  # bottom half (small kana sit here)
        else:
            out.append("[%X]" % t)
    return "".join(out)


def main(argv):
    rom = open(argv[1], "rb").read()
    off, n = int(argv[2], 16), int(argv[3], 16)
    row = int(argv[4]) if len(argv) > 4 else n
    words = [rom[off + 2 * i] | rom[off + 2 * i + 1] << 8 for i in range(n)]
    for r in range(0, n, row):
        print("0x%06X %s" % (off + 2 * r, text(words[r:r + row])))


if __name__ == "__main__":
    main(sys.argv)
