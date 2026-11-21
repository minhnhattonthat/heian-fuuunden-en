import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

ROM = ROOT / "rom" / "Heian Fuuunden (Japan).sfc"


@pytest.mark.skipif(not ROM.exists(), reason="no ROM dump in rom/")
def test_rom_hash_matches():
    import check_rom

    check_rom.check()


@pytest.mark.skipif(not ROM.exists(), reason="no ROM dump in rom/")
def test_header_is_hirom():
    d = ROM.read_bytes()
    assert d[0xFFD5] == 0x31  # HiROM + FastROM
    complement = d[0xFFDC] | (d[0xFFDD] << 8)
    checksum = d[0xFFDE] | (d[0xFFDF] << 8)
    assert complement ^ checksum == 0xFFFF
