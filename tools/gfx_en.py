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
import logo_en  # noqa: E402
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
    apply_help(gfxdir)
    apply_prologue(gfxdir)
    logo_en.apply(gfxdir)


def writes(rom):
    """ROM writes outside the blocks: the credits page table and upload size. `rom` = the original ROM."""
    if struct.unpack_from("<H", rom, UPLOAD_SIZE)[0] != UPLOAD_ORIG:
        raise ValueError("credits upload size is not where expected")
    if struct.unpack_from("<HBBH", rom, PAGE_TABLE) != (0x2028, 16, 12, 0x3D0A):
        raise ValueError("credits page table is not where expected")
    new_tiles, _, table = credits(decode(rom, 0x08C2F8)[0], decode(rom, 0x08CD4E)[0])
    return [(PAGE_TABLE, table), (UPLOAD_SIZE, struct.pack("<H", len(new_tiles)))]


# --- G3/G4 file select, block C8:3E4F (4bpp BG1 tiles from 0; scroll labels on the title's New/Continue menu and
# the three file scrolls). A label is 16 px tall: row 0 is the scroll's colour-2 top line, rows 1-15 paper colour 3,
# kana in ink 1. はじめから = tiles $40-$48 over $50-$58, つづきから = $60-$68 over $70-$78 (72 px), 記録 =
# $49-$4B over $59-$5B (24 px) before the digit tiles $4C-$4E / $5C-$5E (kept). English in the dialogue font, ink 1,
# glyph rows from y 2 (caps on rows 5-13 where the kana sat on 3-14).
FILE_BLOCK = "083E4F.bin"
FILE_LABELS = [   # (top tiles, bottom tiles, English, align)
    (list(range(0x40, 0x49)), list(range(0x50, 0x59)), "New Game", "centre"),   # はじめから
    (list(range(0x60, 0x69)), list(range(0x70, 0x79)), "Continue", "centre"),   # つづきから
    ([0x49, 0x4A, 0x4B], [0x59, 0x5A, 0x5B], "File", "right"),                  # 記録 (then the digit)
]
FILE_PAPER, FILE_INK, FILE_TOP = 3, 1, 2


def redraw_file(data):
    out = bytearray(data)
    for top, bottom, text, align in FILE_LABELS:
        rows = [sum((tile4_px(data, t)[y] for t in half), []) for half in (top, bottom) for y in range(8)]
        w = len(rows[0])
        if set(rows[0]) != {2} or any(c not in (1, 2, 3) for r in rows[1:] for c in r):
            raise ValueError("file-select label %r: not the expected scroll colours" % text)
        px = [rows[0]] + [[FILE_PAPER] * w for _ in range(15)]
        lw, gl = line_ink(text, "dialogue")
        left = (w - lw) // 2 if align == "centre" else w - 4 - lw
        if left < 1:
            raise ValueError("file-select label %r: %d px does not fit %d" % (text, lw, w))
        for x, y in gl:
            px[FILE_TOP + y][left + x] = FILE_INK
        for r, half in enumerate((top, bottom)):
            for k, t in enumerate(half):
                out[32 * t:32 * t + 32] = tile4_bytes([px[8 * r + y][8 * k:8 * k + 8] for y in range(8)])
    return bytes(out)


# --- G7/T8 help panels (the "PUSH KEY" pages). Font block C8:ABF2 = 4bpp BG1 tiles $10+ (block tile k = tile
# $10 + k): frame, pad drawing, PUSH KEY, and one 8x8 kana per tile ($4D-$94, paper colour 2, ink 3; ゛ $7E and ゜
# $7F sit on the row above; $95 is an underline with a ゛). The pages are built from small LZ maps (words $20tt):
# titles 8x2 (row 0 marks, row 1 text), button labels 7x8 (text on rows 0/2/4/6 = Y/X/A/B, underline on the odd
# rows), notes 22x8 (marks on even rows, text on odd rows); C8:AA6E is the status page pre-built as one 32-wide
# map. English: Pixel Operator 8 glyphs (fonts, D10) in the kana cells, one letter per cell; the mark rows go blank.
HELP_FONT = "08ABF2.bin"
HELP_BASE = 0x10
HELP_FREE = [t for t in range(0x4D, 0x95) if t not in range(0x8B, 0x90)]  # 8B-8F = Y X A B … stay
HELP_BLANK, HELP_LINE, HELP_LINE_MARK = 0x18, 0x19, 0x95
HELP_TITLES = {"08A6CF.bin": "Battle", "08A6E9.bin": "Status", "08A706.bin": "Field", "08A724.bin": "Squads"}
# Y, X, A, B. These maps are addressed by a lo16 table at C1:478F (bank C8 fixed in code), so they cannot move to
# bank DF and must re-encode within their original size: けってい is "OK" (fewer literals than "Confirm").
HELP_LABELS = {
    "08A796.bin": ["OK", "", "", "Cancel"],
    "08A7BE.bin": ["OK", "Field", "", "Cancel"],
    "08A7F6.bin": ["Talk", "Status", "Run", ""],      # ダッシュ
    "08A824.bin": ["OK", "Field", "Switch", "Cancel"],
}
HELP_NOTES = {       # 4 lines of 22 cells; the 4th ends by cell 13 (PUSH KEY is drawn on cells 14-21 of that row)
    "08A861.bin": ["* While moving a unit,", "  B frees the cursor.", "  Y on a unit shows", "  its status."],
    "08A8EF.bin": ["* On the status screen", "  Y switches to the", "  unit's usable jutsu", "  and skills."],
    "08A973.bin": ["* Hold A while moving", "  to move faster."],
    "08A9E7.bin": ["* Press A to view the", "  status of the unit", "  under the cursor."],
}
HELP_LAST_LINE = 13
HELP_PANEL = "08AA6E.bin"          # status page as one 32-wide map: its title, labels and notes are the blocks
HELP_PANEL_PARTS = ["08A6E9.bin", "08A7BE.bin", "08A8EF.bin"]   # above, found in it by content


def help_charset():
    chars = set("".join(HELP_TITLES.values()))
    for v in list(HELP_LABELS.values()) + list(HELP_NOTES.values()):
        chars |= set("".join(v))
    chars.discard(" ")
    chars = sorted(chars)
    if len(chars) > len(HELP_FREE):
        raise ValueError("help font: %d characters > %d cells" % (len(chars), len(HELP_FREE)))
    return dict(zip(chars, HELP_FREE))


def redraw_help_font(data):
    out = bytearray(data)
    gl = font_en.glyphs(True)
    for ch, t in help_charset().items():
        rows = gl[ord(ch) - font_en.FIRST][0]
        px = [[3 if r & (0x80 >> x) else 2 for x in range(8)] for r in rows]
        k = t - HELP_BASE
        if {c for r in tile4_px(data, k) for c in r} - {2, 3}:
            raise ValueError("help font cell %02X is not a kana cell" % t)
        out[32 * k:32 * k + 32] = tile4_bytes(px)
    # the underline-with-゛ tile also becomes a plain underline, for any map that still uses it
    k, line = HELP_LINE_MARK - HELP_BASE, HELP_LINE - HELP_BASE
    out[32 * k:32 * k + 32] = data[32 * line:32 * line + 32]
    return bytes(out)


def _help_words(data):
    return list(struct.unpack("<%dH" % (len(data) // 2), data))


def _help_text_row(words, row, w, text, cmap):
    if len(text) > w:
        raise ValueError("help text %r: %d cells > %d" % (text, len(text), w))
    for c in range(w):
        i = row * w + c
        ch = text[c] if c < len(text) else " "
        words[i] = (words[i] & 0xFC00) | (HELP_BLANK if ch == " " else cmap[ch])


def redraw_help_map(name, data):
    cmap, words = help_charset(), _help_words(data)
    if name in HELP_TITLES:
        w = 8
        _help_text_row(words, 0, w, "", cmap)
        _help_text_row(words, 1, w, HELP_TITLES[name], cmap)
    elif name in HELP_LABELS:
        w = 7
        for k, text in enumerate(HELP_LABELS[name]):
            _help_text_row(words, 2 * k, w, text, cmap)
            for c in range(w):
                i = (2 * k + 1) * w + c
                if words[i] & 0x3FF == HELP_LINE_MARK:
                    words[i] = (words[i] & 0xFC00) | HELP_LINE
    else:
        w, lines = 22, HELP_NOTES[name]
        if len(lines) > 4 or (len(lines) == 4 and len(lines[3]) > HELP_LAST_LINE):
            raise ValueError("help notes %s: more than 4 lines, or the 4th runs into PUSH KEY" % name)
        for r in range(8):
            _help_text_row(words, r, w, lines[r // 2] if r % 2 and r // 2 < len(lines) else "", cmap)
    if len(words) % w:
        raise ValueError("help map %s: %d words is not %d wide" % (name, len(words), w))
    return struct.pack("<%dH" % len(words), *words)


def redraw_help_panel(data, parts_old, parts_new):
    """Replace each part (old map -> new map, widths from the part kind) where its old content sits in the panel:
    matched on the part's non-blank cells, written only over the panel's blank and kana cells (the status page
    has PUSH KEY on the notes' last row)."""
    words = _help_words(data)

    def text_cell(t):
        return t in (HELP_BLANK, HELP_LINE) or (0x4D <= t <= HELP_LINE_MARK and t not in range(0x8B, 0x90))

    for name, old, new in zip(HELP_PANEL_PARTS, parts_old, parts_new):
        w = 8 if name in HELP_TITLES else 7 if name in HELP_LABELS else 22
        o, n = _help_words(old), _help_words(new)
        h = len(o) // w
        need = [(y, x) for y in range(h) for x in range(w)      # the panel drops one ゛ the notes block has
                if o[y * w + x] & 0x3FF not in (HELP_BLANK, 0x7E, 0x7F)]
        hits = [(r, c) for r in range(len(words) // 32 - h + 1) for c in range(32 - w + 1)
                if all(words[(r + y) * 32 + c + x] & 0x3FF == o[y * w + x] & 0x3FF for y, x in need)]
        if len(hits) != 1:
            raise ValueError("help panel: part %s found %d times" % (name, len(hits)))
        r, c = hits[0]
        for y in range(h):
            for x in range(w):
                i = (r + y) * 32 + c + x
                if text_cell(words[i] & 0x3FF):
                    words[i] = (words[i] & 0xFC00) | (n[y * w + x] & 0x3FF)
                elif n[y * w + x] & 0x3FF != HELP_BLANK:
                    raise ValueError("help panel: %s text over a non-text cell at row %d col %d" % (name, r + y, c + x))
    return struct.pack("<%dH" % len(words), *words)


def apply_help(gfxdir):
    gfxdir = Path(gfxdir)
    p = gfxdir / HELP_FONT
    p.write_bytes(redraw_help_font(p.read_bytes()))
    old = {}
    for name in [*HELP_TITLES, *HELP_LABELS, *HELP_NOTES]:
        p = gfxdir / name
        old[name] = p.read_bytes()
        p.write_bytes(redraw_help_map(name, old[name]))
    p = gfxdir / HELP_PANEL
    p.write_bytes(redraw_help_panel(p.read_bytes(), [old[n] for n in HELP_PANEL_PARTS],
                                    [(gfxdir / n).read_bytes() for n in HELP_PANEL_PARTS]))


# --- G8/T7 New Game prologue (mode 0A): font C8:D140 (2bpp, $F00 bytes -> BG3 tiles 0-$EF at VRAM $6000) and map
# C8:D861 (32x32, words $20tt). Five bands of 4 tile rows from row 4: furigana on the first two, text (16 px) on the
# last two, x 32 to the line's end. The whole map is on screen from the start; an HDMA window on BG3 reveals each
# band left to right up to where its Japanese ended (x 224 for lines 1-4, x 168 for line 5), so an English line
# must end by then. Colour 3 is the text, colour 1 the highlighted names (山童, 鬼).
PRO_FONT, PRO_MAP = "08D140.bin", "08D861.bin"
PRO_LINES = [         # (text, highlighted words)
    ("Long ago there lived a people", []),
    ("called the Yamawaro, whom the", ["Yamawaro"]),
    ("villagers named oni. Despised,", ["oni"]),
    ("they made their living by spells,", []),
    ("roaming the provinces...", []),
]
PRO_END = [224, 224, 224, 224, 168]
PRO_LEFT, PRO_TEXT, PRO_HI, PRO_BLANK = 32, 3, 1, 0x2000


def prologue(font, pmap):
    px = [[0] * 256 for _ in range(256)]
    for k, ((text, hi), end) in enumerate(zip(PRO_LINES, PRO_END)):
        lw, gl = line_ink(text, "dialogue")
        if PRO_LEFT + lw > end:
            raise ValueError("prologue line %d: ends at x %d, revealed only to %d" % (k + 1, PRO_LEFT + lw, end))
        adv = font_en.glyphs(False)
        pen = [0]
        for ch in text:
            pen.append(pen[-1] + adv[ord(ch) - font_en.FIRST][1])
        spans = [(pen[text.index(w)], pen[text.index(w) + len(w)]) for w in hi]
        top = 8 * (4 * k + 6)
        for x, y in gl:
            colour = PRO_HI if any(a <= x < b for a, b in spans) else PRO_TEXT
            px[top + y][PRO_LEFT + x] = colour
    tiles, index = [bytes(16)], {bytes(16): 0}
    words = []
    for r in range(32):
        for c in range(32):
            data = tile_bytes([px[8 * r + y][8 * c:8 * c + 8] for y in range(8)])
            if data not in index:
                index[data] = len(tiles)
                tiles.append(data)
            words.append(PRO_BLANK | index[data])
    if len(tiles) * 16 > len(font):
        raise ValueError("prologue: %d tiles > %d" % (len(tiles), len(font) // 16))
    out = b"".join(tiles)
    return out + bytes(len(font) - len(out)), struct.pack("<1024H", *words)


def apply_prologue(gfxdir):
    gfxdir = Path(gfxdir)
    font, pmap = prologue((gfxdir / PRO_FONT).read_bytes(), (gfxdir / PRO_MAP).read_bytes())
    (gfxdir / PRO_FONT).write_bytes(font)
    (gfxdir / PRO_MAP).write_bytes(pmap)


EDITS = {CMD_BLOCK: redraw_cmd, GAMEOVER_BLOCK: redraw_gameover, FILE_BLOCK: redraw_file}


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
