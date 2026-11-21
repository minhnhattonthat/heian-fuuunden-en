"""Text lint (phase 5 width gate -> phase 7): per-row budgets from docs/re/windows.md, checked on every `en`.

    python -X utf8 tools/lint.py            errors + one summary line; exit 1 on any error
    python -X utf8 tools/lint.py --max      also write each row's budget into the `max` column of script/*.tsv
    python -X utf8 tools/lint.py --strict   untranslated rows (jp with empty en, not in script/keep_jp.txt) are errors

Budgets (px = English VWF pixels, tools/font_en.text_px):
- dialogue (every row that is not a field or popup): 176 px per line, 160 on the line before `{page}` when it is the
  page's 3rd line (the ▼ arrow), 3 lines per page; `{name}` counts as the widest name, `{num}` as "99999".
  Palace ids 297-2A5 (`SPEAKER`): a speaker line first, not counted in the 3.
- renderer-2 fields (insert.FIELDS): fit_field must succeed (one 16-px line or two 8-px lines).
- party names (insert.PARTY_IDS): insert.party_fits (40 px, narrow font, letters only).
- popups (POPUPS): one line of the window's width.
Plus: control codes other than line/page breaks match the Japanese as a multiset; text encodes with tbl/en.tbl; no
Japanese left in `en`; no ordinal suffix glued to a variable; no stub last line (< 6 chars) in a multi-line page;
leading/trailing blanks kept where the Japanese has them, centred rows match tools/centre.py (blank_errors, D15).
- tilemap text (script/tilemaps.tsv, check_tilemap): one 8-px cell per character within the `max` cell budget.
Warnings (printed, not errors): a page that ends mid-clause before a `{page}` (page_warnings; PAGE_WAIVED skips).
"""
import collections
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import centre  # noqa: E402
import font_en  # noqa: E402
import insert  # noqa: E402
import kss_script  # noqa: E402
import kss_text  # noqa: E402
import smallfont_en  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
KEEP = ROOT / "script" / "keep_jp.txt"
LINE_PX, LAST_PX, LINES = 176, 160, 3
# (first id, last id, px, state): single-line renderer-2 popups (windows.md)
POPUPS = [
    (0x28B, 0x28B, 112, "measured"),
    # 243/244: the save-menu window shows 15 tiles (the Japanese uploads 10 x 12 px); a 109-px pad left tile 15 as a
    # see-through hole (phase 8, work/qa/qa_pad, D21)
    (0x243, 0x243, 120, "measured"), (0x244, 0x244, 120, "measured"),
    (0x1C8, 0x1C9, 128, "measured"),
    (0x28D, 0x28E, 112, "measured"),
]
# Palace scene (windows.md): every page starts with the speaker's name on its own line, then up to 3 lines. No code
# or script reaches these ids (cut scene); the normal box shows 3 rows, so they are linted as speaker + 3.
SPEAKER = (0x297, 0x2A5)
BREAKS = {"{br}", "{page}"}
LAYOUT = {"{small}", "{sbr}", "{narrow}"}
CTRL = re.compile(r"\{\w+\}")
JP = re.compile(r"[　-ヿ一-鿿＀-￯]")
ORDINAL = re.compile(r"\{(?:num|name)\}(?:st|nd|rd|th)\b")
NUM_PX = font_en.text_px("99999")
TILEMAPS = "tilemaps"                    # script/tilemaps.tsv: small-font tilemap text, budgets in cells
TILE_CELLS = re.compile(r"(\d+)(?:x(\d+))? cells")
# Rows whose sentences run across `{page}` on purpose (page_warnings skips them): the spell chants are paced one
# phrase per box, as in the Japanese.
PAGE_WAIVED = {"1CA", "1CB", "1D1", "1D2", "1D3"}


def popup(row):
    hit = [(px, st) for i in insert.ids_of(row) for lo, hi, px, st in POPUPS if lo <= i <= hi]
    return min(hit) if hit else None


# Rows whose `{name}` can only be one kind of name, read from the Japanese around it: {row id: (first, last) name
# ids}. Every other row gets the widest name of all. Squad messages ({name}部隊) name the leader by the short party
# name; 214 summons a shikigami; 112/218/21E name an item; 1B9 (province card, windows.md) a province.
NAME_CLASSES = {
    **{i: insert.PARTY_IDS for i in (0x1BC, 0x222, 0x224, 0x225, 0x22F)},
    0x214: (0x182, 0x1A6),
    **{i: (0x001, 0x053) for i in (0x112, 0x218, 0x21E)},
    0x1B9: (0x24A, 0x288),
}


def name_px(rows, row=None):
    """Widest English name `{name}` can stand for in `row` (fields and party names in the 16-px dialogue font): the
    row's NAME_CLASSES range, else every name; 64 px until names are translated."""
    cls = NAME_CLASSES.get(insert.ids_of(row)[0]) if row else None
    w = [font_en.text_px(r["en"]) for r in rows if r["en"] and (insert.is_field(r) or any(
        insert.PARTY_IDS[0] <= i <= insert.PARTY_IDS[1] for i in insert.ids_of(r)))
        and (cls is None or any(cls[0] <= i <= cls[1] for i in insert.ids_of(r)))]
    return max(w + [64])


def budget(row):
    """Short budget label for the `max` column."""
    if any(insert.PARTY_IDS[0] <= i <= insert.PARTY_IDS[1] for i in insert.ids_of(row)):
        return "%d narrow" % insert.PARTY_PX
    if insert.is_field(row):
        return "%d field" % insert.field_px(row)
    p = popup(row)
    if p:
        return "%d popup%s" % (p[0], "" if p[1] == "measured" else " (guess)")
    return "%s%d/%d x%d" % ("speaker + " if speaker(row) else "", LINE_PX, LAST_PX, LINES)


def speaker(row):
    return any(SPEAKER[0] <= i <= SPEAKER[1] for i in insert.ids_of(row))


def line_px(line, npx):
    return (font_en.text_px(CTRL.sub("", line)) + npx * line.count("{name}") + NUM_PX * line.count("{num}"))


def check_row(row, npx, en_t):
    """Error strings for one row's `en`."""
    en, err = row["en"], []
    if JP.search(en):
        err.append("Japanese left in en")
    try:
        kss_script.encode(en_t, en)
    except Exception as e:  # noqa: BLE001 - the table codec raises several types
        err.append("does not encode: %s" % e)
    codes = lambda s: collections.Counter(c for c in CTRL.findall(s) if c not in BREAKS | LAYOUT)  # noqa: E731
    if codes(en) != codes(row["jp"]):
        err.append("control codes %s != jp %s" % (dict(codes(en)), dict(codes(row["jp"]))))
    if ORDINAL.search(en):
        err.append("ordinal suffix after a variable")
    ids = insert.ids_of(row)
    if any(insert.PARTY_IDS[0] <= i <= insert.PARTY_IDS[1] for i in ids) and insert.party_fits(en):
        err.append(insert.party_fits(en))
    if insert.is_field(row):
        if "{" not in en:
            try:
                insert.fit_field(en, insert.field_px(row))
            except ValueError as e:
                err.append(str(e))
        return err
    p = popup(row)
    if p:
        if "{br}" in en or "{page}" in en or line_px(en, npx) > p[0]:
            err.append("%d px, popup %d (one line)" % (line_px(en, npx), p[0]))
        return err
    pages = en.split("{page}")
    for pi, page in enumerate(pages):
        lines = page.split("{br}")
        if speaker(row):
            if line_px(lines[0], npx) > LINE_PX:
                err.append("page %d speaker line: %d px > %d" % (pi + 1, line_px(lines[0], npx), LINE_PX))
            lines = lines[1:]
        if len(lines) > LINES:
            err.append("page %d has %d lines (max %d)" % (pi + 1, len(lines), LINES))
        for k, line in enumerate(lines):
            limit = LAST_PX if (k == LINES - 1 and pi < len(pages) - 1) else LINE_PX
            if line_px(line, npx) > limit:
                err.append("page %d line %d: %d px > %d" % (pi + 1, k + 1, line_px(line, npx), limit))
        if len(lines) > 1 and 0 < len(CTRL.sub("", lines[-1]).strip()) < 6:
            err.append("page %d: stub last line %r" % (pi + 1, lines[-1]))
    return err


def check_tilemap(row):
    """Error strings for a small-font tilemap row (script/tilemaps.tsv, graphics text drawn in phase 8): one 8-px cell
    per character, `{br}` starts the next row pair; the budget is the `max` column ("18x2 cells" = 2 rows of 18,
    "10 cells", "8 cells + values" = 8 before the value tiles)."""
    m = TILE_CELLS.match(row["max"])
    if not m:
        return ["max %r is not a cell budget" % row["max"]]
    width, nrows = int(m.group(1)), int(m.group(2) or 1)
    lines, err = row["en"].split("{br}"), []
    try:
        smallfont_en.cells_of(row["en"].replace("{br}", ""))
    except ValueError as e:
        err.append(str(e))
    if len(lines) > nrows:
        err.append("%d rows > %d" % (len(lines), nrows))
    err += ["row %d: %d cells > %d" % (k + 1, len(ln), width) for k, ln in enumerate(lines) if len(ln) > width]
    return err


def page_warnings(en):
    """Pages that end mid-clause (`,` `;` or a bare word) where the next page goes on in lower case (glossary style
    rule: a sentence never runs across a `{page}` break mid-clause). Warnings, not errors."""
    plain = [CTRL.sub("", p.replace("{name}", "Name").replace("{num}", "9")).strip() for p in en.split("{page}")]
    return ["page %d ends mid-clause: ...%s" % (k + 1, a[-24:]) for k, (a, b) in enumerate(zip(plain, plain[1:]))
            if a and b and (a[-1] in ",;" or a[-1].isalpha()) and b[0].islower()]


def blank_errors(row, rows):
    """Leading/trailing blanks (pipeline §Checks): a centred, indented or fixed layout row (tools/centre.py, D15)
    must match its computed layout; any other non-field row keeps a leading/trailing blank where the Japanese has
    one (a leading `{br}`, an empty first line, counts as a leading blank). Field rows are exempt: fit_field lays
    them out."""
    if insert.is_field(row) or row["kind"] == "data":
        return []
    want = centre.layout(row, rows)
    if want is not None:
        return [] if want == row["en"] else ["layout %r != %r (run tools/centre.py)" % (row["en"], want)]
    jp, en = centre.ends(row["jp"])[0], centre.ends(row["en"])[0]
    err = []
    if jp[:1] in tuple(centre.BLANKS) and not (en[:1] == " " or en.startswith("{br}")):
        err.append("Japanese starts with a blank, English does not (add the row to tools/centre.py)")
    if jp[-1:] in tuple(centre.BLANKS) and en[-1:] != " ":
        err.append("Japanese ends with a blank, English does not")
    return err


def run(strict=False, write_max=False, script_dir=None, warnings=None):
    """(errors, untranslated count); errors = ["<file> <id>: <message>"]. Page-break warnings go to `warnings`."""
    script = kss_script.load_script(script_dir or kss_script.SCRIPT)
    rows = [r for b, rs in script.items() if b in kss_text.BANKS for r in rs]
    npx, en_t = name_px(rows), kss_script.table(insert.EN_TBL)
    keep = set()
    if KEEP.exists():
        keep = {ln.split()[0] for ln in KEEP.read_text(encoding="utf-8").splitlines() if ln.strip() and ln[0] != "#"}
    errors, todo = [], 0
    for r in script.get(TILEMAPS, []):
        if r["en"]:
            errors += ["%s %s: %s" % (TILEMAPS, r["id"], e) for e in check_tilemap(r)]
        elif r["jp"].strip() and r["id"] not in keep:
            todo += 1
            if strict:
                errors.append("%s %s: untranslated" % (TILEMAPS, r["id"]))
    for bank, rs in script.items():
        if bank not in kss_text.BANKS:
            continue
        for r in rs:
            if r["kind"] == "data":
                continue
            if write_max:
                r["max"] = budget(r)
            if not r["en"]:
                if r["jp"].strip() and r["id"] not in keep:
                    todo += 1
                    if strict:
                        errors.append("%s %s: untranslated" % (bank, r["id"]))
                continue
            rpx = name_px(rows, r) if "{name}" in r["en"] else npx
            errors += ["%s %s: %s" % (bank, r["id"], e) for e in check_row(r, rpx, en_t) + blank_errors(r, rows)]
            if warnings is not None and r["id"] not in PAGE_WAIVED:
                warnings += ["%s %s: %s" % (bank, r["id"], w) for w in page_warnings(r["en"])]
        if write_max:
            kss_script.write_tsv(Path(script_dir or kss_script.SCRIPT) / (bank + ".tsv"), rs)
    return errors, todo


def main():
    strict, write_max = "--strict" in sys.argv, "--max" in sys.argv
    warnings = []
    errors, todo = run(strict, write_max, warnings=warnings)
    for w in warnings:
        print("warn:", w)
    for e in errors:
        print(e)
    print("lint: %d errors, %d warnings, %d rows untranslated%s"
          % (len(errors), len(warnings), todo, " (errors)" if strict else ""))
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
