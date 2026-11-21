"""inkbox.py over every centred choice/popup box of a warp tour (phase 8 gate item; decisions D15, D21).

    python -X utf8 tools/inkbox_check.py [--tour work/qa/en_warp]

Each BOXES row: scene, the inside of one box in its warp shot (x,y,w,h; tools/boxedges.py finds them), the allowed
left/right margin difference, and why. VWF text is centred in 4-px spaces, so those boxes allow 4 px. Boxes whose
Japanese fills from the left (244 quit, 28B no items, 1C8/1C9 bag full) or puts options where the cursor expects
them (28E squad confirm) are not centred and are not listed. Exit 1 if any box is off-centre or empty.
"""
import argparse
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))
from skill import SKILL  # noqa: E402

BOXES = [
    ("battle_save_no", "86,98,68,26", 2, "Yes/No choice box under 229 (cursor on No, so it sits between the options)"),
    ("battle_save_prompt", "30,42,196,26", 4, "229 Save your progress? (centred, D15)"),
    ("battle_help_prompt", "30,42,196,26", 4, "0B8 Read the help? (centred, D21)"),
    ("battle_win", "30,42,196,26", 4, "battle-end message (centred, D15)"),
    ("save_message", "61,98,126,26", 4, "243 Saved. in the 120-px save popup (D21)"),
]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tour", default=str(REPO / "work/qa/en_warp"))
    a = ap.parse_args()
    bad = 0
    for scene, rect, tol, why in BOXES:
        shot = Path(a.tour) / scene / ("warp_%s.png" % scene)
        r = subprocess.run([sys.executable, "-X", "utf8", str(Path(SKILL) / "scripts/inkbox.py"), str(shot), rect,
                            "--tol", str(tol)], capture_output=True, text=True)
        print("%-20s %s  %s  (%s)" % (scene, "ok  " if r.returncode == 0 else "FAIL", r.stdout.strip(), why))
        bad += r.returncode != 0
    print("%d/%d boxes centred" % (len(BOXES) - bad, len(BOXES)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
