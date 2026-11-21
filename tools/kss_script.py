"""Dialogue script: word codec over tbl/jp.tbl, dump to script/<bank>.tsv, read it back (phase 4).

    python -X utf8 tools/kss_script.py dump [--force]   write script/C3.tsv and script/C6.tsv from the ROM
    python -X utf8 tools/kss_script.py show ID          print one id's text

Text is decoded one 16-bit word at a time (tools/tbl.py on the word's two bytes), so an unknown word becomes
`[lo][hi]` and never shifts the alignment. Control codes: {br} FE, {page} FD, {name} FC, {num} 56, {end2} FB; the
final {end} (FF) is left off the text and added back by `encode`.

TSV columns: id, kind, jp, en, max, notes
    id    the table ids pointing at the string, hex, joined with '+' when shared (e.g. `1C4+1C5`)
    kind  text, or data (decodes but is not text: the 0x4FF dummy zero run)
    max   the measured budget (phase 5); empty until measured
`dump` never overwrites English: it refuses an existing file without --force, and with --force keeps en, max and
notes of every id it finds there.
"""
import argparse
import csv
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kss_text  # noqa: E402
from tbl import Table  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
ROM = ROOT / "rom" / "Heian Fuuunden (Japan).sfc"
TBL = ROOT / "tbl" / "jp.tbl"
SCRIPT = ROOT / "script"
COLS = ["id", "kind", "jp", "en", "max", "notes"]
END = 0xFF
DATA_IDS = {0x4FF: "dummy pointer to the zero run at the C3 bank end (0x3F866), no terminator"}


def table(path=TBL):
    return Table.load(path)


def decode(t, words):
    """Words (terminator included) -> text; a final FF is dropped."""
    if words and words[-1] == END:
        words = words[:-1]
    return "".join(t.decode(struct.pack("<H", w), length=2)[0] for w in words)


def encode(t, text, terminate=True):
    """Text -> words, FF appended unless the text already ends in {end2} or terminate is False."""
    b = t.encode(text)
    if len(b) % 2:
        raise ValueError("odd byte count encoding %r" % text)
    words = list(struct.unpack("<%dH" % (len(b) // 2), b))
    if terminate and not text.endswith("{end2}"):
        words.append(END)
    return words


def id_key(ids):
    return "+".join("%03X" % i for i in ids)


def rows_from_rom(rom, t):
    """{bank: [row dicts]} in bank order."""
    out = {}
    for bank, items in kss_text.unpack(rom).items():
        rows = []
        for it in items:
            if "ids" not in it:
                continue
            data = [i for i in it["ids"] if i in DATA_IDS]
            rows.append({"id": id_key(it["ids"]), "kind": "data" if data else "text",
                         "jp": decode(t, it["words"]), "en": "", "max": "",
                         "notes": DATA_IDS[data[0]] if data else ""})
        out[bank] = rows
    return out


def read_tsv(path):
    with open(path, encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE))
    for n, r in enumerate(rows, 2):
        if None in r or None in r.values() or list(r) != COLS:
            raise ValueError("%s line %d: expected %d columns %s" % (path, n, len(COLS), COLS))
    return rows


def write_tsv(path, rows):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        w = csv.DictWriter(f, COLS, delimiter="\t", quoting=csv.QUOTE_NONE, lineterminator="\n", escapechar=None)
        w.writeheader()
        for r in rows:
            if any(c in v for v in r.values() for c in "\t\n"):
                raise ValueError("tab or newline in row %s" % r["id"])
            w.writerow(r)


def load_script(script_dir=SCRIPT):
    return {p.stem: read_tsv(p) for p in sorted(Path(script_dir).glob("*.tsv"))}


def dump(force=False, script_dir=SCRIPT):
    rom = ROM.read_bytes()
    t = table()
    Path(script_dir).mkdir(exist_ok=True)
    for bank, rows in rows_from_rom(rom, t).items():
        path = Path(script_dir) / ("%s.tsv" % bank)
        if path.exists():
            if not force:
                raise SystemExit("%s exists; --force keeps its en/max/notes and refreshes jp" % path)
            old = {r["id"]: r for r in read_tsv(path)}
            for r in rows:
                o = old.get(r["id"])
                if o:
                    r.update(en=o["en"], max=o["max"], notes=o["notes"] or r["notes"])
                    if o["jp"] != r["jp"] and o["en"]:
                        print("jp changed for translated id %s: re-check its en" % r["id"])
        write_tsv(path, rows)
        print("%s: %d strings" % (path, len(rows)))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("dump")
    d.add_argument("--force", action="store_true")
    s = sub.add_parser("show")
    s.add_argument("id", type=lambda v: int(v, 16))
    a = ap.parse_args()
    if a.cmd == "dump":
        dump(a.force)
    else:
        rom, t = ROM.read_bytes(), table()
        p = kss_text.pointers(rom)[a.id]
        base = kss_text.BANKS[kss_text.bank_of(a.id)][0]
        print(decode(t, kss_text.read_words(rom, base, p)))


if __name__ == "__main__":
    main()
