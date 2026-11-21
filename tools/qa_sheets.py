"""Side-by-side contact sheets of a warp tour against the original's, for the visual-QA gate (qa_gate.py).

    python -X utf8 tools/qa_sheets.py [--en work/qa/en_warp] [--jp work/qa/tour_jp] [--out work/qa/tour]
           [--per 8] [--glob 'msg_*.png']

Collects each scene's shot (<tour>/<scene>/warp_<scene>.png, or every --glob match per scene dir) into
<out>/en/ and <out>/jp/ under the same names, then writes <out>/sheet_NNN.png pages of --per pairs (English left,
Japanese right, full size) and <out>/sheets.tsv (sheet, the shots on it). Scenes the Japanese tour lacks get the
English shot alone.
"""
import argparse
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))
from skill import SKILL  # noqa: E402


def shots(tour, glob):
    out = {}
    for d in sorted(p for p in Path(tour).iterdir() if p.is_dir()):
        for f in sorted(d.glob(glob or "warp_%s.png" % d.name)):
            out[f.name] = f
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--en", default=str(REPO / "work/qa/en_warp"))
    ap.add_argument("--jp", default=str(REPO / "work/qa/tour_jp"))
    ap.add_argument("--out", default=str(REPO / "work/qa/tour"))
    ap.add_argument("--per", type=int, default=8)
    ap.add_argument("--glob", default="")
    a = ap.parse_args()
    out = Path(a.out)
    for sub in ("en", "jp"):
        shutil.rmtree(out / sub, ignore_errors=True)
        (out / sub).mkdir(parents=True)
    for old in out.glob("sheet_*.png"):
        old.unlink()
    en, jp = shots(a.en, a.glob), shots(a.jp, a.glob) if Path(a.jp).is_dir() else {}
    for name, f in en.items():
        shutil.copy(f, out / "en" / name)
        if name in jp:
            shutil.copy(jp[name], out / "jp" / name)
    names = sorted(en)
    index = []
    for k in range(0, len(names), a.per):
        group = names[k:k + a.per]
        sheet = out / ("sheet_%03d.png" % (k // a.per + 1))
        paired = [n for n in group if (out / "jp" / n).exists()]
        cmd = [sys.executable, "-X", "utf8", str(Path(SKILL) / "scripts/sheet.py"),
               *[str(out / "en" / n) for n in group], "--div", "1", "--cols", "2", "--max", str(a.per),
               "--out", str(sheet)]
        if len(paired) == len(group):
            cmd += ["--compare", str(out / "jp")]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL)
        index.append("%s\t%s" % (sheet.name, " ".join(Path(n).stem for n in group)))
    (out / "sheets.tsv").write_text("\n".join(index) + "\n", encoding="utf-8")
    print("%d shots, %d sheets in %s" % (len(names), len(index), out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
