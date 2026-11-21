"""Static graphics sweep: render every compressed block chain and every raw bank as grey tile sheets.

Each source starts on a new sheet row (32 tiles per row); SHEET_index.tsv maps sheet rows to the source offset.
Type-2 blocks (word RLE, tilemaps) are skipped and listed, as is anything else not rendered, so nothing drops
silently (references/graphics.md §Survey).

    python -X utf8 tools/gfx_sweep.py ROM --blocks work/re/blocks.tsv --raw 0xA0000-0xB0000,.. --out work/qa/sweep
        [--fmt 4|2] [--rows 96]
"""
import argparse
import os

from PIL import Image, ImageDraw

from kss_comp import decode

COLS = 32


def tile_px(buf, i, bpp):
    size = 8 * bpp
    t = buf[i * size:(i + 1) * size]
    px = []
    for y in range(8):
        row = []
        for x in range(8):
            bit = 7 - x
            v = 0
            for p in range(bpp):
                byte = t[(p // 2) * 16 + y * 2 + (p & 1)]
                v |= ((byte >> bit) & 1) << p
            row.append(v)
        px.append(row)
    return px


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rom")
    ap.add_argument("--blocks")
    ap.add_argument("--min-chain", type=int, default=5)
    ap.add_argument("--raw", default="")
    ap.add_argument("--out", required=True)
    ap.add_argument("--fmt", type=int, default=4)
    ap.add_argument("--rows", type=int, default=96)
    ap.add_argument("--zoom", type=int, default=2)
    a = ap.parse_args()
    rom = open(a.rom, "rb").read()
    bpp = a.fmt
    tsize = 8 * bpp
    sources = []  # (label, bytes)
    skipped = []
    if a.blocks:
        rows = [l.rstrip("\n").split("\t") for l in open(a.blocks).readlines()[1:]]
        rows = [(int(o, 16), int(t), int(p), int(z), s) for o, t, p, z, s in rows]
        # keep chains of >= min_chain blocks, or chains holding a logged seed
        chains, cur = [], None
        for r in rows:
            if cur and cur[-1][0] + cur[-1][2] == r[0]:
                cur.append(r)
            else:
                cur = [r]
                chains.append(cur)
        for ch in chains:
            if len(ch) < a.min_chain and not any(r[4] for r in ch):
                skipped.append("chain 0x%06X (%d blocks): too short, likely noise" % (ch[0][0], len(ch)))
                continue
            for off, typ, _, size, _ in ch:
                if typ == 2:
                    skipped.append("block 0x%06X: type 2 (tilemap)" % off)
                    continue
                if size < tsize:
                    skipped.append("block 0x%06X: %d bytes, under one tile" % (off, size))
                    continue
                sources.append(("blk %06X" % off, decode(rom, off)[0]))
    for rng in filter(None, a.raw.split(",")):
        lo, hi = (int(x, 16) for x in rng.split("-"))
        for s in range(lo, hi, 0x2000):
            sources.append(("raw %06X" % s, rom[s:min(hi, s + 0x2000)]))
    os.makedirs(a.out, exist_ok=True)
    # lay out rows
    lines = []  # (label, buf, first tile)
    for label, buf in sources:
        n = len(buf) // tsize
        for t0 in range(0, n, COLS):
            lines.append((label, buf, t0, min(COLS, n - t0)))
    z = a.zoom
    index = open(os.path.join(a.out, "index.tsv"), "w", newline="\n")
    index.write("sheet\trow\tsource\tfirst_tile\tbyte_offset\n")
    for sheet, start in enumerate(range(0, len(lines), a.rows)):
        chunk = lines[start:start + a.rows]
        img = Image.new("L", (COLS * 8 * z + 70, len(chunk) * 8 * z), 0)
        dr = ImageDraw.Draw(img)
        prev = None
        for r, (label, buf, t0, n) in enumerate(chunk):
            for i in range(n):
                px = tile_px(buf, t0 + i, bpp)
                for y in range(8):
                    for x in range(8):
                        v = px[y][x] * 255 // ((1 << bpp) - 1)
                        if v:
                            dr.rectangle([70 + (i * 8 + x) * z, (r * 8 + y) * z,
                                          70 + (i * 8 + x) * z + z - 1, (r * 8 + y) * z + z - 1], fill=v)
            if label != prev:
                dr.text((2, r * 8 * z), label[4:], fill=255)
                dr.line([0, r * 8 * z, 68, r * 8 * z], fill=128)
                prev = label
            index.write("%d\t%d\t%s\t%d\t0x%X\n" % (sheet, r, label, t0, t0 * tsize))
        img.save(os.path.join(a.out, "sheet_%03d.png" % sheet))
    index.close()
    for s in skipped:
        print("skipped", s)
    print("%d sources, %d rows, %d sheets -> %s" % (len(sources), len(lines), (len(lines) + a.rows - 1) // a.rows,
                                                     a.out))


if __name__ == "__main__":
    main()
