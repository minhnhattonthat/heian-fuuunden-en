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


def test_banner_offsets(rom):
    """Place/exit banners (72 px from x 88): the build centres replaced strings by whole tiles and never pushes one
    past the window; Japanese entries keep the original offsets."""
    assert rom[0x01364D:0x01364D + 4] == bytes([2, 2, 1, 1]) and rom[0x016869:0x016869 + 4] == bytes([0, 0, 1, 2])
    off = insert.banner_offsets({0x101: "Kyoto", 0x117: "{small}Toward the{sbr}San'in Road", 0x12C: "x" * 40,
                                 0x1BF: "Kada Port"})
    assert set(off) == {0x01364D, 0x016869, 0x016869 + 0x15, 0x01364D + 0x13}   # $1088 = 0x14 -> id 0x1BF
    for o, text in ((0x01364D, "Kyoto"), (0x016869, "{small}Toward the{sbr}San'in Road"), (0x01364D + 0x13, "Kada Port")):
        w = insert.drawn_px(text)
        assert off[o] * 8 + w <= insert.BANNER_PX and abs((insert.BANNER_PX - w) / 2 - off[o] * 8) <= 4, (text, off[o])
    assert off[0x016869 + 0x15] == 0      # too wide: left edge, the lint reports it
    out, _ = insert.insert(rom, "build")
    texts = {}
    for ids, _, row in insert.strings("build"):
        text = insert.text_of(row, "build")
        if text is not None:
            texts.update({i: text for i in ids})
    built = insert.banner_offsets(texts)
    for o in range(0x01364D, 0x01364D + 0x1A):   # replaced entries get their centred offset, the rest stay
        assert out[o] == built.get(o, rom[o]), hex(o)


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
            text = insert.text_of(row, mode) or row["jp"]
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
    assert insert.fit_field("Sadamitsu") == "{narrow}Sadamitsu"     # one word, too wide for both other fonts
    assert insert.fit_field("Fire Seal of Agni").startswith("{narrow}")
    with pytest.raises(ValueError):
        insert.fit_field("Fire Seal of the Burning Agni")


def test_party_fits():
    """Party list: narrow font, 40 px (5 tiles), letters only."""
    for name in ("Sadamitsu", "Yasumasa", "Semimaru", "Kagura"):
        assert insert.party_fits(name) is None, name
    assert insert.party_fits("Kagura!") is not None
    assert insert.party_fits("Sadamitsu Minamoto") is not None


def test_font_table_agree():
    t = kss_script.table(insert.EN_TBL)
    w = font_en.widths()
    for ch in w:
        if ch in "{}\x7f":
            continue
        assert t.encode(ch) == struct.pack("<H", 0x400 + ord(ch))
    assert max(w.values()) <= 8, "a glyph wider than one tile breaks VwfDraw's two-tile spill"
    assert max(font_en.widths(small=True).values()) <= 9   # ink <= 8 px (the cell); advance 9 spills one tile
    assert max(font_en.widths(small="narrow").values()) <= 9
    assert t.encode("{small}") == struct.pack("<H", 0x401) and t.encode("{sbr}") == struct.pack("<H", 0x40A)
    assert t.encode("{narrow}") == struct.pack("<H", 0x402)
    narrow = font_en.glyphs("narrow")
    for ch in insert.NARROW_CHARS - {" "}:
        assert any(narrow[ord(ch) - 0x20][0]), "narrow font has no %r" % ch


def test_hooks_assembled(built_rom):
    d = built_rom("marker")                               # built from the current sources (tests/conftest.py)
    for addr in (0x17270, 0x174F1, 0x1754D, 0x173A5, 0x175B8, 0x17564):
        assert d[addr] == 0x5C and d[addr + 3] == 0xDF, hex(addr)  # JML $DFxxxx
    assert d[0x17537:0x1753A] == bytes([0x69, 0x30, 0x04])
    for addr in (0x12C04, 0x132AE, 0x13327, 0x16011):     # party list, squad panels, name slot -> PartyName
        assert d[addr] == 0x22 and d[addr + 3] == 0xDF, hex(addr)
        assert d[addr + 1:addr + 4] == d[0x12C05:0x12C08], hex(addr)   # all the same JSL target
    for addr in (0x12C0D, 0x132B7, 0x13360):              # buffer step per slot: dw $0050
        assert d[addr:addr + 2] == bytes([0x50, 0x00]), hex(addr)
    assert d[0x1A3CB:0x1A3CF] == bytes([0x00, 0x72, 0x28, 0x72])   # 5-tile slots


def test_party_tilemaps():
    """The two party panels get 5-tile one-row slots matching the asm slot table ($7200 + n * $28)."""
    import gfx_edits
    import kss_comp
    rom = (ROOT / "rom" / "Heian Fuuunden (Japan).sfc").read_bytes()
    for name, base in gfx_edits.PARTY_PANELS.items():
        data, _ = kss_comp.decode(rom, int(name[:6], 16))
        new = gfx_edits.widen_party(data, base)
        w = struct.unpack("<%dH" % (len(new) // 2), new)
        assert [x & 0x3FF for x in w[4 * 32 + 4:4 * 32 + 9]] == [base + k for k in range(5)]
        assert [x & 0x3FF for x in w[8 * 32 + 25:8 * 32 + 30]] == [base + 35 + k for k in range(5)]
        assert not any(x & 0x3FF for x in w[5 * 32:6 * 32])        # the row under the names is blank
