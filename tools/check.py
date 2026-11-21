"""check.py: the repo's one-command check (tests + text lint). The pre-commit hook runs it.

Exit code is pytest's: non-zero blocks the commit."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

if __name__ == "__main__":
    r = subprocess.run([sys.executable, "-X", "utf8", "-m", "pytest", "-q", str(ROOT / "tests")], cwd=ROOT)
    sys.exit(r.returncode)
