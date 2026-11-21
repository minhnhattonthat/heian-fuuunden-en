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
# Renderer-2 name fields (docs/re/windows.md, measured from tools/lua/r2log.lua + shots). A name wider than its
# field in the 16-px font goes in as `{small}line 1{sbr}line 2` in the 8-px font, each line <= the field
# (asm/main.asm VwfMenu small mode). A string shown in several fields takes the smallest.
FIELD_PX = 48
FIELDS = [   # (first id, last id, px)
    (0x001, 0x0FE, 48),    # items, equipment, names: item grid / status (6 tiles; C1:2D13, C1:29D9)
    (0x13C, 0x1B8, 48),    # jutsu / shikigami lists, squad label (6-8 tiles; C5:0D03.., C5:226F.., C1:4FF3)
    (0x24A, 0x288, 48),    # provinces: overworld label (6 tiles; C1:5018)
]
# Party list (ids 054-083, also shown in the 48-px status field): asm/main.asm PartyName draws every name there in
# the narrow 8-px font on one row of 5 tiles, whatever form the string has ({small}/{narrow}/{sbr} are skipped).
PARTY_IDS = (0x054, 0x083)
PARTY_PX = 40
NARROW_CHARS = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 -.'")


def party_fits(text):
    """Error text when an English party-list name does not fit its slot, else None."""
    if set(text) - NARROW_CHARS:
        return "%r: the narrow font has no %s" % (text, "".join(sorted(set(text) - NARROW_CHARS)))
    if font_en.text_px(text, "narrow") > PARTY_PX + 1:
        return "%r: %d px in the narrow font, party slot %d" % (text, font_en.text_px(text, "narrow") - 1, PARTY_PX)
    return None


def ids_of(row):
    return [int(x, 16) for x in row["id"].split("+")]


def field_px(row):
    """Smallest measured field among the row's ids, or None for text that is not a renderer-2 field."""
    px = [p for i in ids_of(row) for lo, hi, p in FIELDS if lo <= i <= hi]
    return min(px) if px else None


def is_field(row):
    return field_px(row) is not None


def fit_field(text, px=FIELD_PX):
    """Plain English name -> what goes in the ROM, first that fits the field: one 16-px line; one or two 8-px lines
    (Pixel Operator 8, split at the space that balances them best); one or two lines in the narrow 8-px font.
    ValueError when none fits (the lint reports it)."""
    if font_en.text_px(text) <= px:
        return text
    for code, font in (("{small}", True), ("{narrow}", "narrow")):
        if font_en.text_px(text, font) <= px:
            return code + text
        words = text.split(" ")
        best = None
        for k in range(1, len(words)):
            a, b = " ".join(words[:k]), " ".join(words[k:])
            wa, wb = font_en.text_px(a, font), font_en.text_px(b, font)
            if wa <= px and wb <= px and (best is None or max(wa, wb) < best[0]):
                best = (max(wa, wb), a, b)
        if best is not None:
            return "%s%s{sbr}%s" % (code, best[1], best[2])
    raise ValueError("%r fits no 16-px line or two 8-px lines of %d px" % (text, px))


def small_lines(tag, width=FIELD_PX):
    """Marker for a name field: `[id]` + filler words over two full small lines."""
    lines, text = [tag + " "], FILLER
    for c in text:
        if font_en.text_px(lines[-1] + c, True) > width:
            if len(lines) == 2:
                break
            lines.append("")
            if c == " ":
                continue
        lines[-1] += c
    return "{small}" + "{sbr}".join(s.strip() for s in lines)


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
    if is_field(row) and "{" not in jp:
        return small_lines(tag, max(field_px(row), FIELD_PX))   # the tag needs 48; narrower fields overflow
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
                if any(PARTY_IDS[0] <= i <= PARTY_IDS[1] for i in ids_of(r)) and party_fits(r["en"]):
                    raise ValueError("%s %s" % (r["id"], party_fits(r["en"])))
                en = fit_field(r["en"], field_px(r)) if is_field(r) and "{" not in r["en"] else r["en"]
                out.append((ids_of(r), kss_script.encode(en_t, en), r))
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
