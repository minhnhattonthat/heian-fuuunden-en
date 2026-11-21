"""tools/debug/scenes.tsv is well formed: 6 columns, unique names, slot/ram pokes and route steps warp.lua accepts."""
import re
from pathlib import Path

SCENES = Path(__file__).resolve().parents[1] / "tools/debug/scenes.tsv"
POKES = re.compile(r"^([0-9A-Fa-f]+=[0-9A-Fa-f]+)(,[0-9A-Fa-f]+=[0-9A-Fa-f]+)*$")
STEP = re.compile(r"^(\d+\s+\S+|wait\s+[0-9A-Fa-f]+(\.[0-9A-Fa-f]+(\.[0-9A-Fa-f]+)?)?|poke\s+\S+|mash\s+\d+)$")


def rows():
    out = []
    for line in SCENES.read_text(encoding="utf-8").splitlines():
        if line and not line.startswith("#"):
            out.append(line.split("\t"))
    return out


def test_columns_and_names():
    rs = rows()
    assert rs
    for r in rs:
        assert len(r) == 6, r
    names = [r[0] for r in rs]
    assert len(names) == len(set(names))


def test_pokes_and_routes_parse():
    for name, slot, ram, route, hold, _ in rows():
        for spec in (slot, ram):
            assert spec == "" or POKES.match(spec), (name, spec)
            for v in re.findall(r"=([0-9A-Fa-f]+)", spec):
                assert len(v) % 2 == 0, (name, spec)  # whole bytes, written little-endian
        for step in filter(None, (s.strip() for s in route.split(";"))):
            assert STEP.match(step), (name, step)
            if step.startswith("poke "):
                assert POKES.match(step[5:]), (name, step)
        assert hold.isdigit(), (name, hold)
