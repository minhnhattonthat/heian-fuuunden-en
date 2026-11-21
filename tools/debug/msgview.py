"""Show string ids in the dialogue box from cold boots (tools/debug/msgview.lua), in parallel runs, with shots.

    python -X utf8 tools/debug/msgview.py [--rom build/heian_en.sfc] [--out work/qa/cover/view]
           [--ids 451,0B9 | --uncovered work/qa/cover] [--skip 297-2A6] [--per 22] [--jobs 3]

Each run boots, starts a new game, mashes A through the opening and swaps the next ids of its list into each
message the opening shows (~25 slots per boot). Runs log `TEXT <id>` (tools/lua/textids.lua), so the out dir is a
text-coverage log dir for textcover.py, and keep one shot per page (msg_<id>_<page>.png). Ids a run did not reach
(the opening ran out) go to the next round. --uncovered takes every id of build/strings.tsv that no log.txt under
that dir shows. Exits 1 if an id was never shown.

Coverage from here proves the string decodes and draws in the dialogue box; names, items and menu strings drawn by
renderer 2 are checked for width by the lint (field budgets in docs/re/windows.md), not by these shots.
"""
import argparse
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tools"))
from skill import SKILL  # noqa: E402

NEWGAME = REPO / "tools/routes/newgame_pages.txt"
TEXT = re.compile(r"^TEXT ([0-9A-Fa-f]+)", re.M)
SHOW = re.compile(r"^SHOW ([0-9A-Fa-f]+)", re.M)


def parse_ids(spec):
    out = []
    for part in filter(None, spec.split(",")):
        lo, _, hi = part.partition("-")
        out += range(int(lo, 16), int(hi or lo, 16) + 1)
    return out


def shown_in(logdir):
    seen = set()
    for log in Path(logdir).rglob("log.txt"):
        seen.update(int(a, 16) for a in TEXT.findall(log.read_text(encoding="utf-8", errors="replace")))
    return seen


def route(path):
    """New game (the first 11 steps of newgame_pages.txt), then A every 60 frames."""
    head = [l for l in NEWGAME.read_text(encoding="utf-8").splitlines() if not l.startswith("#")][:11]
    path.write_text("\n".join(head + ["6 a", "54 -"] * 600) + "\n", encoding="utf-8")


def run(name, ids, args):
    out = Path(args.out) / name
    cmd = [sys.executable, "-X", "utf8", str(Path(SKILL) / "scripts/emu.py"), args.rom, "--out", str(out),
           "--route", str(Path(args.out) / "route.txt"),
           "--script", str(REPO / "tools/debug/msgview.lua"), "--script", str(REPO / "tools/lua/textids.lua"),
           "--var", "IDS='%s'" % ",".join("%X" % i for i in ids), "--frames", str(args.frames), "--timeout", "900"]
    with open(str(out) + ".log", "w", encoding="utf-8") as fh:
        subprocess.call(cmd, stdout=fh, stderr=subprocess.STDOUT)
    log = (out / "log.txt").read_text(encoding="utf-8", errors="replace") if (out / "log.txt").exists() else ""
    return {int(a, 16) for a in SHOW.findall(log)}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--rom", default=str(REPO / "build/heian_en.sfc"))
    ap.add_argument("--out", default=str(REPO / "work/qa/cover/view"))
    ap.add_argument("--ids", default="")
    ap.add_argument("--uncovered", help="log dir: take the ids of build/strings.tsv none of its logs show")
    ap.add_argument("--skip", default="", help="ids never to force (hex, ranges a-b)")
    ap.add_argument("--per", type=int, default=22)
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--frames", type=int, default=40000)
    a = ap.parse_args()
    if a.uncovered:
        every = [int(l.split("\t")[0], 16) for l in (REPO / "build/strings.tsv").read_text().splitlines() if l]
        seen = shown_in(a.uncovered)
        todo = [i for i in every if i not in seen]
    else:
        todo = parse_ids(a.ids)
    skip = set(parse_ids(a.skip))
    todo = [i for i in todo if i not in skip]
    Path(a.out).mkdir(parents=True, exist_ok=True)
    route(Path(a.out) / "route.txt")
    rnd = 0
    while todo:
        chunks = [todo[k:k + a.per] for k in range(0, len(todo), a.per)]
        names = ["r%d_%03d" % (rnd, k) for k in range(len(chunks))]
        print("round %d: %d ids in %d runs" % (rnd, len(todo), len(chunks)), flush=True)
        with ThreadPoolExecutor(a.jobs) as ex:
            shown = set().union(*ex.map(lambda nc: run(nc[0], nc[1], a), zip(names, chunks)))
        left = [i for i in todo if i not in shown]
        if len(left) == len(todo):
            print("no progress; never shown: " + ",".join("%03X" % i for i in left))
            return 1
        todo, rnd = left, rnd + 1
    print("all ids shown")
    return 0


if __name__ == "__main__":
    sys.exit(main())
