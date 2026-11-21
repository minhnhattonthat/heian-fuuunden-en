import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import kss_comp  # noqa: E402
import smallfont  # noqa: E402
import textmap  # noqa: E402

pytestmark = pytest.mark.skipif(not textmap.ROM.exists(), reason="no ROM dump in rom/")


def test_logged_blocks_chain_exactly():
    # Sources the game decompressed (work/qa/dec_*): each block ends where the next one starts.
    d = textmap.ROM.read_bytes()
    chain = [0x80000, 0x80E29, 0x80EAD, 0x80F1C, 0x81037, 0x81156, 0x81206, 0x831F3]
    for a, b in zip(chain, chain[1:]):
        out, n = kss_comp.decode(d, a)
        assert a + n == b
    assert len(kss_comp.decode(d, 0x88954)[0]) == 0x1600  # small font, DMA'd as 0x1600 bytes


def test_save_menu_tilemap_text():
    d = textmap.ROM.read_bytes()
    out, _ = kss_comp.decode(d, 0x871C2)
    words = [out[i] | out[i + 1] << 8 for i in range(0, 16, 2)]
    assert smallfont.text(words) == "きろくしておわる"


def test_menu_caption_table():
    d = textmap.ROM.read_bytes()
    words = [d[0x19E8B + 2 * i] | d[0x19E8C + 2 * i] << 8 for i in range(10)]
    assert smallfont.text(words) == "どうぐを　つかいます"
