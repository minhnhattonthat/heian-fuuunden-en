"""English lettering in compressed graphics blocks (docs/re/graphics.md, Phase 8), applied by build.py to the
unpacked blocks before gfx_blocks.pack (a block that grows moves; its pointer is in gfx_blocks.RELOC_PTRS).

G6 battle command labels, block C8:B282 (2bpp, BG3 tiles $12C+; the battle code puts the selected command's label
beside the icon column at map columns 24-28). Each label is 5 x 2 tiles = 40 x 16 px: a colour-3 frame round a
37 x 13 inner area of paper colour 2 (x 1-37, y 1-13). The tiles (block-relative, top row then bottom row) were
read from the BG3 map in the four battle_cmd_* scenes (warp.lua DUMP_PPU=1); どうぐ's (not reachable without
items) follow the same 5-tile stride. English (decision D18): the narrow 8-px font, one centred line with the caps
on rows 4-10, since "Shikigami" (47 px in the dialogue font) needs it and the five labels share one look.

    python -X utf8 tools/gfx_en.py preview OUT.png [--zoom 4]   every redrawn label from the unpacked blocks
"""
import argparse
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import font_en  # noqa: E402
from kss_comp import decode  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
PAPER, INK = 2, 3


def tile_px(b, t):
    o = 16 * t
    return [[((b[o + 2 * y] >> (7 - x)) & 1) | (((b[o + 2 * y + 1] >> (7 - x)) & 1) << 1) for x in range(8)]
            for y in range(8)]


def tile_bytes(rows):
    out = bytearray()
    for row in rows:
        out += bytes([sum((c & 1) << (7 - x) for x, c in enumerate(row)),
                      sum(((c >> 1) & 1) << (7 - x) for x, c in enumerate(row))])
    return bytes(out)


def canvas(b, rows_of_tiles):
    """Pixel rows of the tiles laid out as rows_of_tiles (lists of tile numbers, one list per 8-px row)."""
    px = []
    for tiles in rows_of_tiles:
        ts = [tile_px(b, t) for t in tiles]
        px += [sum((t[y] for t in ts), []) for y in range(8)]
    return px


def put_canvas(out, rows_of_tiles, px):
    for r, tiles in enumerate(rows_of_tiles):
        for k, t in enumerate(tiles):
            out[16 * t:16 * t + 16] = tile_bytes([px[8 * r + y][8 * k:8 * k + 8] for y in range(8)])


def line_ink(text, kind="narrow", spacing=0):
    """(width, {(x, y)}) of one line in font_en's narrow (8-px) or dialogue (16-px) font, `spacing` extra px after
    each letter."""
    gl = font_en.glyphs(kind if kind == "narrow" else False)
    ink, x = set(), 0
    for c in text:
        rows, adv = gl[ord(c) - font_en.FIRST]
        for y, m in enumerate(rows):
            for dx in range(8):
                if m & (0x80 >> dx):
                    ink.add((x + dx, y))
        x += adv + spacing
    return (max(x for x, _ in ink) + 1 if ink else 0), ink


# --- G6 battle command labels -----------------------------------------------------------------------------------
CMD_BLOCK = "08B282.bin"
CMD_LABELS = [       # (top tiles, bottom tiles, English)
    (list(range(11, 16)), list(range(27, 32)), "Attack"),        # こうげき
    (list(range(32, 37)), list(range(48, 53)), "Jutsu"),         # じゅつ
    (list(range(37, 42)), list(range(53, 58)), "Items"),         # どうぐ
    (list(range(42, 47)), list(range(58, 63)), "Shikigami"),     # しきがみ
    ([47, 64, 65, 66, 67], [63, 68, 69, 70, 71], "Wait"),        # たいき
]
CMD_INNER = (1, 1, 37, 13)   # x, y, w, h
CMD_CAP_TOP = 4


def draw_label(px, text, inner, cap_top, kind="narrow"):
    x0, y0, w, h = inner
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            px[y][x] = PAPER
    lw, ink = line_ink(text, kind)
    if lw > w:
        raise ValueError("label %r: %d px > %d" % (text, lw, w))
    left = x0 + (w - lw) // 2
    for x, y in ink:
        if not (y0 <= cap_top + y < y0 + h):
            raise ValueError("label %r: ink row %d outside the box" % (text, cap_top + y))
        px[cap_top + y][left + x] = INK


def redraw_cmd(data):
    out = bytearray(data)
    for top, bottom, text in CMD_LABELS:
        px = canvas(data, [top, bottom])
        frame = [px[0][1:38], px[14][1:38], [r[0] for r in px[1:14]], [r[38] for r in px[1:14]]]
        if any(c != INK for side in frame for c in side):
            raise ValueError("command label %r: frame not where expected" % text)
        draw_label(px, text, CMD_INNER, CMD_CAP_TOP)
        put_canvas(out, [top, bottom], px)
    return bytes(out)


def tile4_px(b, t):
    o = 32 * t
    return [[sum(((b[o + (p // 2) * 16 + 2 * y + (p & 1)] >> (7 - x)) & 1) << p for p in range(4)) for x in range(8)]
            for y in range(8)]


def tile4_bytes(rows):
    out = bytearray(32)
    for y, row in enumerate(rows):
        for p in range(4):
            out[(p // 2) * 16 + 2 * y + (p & 1)] = sum(((c >> p) & 1) << (7 - x) for x, c in enumerate(row))
    return bytes(out)


def draw_card(size, lines, ink, outline, tops):
    """size (w, h) pixel rows of colour 0 with each line in the dialogue font, bold (each ink pixel doubled to the
    right, letters 1 px further apart so they stay apart), centred, its glyph rows starting at tops[k], and a 1-px outline (8 neighbours) in `outline`."""
    w, h = size
    px = [[0] * w for _ in range(h)]
    pts = set()
    for text, top in zip(lines, tops):
        lw, gl = line_ink(text, "dialogue", spacing=1)
        left = (w - (lw + 1)) // 2
        for x, y in gl:
            pts |= {(left + x, top + y), (left + x + 1, top + y)}
    for x, y in pts:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if not (0 <= x + dx < w and 0 <= y + dy < h):
                    raise ValueError("card %r: outline leaves the %dx%d box" % (lines, w, h))
                px[y + dy][x + dx] = outline
    for x, y in pts:
        px[y][x] = ink
    return px


# --- G13 game-over card, block C8:9BAF (4bpp OBJ tiles at VRAM $4000; four 16x16 sprites at (112,111) make a
# 32x32 終 from tiles 0-7 / 16-23 in the 16-wide OBJ layout; ink colour 7 with a colour-12 outline, palette 4).
GAMEOVER_BLOCK = "089BAF.bin"
GAMEOVER_TILES = [[0, 1, 2, 3], [16, 17, 18, 19], [4, 5, 6, 7], [20, 21, 22, 23]]
GAMEOVER = (["GAME", "OVER"], 7, 12, [2, 15])


def redraw_gameover(data):
    lines, ink, outline, tops = GAMEOVER
    old = [r for row in GAMEOVER_TILES for r in zip(*[tile4_px(data, t) for t in row])]
    if {c for r in old for t in r for c in t} != {0, ink, outline}:
        raise ValueError("game-over card: colours are not the expected 0/%d/%d" % (ink, outline))
    px = draw_card((32, 32), lines, ink, outline, tops)
    out = bytearray(data)
    for r, row in enumerate(GAMEOVER_TILES):
        for k, t in enumerate(row):
            out[32 * t:32 * t + 32] = tile4_bytes([px[8 * r + y][8 * k:8 * k + 8] for y in range(8)])
    return bytes(out)


# --- G9/G10/G14 credits (decision D3: English) ------------------------------------------------------------------
# Mode 9 sub 2 (CB:E4B4 state table) decodes the credits tiles C8:C2F8 (load table C1:EFA1 entry 12: to $7F:4000,
# uploaded to BG3 VRAM $6000, $1340 bytes = tiles 0-$133) and the 32x64 map C8:CD4E (to $7E:2000). Then:
#   - title: map rows 32-33 (all 32 columns) -> BG3 row 12 ($7E:2800, $80 bytes, CB:E55E);
#   - 7 staff pages, table C1:8265 (6 bytes: src lo16 in $7E, rows, columns, VRAM word address), copied by
#     CB:E623 one at a time (the BG3 map is cleared between pages, CB:E691) and slid in by the scroll;
#   - end card: rows 40-49, columns 0-23 -> $3988 (CB:E6B7): "1995 KSS" (row 40) and 終 (rows 44-49, cols 16-21).
# The Japanese pages are vertical kanji in 16x16 cells. English: horizontal lines in the dialogue font (VWF, glyph
# rows 0-15 on a 2-tile row), role first, a half-line gap, then the names; every page is 12 columns (96 px, VRAM
# $3D0A) or 8 (64 px, $3D0C) and 16 rows, laid out afresh in the map, with the page table rewritten to match.
# Tiles are cut from the rendered map and deduplicated; the upload size in the load table grows with them (BG3
# tiles up to $37F are free: $7C00 is the BG1 map; $7F:5800+ is not used after the decode, checked with a WRAM
# access log over the whole roll). Staff names: Hepburn readings of the kanji (docs/decisions.md D19).
CREDITS_TILES = "08C2F8.bin"
CREDITS_MAP = "08CD4E.bin"
PAGE_TABLE = 0x018265          # C1:8265, 7 x 6 bytes
UPLOAD_SIZE = 0x01F021         # C1:EFA1 + 12 * 10 + 8: bytes uploaded from $7F:4000 to VRAM $6000
UPLOAD_ORIG = 0x1340
MAX_TILES = 0x380
CREDIT_PAGES = [   # (map row, map column, rows, columns, VRAM word address, lines; "" = half-line gap)
    (0, 0, 16, 12, 0x3D0A, ["Planning", "Script", "Art Director", "", "Yukio Morimoto"]),     # 企画・脚本 作画監督
    (0, 12, 16, 12, 0x3D0A, ["Planning and", "Production", "", "Hiroshi Masada"]),           # 企画・制作
    (0, 24, 16, 8, 0x3D0C, ["Production", "", "Tsuyoshi No"]),                               # 制作
    (16, 0, 16, 12, 0x3D0A, ["Art and Animation", "", "Shinichi Nitta", "Yoshito Hattori",   # 作画・動画
                             "Shuichi Kajiwara"]),
    (16, 12, 16, 12, 0x3D0A, ["Music", "", "Shinya Kurahashi", "Kinuyo Yamashita",            # 音楽
                              "Iku Mizutani"]),
    (16, 24, 16, 8, 0x3D0C, ["Executive", "Producer", "", "Isao Kato"]),                     # 製作指揮
    (48, 0, 16, 12, 0x3D0A, ["General Director", "", "Hideo Takano"]),                       # 総指揮
]
TITLE = (32, "Heian Fuuunden")         # map row, one line across all 32 columns
END_ROW, END_COLS = 40, 24             # the end-card rect: rows 40-49, columns 0-23
KSS = (40, range(0, 16))               # row and columns of the "1995 KSS" cells, kept as drawn
THE_END = (44, 16, ["THE", "END"])     # 48x48 at map row 44, column 16 (where 終 was), palette 1 as 終


def _blit_line(px, text, left, top):
    lw, gl = line_ink(text, "dialogue")
    for x, y in gl:
        px[top + y][left + x] = INK
    return lw


def the_end_px(lines):
    """48x48: two lines of bold dialogue-font caps at 24x24, doubled."""
    small = [[0] * 24 for _ in range(24)]
    for text, top in zip(lines, (-1, 10)):
        lw, gl = line_ink(text, "dialogue", spacing=1)
        left = (24 - (lw + 1)) // 2
        for x, y in gl:
            for dx in (0, 1):
                if not (0 <= top + y < 24 and 0 <= left + x + dx < 24):
                    raise ValueError("end card %r leaves the box" % text)
                small[top + y][left + x + dx] = INK
    return [[small[y // 2][x // 2] for x in range(48)] for y in range(48)]


def credits(tiles, cmap):
    """(new tiles, new map, page table bytes) from the original credits tiles and map."""
    words = list(struct.unpack("<2048H", cmap))
    px = [[0] * 256 for _ in range(512)]            # the 32x64 map as pixels
    attr = [[0] * 32 for _ in range(64)]
    owned = set()                                   # cells whose tile is drawn here (others stay blank)
    for c in KSS[1]:
        w = words[KSS[0] * 32 + c]
        if w & 0x3FF:
            tp = tile_px(tiles, w & 0x3FF)
            for y in range(8):
                px[8 * KSS[0] + y][8 * c:8 * c + 8] = tp[y]
            attr[KSS[0]][c] = w & 0xFC00
            owned.add((KSS[0], c))
    table = bytearray()
    for r0, c0, rows, cols, dst, lines in CREDIT_PAGES:
        heights = [8 if t == "" else 16 for t in lines]
        top = 8 * r0 + ((8 * rows - sum(heights)) // 2) // 8 * 8
        for t, h in zip(lines, heights):
            if t:
                lw, _ = line_ink(t, "dialogue")
                if lw > 8 * cols:
                    raise ValueError("credits line %r: %d px > %d" % (t, lw, 8 * cols))
                _blit_line(px, t, 8 * c0 + (8 * cols - lw) // 2, top)
            top += h
        owned |= {(r, c) for r in range(r0, r0 + rows) for c in range(c0, c0 + cols)}
        table += struct.pack("<HBBH", 0x2000 + 2 * (32 * r0 + c0), rows, cols, dst)
    r, text = TITLE
    lw, _ = line_ink(text, "dialogue")
    _blit_line(px, text, (256 - lw) // 2, 8 * r)
    owned |= {(r + k, c) for k in (0, 1) for c in range(32)}
    er, ec, lines = THE_END
    end = the_end_px(lines)
    for y in range(48):
        px[8 * er + y][8 * ec:8 * ec + 48] = end[y]
    for k in range(6):
        for c in range(6):
            attr[er + k][ec + c] = 0x0400
            owned.add((er + k, ec + c))
    # the end card must not show anything of the pages it overlaps
    for r in range(END_ROW, END_ROW + 10):
        for c in range(END_COLS):
            if (r, c) in owned and not (r == KSS[0] or er <= r < er + 6 and ec <= c < ec + 6) and \
                    any(px[8 * r + y][8 * c + x] for y in range(8) for x in range(8)):
                raise ValueError("credits: page ink inside the end card at row %d col %d" % (r, c))
    out_tiles, index = [bytes(16)], {bytes(16): 0}
    new = [0] * 2048
    for r in range(64):
        for c in range(32):
            data = tile_bytes([px[8 * r + y][8 * c:8 * c + 8] for y in range(8)])
            if data not in index:
                index[data] = len(out_tiles)
                out_tiles.append(data)
            new[32 * r + c] = attr[r][c] | index[data] if index[data] else 0
    if len(out_tiles) > MAX_TILES:
        raise ValueError("credits: %d tiles > %d" % (len(out_tiles), MAX_TILES))
    return b"".join(out_tiles), struct.pack("<2048H", *new), bytes(table)


def apply_blocks(gfxdir):
    gfxdir = Path(gfxdir)
    for name, fn in EDITS.items():
        p = gfxdir / name
        p.write_bytes(fn(p.read_bytes()))
    new_tiles, new_map, _ = credits((gfxdir / CREDITS_TILES).read_bytes(), (gfxdir / CREDITS_MAP).read_bytes())
    (gfxdir / CREDITS_TILES).write_bytes(new_tiles)
    (gfxdir / CREDITS_MAP).write_bytes(new_map)


def writes(rom):
    """ROM writes outside the blocks: the credits page table and upload size. `rom` = the original ROM."""
    if struct.unpack_from("<H", rom, UPLOAD_SIZE)[0] != UPLOAD_ORIG:
        raise ValueError("credits upload size is not where expected")
    if struct.unpack_from("<HBBH", rom, PAGE_TABLE) != (0x2028, 16, 12, 0x3D0A):
        raise ValueError("credits page table is not where expected")
    new_tiles, _, table = credits(decode(rom, 0x08C2F8)[0], decode(rom, 0x08CD4E)[0])
    return [(PAGE_TABLE, table), (UPLOAD_SIZE, struct.pack("<H", len(new_tiles)))]


EDITS = {CMD_BLOCK: redraw_cmd, GAMEOVER_BLOCK: redraw_gameover}


def preview(out, zoom=4, gfxdir=ROOT / "work" / "unpack" / "gfx"):
    from PIL import Image
    grey = [(0, 0, 0), (90, 90, 90), (170, 170, 170), (255, 255, 255)]
    data = redraw_cmd((Path(gfxdir) / CMD_BLOCK).read_bytes())
    img = Image.new("RGB", (44, 20 * len(CMD_LABELS)), (80, 0, 0))
    for k, (top, bottom, _) in enumerate(CMD_LABELS):
        for y, row in enumerate(canvas(data, [top, bottom])):
            for x, c in enumerate(row):
                img.putpixel((2 + x, 2 + 20 * k + y), grey[c])
    img.resize((img.width * zoom, img.height * zoom), Image.NEAREST).save(out)
    print("wrote", out)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("preview")
    p.add_argument("out")
    p.add_argument("--zoom", type=int, default=4)
    a = ap.parse_args()
    preview(a.out, a.zoom)


if __name__ == "__main__":
    sys.exit(main())
