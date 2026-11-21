"""Relocate every dialogue-table string into the expanded ROM (phase 5+).

The ROM grows to 2 MB (0x180000-0x1FFFFF = banks $D8-$DF, 0xFF fill). `PTRS` at $D8:0000 holds 0x614 entries of
4 bytes (address lo16, bank as a word) read by the hooks in asm/main.asm; strings follow from $D8:1850 and never
cross a bank. Bank $DF is kept for code and the font. The original C3/C6 strings stay where they are, unreferenced.

Text per row (script/*.tsv): `en` when present (tbl/en.tbl), else the marker line in marker mode, else `jp`
(tbl/jp.tbl). Rows of kind `data` keep pointing at their original bytes.
"""
import re
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import font_en  # noqa: E402
import kss_script  # noqa: E402
import kss_text  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
EN_TBL = ROOT / "tbl" / "en.tbl"
SIZE = 0x200000
PTRS = 0x180000
TEXT_START = PTRS + 4 * kss_text.COUNT
TEXT_END = 0x1F0000           # $DF is code + font
FILLER = "The quick brown fox jumps over the lazy dog. "
LINE_PX = 176                 # dialogue line buffer (asm/main.asm LINE_PX)
NAME_PX = 128                 # renderer 2 limit (asm/main.asm MENU_PX)
CTRL = re.compile(r"(\{\w+\})")
BREAKS = ("{br}", "{page}", "{end2}")


def ids_of(row):
    return [int(x, 16) for x in row["id"].split("+")]


def fill(prefix, width):
    s = prefix
    for c in FILLER * 8:
        if font_en.text_px(s + c) > width:
            break
        s += c
    return s.rstrip()


def marker(row):
    """`[id]` + filler at full width for every line; control codes kept where the Japanese has them."""
    jp = row["jp"]
    tag = "[%s]" % row["id"].split("+")[0]
    parts = CTRL.split(jp)
    namelike = not any(p.startswith("{") for p in parts if p) and len(jp) <= 8
    width = NAME_PX if namelike else LINE_PX
    out, line, first = [], [], True

    def flush():
        nonlocal first
        inline = sum(1 for p in line if p in ("{name}", "{num}"))
        w = width - 40 * inline
        text = fill(tag + " " if first else "", w) if first or any(not p.startswith("{") for p in line) else ""
        first = False
        out.append(text + "".join(p for p in line if p.startswith("{")))

    for p in parts:
        if not p:
            continue
        if p in BREAKS:
            flush()
            out.append(p)
            line = []
        else:
            line.append(p)
    flush()
    return "".join(out)


def strings(mode="build", script_dir=None, qa=None):
    """[(ids, words or None, row)] in script order; words None = keep the original pointer (kind data).
    qa: {first id (hex str): English text} overrides for stress builds (`build.py marker --qa 2A7=...`)."""
    jp_t, en_t = kss_script.table(), kss_script.table(EN_TBL)
    out = []
    for bank, rows in kss_script.load_script(script_dir or kss_script.SCRIPT).items():
        if bank not in kss_text.BANKS:
            continue                    # tilemaps.tsv: graphics text, not the table
        for r in rows:
            if qa and r["id"].split("+")[0] in qa:
                out.append((ids_of(r), kss_script.encode(en_t, qa[r["id"].split("+")[0]]), r))
            elif r["kind"] == "data":
                out.append((ids_of(r), None, r))
            elif r["en"]:
                out.append((ids_of(r), kss_script.encode(en_t, r["en"]), r))
            elif mode == "marker":
                out.append((ids_of(r), kss_script.encode(en_t, marker(r)), r))
            else:
                out.append((ids_of(r), kss_script.encode(jp_t, r["jp"]), r))
    return out


def insert(rom, mode="build", script_dir=None, qa=None):
    """Original ROM bytes -> expanded bytearray with the strings and PTRS written. Returns (rom, stats)."""
    out = bytearray(rom) + b"\xff" * (SIZE - len(rom))
    orig = kss_text.pointers(rom)
    ptr = [None] * kss_text.COUNT
    pos = TEXT_START
    for ids, words, row in strings(mode, script_dir, qa):
        if words is None:
            for i in ids:
                ptr[i] = (orig[i], 0xC3 if kss_text.bank_of(i) == "C3" else 0xC6)
            continue
        data = struct.pack("<%dH" % len(words), *words)
        if (pos & 0xFFFF) + len(data) > 0x10000:
            pos = (pos | 0xFFFF) + 1
        if pos + len(data) > TEXT_END:
            raise ValueError("text does not fit in $D8-$DE")
        out[pos:pos + len(data)] = data
        for i in ids:
            ptr[i] = (pos & 0xFFFF, 0xC0 | (pos >> 16))
        pos += len(data)
    missing = [i for i, p in enumerate(ptr) if p is None]
    if missing:
        raise ValueError("ids with no string: %s" % missing[:10])
    for i, (lo, bank) in enumerate(ptr):
        struct.pack_into("<HH", out, PTRS + 4 * i, lo, bank)
    return out, {"text_end": "0x%06X" % pos, "free": TEXT_END - pos}


if __name__ == "__main__":
    import kss_script as ks
    rows = [r for b, rows in ks.load_script().items() if b in kss_text.BANKS for r in rows]
    for r in rows[:: max(1, len(rows) // 12)]:
        print(r["id"], marker(r))
