"""build.py: the one entry point for building the patched ROM.

    python -X utf8 build.py                      unpack the original, repack with the edits in the repo -> build/heian_en.sfc
    python -X utf8 build.py identity             unpack to work/unpack/, repack from those files, compare with the original
    python -X utf8 build.py identity --recompress   same, and re-encode every graphics block (encoder check)
    python -X utf8 build.py marker [--qa ID=TEXT].. [--out F]   `[id]` filler for every untranslated line
                                                 -> build/heian_marker.sfc (phase 5 width gate)

Steps (docs/re/text.md, docs/re/compression.md):
  1. check the dump against rom.sha1;
  2. dialogue banks C3/C6 + pointer table: tools/kss_text.py (no English yet: phase 4-7);
  3. compressed graphics/tilemap blocks in gfx/blocks.tsv: tools/gfx_blocks.py; build/marker apply
     tools/gfx_edits.py after the 2 MB expansion (party-list tilemaps; a block that grows moves to $DF:8000+);
  4. header checksum (mirrored sum for 1.5 MB).
Phase 3 state: no edits exist, so the build is byte-identical to the original (tests/test_identity.py).
"""
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "tools"))

import bps  # noqa: E402
import check_rom  # noqa: E402
import font_en  # noqa: E402
import gfx_blocks  # noqa: E402
import gfx_edits  # noqa: E402
import insert  # noqa: E402
import kss_text  # noqa: E402

ROM = ROOT / "rom" / "Heian Fuuunden (Japan).sfc"
OUT = ROOT / "build" / "heian_en.sfc"
MARKER = ROOT / "build" / "heian_marker.sfc"
ASAR = ROOT / "tools" / "asar" / "asar.exe"
UNPACK = ROOT / "work" / "unpack"


def unpack(rom, outdir):
    outdir = Path(outdir)
    (outdir / "text").mkdir(parents=True, exist_ok=True)
    for bank, items in kss_text.unpack(rom).items():
        (outdir / "text" / ("%s.json" % bank)).write_text(
            json.dumps(items, indent=1, ensure_ascii=False), encoding="utf-8")
    gfx_blocks.unpack(rom, outdir / "gfx")


def repack(rom, indir, recompress=False):
    indir = Path(indir)
    layout = {b: json.loads((indir / "text" / ("%s.json" % b)).read_text(encoding="utf-8"))
              for b in kss_text.BANKS}
    out = kss_text.pack(rom, layout)
    out, stats = gfx_blocks.pack(out, indir / "gfx", recompress=recompress)
    out, _ = bps.snes_checksum(out)
    return out, stats


def identity(recompress=False, workdir=None):
    """Unpack and repack with no edits; return (rebuilt bytes, original bytes, block stats)."""
    rom = ROM.read_bytes()
    if workdir is None:
        workdir = UNPACK
        shutil.rmtree(workdir, ignore_errors=True)
    unpack(rom, workdir)
    out, stats = repack(rom, workdir, recompress)
    return out, rom, stats


def assemble(path):
    """Apply asm/main.asm to the ROM file at `path` with the repo's asar (tools/asar/, gitignored)."""
    font_en.build()
    r = subprocess.run([str(ASAR), "--fix-checksum=off", "--no-title-check",str(ROOT / "asm" / "main.asm"), str(path)],
                       capture_output=True, text=True, errors="replace")
    if r.returncode:
        path.unlink(missing_ok=True)
        raise SystemExit("asar failed:\n" + r.stdout + r.stderr)


def build(mode="build", qa=None, path=None):
    """mode build: English where `en` is filled, Japanese elsewhere; marker: `[id]` filler where `en` is empty.
    qa: {id: text} overrides for one-off stress builds (`marker --qa 2A7="..." --out build/x.sfc`)."""
    rom = ROM.read_bytes()
    with tempfile.TemporaryDirectory() as tmp:
        unpack(rom, tmp)
        out, _ = repack(rom, tmp)
        out, stats = insert.insert(out, mode, qa=qa)
        gfx_edits.apply(Path(tmp) / "gfx")     # after the 2 MB expansion: grown blocks move to $DF:8000+
        out, _ = gfx_blocks.pack(out, Path(tmp) / "gfx")
    path = Path(path) if path else (OUT if mode == "build" else MARKER)
    path.parent.mkdir(exist_ok=True)
    path.unlink(missing_ok=True)
    path.write_bytes(out)
    assemble(path)
    out, _ = bps.snes_checksum(path.read_bytes())
    path.write_bytes(out)
    return path, out, stats


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("cmd", nargs="?", default="build", choices=["build", "identity", "marker"])
    ap.add_argument("--recompress", action="store_true")
    ap.add_argument("--qa", action="append", default=[], metavar="ID=TEXT",
                    help="override one string (first id, hex) with English text; repeatable")
    ap.add_argument("--out", help="output ROM path (default build/heian_en.sfc or build/heian_marker.sfc)")
    a = ap.parse_args()
    check_rom.check()
    if a.cmd == "identity":
        out, rom, stats = identity(a.recompress)
        same = out == rom
        diff = sum(1 for x, y in zip(out, rom) if x != y)
        print("identity: %s (%d bytes differ); blocks %s" % ("IDENTICAL" if same else "DIFFERENT", diff, stats))
        sys.exit(0 if same else 1)
    qa = dict(q.split("=", 1) for q in a.qa)
    path, out, stats = build(a.cmd, qa, a.out)
    print("%s  %s  sha1 %s  text %s" % (path, len(out), hashlib.sha1(out).hexdigest(), stats))


if __name__ == "__main__":
    main()
