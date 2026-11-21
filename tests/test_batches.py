"""Translation batches (tools/batches.py): all shipped English passes the batch check (glossary, honorifics, codes)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import batches  # noqa: E402


def test_shipped_english_passes():
    assert batches.main(["check"]) == 0


def test_rules_catch():
    terms = batches.glossary()
    row = {"id": "131", "kind": "text", "jp": "晴明様、{name}を見た", "en": "", "max": "", "notes": ""}
    got = batches.problems(row, "Seimei, I saw it", terms)
    assert any("honorific" in p for p in got) and any("control codes" in p for p in got)
    assert batches.problems(row, "Seimei-sama!{br}I saw {name}.", terms) == []
    assert any("glossary" in p for p in batches.problems(row, "Lord-sama!{br}I saw {name}.", terms))
    assert batches.has_term("神楽が来た", "神楽") and not batches.has_term("神楽唄", "神楽")
