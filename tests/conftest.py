"""Shared fixtures: ROMs built from the current sources into a temp dir, once per test session (never the build/
artifacts, which can be stale or missing)."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))


@pytest.fixture(scope="session")
def built_rom(tmp_path_factory):
    """built_rom(mode) -> bytes of build.build(mode) ('build' or 'marker'); skips with no ROM dump or asar."""
    import build
    if not (build.ROM.exists() and build.ASAR.exists()):
        pytest.skip("no ROM dump in rom/ or no asar in tools/asar/")
    cache = {}

    def get(mode):
        if mode not in cache:
            _, cache[mode], _ = build.build(mode, path=tmp_path_factory.mktemp(mode) / ("%s.sfc" % mode))
        return cache[mode]
    return get
