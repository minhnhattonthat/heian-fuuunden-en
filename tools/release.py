"""release.py: build, gate and package a release (patch + README only; never publishes).

    python -X utf8 tools/release.py [--version 1.0] [--force] [--skip-smoke]

Stops at the first failure, in this order: build -> tests + lint (tools/check.py) -> smoke boot -> jp_left.py over
every pointer the build's text table uses (tools/jp_slots.py) -> qa_gate.py check on every work/qa/**/manifest.tsv
(visual tour, story pass; verdicts in the sibling `verdicts/` dir) -> textcover.py -> no unticked line in
docs/polish.md -> no template placeholder in README.md -> debug tool off -> SNES header checksum -> BPS patch ->
re-apply to a clean original and compare -> release/Heian_Fuuunden_EN_vX.Y.zip (the .bps + README.txt).
The playable image (checksum fixed, = original + patch) is written to build/Heian_Fuuunden_EN_vX.Y.sfc; build/heian_en.sfc
stays the plain build the QA manifests hash. Refuses to overwrite an existing version's files without --force.
Publishing (gh release) is the owner's call.
"""
import argparse
import hashlib
import re
import subprocess
import sys
import zipfile
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

ORIG = ROOT / "rom" / "Heian Fuuunden (Japan).sfc"
BUILT = ROOT / "build" / "heian_en.sfc"
OUTDIR = ROOT / "release"
README_TMPL = ROOT / "docs" / "release-readme.txt"
PLACEHOLDER = re.compile(r"<(?:Game title|platform|publisher|year|repo|file|size|sha1|game|ext|Translated[^>]*|"
                         r"Left in Japanese|none known[^>]*|Dialogue[^>]*|Menus[^>]*|Title screen[^>]*|Name entry|"
                         r"Songs[^>]*)>")


def step(name, cmd=None, ok=None):
    print(f"== {name}", flush=True)
    if cmd is not None:
        ok = subprocess.run(cmd, cwd=ROOT).returncode == 0
    if not ok:
        raise SystemExit(f"release stopped: {name} failed")


def py(*args):
    return [sys.executable, "-X", "utf8", *map(str, args)]


def hashes(data):
    return {"size": len(data), "crc32": f"{zlib.crc32(data):08X}", "md5": hashlib.md5(data).hexdigest(),
            "sha1": hashlib.sha1(data).hexdigest()}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--version", default="1.0")
    ap.add_argument("--force", action="store_true", help="overwrite this version's existing patch/zip")
    ap.add_argument("--skip-smoke", action="store_true", help="debugging the script only; never for a real release")
    a = ap.parse_args(argv)
    from skill import SKILL
    import bps
    scripts = Path(SKILL) / "scripts"

    stem = f"Heian_Fuuunden_EN_v{a.version}"
    bpsf, zipf, playable = OUTDIR / f"{stem}.bps", OUTDIR / f"{stem}.zip", ROOT / "build" / f"{stem}.sfc"
    if (bpsf.exists() or zipf.exists()) and not a.force:
        raise SystemExit(f"{bpsf.name} / {zipf.name} already exist; pass --force to overwrite")

    step("build", py(ROOT / "build.py"))
    step("tests + lint", py(ROOT / "tools" / "check.py"))
    if not a.skip_smoke:
        step("smoke", py(scripts / "emu.py", BUILT, "--out", ROOT / "work" / "qa" / "release_smoke",
                         "--route", ROOT / "tools" / "routes" / "boot.txt", "--smoke"))
    step("pointer slots", py(ROOT / "tools" / "jp_slots.py", BUILT, "--out", ROOT / "build" / "jp_slots.txt"))
    step("jp_left (no Japanese a text pointer reaches)",
         py(scripts / "jp_left.py", BUILT, "--tbl", ROOT / "tbl" / "jp.tbl", "--slots", ROOT / "build" / "jp_slots.txt"))
    manifests = sorted((ROOT / "work" / "qa").rglob("manifest.tsv"))
    for m in manifests:
        print("  manifest:", m.relative_to(ROOT))
    step("QA manifests present (visual tour + story pass)",
         ok=any(m.parent.name == "story" for m in manifests) and len(manifests) >= 2)
    for m in manifests:
        step(f"qa_gate {m.relative_to(ROOT)}", py(scripts / "qa_gate.py", "check", m, m.parent / "verdicts"))
    step("text coverage", py(scripts / "textcover.py", ROOT / "work" / "qa" / "cover", ROOT / "build" / "strings.tsv"))
    open_polish = [ln for ln in (ROOT / "docs" / "polish.md").read_text(encoding="utf-8").splitlines()
                   if ln.lstrip().startswith("- [ ]")]
    for ln in open_polish:
        print("  unticked:", ln[:120])
    step("docs/polish.md all ticked", ok=not open_polish)
    left = PLACEHOLDER.findall((ROOT / "README.md").read_text(encoding="utf-8"))
    if left:
        print("  placeholders:", left)
    step("README.md has no template placeholder", ok=not left)
    # The debug tool is emulator Lua (tools/debug/warp.lua, tools/lua/god.lua) poking RAM from outside; nothing of it
    # is assembled into the ROM, and the build above ran with no marker/--qa override. Guard against a stray patch.
    asm = "".join(p.read_text(encoding="utf-8") for p in (ROOT / "asm").glob("*.asm"))
    step("debug tool off in the build", ok=not re.search(r"\bdebug", asm, re.I))

    orig, plain = ORIG.read_bytes(), BUILT.read_bytes()
    built, total = bps.snes_checksum(plain)
    print(f"  header checksum {total:04X}")
    playable.write_bytes(built)
    patch = bps.make(orig, built)
    step("patch re-applied to a clean original == build", ok=bps.apply(ORIG.read_bytes(), patch) == built)
    OUTDIR.mkdir(exist_ok=True)
    bpsf.write_bytes(patch)
    step("patch file round-trip", ok=bps.apply(orig, bpsf.read_bytes()) == built)

    ho, hb = hashes(orig), hashes(built)
    readme = README_TMPL.read_text(encoding="utf-8").format(
        version=a.version, patch=bpsf.name, o_size=ho["size"], o_crc=ho["crc32"], o_md5=ho["md5"],
        o_sha1=ho["sha1"], b_size=hb["size"], b_crc=hb["crc32"], b_sha1=hb["sha1"])
    with zipfile.ZipFile(zipf, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr(bpsf.name, patch)
        z.writestr("README.txt", readme.replace("\n", "\r\n"))
    with zipfile.ZipFile(zipf) as z:
        names = sorted(z.namelist())
        step("zip = patch + README", ok=names == sorted([bpsf.name, "README.txt"]) and
             bps.apply(orig, z.read(bpsf.name)) == built)
    print(f"{zipf.relative_to(ROOT)}: {zipf.stat().st_size} bytes; patch {len(patch)} bytes "
          f"sha1 {hashlib.sha1(patch).hexdigest()}; base crc32 {ho['crc32']} sha1 {ho['sha1']}; "
          f"result {playable.relative_to(ROOT)} crc32 {hb['crc32']} sha1 {hb['sha1']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
