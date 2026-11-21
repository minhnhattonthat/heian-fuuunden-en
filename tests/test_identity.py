"""Phase 3 identity build: unpack -> repack with no edits gives the original ROM, and the packers handle edits."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

import bps  # noqa: E402
import build  # noqa: E402
import gfx_blocks  # noqa: E402
import kss_comp  # noqa: E402
import kss_text  # noqa: E402

pytestmark = pytest.mark.skipif(not build.ROM.exists(), reason="no ROM dump in rom/")


def test_identity_build(tmp_path):
    out, rom, stats = build.identity(workdir=tmp_path)
    assert stats["kept"] == len(gfx_blocks.blocks())
    assert out == rom


def test_every_block_roundtrips_through_the_encoder(tmp_path):
    rom = build.ROM.read_bytes()
    gfx_blocks.unpack(rom, tmp_path)
    out, stats = gfx_blocks.pack(rom, tmp_path, recompress=True)  # raises on any roundtrip failure
    assert out == rom
    assert stats["encoded"] == len(gfx_blocks.blocks())
    assert stats["exact"] >= 302  # all type 0 and 2 blocks, 187 of 426 LZ blocks


def test_header_checksum_rule():
    rom = build.ROM.read_bytes()
    assert bps.snes_checksum(rom)[0] == rom  # mirrored sum for 1.5 MB reproduces $F5A2


def test_text_edit_moves_later_strings():
    rom = build.ROM.read_bytes()
    layout = kss_text.unpack(rom)
    items = layout["C6"]
    first = next(it for it in items if "ids" in it)
    target = first["ids"][0]
    before = {i: kss_text.read_words(rom, kss_text.BANKS[kss_text.bank_of(i)][0], p)
              for i, p in enumerate(kss_text.pointers(rom))}
    first["words"] = [0x01, 0x02] + first["words"]
    tail = items[-1]
    assert "raw" in tail and len(tail["raw"]) >= 8
    tail["raw"] = tail["raw"][8:]  # the 92 unreferenced bytes at the end of C6 absorb the growth
    out = kss_text.pack(rom, layout)
    after = {i: kss_text.read_words(out, kss_text.BANKS[kss_text.bank_of(i)][0], p)
             for i, p in enumerate(kss_text.pointers(out))}
    assert after[target] == [0x01, 0x02] + before[target]
    assert all(after[i] == before[i] for i in before if i != target and i not in first["ids"])


def test_text_overflow_is_refused():
    rom = build.ROM.read_bytes()
    layout = kss_text.unpack(rom)
    next(it for it in layout["C6"] if "ids" in it)["words"] += [0] * 64
    with pytest.raises(ValueError, match="overflows"):
        kss_text.pack(rom, layout)


def test_block_edit_lands_in_rom(tmp_path):
    rom = build.ROM.read_bytes()
    gfx_blocks.unpack(rom, tmp_path)
    for off, typ, packed, size in gfx_blocks.blocks():
        f = tmp_path / gfx_blocks.name(off)
        data = bytearray(f.read_bytes())
        data[0] ^= 0xFF
        if len(kss_comp.encode(typ, bytes(data))) <= packed:
            f.write_bytes(bytes(data))
            break
    else:
        pytest.fail("no block could take a one-byte edit in place")
    out, stats = gfx_blocks.pack(rom, tmp_path)
    assert stats["encoded"] == 1
    assert kss_comp.decode(out, off)[0] == bytes(data)
