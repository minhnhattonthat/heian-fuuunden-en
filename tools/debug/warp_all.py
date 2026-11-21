"""Warp to every scene in tools/debug/scenes.tsv from a cold boot, in parallel; regenerate the savestate library.

    python -X utf8 tools/debug/warp_all.py [--rom build/heian_en.sfc] [--only a,b] [--jobs 3] [--no-states]
           [--scenes F] [--out work/qa/warp]

Each scene runs `emu.py ROM --script tools/debug/warp.lua --var SCENE='<name>'` into <out>/<name>/, keeps the
shot `warp_<name>.png`, and (unless --no-states) saves work/states/<name>.mss after warp.lua logged WARP_OK.
Writes <out>/index.tsv (scene, ok, frame line) and exits 1 if any scene failed.
"""
import argparse
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tools"))
from skill import SKILL  # noqa: E402


def scenes(path):
    out = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if line.strip() and not line.startswith("#"):
            cols = line.split("\t")
            assert len(cols) == 6, f"{path}: {len(cols)} columns, want 6: {line!r}"
            out.append(cols)
    return out


def run(name, args):
    out = Path(args.out) / name
    cmd = [sys.executable, "-X", "utf8", str(Path(SKILL) / "scripts" / "emu.py"), args.rom, "--out", str(out),
           "--script", str(REPO / "tools/debug/warp.lua"), "--var", f"SCENE='{name}'",
           "--var", f"SCENES_TSV=[[{Path(args.scenes).resolve().as_posix()}]]",
           "--frames", str(args.frames), "--timeout", "900"]
    if not args.no_states:
        cmd += ["--var", f"WARP_STATE=[[{(REPO / 'work/states' / (name + '.mss')).as_posix()}]]"]
    cmd += args.extra
    with open(str(out) + ".log", "w", encoding="utf-8") as fh:
        rc = subprocess.call(cmd, stdout=fh, stderr=subprocess.STDOUT)
    log = (out / "log.txt").read_text(encoding="utf-8", errors="replace") if (out / "log.txt").exists() else ""
    ok = [l for l in log.splitlines() if l.startswith("WARP_OK")]
    return name, rc == 0 and bool(ok), (ok[0] if ok else f"rc={rc} no WARP_OK")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--rom", default=str(REPO / "rom/Heian Fuuunden (Japan).sfc"))
    ap.add_argument("--scenes", default=str(REPO / "tools/debug/scenes.tsv"))
    ap.add_argument("--out", default=str(REPO / "work/qa/warp"))
    ap.add_argument("--only", default="")
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--frames", type=int, default=9000)
    ap.add_argument("--no-states", action="store_true")
    ap.add_argument("extra", nargs="*", help="extra emu.py args after --")
    args = ap.parse_args()
    names = [c[0] for c in scenes(args.scenes)]
    if args.only:
        want = args.only.split(",")
        missing = [w for w in want if w not in names]
        assert not missing, f"unknown scenes: {missing}"
        names = [n for n in names if n in want]
    Path(args.out).mkdir(parents=True, exist_ok=True)
    (REPO / "work/states").mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(args.jobs) as ex:
        results = list(ex.map(lambda n: run(n, args), names))
    lines = [f"{n}\t{'ok' if ok else 'FAIL'}\t{msg}" for n, ok, msg in results]
    (Path(args.out) / "index.tsv").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    bad = [n for n, ok, _ in results if not ok]
    print(f"{len(results) - len(bad)}/{len(results)} scenes ok" + (f"; failed: {','.join(bad)}" if bad else ""))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
