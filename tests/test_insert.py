"""Phase 5 relocation: every id's 24-bit pointer reaches its string, decoded back to the text that went in; no string
crosses a bank; the English font and table agree; the assembled hooks are where docs/re/hooks.md says."""
import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import font_en  # noqa: E402
import insert  # noqa: E402
import kss_script  # noqa: E402
import kss_text  # noqa: E402

pytestmark = pytest.mark.skipif(not kss_script.ROM.exists(), reason="no ROM dump in rom/")


@pytest.fixture(scope="module")
def rom():
    return kss_script.ROM.read_bytes()


def words_at(rom, addr):
    out, j = [], addr
    while True:
        w = struct.unpack_from("<H", rom, j)[0]
        out.append(w)
        j += 2
        if w in kss_text.ENDS:
            return out, j


@pytest.mark.parametrize("mode", ["build", "marker"])
def test_pointers_reach_strings(rom, mode):
    out, stats = insert.insert(rom, mode)
    assert len(out) == insert.SIZE and stats["free"] > 0
    en_t, jp_t = kss_script.table(insert.EN_TBL), kss_script.table()
    for ids, words, row in insert.strings(mode):
        for i in ids:
            lo, bank = struct.unpack_from("<HH", out, insert.PTRS + 4 * i)
            if words is None:  # kind data: original pointer
                assert (lo, bank) == (kss_text.pointers(rom)[i], 0xC3)
                continue
            addr = ((bank & 0x3F) << 16) | lo
            assert insert.TEXT_START <= addr < insert.TEXT_END
            got, end = words_at(out, addr)
            assert got == words, row["id"]
            assert (addr >> 16) == ((end - 1) >> 16), "string %s crosses a bank" % row["id"]
            text = row["en"] or (insert.marker(row) if mode == "marker" else row["jp"])
            assert kss_script.decode(en_t if (row["en"] or mode == "marker") else jp_t, got) == \
                text.removesuffix("{end2}") + ("{end2}" if text.endswith("{end2}") else "")


def test_marker_lines_fit():
    """Marker lines stay inside the buffer they are drawn into (the VWF drops glyphs past the end)."""
    for b, rows in kss_script.load_script().items():
        if b not in kss_text.BANKS:
            continue
        for r in rows:
            m = insert.marker(r)
            if m.startswith("{small}"):
                for line in m[len("{small}"):].split("{sbr}"):
                    assert font_en.text_px(line, small=True) <= max(insert.field_px(r), insert.FIELD_PX), r["id"]
                continue
            for line in insert.CTRL.sub("\n", m).split("\n"):
                assert font_en.text_px(line) <= insert.LINE_PX, r["id"]


def test_fit_field():
    """Names: 16-px when they fit the field, else two balanced 8-px lines, else an error (never cut)."""
    assert insert.fit_field("Kagura") == "Kagura"
    assert insert.fit_field("Bronze Sword") == "{small}Bronze{sbr}Sword"
    for text in ("Suzaku Armor", "Healing Herb"):
        out = insert.fit_field(text)
        assert out.startswith("{small}")
        for line in out[len("{small}"):].split("{sbr}"):
            assert font_en.text_px(line, small=True) <= insert.FIELD_PX
    with pytest.raises(ValueError):
        insert.fit_field("Fire Seal of Agni")
    with pytest.raises(ValueError):
        insert.fit_field("Hiroyuki", 24)     # party list (3 tiles): needs the widening in docs/status.md


def test_font_table_agree():
    t = kss_script.table(insert.EN_TBL)
    w = font_en.widths()
    for ch in w:
        if ch in "{}\x7f":
            continue
        assert t.encode(ch) == struct.pack("<H", 0x400 + ord(ch))
    assert max(w.values()) <= 8, "a glyph wider than one tile breaks VwfDraw's two-tile spill"
    assert max(font_en.widths(small=True).values()) <= 9   # ink <= 8 px (the cell); advance 9 spills one tile
    assert t.encode("{small}") == struct.pack("<H", 0x401) and t.encode("{sbr}") == struct.pack("<H", 0x40A)


def test_hooks_assembled():
    built = ROOT / "build" / "heian_marker.sfc"
    if not built.exists():
        pytest.skip("no marker build")
    d = built.read_bytes()
    for addr in (0x17270, 0x174F1, 0x1754D, 0x173A5, 0x175B8, 0x17564):
        assert d[addr] == 0x5C and d[addr + 3] == 0xDF, hex(addr)  # JML $DFxxxx
    assert d[0x17537:0x1753A] == bytes([0x69, 0x30, 0x04])
