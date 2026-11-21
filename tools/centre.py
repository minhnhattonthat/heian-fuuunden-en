"""Leading/trailing blanks the Japanese uses for layout, carried into the English (decision D15).

    python -X utf8 tools/centre.py           rewrite `en` of every LAYOUT row in script/*.tsv (idempotent)
    python -X utf8 tools/centre.py --check   list rows whose `en` differs from the layout; exit 1 if any

The Japanese centres short one-line messages (battle popups, the save prompt, the prologue cards) with full-width
indents. The English is laid out here, never by hand, so a later wording change only needs a re-run:
- CENTRE rows: each line's leading spaces are recomputed to centre it in the row's box (spaces are 4 px). A line
  with `{name}` is centred for a typical name of its class (median width), but never pushed so far that the widest
  name would run past the box. An empty line (the prologue cards' blank first line) stays empty.
- INDENT rows: the Japanese indent is kept as pixels (one full-width blank = 16 px = 4 spaces).
- FIXED rows: a set layout (the yes/no line puts each option where the cursor expects it).
- Any row whose Japanese ends in a blank keeps one trailing space (the lint's blank check, lint.blank_errors).
- Renderer-2 popups (lint.POPUPS) are padded with spaces to the window width: MenuEnd uploads only the tiles the
  text covers, and a short line otherwise leaves a see-through hole in the window.
"""
import re
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import font_en  # noqa: E402
import insert  # noqa: E402
import kss_script  # noqa: E402
import kss_text  # noqa: E402

SPACE_PX = font_en.text_px(" ")
BLANKS = " 　"
DIALOGUE = 176
# id -> box px. Battle messages and the province card share the battle box (VWF buffer 176 px, centred in the
# ~200-px frame: windows.md); 243 is the 112-px save popup.
CENTRE = {
    **{i: DIALOGUE for i in (0x1B9, 0x1C5, 0x227, 0x228, 0x229, 0x248, 0x249, 0x289, 0x28A, 0x293, 0x294, 0x296)},
    **{i: DIALOGUE for i in range(0x204, 0x226) if i != 0x210},
    0x243: 112,
}
INDENT = {0x245, 0x246}
# 28E yes/no (windows.md): the cursor sits at +10..16 and +58..64 px, so Yes starts at +24 and No at +72.
FIXED = {0x28E: " " * 6 + "Yes" + " " * ((72 - 24 - font_en.text_px("Yes")) // SPACE_PX) + "No"}
LINE = re.compile(r"(\{br\}|\{page\})")
END = re.compile(r"(\{end2?\})+$")


def ends(text):
    """(body, end codes) of a string."""
    m = END.search(text)
    return (text[:m.start()], m.group()) if m else (text, "")


def name_widths(rows, row):
    """(typical, widest) px of what `{name}` stands for in `row`."""
    import lint  # lint imports this module
    cls = lint.NAME_CLASSES.get(insert.ids_of(row)[0], insert.PARTY_IDS)
    w = [font_en.text_px(r["en"]) for r in rows if r["en"] and r["kind"] != "data"
         and any(cls[0] <= i <= cls[1] for i in insert.ids_of(r))]
    return (statistics.median(w) if w else 64), lint.name_px(rows, row)


def centre_line(line, box, typ, widest):
    import lint
    line = line.lstrip(" ")
    if not line:
        return line
    free = min((box - lint.line_px(line, typ)) / 2, box - lint.line_px(line, widest))
    return " " * max(0, int(free // SPACE_PX)) + line


def layout(row, rows):
    """The `en` this row should have, or None if it is not a layout row."""
    rid = insert.ids_of(row)[0]
    if not row["en"] or row["kind"] == "data" or insert.is_field(row):
        return None
    body, end = ends(row["en"])
    trail = ends(row["jp"])[0][-1:] in tuple(BLANKS)
    import lint
    pop = lint.popup(row)
    if not (rid in CENTRE or rid in INDENT or rid in FIXED or pop):
        return body.rstrip(" ") + " " + end if trail else None
    body = body.rstrip(" ")
    if rid in FIXED:
        body = FIXED[rid]
    elif rid in INDENT:
        jp_body = ends(row["jp"])[0]
        n = len(jp_body) - len(jp_body.lstrip(BLANKS))
        body = " " * (n * 16 // SPACE_PX) + body.lstrip(" ")
    elif rid in CENTRE:
        typ, widest = name_widths(rows, row) if "{name}" in body else (0, 0)
        parts = LINE.split(body)
        body = "".join(p if LINE.fullmatch(p) else centre_line(p, CENTRE[rid], typ, widest) for p in parts)
    if pop and "{" not in body:
        # renderer-2 popup: MenuEnd uploads only the tiles the text covers, so pad to the window width or the rest
        # of the window shows through as a hole (the Japanese fills it with blanks)
        return body + " " * ((pop[0] - font_en.text_px(body)) // SPACE_PX) + end
    return body + (" " if trail else "") + end


def main():
    check = "--check" in sys.argv
    script = kss_script.load_script()
    rows = [r for b, rs in script.items() if b in kss_text.BANKS for r in rs]
    bad = 0
    for bank, rs in script.items():
        if bank not in kss_text.BANKS:
            continue
        changed = False
        for r in rs:
            want = layout(r, rows)
            if want is not None and want != r["en"]:
                bad += 1
                print("%s %s: %r -> %r" % (bank, r["id"], r["en"], want))
                r["en"], changed = want, True
        if changed and not check:
            kss_script.write_tsv(kss_script.SCRIPT / (bank + ".tsv"), rs)
    print("centre: %d rows %s" % (bad, "differ" if check else "rewritten"))
    sys.exit(1 if check and bad else 0)


if __name__ == "__main__":
    main()
