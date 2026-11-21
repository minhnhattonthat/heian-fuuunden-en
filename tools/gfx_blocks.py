"""Compressed graphics/tilemap blocks (docs/re/compression.md): unpack to files, pack back.

`gfx/blocks.tsv` lists every block (offset, type, packed size, output size) found by tools/kss_blocks.py.
unpack() decodes each one; pack() writes a block back only where its decoded bytes differ from the original:
an unchanged block keeps its original packed bytes (the game's compressor breaks LZ ties differently from ours,
so re-encoding is not byte-exact for every block, only content-exact). A changed block is re-encoded with the
same type and must fit in the original space for now; relocation to new space comes with the first edit that
needs it (phase 5/7).
"""
import csv
from pathlib import Path

from kss_comp import decode, encode

ROOT = Path(__file__).resolve().parents[1]
LIST = ROOT / "gfx" / "blocks.tsv"


def blocks(path=LIST):
    """[(offset, type, packed, size)] in file order."""
    with open(path, newline="") as f:
        rows = [(int(r["offset"], 16), int(r["type"]), int(r["packed"]), int(r["size"]))
                for r in csv.DictReader(f, delimiter="\t")]
    return sorted(rows)


def name(off):
    return "%06X.bin" % off


def unpack(rom, outdir, path=LIST):
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    prev_end = 0
    for off, typ, packed, size in blocks(path):
        if off < prev_end:
            raise ValueError("block 0x%06X overlaps the previous one" % off)
        data, n = decode(rom, off)
        if (rom[off], n, len(data)) != (typ, packed, size):
            raise ValueError("block 0x%06X does not match gfx/blocks.tsv" % off)
        (outdir / name(off)).write_bytes(data)
        prev_end = off + n


def pack(rom, indir, path=LIST, recompress=False):
    """Return (new rom, stats). stats counts kept / re-encoded / exact (re-encoded and byte-identical)."""
    out = bytearray(rom)
    indir = Path(indir)
    stats = {"kept": 0, "encoded": 0, "exact": 0}
    for off, typ, packed, size in blocks(path):
        data = (indir / name(off)).read_bytes()
        orig, n = decode(rom, off)
        if data == orig and not recompress:
            stats["kept"] += 1
            continue
        blk = encode(typ, data)
        if decode(blk, 0) != (data, len(blk)):
            raise AssertionError("encoder roundtrip failed for block 0x%06X" % off)
        stats["encoded"] += 1
        if blk == rom[off:off + n]:
            stats["exact"] += 1
            continue
        if data == orig:
            continue  # recompress check only: content-exact is enough, keep the original bytes
        if len(blk) > n:
            raise ValueError("block 0x%06X grew %d -> %d bytes: needs relocation" % (off, n, len(blk)))
        out[off:off + len(blk)] = blk
    return bytes(out), stats
