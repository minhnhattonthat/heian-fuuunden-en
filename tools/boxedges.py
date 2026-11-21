"""Find a window's inner rect in a screenshot, for inkbox.py: walk out from a point inside the box until the
border's light frame pixels.

    python -X utf8 tools/boxedges.py SHOT.png X,Y [X,Y ...] [--frame 200]

From each seed (a pixel of the box's fill whose row and column cross no text: e.g. near a corner, above the
text), scans left/right along its row and up/down along its column for the first pixel whose brightest channel is
>= --frame (the window frame). Prints `x,y,w,h` of the inside (frame excluded) per seed.
"""
import argparse
import struct
import sys
import zlib
from pathlib import Path


def load_png(path):
    """8-bit RGB/RGBA PNG -> (w, h, rows of (r,g,b))."""
    data = Path(path).read_bytes()
    pos, idat, w = 8, b"", 0
    while pos < len(data):
        n, typ = struct.unpack(">I4s", data[pos:pos + 8])
        body = data[pos + 8:pos + 8 + n]
        if typ == b"IHDR":
            w, h, depth, ctype = struct.unpack(">IIBB", body[:10])
            assert depth == 8 and ctype in (2, 6), "want 8-bit RGB/RGBA"
            bpp = 3 if ctype == 2 else 4
        elif typ == b"IDAT":
            idat += body
        pos += 12 + n
    raw, rows, prev = zlib.decompress(idat), [], bytearray(w * bpp)
    stride = w * bpp
    for y in range(h):
        f, line = raw[y * (stride + 1)], bytearray(raw[y * (stride + 1) + 1:(y + 1) * (stride + 1)])
        for i in range(stride):
            a = line[i - bpp] if i >= bpp else 0
            b, c = prev[i], prev[i - bpp] if i >= bpp else 0
            if f == 1: line[i] = (line[i] + a) & 255
            elif f == 2: line[i] = (line[i] + b) & 255
            elif f == 3: line[i] = (line[i] + (a + b) // 2) & 255
            elif f == 4:
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                line[i] = (line[i] + (a if pa <= pb and pa <= pc else b if pb <= pc else c)) & 255
        rows.append([tuple(line[x * bpp:x * bpp + 3]) for x in range(w)])
        prev = line
    return w, h, rows


def edge(get, start, step, limit, frame):
    """First index from start (exclusive) in direction step whose pixel is frame-bright."""
    i = start
    while 0 <= i + step < limit:
        i += step
        if max(get(i)) >= frame:
            return i
    return i


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("png")
    ap.add_argument("seeds", nargs="+")
    ap.add_argument("--frame", type=int, default=200)
    a = ap.parse_args()
    w, h, px = load_png(a.png)
    for s in a.seeds:
        x, y = map(int, s.split(","))
        lx = edge(lambda i: px[y][i], x, -1, w, a.frame)
        rx = edge(lambda i: px[y][i], x, 1, w, a.frame)
        ty = edge(lambda i: px[i][x], y, -1, h, a.frame)
        by = edge(lambda i: px[i][x], y, 1, h, a.frame)
        print("%d,%d,%d,%d" % (lx + 1, ty + 1, rx - lx - 1, by - ty - 1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
