"""kanjictx.py: where the script uses given glyph codes, with context (checks a tbl/jp.tbl reading).

    python -X utf8 tools/kanjictx.py 0A5 170 17D [--n 3] [--w 8]
    python -X utf8 tools/kanjictx.py --unused      codes 0x58-0x376 in the table that no string uses
    python -X utf8 tools/kanjictx.py --dups        characters with more than one code, and which codes are used
"""
import argparse
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kss_text  # noqa: E402
import kss_script  # noqa: E402


def uses(rom, t):
    """{code: [(id, index, decoded chars)]}"""
    out = defaultdict(list)
    for items in kss_text.unpack(rom).values():
        for it in items:
            if "ids" not in it:
                continue
            chars = [kss_script.decode(t, [w]) for w in it["words"]]
            for k, w in enumerate(it["words"]):
                out[w].append((it["ids"][0], k, chars))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("codes", nargs="*", type=lambda v: int(v, 16))
    ap.add_argument("--n", type=int, default=3)
    ap.add_argument("--w", type=int, default=8)
    ap.add_argument("--unused", action="store_true")
    ap.add_argument("--dups", action="store_true")
    a = ap.parse_args()
    rom, t = kss_script.ROM.read_bytes(), kss_script.table()
    u = uses(rom, t)
    if a.unused:
        print(" ".join("%03X%s" % (c, kss_script.decode(t, [c])) for c in range(0x58, 0x377) if not u.get(c)))
    if a.dups:
        by = defaultdict(list)
        for key, ch in t.dec.items():
            if len(key) == 2:
                by[ch].append(key[0] | key[1] << 8)
        for ch, cs in by.items():
            if len(cs) > 1:
                print(ch, " ".join("%03X:%d" % (c, len(u.get(c, []))) for c in cs))
    for c in a.codes:
        hits = u.get(c, [])
        print("%03X %s  %d uses" % (c, kss_script.decode(t, [c]), len(hits)))
        for i, k, chars in hits[:a.n]:
            print("   %03X  %s" % (i, "".join(chars[max(0, k - a.w):k]) + "<" + chars[k] + ">"
                               + "".join(chars[k + 1:k + 1 + a.w])))


if __name__ == "__main__":
    main()
