"""Text lint (tools/lint.py): the repo's script passes, and each rule catches what it is for."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import insert  # noqa: E402
import kss_script  # noqa: E402
import lint  # noqa: E402


@pytest.fixture(scope="module")
def en_t():
    return kss_script.table(insert.EN_TBL)


def row(i, jp, en):
    return {"id": i, "kind": "text", "jp": jp, "en": en, "max": "", "notes": ""}


def test_script_passes():
    errors, _ = lint.run()
    assert errors == []


def test_dialogue_widths(en_t):
    ok = "M" * 22                                    # 176 px exactly
    assert lint.check_row(row("300", "あ{br}い", ok + "{br}" + "Fine words"), 64, en_t) == []
    assert lint.check_row(row("300", "あ", ok + "M"), 64, en_t)
    # third line before {page}: 160 px (the arrow); on the last page 176 is fine
    three = "Some words{br}Some words{br}" + ok
    assert lint.check_row(row("300", "あ{page}い", three + "{page}Done here."), 64, en_t)
    assert lint.check_row(row("300", "あ", three), 64, en_t) == []
    assert lint.check_row(row("300", "あ", "a{br}b{br}c{br}d words"), 64, en_t)   # 4 lines


def test_speaker_pages(en_t):
    # palace ids 297-2A5: a speaker line, then up to 3 text lines
    jp = "女官{br}あ{br}い"
    assert lint.check_row(row("29B", jp, "Lady-in-waiting{br}Words of a line{br}More of them{br}And the end."),
                          64, en_t) == []
    assert lint.check_row(row("29B", jp, "Lady{br}Words here{br}More words{br}Third line{br}Fourth one"), 64, en_t)
    assert lint.budget(row("29B", jp, "")) == "speaker + 176/160 x3"


def test_codes_names_and_style(en_t):
    assert lint.check_row(row("205", "{name}のばんです", "It is your turn."), 64, en_t)        # {name} lost
    assert lint.check_row(row("205", "{name}のばんです", "{name}'s turn."), 64, en_t) == []
    assert lint.check_row(row("205", "{name}のばんです", "M" * 14 + " {name}"), 64, en_t)     # + 64-px name
    assert lint.check_row(row("217", "{num}経験", "{num}th try"), 64, en_t)                   # ordinal
    assert lint.check_row(row("300", "あ", "日本"), 64, en_t)                                  # Japanese left
    assert lint.check_row(row("300", "あ{br}い", "A long enough line{br}ok."), 64, en_t)       # stub last line


def tile(en, cells):
    return {"id": "option0", "kind": "tilemap", "jp": "もじのはやさ", "en": en, "max": cells, "notes": ""}


def test_tilemap_cells():
    # small-font tilemap text: one 8-px cell per character, {br} = next row pair, budget from `max`
    assert lint.check_tilemap(tile("Messages", "8 cells + values")) == []
    assert lint.check_tilemap(tile("Text speed", "8 cells + values"))             # 10 cells > 8
    assert lint.check_tilemap(tile("View your allies'{br}abilities", "18x2 cells")) == []
    assert lint.check_tilemap(tile("A{br}B{br}C", "18x2 cells"))                  # 3 rows > 2
    assert lint.check_tilemap(tile("Saved.", "9 cells")) == []
    assert lint.check_tilemap(tile("Saved.", "")) != []                            # no budget
    assert lint.check_tilemap(tile("記録", "9 cells"))                             # Japanese left


def test_blanks():
    # D15: a Japanese leading/trailing blank needs one in the English; centred rows must match tools/centre.py
    assert lint.blank_errors(row("300", "　あ", "Words"), [])                       # indent dropped
    assert lint.blank_errors(row("300", "　あ", " Words"), []) == []
    assert lint.blank_errors(row("300", "あ　{end2}", "Words{end2}"), [])          # trailing blank dropped
    assert lint.blank_errors(row("300", "あ　{end2}", "Words {end2}"), []) == []
    assert lint.blank_errors(row("300", "　　{br}あ", "{br}Words"), []) == []  # blank first line
    assert lint.blank_errors(row("206", "　　　体力", "Vitality rose!"), [])  # not centred
    assert lint.blank_errors(row("206", "　　　体力", " " * 13 + "Vitality rose!"), []) == []
    assert lint.blank_errors(row("001", "　小刀", "Short Sword"), []) == []        # field: fit_field lays out


def test_page_break_warnings():
    assert lint.page_warnings("We do our best,{page}but the Kebiishi fail.")
    assert lint.page_warnings("I will tell you now...{page}Fifteen years ago.") == []
    assert lint.page_warnings("Done.{page}{name} joins.") == []


def test_fields_popups_party(en_t):
    assert lint.check_row(row("101", "京の都", "Kyoto"), 64, en_t) == []
    assert lint.check_row(row("101", "京の都", "The Capital of Heian Kyo Long"), 64, en_t)
    assert lint.check_row(row("28B", "道具がありません！", "You have no items!"), 64, en_t) == []
    assert lint.check_row(row("28B", "道具がありません！", "You have no items at all, sorry!"), 64, en_t)
    assert lint.check_row(row("054", "神楽", "Kagura"), 64, en_t) == []
    assert lint.check_row(row("054", "神楽", "Kagura-sama!"), 64, en_t)
    assert lint.budget(row("054", "", "")) == "40 narrow" and lint.budget(row("28D", "", "")) == "112 popup"
    assert lint.budget(row("1C8", "", "")) == "128 popup"
    assert lint.budget(row("0FF", "", "")) == "24 field" and lint.budget(row("203", "", "")) == "24 field"
    assert lint.check_row(row("0FF", "価値", "Cost"), 64, en_t) == []
    assert lint.check_row(row("0FF", "価値", "Market price"), 64, en_t)
