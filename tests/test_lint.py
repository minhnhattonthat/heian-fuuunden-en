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


def test_codes_names_and_style(en_t):
    assert lint.check_row(row("205", "{name}のばんです", "It is your turn."), 64, en_t)        # {name} lost
    assert lint.check_row(row("205", "{name}のばんです", "{name}'s turn."), 64, en_t) == []
    assert lint.check_row(row("205", "{name}のばんです", "M" * 14 + " {name}"), 64, en_t)     # + 64-px name
    assert lint.check_row(row("217", "{num}経験", "{num}th try"), 64, en_t)                   # ordinal
    assert lint.check_row(row("300", "あ", "日本"), 64, en_t)                                  # Japanese left
    assert lint.check_row(row("300", "あ{br}い", "A long enough line{br}ok."), 64, en_t)       # stub last line


def test_fields_popups_party(en_t):
    assert lint.check_row(row("101", "京の都", "Kyoto"), 64, en_t) == []
    assert lint.check_row(row("101", "京の都", "The Capital of Heian Kyo Long"), 64, en_t)
    assert lint.check_row(row("28B", "道具がありません！", "You have no items!"), 64, en_t) == []
    assert lint.check_row(row("28B", "道具がありません！", "You have no items at all, sorry!"), 64, en_t)
    assert lint.check_row(row("054", "神楽", "Kagura"), 64, en_t) == []
    assert lint.check_row(row("054", "神楽", "Kagura-sama!"), 64, en_t)
    assert lint.budget(row("054", "", "")) == "40 narrow" and lint.budget(row("28D", "", "")).endswith("(guess)")
    assert lint.budget(row("1C8", "", "")) == "128 popup"
