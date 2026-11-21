"""Enumerate the compressed blocks (tools/kss_comp.py format) in the ROM.

Blocks are stored back to back: each ends where the next begins. Seeds are the sources logged by
tools/lua/declog.lua; from each seed the walker follows the chain forwards until a block fails to decode, then
scans for chains of at least MIN_CHAIN blocks anywhere else in the given banks. Prints every skipped gap.

    python -X utf8 tools/kss_blocks.py ROM [--banks 4,8] [--seeds work/qa/dec_*/log.txt] [--tsv OUT.tsv]
"""
import argparse
import glob
import re

from kss_comp import Bad, decode

MIN_CHAIN = 3


def try_block(rom, off, end):
    if off >= end or rom[off] > 2:
        return None
    try:
        out, n = decode(rom, off)
    except (Bad, IndexError, ValueError):
        return None
    if off + n > end:
        return None
    return out, n


def walk(rom, off, end):
    chain = []
    while True:
        r = try_block(rom, off, end)
        if not r:
            return chain, off
        chain.append((off, rom[off], r[1], len(r[0])))
        off += r[1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rom")
    ap.add_argument("--banks", default="4,8")
    ap.add_argument("--seeds", default="work/qa/dec_*/log.txt")
    ap.add_argument("--tsv")
    a = ap.parse_args()
    rom = open(a.rom, "rb").read()
    seeds = set()
    for f in glob.glob(a.seeds):
        for m in re.finditer(r"src=([0-9A-F]{6})", open(f).read()):
            seeds.add(int(m.group(1), 16) & 0x3FFFFF)
    blocks = {}
    for bank in [int(b, 16) for b in a.banks.split(",")]:
        start, end = bank << 16, (bank + 1) << 16
        off = start
        while off < end:
            chain, stop = walk(rom, off, end)
            if len(chain) >= MIN_CHAIN or (chain and off in seeds):
                for b in chain:
                    blocks[b[0]] = b
                off = stop
            else:
                off += 1
    for s in seeds:
        if s not in blocks:
            chain, _ = walk(rom, s, (s | 0xFFFF) + 1)
            for b in chain:
                blocks.setdefault(b[0], b)
    rows = sorted(blocks.values())
    prev = None
    for b in rows:
        if prev is not None and b[0] != prev:
            print("gap 0x%06X-0x%06X (%d bytes)" % (prev, b[0], b[0] - prev))
        prev = b[0] + b[2]
    print("%d blocks, %d seeds, seeds missed: %s" % (len(rows), len(seeds),
          [hex(s) for s in sorted(seeds) if s not in blocks]))
    if a.tsv:
        with open(a.tsv, "w", newline="\n") as f:
            f.write("offset\ttype\tpacked\tsize\tseed\n")
            for b in rows:
                f.write("0x%06X\t%d\t%d\t%d\t%s\n" % (b[0], b[1], b[2], b[3], "y" if b[0] in seeds else ""))


if __name__ == "__main__":
    main()
