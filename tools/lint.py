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
Japanese left in `en`; no ordinal suffix glued to a variable; no stub last line (< 6 chars) in a multi-line page.
"""
import collections
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import font_en  # noqa: E402
import insert  # noqa: E402
import kss_script  # noqa: E402
import kss_text  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
KEEP = ROOT / "script" / "keep_jp.txt"
LINE_PX, LAST_PX, LINES = 176, 160, 3
# (first id, last id, px, state): single-line renderer-2 popups (windows.md)
POPUPS = [
    (0x28B, 0x28B, 112, "measured"), (0x243, 0x243, 112, "measured"),
    (0x244, 0x244, 112, "measured"),
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


def popup(row):
    hit = [(px, st) for i in insert.ids_of(row) for lo, hi, px, st in POPUPS if lo <= i <= hi]
    return min(hit) if hit else None


def name_px(rows):
    """Widest English name `{name}` can stand for (fields and party names in the 16-px dialogue font); 64 px until
    names are translated."""
    w = [font_en.text_px(r["en"]) for r in rows if r["en"] and (insert.is_field(r) or any(
        insert.PARTY_IDS[0] <= i <= insert.PARTY_IDS[1] for i in insert.ids_of(r)))]
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


def run(strict=False, write_max=False, script_dir=None):
    """(errors, untranslated count); errors = ["<file> <id>: <message>"]."""
    script = kss_script.load_script(script_dir or kss_script.SCRIPT)
    rows = [r for b, rs in script.items() if b in kss_text.BANKS for r in rs]
    npx, en_t = name_px(rows), kss_script.table(insert.EN_TBL)
    keep = set()
    if KEEP.exists():
        keep = {ln.split()[0] for ln in KEEP.read_text(encoding="utf-8").splitlines() if ln.strip() and ln[0] != "#"}
    errors, todo = [], 0
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
            errors += ["%s %s: %s" % (bank, r["id"], e) for e in check_row(r, npx, en_t)]
        if write_max:
            kss_script.write_tsv(Path(script_dir or kss_script.SCRIPT) / (bank + ".tsv"), rs)
    return errors, todo


def main():
    strict, write_max = "--strict" in sys.argv, "--max" in sys.argv
    errors, todo = run(strict, write_max)
    for e in errors:
        print(e)
    print("lint: %d errors, %d rows untranslated%s" % (len(errors), todo, " (errors)" if strict else ""))
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
