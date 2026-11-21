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


# Blocks that may grow: where the game keeps their 24-bit pointers (file offsets of the 3 pointer bytes; found by
# scanning the ROM for the block address, each checked against the original bytes before patching). A grown block
# moves to RELOC_AREA (bank $DF upper half, after the code; 2 MB builds only).
RELOC_PTRS = {
    0x08939E: [0x01EEA7, 0x01EF33],            # party panel A tilemap (graphics load table C1:EE..)
    0x089450: [0x01EEB1, 0x01EED9, 0x01EF3D],  # party panel B tilemap
    0x0871C2: [0x01F24C],                      # save menu map (T2), load table C1:F2..
    0x08723A: [0x01F242],                      # options map (T3)
    0x0872B5: [0x01F22E],                      # quit map (T4)
    0x0872E0: [0x01F238],                      # saved map (T5)
    0x088954: [0x01F037, 0x01F0C3],            # small font (G5, smallfont_en)
    0x08B282: [0x01EFF1],                      # battle command labels (G6, gfx_en)
    0x089BAF: [0x01F091],                      # game-over card (G13, gfx_en)
    0x08C2F8: [0x01F019],                      # credits tiles (G9, gfx_en)
    0x08CD4E: [(0x0BE547, 0x0BE54C)],          # credits map (CB:E546 LDA #$CD4E / LDA #$00C8, gfx_en)
    # (lo, bank): named by code as LDA #$lo16 / LDA #$00bank: file offsets of the two operands
    0x08BBEE: [(0x05265B, 0x052660)],          # Yes/No box map (C5:265A, tilemap_text "yesno")
}
RELOC_AREA = (0x1F8000, 0x200000)


def _relocate(out, off, blk, cursor):
    ptrs = RELOC_PTRS.get(off)
    if not ptrs:
        raise ValueError("block 0x%06X grew: needs relocation (add its pointers to RELOC_PTRS)" % off)
    if len(out) < RELOC_AREA[1]:
        raise ValueError("block 0x%06X grew: relocation needs the 2 MB ROM" % off)
    if cursor + len(blk) > RELOC_AREA[1]:
        raise ValueError("relocation area full")
    if any(b != 0xFF for b in out[cursor:cursor + len(blk)]):
        raise ValueError("relocation area at 0x%06X is not free" % cursor)
    out[cursor:cursor + len(blk)] = blk
    old = bytes([off & 0xFF, (off >> 8) & 0xFF, 0xC0 + (off >> 16)])
    new = bytes([cursor & 0xFF, (cursor >> 8) & 0xFF, 0xC0 + (cursor >> 16)])
    for p in ptrs:
        if isinstance(p, tuple):            # code operands: lo16 at p[0], bank at p[1]
            lo, bank = p
            if bytes(out[lo:lo + 2]) != old[:2] or out[bank] != old[2]:
                raise ValueError("operands at 0x%06X/0x%06X do not name block 0x%06X" % (lo, bank, off))
            out[lo:lo + 2], out[bank] = new[:2], new[2]
            continue
        if bytes(out[p:p + 3]) != old:
            raise ValueError("pointer at 0x%06X does not hold block 0x%06X" % (p, off))
        out[p:p + 3] = new
    return cursor + len(blk)


def pack(rom, indir, path=LIST, recompress=False):
    """Return (new rom, stats). stats counts kept / re-encoded / exact (re-encoded and byte-identical) / moved.
    A block that grows moves to RELOC_AREA when its pointers are known (RELOC_PTRS); `rom` must then be 2 MB."""
    out = bytearray(rom)
    indir = Path(indir)
    stats = {"kept": 0, "encoded": 0, "exact": 0, "moved": 0}
    cursor = RELOC_AREA[0]
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
            cursor = _relocate(out, off, blk, cursor)
            stats["moved"] += 1
            continue
        out[off:off + len(blk)] = blk
    return bytes(out), stats
