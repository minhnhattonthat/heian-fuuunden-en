"""tools/debug/save.py: slot layout, checksum (popcount of slot bytes 0x30-0x89F) and little-endian edits."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools" / "debug"))
import save  # noqa: E402


def test_checksum_and_edit():
    sram = bytearray(save.SIZE)
    base = save.slot_base(2)
    assert base == 0x600 + 0x8A0
    sram[base + 0x30] = 0xFF            # 8 bits
    sram[base + 0x89F] = 0x03           # 2 bits
    sram[base + 0x2F] = 0xFF            # header: not counted
    assert save.checksum(sram, 2) == 10
    c = save.apply(sram, 2, ["132=0B", "138=0770"])
    lv = save.live(sram, 2)
    assert lv[0x132] == 0x0B and lv[0x138:0x13A] == b"\x70\x07"
    assert c == save.stored_checksum(sram, 2) == save.checksum(sram, 2)
    assert sram[save.SUMS + 2] | sram[save.SUMS + 3] << 8 == c
