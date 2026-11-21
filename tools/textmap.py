"""textmap.py: decode the dialogue table (C3:0000) with the kana known so far; report coverage (recon helper).

    python -X utf8 tools/textmap.py [--dump OUT.txt] [--ids 0x1C0-0x1D0]

Format (docs/re/text.md): 0x614 16-bit pointers at C3:0000; id -> bank by id*2: <0x600 C3, <0x800 C6,
<0xA00 C3, else C6. Strings are 16-bit LE glyph codes ended by 0xFF or 0xFB. Kanji print as [XXX] until
tbl/jp.tbl exists (phase 4).
"""
import argparse
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROM = ROOT / "rom" / "Heian Fuuunden (Japan).sfc"
TABLE = 0x30000
COUNT = 0x614
KANA = "あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをんぁぃぅぇぉゃゅょっ" \
       "がぎぐげござじずぜぞだぢづでどばびぶべぼぱぴぷぺぽ。、！ー？"
CTRL = {0x00: "　", 0xFE: "/", 0xFD: "▼", 0xFC: "<N>", 0x56: "<#>"}
ENDS = (0xFF, 0xFB)


def bank(i):
    x = i * 2
    return 0x60000 if x >= 0xA00 or 0x600 <= x < 0x800 else 0x30000


def words(d, i):
    ptrs = struct.unpack_from(f"<{COUNT}H", d, TABLE)
    b, j, out = bank(i), ptrs[i], []
    while j < 0x10000:
        w = struct.unpack_from("<H", d, b + j)[0]
        out.append(w)
        j += 2
        if w in ENDS:
            break
    return b + ptrs[i], out


def decode(ws):
    s = ""
    for w in ws:
        if w in CTRL:
            s += CTRL[w]
        elif 1 <= w <= len(KANA):
            s += KANA[w - 1]
        elif w in ENDS:
            s += f"<{w:X}>"
        else:
            s += f"[{w:X}]"
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dump")
    ap.add_argument("--ids")
    a = ap.parse_args()
    d = ROM.read_bytes()
    ids = range(COUNT)
    if a.ids:
        lo, hi = (int(x, 0) for x in a.ids.split("-"))
        ids = range(lo, hi + 1)
    cov = {0x30000: bytearray(0x10000), 0x60000: bytearray(0x10000)}
    lines = []
    for i in ids:
        off, ws = words(d, i)
        b = bank(i)
        for k in range(off - b, off - b + 2 * len(ws)):
            if k < 0x10000:
                cov[b][k] = 1
        lines.append(f"{i:03X}\t{off:06X}\t{decode(ws)}")
    if a.dump:
        Path(a.dump).write_text("\n".join(lines) + "\n", encoding="utf-8")
    elif a.ids:
        print("\n".join(lines))
    if not a.ids:
        for b, c in cov.items():
            gaps, s = [], None
            for k in range(0x10000):
                if not c[k] and s is None:
                    s = k
                if c[k] and s is not None:
                    gaps.append((s, k))
                    s = None
            if s is not None:
                gaps.append((s, 0x10000))
            print(f"bank {b:06X} unreferenced: " + ", ".join(f"{b + x:06X}-{b + y:06X}" for x, y in gaps))


if __name__ == "__main__":
    main()
