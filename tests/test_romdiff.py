"""Phase 7 ROM check: the English and marker builds change no byte outside tools/romdiff_ranges.txt (romdiff.py),
and the check catches a stray write."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

import build  # noqa: E402

pytestmark = pytest.mark.skipif(not (build.ROM.exists() and build.ASAR.exists()),
                                reason="no ROM dump in rom/ or no asar in tools/asar/")


@pytest.mark.parametrize("mode", ["build", "marker"])
def test_build_writes_only_allowed_ranges(tmp_path, mode):
    _, out, _ = build.build(mode, path=tmp_path / ("%s.sfc" % mode))   # build() itself fails on a romdiff error
    assert build.romdiff_errors(build.ROM.read_bytes(), out) == []


def test_stray_write_is_caught():
    orig = build.ROM.read_bytes()
    bad = bytearray(orig)
    bad[0x050000] ^= 0xFF                      # graphics/data bank: no range allows it
    assert build.romdiff_errors(orig, bytes(bad))
    ranges = build.allowed_ranges()
    assert all(r.start <= r.stop - 1 for r in ranges) and len(ranges) >= 20
