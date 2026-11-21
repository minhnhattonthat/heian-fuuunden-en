"""Find byte patterns in the original ROM; print HiROM CPU addresses.

    python tools/romgrep.py HEX [HEX..] [--rom F] [--max N]
"""
import argparse
import re

ap = argparse.ArgumentParser()
ap.add_argument("pats", nargs="+")
ap.add_argument("--rom", default="rom/Heian Fuuunden (Japan).sfc")
ap.add_argument("--max", type=int, default=60)
a = ap.parse_args()
d = open(a.rom, "rb").read()
for pat in a.pats:
    b = bytes.fromhex(pat)
    hits = [m.start() for m in re.finditer(re.escape(b), d)]
    print(pat, len(hits), " ".join("%06X" % (0xC00000 + h) for h in hits[: a.max]))
