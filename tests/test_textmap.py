import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import textmap  # noqa: E402

pytestmark = pytest.mark.skipif(not textmap.ROM.exists(), reason="no ROM dump in rom/")


def test_save_prompt_decodes():
    d = textmap.ROM.read_bytes()
    _, ws = textmap.words(d, 0x229)
    assert textmap.decode(ws) == "　　　きろくしますか？<FB>"  # FB: end + Yes/No prompt (guess)


def test_bank_split():
    assert textmap.bank(0x2FF) == 0x30000
    assert textmap.bank(0x300) == 0x60000
    assert textmap.bank(0x400) == 0x30000
    assert textmap.bank(0x500) == 0x60000


def test_every_string_terminates():
    d = textmap.ROM.read_bytes()
    for i in range(textmap.COUNT):
        if i == 0x4FF:  # dummy entry: points at the zero tail of C3 (0x3F866-0x3FFFF), no terminator
            continue
        _, ws = textmap.words(d, i)
        assert ws[-1] in textmap.ENDS, hex(i)
