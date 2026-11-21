"""English title logo (graphics.md G1, decision D23): "HEIAN / FUUUNDEN" in the original's three-colour style.

The logo is BG3 (2bpp, palette 3, priority) at screen (16,48): a 28 x 8 tile grid of unique tiles from block
C8:31F3 (VRAM $4000, tiles $200+), map row r column c = tile r*16+c (c < 16) or $80+r*16+(c-16); $FF is the blank
tile, $FC-$FE unused. Its drop shadow is the same image as sprites from block C8:0000 (VRAM $C000, 4bpp, colours
+12 = 13/14/15, dark sprite palette + colour math): 64x64 sprites at tiles 0, 8, 128 and 32x32 at 136 and 200,
placed at (19,47) (83,47) (147,47) (211,47) (211,79), so sprite-local pixels are logo pixels and the shadow falls
(+3,-1) from the logo. Neither map nor OAM changes: the English image is 224 x 64 like the original.

Style copied from the kanji: fill 1 (red), a 1 px rim of colour 2 (salmon) on the fill's right and bottom edges,
and a 1 px 8-neighbour outline of colour 3 (yellow). Font: Shojumaru (OFL, fonts/Shojumaru-Regular.ttf),
thresholded at 50% so no other colours appear; two centred lines.

    python -X utf8 tools/logo_en.py render     fonts/Shojumaru-Regular.ttf -> gfx/logo_en.png (commit the PNG)
    python -X utf8 tools/logo_en.py preview OUT.png [--zoom 4]   the committed PNG, zoomed
The build (gfx_en.apply_blocks) reads only gfx/logo_en.png.
"""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FONT = ROOT / "fonts" / "Shojumaru-Regular.ttf"
PNG = ROOT / "gfx" / "logo_en.png"
W, H = 224, 64
LINES = [("HEIAN", 36, 3), ("FUUUNDEN", 36, 1)]   # text, font px, tracking px
GAP = 2
PAL = [(60, 90, 140), (248, 40, 72), (248, 144, 104), (248, 248, 144)]   # 0 = transparent (shown as sky blue)
TILES_BLOCK, SPRITE_BLOCK = "0831F3.bin", "080000.bin"
SPRITES = [(0, 8, 0, 0), (8, 8, 64, 0), (128, 8, 128, 0), (136, 4, 192, 0), (200, 4, 192, 32)]  # tile, n, x, y
SHADOW_ADD = 12


def _line_mask(text, size, track):
    from PIL import Image, ImageDraw, ImageFont
    f = ImageFont.truetype(str(FONT), size)
    im = Image.new("L", (int(sum(f.getlength(ch) for ch in text) + track * len(text)) + 4, size * 2), 0)
    d = ImageDraw.Draw(im)
    x = 2
    for ch in text:
        d.text((x, size // 2), ch, font=f, fill=255)
        x += f.getlength(ch) + track
    im = im.point(lambda v: 255 if v >= 128 else 0)
    return im.crop(im.getbbox())


def render():
    from PIL import Image
    maxh = (H - 2 - GAP * (len(LINES) - 1)) // len(LINES)
    masks = []
    for text, size, track in LINES:
        m = _line_mask(text, size, track)
        s = min((W - 4) / m.width, maxh / m.height, 1.0)
        if s < 1.0:
            m = m.resize((round(m.width * s), round(m.height * s)), Image.LANCZOS).point(lambda v: 255 if v >= 128 else 0)
        masks.append(m)
    canvas = Image.new("L", (W, H), 0)
    y = (H - sum(m.height for m in masks) - GAP * (len(masks) - 1)) // 2
    for m in masks:
        canvas.paste(m, ((W - m.width) // 2, y))
        y += m.height + GAP
    ink = [[canvas.getpixel((x, y)) > 0 for x in range(W)] for y in range(H)]
    on = lambda x, y: 0 <= x < W and 0 <= y < H and ink[y][x]  # noqa: E731
    out = Image.new("RGB", (W, H))
    for y in range(H):
        for x in range(W):
            if ink[y][x]:
                c = 2 if not (on(x + 1, y) and on(x, y + 1)) else 1
            elif any(on(x + dx, y + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)):
                c = 3
            else:
                c = 0
            out.putpixel((x, y), PAL[c])
    PNG.parent.mkdir(exist_ok=True)
    out.save(PNG)
    print("wrote", PNG, [m.size for m in masks])


def pixels(path=PNG):
    from PIL import Image
    im = Image.open(path).convert("RGB")
    if im.size != (W, H):
        raise ValueError("%s: %s, expected %dx%d" % (path, im.size, W, H))
    index = {c: i for i, c in enumerate(PAL)}
    px = []
    for y in range(H):
        row = []
        for x in range(W):
            c = im.getpixel((x, y))
            if c not in index:
                raise ValueError("%s: colour %s at (%d,%d) is not in the logo palette" % (path, c, x, y))
            row.append(index[c])
        px.append(row)
    return px


def logo_tile(r, c):
    return r * 16 + c if c < 16 else 0x80 + r * 16 + (c - 16)


def redraw_tiles(data, px):
    out = bytearray(data)
    for r in range(H // 8):
        for c in range(W // 8):
            o = 16 * logo_tile(r, c)
            for y in range(8):
                row = px[8 * r + y][8 * c:8 * c + 8]
                out[o + 2 * y] = sum((v & 1) << (7 - x) for x, v in enumerate(row))
                out[o + 2 * y + 1] = sum((v >> 1) << (7 - x) for x, v in enumerate(row))
    return bytes(out)


def redraw_shadow(data, px):
    out = bytearray(data)
    for t0, n, lx, ly in SPRITES:
        for r in range(n):
            for c in range(n):
                o = 32 * (t0 + r * 16 + c)
                for y in range(8):
                    row = [v + SHADOW_ADD if v else 0 for v in px[ly + 8 * r + y][lx + 8 * c:lx + 8 * c + 8]]
                    for k in range(4):
                        out[o + 16 * (k // 2) + 2 * y + (k & 1)] = sum(((v >> k) & 1) << (7 - x) for x, v in enumerate(row))
    return bytes(out)


def apply(gfxdir):
    gfxdir = Path(gfxdir)
    px = pixels()
    for name, fn in ((TILES_BLOCK, redraw_tiles), (SPRITE_BLOCK, redraw_shadow)):
        p = gfxdir / name
        p.write_bytes(fn(p.read_bytes(), px))


def preview(out, zoom):
    from PIL import Image
    Image.open(PNG).resize((W * zoom, H * zoom), Image.NEAREST).save(out)
    print("wrote", out)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("render")
    p = sub.add_parser("preview")
    p.add_argument("out")
    p.add_argument("--zoom", type=int, default=4)
    a = ap.parse_args()
    if a.cmd == "render":
        render()
    else:
        preview(a.out, a.zoom)


if __name__ == "__main__":
    sys.exit(main())
