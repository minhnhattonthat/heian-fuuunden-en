# Fonts

Every font or glyph sheet the build reads ends up inside the released patch, so its licence must allow that. One row
per file; a font with no known licence doesn't go into a release.

| File | Source (URL, version) | Licence | Redistributable in a patch | Used for | Changes made |
|---|---|---|---|---|---|
| fonts/en16.png | Pixel Operator (PixelOperator.ttf) by Jayvee Enaguas, https://www.dafont.com/pixel-operator.font (2018 zip), rendered at 16 px by `tools/font_en.py render` | CC0 1.0 | yes | dialogue + menu VWF (8x16 cells, ASCII) | rendered 1 px left, thresholded to 1bpp; advance = ink + 1 px, space 4 px |
| fonts/en_narrow.png | drawn for this project: the glyph art in `tools/font_narrow.py` (no outside source) | same as the repo (own work) | yes | party-list names (always) and `{narrow}` names in 48-px fields (8x8 cells; letters, digits, space, `- . '`) | none: generated from the art; advance = ink + 1 px, space 3 px |
| fonts/en8.png | Pixel Operator 8 (PixelOperator8.ttf, same zip) by Jayvee Enaguas, rendered at 8 px by `tools/font_en.py render TTF --small` | CC0 1.0 | yes | two-line names in renderer-2 menu fields (8x8 cells, ASCII; `{small}` mode) | thresholded to 1bpp; advance = ink + 1 px, space 3 px |
| fonts/Shojumaru-Regular.ttf (licence fonts/OFL-Shojumaru.txt) -> gfx/logo_en.png | Shojumaru by Astigmatic, https://github.com/google/fonts/tree/main/ofl/shojumaru (main, 2026-11-22; sha1 85391cf2) | SIL OFL 1.1 | yes (the patch ships rendered pixels, not the font) | title logo "HEIAN / FUUUNDEN" (G1, D23), rendered by `tools/logo_en.py render` | 36 px, 3/1 px tracking, thresholded at 50%, then the logo's fill / rim / outline colours added |
