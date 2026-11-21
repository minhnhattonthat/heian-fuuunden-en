"""Small-font tilemap text (docs/re/graphics.md T1-T5): menu captions and save/option/quit screens.

These are BG3 tilemaps, not strings: each glyph is a top tile t and a bottom tile t+0x10 (tools/smallfont.py), so
English goes in by redrawing small-font cells and rewriting the map (phase 5), not through tbl/jp.tbl.

    python -X utf8 tools/tilemap_text.py dump [--force]   write script/tilemaps.tsv (never clobbers en without --force)
    python -X utf8 tools/tilemap_text.py list             print every entry

Each entry is one row pair (top row, bottom row) of a map of `width` words. Small kana sit in the bottom tile only.
"""
import argparse
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kss_comp  # noqa: E402
import kss_script  # noqa: E402
import smallfont  # noqa: E402

CAPTIONS = 0x19E7F  # C1:9E7F, 6 pointers into bank C1, each 2 rows x 18 words
SMALL_BOTTOM = {0x2C: "ょ", 0x0F: "っ"}
# (prefix, LZ/RLE block file offset, map width in words, screen)
BLOCKS = [("save", 0x871C2, 10, "menu -> save (T2)"),
          ("option", 0x8723A, 16, "menu -> settings (T3)"),
          ("quit", 0x872B5, 9, "scene quit_nosave (T4)"),
          ("saved", 0x872E0, 9, "scene save_message (T5)")]


def pair_text(top, bottom):
    out = []
    for t, b in zip(top, bottom):
        t, b = t & 0x3FF, b & 0x3FF
        if t in smallfont.CHARS:
            out.append(smallfont.CHARS[t])
        elif t - 1 in smallfont.KANJI:
            continue
        elif t in (0, 1) and b in SMALL_BOTTOM:
            out.append(SMALL_BOTTOM[b])
        elif t in (0, 1):
            out.append("　")
        else:
            out.append("[%X]" % t)
    return "".join(out).rstrip("　")


def pairs(words, width, where):
    """Yield (row, text, offset of the top row) for every row with text and the row below it."""
    rows = [words[i:i + width] for i in range(0, len(words), width)]
    r = 0
    while r < len(rows):
        top = rows[r]
        if any((w & 0x3FF) in smallfont.CHARS for w in top):
            bottom = rows[r + 1] if r + 1 < len(rows) else [0] * width
            yield r, pair_text(top, bottom), where + 2 * r * width
            r += 2
        else:
            r += 1


def entries(rom):
    out = []
    ptrs = struct.unpack_from("<6H", rom, CAPTIONS)
    for k, p in enumerate(ptrs):
        off = 0x10000 + p
        words = struct.unpack_from("<36H", rom, off)
        for _, text, _ in pairs(list(words), 18, off):
            out.append({"id": "caption%d" % k, "jp": text,
                        "notes": "C1:%04X, 18x2 words, field menu caption (T1)" % p})
    for prefix, off, width, screen in BLOCKS:
        data = kss_comp.decode(rom, off)[0]
        words = list(struct.unpack("<%dH" % (len(data) // 2), data))
        for n, (row, text, _) in enumerate(pairs(words, width, 0)):
            out.append({"id": "%s%d" % (prefix, n), "jp": text,
                        "notes": "block C8:%04X row %d, width %d, %s" % (off & 0xFFFF, row, width, screen)})
    return out


def dump(force=False, path=kss_script.SCRIPT / "tilemaps.tsv"):
    rows = [dict(id=e["id"], kind="tilemap", jp=e["jp"], en="", max="", notes=e["notes"])
            for e in entries(kss_script.ROM.read_bytes())]
    if path.exists():
        if not force:
            raise SystemExit("%s exists; --force keeps its en/max" % path)
        old = {r["id"]: r for r in kss_script.read_tsv(path)}
        for r in rows:
            if r["id"] in old:
                r.update(en=old[r["id"]]["en"], max=old[r["id"]]["max"])
    kss_script.write_tsv(path, rows)
    print("%s: %d entries" % (path, len(rows)))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("dump")
    d.add_argument("--force", action="store_true")
    sub.add_parser("list")
    a = ap.parse_args()
    if a.cmd == "dump":
        dump(a.force)
    else:
        for e in entries(kss_script.ROM.read_bytes()):
            print(e["id"], e["jp"], "|", e["notes"])


if __name__ == "__main__":
    main()
