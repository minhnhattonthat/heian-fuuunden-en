"""Phase 4 extract: tbl/jp.tbl decodes every string, re-encoding gives the original words, script/ matches the
ROM, and the text banks are fully covered (every byte is a string or a known, explained raw run)."""
import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import kss_script  # noqa: E402
import kss_text  # noqa: E402
import tilemap_text  # noqa: E402

pytestmark = pytest.mark.skipif(not kss_script.ROM.exists(), reason="no ROM dump in rom/")

# Bytes in the text banks that no table pointer reaches, each explained (docs/re/text.md §Text ranges).
RAW_RUNS = {
    ("C3", 0x3143A): (2, "orphan FF terminator, no pointer"),
    ("C3", 0x33AA4): (12, "orphan string ・・・・。, no 16- or 24-bit reference anywhere"),
    ("C3", 0x33B98): (12, "orphan string ・・・・。, no 16- or 24-bit reference anywhere"),
    ("C3", 0x347CC): (18, "orphan string おいていくぞ！！, no reference anywhere"),
    ("C6", 0x6FFA4): (92, "zero fill to the bank end"),
}


@pytest.fixture(scope="module")
def rom():
    return kss_script.ROM.read_bytes()


@pytest.fixture(scope="module")
def table():
    return kss_script.table()


@pytest.fixture(scope="module")
def layout(rom):
    return kss_text.unpack(rom)


def strings(layout):
    for bank, items in layout.items():
        for it in items:
            if "ids" in it:
                yield bank, it


def test_table_covers_every_glyph_and_control(table):
    for code in list(range(0x00, 0x56)) + list(range(0x58, 0x377)) + list(range(0x380, 0x3B7)):
        if code in (0x56, 0xFB, 0xFC, 0xFD, 0xFE, 0xFF):
            continue
        assert struct.pack("<H", code) in table.dec, "code %03X has no character" % code
    for code, name in ((0x56, "num"), (0xFB, "end2"), (0xFC, "name"), (0xFD, "page"), (0xFE, "br"), (0xFF, "end")):
        assert table.ctrl[struct.pack("<H", code)] == (name, 0)


def test_every_string_roundtrips(layout, table):
    n = 0
    for bank, it in strings(layout):
        words = it["words"]
        text = kss_script.decode(table, words)
        again = kss_script.encode(table, text, terminate=words[-1] in kss_text.ENDS)
        assert again == words, "id %s: %r" % (kss_script.id_key(it["ids"]), text)
        n += len(it["ids"])
    assert n == kss_text.COUNT


def test_no_unknown_codes_in_text(layout, table):
    for bank, it in strings(layout):
        text = kss_script.decode(table, it["words"])
        assert "[" not in text, "id %s has an unknown code: %r" % (kss_script.id_key(it["ids"]), text)


def test_script_files_match_the_rom(rom, table):
    script = kss_script.load_script()
    want = kss_script.rows_from_rom(rom, table)
    for bank in ("C3", "C6"):
        have = script[bank]
        assert [r["id"] for r in have] == [r["id"] for r in want[bank]], bank
        for h, w in zip(have, want[bank]):
            assert (h["kind"], h["jp"]) == (w["kind"], w["jp"]), "%s: regenerate with dump --force" % h["id"]
    ids = [int(i, 16) for b in ("C3", "C6") for r in script[b] for i in r["id"].split("+")]
    assert sorted(ids) == list(range(kss_text.COUNT))


def test_text_banks_fully_covered(layout):
    found = {}
    for bank, items in layout.items():
        base, pos = kss_text.BANKS[bank]
        for it in items:
            if "raw" in it:
                found[(bank, pos)] = len(it["raw"]) // 2
                pos += len(it["raw"]) // 2
            else:
                pos += 2 * len(it["words"])
        assert pos == base + 0x10000, "%s items end at %X, not the bank end" % (bank, pos)
    assert found == {k: v[0] for k, v in RAW_RUNS.items()}


def test_orphan_runs_have_no_reference(rom):
    for (bank, off), (size, why) in RAW_RUNS.items():
        if "orphan" not in why:
            continue
        ptr = off & 0xFFFF
        assert bytes([ptr & 0xFF, ptr >> 8, 0xC0 | (off >> 16)]) not in rom, "%X has a 24-bit reference" % off
        table = struct.unpack_from("<%dH" % kss_text.COUNT, rom, kss_text.TABLE)
        assert ptr not in table


def test_data_rows_are_marked(layout, table):
    script = {r["id"]: r for b in ("C3", "C6") for r in kss_script.load_script()[b]}
    for i in kss_script.DATA_IDS:
        row = next(r for k, r in script.items() if "%03X" % i in k.split("+"))
        assert row["kind"] == "data" and row["en"] == ""


def test_tilemap_text_matches_the_rom(rom):
    have = kss_script.read_tsv(kss_script.SCRIPT / "tilemaps.tsv")
    want = tilemap_text.entries(rom)
    assert [(r["id"], r["jp"]) for r in have] == [(e["id"], e["jp"]) for e in want]
    assert {r["id"].rstrip("0123456789") for r in have} == {"caption", "save", "option", "quit", "saved"}


def test_dump_refuses_to_clobber(tmp_path):
    (tmp_path / "C3.tsv").write_text("x\n", encoding="utf-8")
    with pytest.raises(SystemExit):
        kss_script.dump(force=False, script_dir=tmp_path)


def test_dump_force_keeps_english(tmp_path, rom, table):
    kss_script.dump(script_dir=tmp_path)
    rows = kss_script.read_tsv(tmp_path / "C6.tsv")
    rows[5]["en"], rows[5]["notes"] = "Kept.", "note"
    kss_script.write_tsv(tmp_path / "C6.tsv", rows)
    kss_script.dump(force=True, script_dir=tmp_path)
    again = kss_script.read_tsv(tmp_path / "C6.tsv")
    assert (again[5]["en"], again[5]["notes"]) == ("Kept.", "note")
