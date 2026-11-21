"""Heian Fuuunden SRAM (.srm) editor: read or edit a save slot and fix its checksum (docs/re/save.md).

    python -X utf8 tools/debug/save.py show SAVE.srm [--slot 1]
    python -X utf8 tools/debug/save.py edit SAVE.srm OUT.srm [--slot 1] 132=01 138=0770 ...
    python -X utf8 tools/debug/save.py scene SAVE.srm OUT.srm NAME     # apply scenes.tsv slot edits of NAME

Offsets are into the 0x870-byte live state (000-56F = SRAM $30:6000.., 570-86F = WRAM $0D00..); a value of more
than two hex digits is written little-endian. Start from a game-written save (any run's `<rom>.srm`).
"""
import argparse
import sys
from pathlib import Path

SIZE = 0x2000
SLOT0, SLOT_LEN, HEAD, LIVE = 0x600, 0x8A0, 0x30, 0x870
SUMS = 0x5FA
SQUADS = 6

# Live-state fields (offsets into the live state), verified ones in docs/re/save.md
FIELDS = {
    "unk_000": (0x000, 1),
    "squad": (0x001, 1),        # active squad 1..6 (menu "change squad")
    "maps": (0x132, SQUADS),    # map id per squad
    "xs": (0x138, 2 * SQUADS),  # x per squad (words, pixels)
    "ys": (0x144, 2 * SQUADS),  # y per squad
    "flags": (0x240, 0x30),     # event flags (bytes)
}


def slot_base(n):
    assert 1 <= n <= 3, "slot is 1..3"
    return SLOT0 + (n - 1) * SLOT_LEN


def checksum(sram, n):
    b = slot_base(n)
    return sum(bin(x).count("1") for x in sram[b + HEAD:b + SLOT_LEN]) & 0xFFFF


def stored_checksum(sram, n):
    o = SUMS + (n - 1) * 2
    return sram[o] | sram[o + 1] << 8


def fix(sram, n):
    c = checksum(sram, n)
    o = SUMS + (n - 1) * 2
    sram[o], sram[o + 1] = c & 0xFF, c >> 8
    return c


def live(sram, n):
    b = slot_base(n) + HEAD
    return sram[b:b + LIVE]


def apply(sram, n, edits):
    b = slot_base(n) + HEAD
    for e in edits:
        off, val = e.split("=")
        off, digits = int(off, 16), val.strip()
        assert len(digits) % 2 == 0, f"odd hex length: {e}"
        data = bytes.fromhex(digits)[::-1]
        assert off + len(data) <= LIVE, f"offset past live state: {e}"
        sram[b + off:b + off + len(data)] = data
    return fix(sram, n)


def scene_edits(name):
    tsv = Path(__file__).with_name("scenes.tsv")
    for line in tsv.read_text(encoding="utf-8").splitlines():
        cols = line.split("\t")
        if cols[0] == name:
            return [e for e in cols[1].split(",") if e.strip()]
    raise SystemExit(f"scene not found: {name}")


def show(sram, n):
    lv = live(sram, n)
    ok = checksum(sram, n) == stored_checksum(sram, n)
    print(f"slot {n}: checksum stored {stored_checksum(sram, n):04X} computed {checksum(sram, n):04X} "
          f"{'ok' if ok else 'BAD'}")
    print(f"  squad {lv[1]}  maps {lv[0x132:0x138].hex(' ')}")
    xs = [lv[0x138 + 2 * i] | lv[0x139 + 2 * i] << 8 for i in range(SQUADS)]
    ys = [lv[0x144 + 2 * i] | lv[0x145 + 2 * i] << 8 for i in range(SQUADS)]
    print("  pos " + " ".join(f"({x:04X},{y:04X})" for x, y in zip(xs, ys)))
    print(f"  flags 240: {lv[0x240:0x270].hex(' ')}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["show", "edit", "scene"])
    ap.add_argument("save")
    ap.add_argument("rest", nargs="*")
    ap.add_argument("--slot", type=int, default=1)
    a = ap.parse_args()
    sram = bytearray(Path(a.save).read_bytes())
    assert len(sram) == SIZE, f"{a.save}: {len(sram)} bytes, want {SIZE}"
    if a.cmd == "show":
        show(sram, a.slot)
        return 0
    if len(a.rest) < 2:
        ap.error("edit/scene need OUT and edits or a scene name")
    out = a.rest[0]
    edits = a.rest[1:] if a.cmd == "edit" else scene_edits(a.rest[1])
    c = apply(sram, a.slot, edits)
    Path(out).write_bytes(sram)
    print(f"wrote {out}: slot {a.slot}, {len(edits)} edits, checksum {c:04X}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
