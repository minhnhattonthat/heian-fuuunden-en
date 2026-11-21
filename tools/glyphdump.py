"""Print dialogue-font glyphs as text (2bpp values 0-3), looked up through the C1:F2F4 glyph table.

    python tools/glyphdump.py CODE [CODE..]      (hex codes, e.g. 01 58 2e1)
Layout per glyph (verified from C1:73A5): 64 bytes = top-left, top-right, bottom-left, bottom-right 8x8 2bpp tiles.
"""
import sys

ROM = "rom/Heian Fuuunden (Japan).sfc"


def glyph(d, code):
    ptr = d[0x1F2F4 + code * 2] | d[0x1F2F5 + code * 2] << 8
    g = d[0x90000 + ptr: 0x90000 + ptr + 64]
    rows = []
    for half in (0, 32):
        for r in range(8):
            line = []
            for t in (0, 16):
                b0, b1 = g[half + t + r * 2], g[half + t + r * 2 + 1]
                line += [((b0 >> (7 - x)) & 1) | (((b1 >> (7 - x)) & 1) << 1) for x in range(8)]
            rows.append(line)
    return ptr, rows


if __name__ == "__main__":
    d = open(ROM, "rb").read()
    for c in sys.argv[1:]:
        ptr, rows = glyph(d, int(c, 16))
        print("code %s ptr C9:%04X" % (c, ptr))
        for r in rows:
            print("".join(".123"[v] for v in r))
