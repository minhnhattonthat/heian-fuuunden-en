"""Pointer slots of a built ROM for `jp_left.py --slots` (phase 9 leftover-Japanese scan).

    python -X utf8 tools/jp_slots.py [ROM] [--out FILE]     (default build/heian_en.sfc -> build/jp_slots.txt)

One "SLOT TARGET" line (hex file offsets) per dialogue-table id: SLOT is the 4-byte entry in insert.PTRS
($D8:0000, address lo16 + bank word), TARGET the HiROM file offset it points at. Rows of kind `data` (still pointing
at their original bytes) are left out: they are not text. Then:
    jp_left.py build/heian_en.sfc --tbl tbl/jp.tbl --le16 --slots build/jp_slots.txt
"""
import argparse
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import insert  # noqa: E402
import kss_script  # noqa: E402
import kss_text  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


def data_ids():
    out = set()
    for rows in kss_script.load_script().values():
        for r in rows:
            if r["kind"] == "data":
                out.update(int(x, 16) for x in r["id"].split("+"))
    return out


def slots(rom):
    skip = data_ids()
    lines = []
    for i in range(kss_text.COUNT):
        if i in skip:
            continue
        slot = insert.PTRS + 4 * i
        lo, bank = struct.unpack_from("<HH", rom, slot)
        lines.append("%06X %06X" % (slot, ((bank & 0x3F) << 16) | lo))
    return lines


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("rom", nargs="?", default=str(ROOT / "build" / "heian_en.sfc"))
    ap.add_argument("--out", default=str(ROOT / "build" / "jp_slots.txt"))
    a = ap.parse_args()
    lines = slots(Path(a.rom).read_bytes())
    Path(a.out).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("%s: %d slots" % (a.out, len(lines)))


if __name__ == "__main__":
    main()
