"""G1 title logo (tools/logo_en.py): the tile and shadow-sprite writers reproduce the original blocks from the
original logo's pixels, so the layout they assume (tile grid, sprite tiles, colour +12) is the game's; and the
committed English PNG stays inside the logo palette and leaves the sprite block's other tiles alone."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

import build  # noqa: E402
import logo_en  # noqa: E402
from kss_comp import decode  # noqa: E402

pytestmark = pytest.mark.skipif(not build.ROM.exists(), reason="no ROM dump in rom/")


def _blocks():
    rom = build.ROM.read_bytes()
    return decode(rom, 0x0831F3)[0], decode(rom, 0x080000)[0]


def _orig_pixels(tiles):
    px = [[0] * logo_en.W for _ in range(logo_en.H)]
    for r in range(logo_en.H // 8):
        for c in range(logo_en.W // 8):
            o = 16 * logo_en.logo_tile(r, c)
            for y in range(8):
                for x in range(8):
                    px[8 * r + y][8 * c + x] = ((tiles[o + 2 * y] >> (7 - x)) & 1) | \
                        (((tiles[o + 2 * y + 1] >> (7 - x)) & 1) << 1)
    return px


def test_writers_roundtrip_the_original_logo():
    tiles, sprites = _blocks()
    px = _orig_pixels(tiles)
    assert logo_en.redraw_tiles(tiles, px) == tiles
    assert logo_en.redraw_shadow(sprites, px) == sprites


def test_english_logo_changes_only_logo_tiles():
    tiles, sprites = _blocks()
    px = logo_en.pixels()
    new_t, new_s = logo_en.redraw_tiles(tiles, px), logo_en.redraw_shadow(sprites, px)
    assert new_t[16 * 0xFC:] == tiles[16 * 0xFC:]
    used = {t0 + r * 16 + c for t0, n, _, _ in logo_en.SPRITES for r in range(n) for c in range(n)}
    for t in range(len(sprites) // 32):
        if t not in used:
            assert new_s[32 * t:32 * t + 32] == sprites[32 * t:32 * t + 32], "sprite tile %d" % t
    assert any(v for row in px for v in row)
