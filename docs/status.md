# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 5. Engine spike and marker build next (phase 4 extract done). Last build: `build/heian_en.sfc`
  2026-11-21, sha1 `3b0ca4a2...` = the original (no edits yet), smoke ok.
- **Done:**
  - Phase 4 (`docs/re/text.md` §Encoding, §Script files): `tbl/jp.tbl` covers every glyph (kana, 0x58-0x376 kanji read
    by eye with `tools/kanjisheet.py`, rare ones checked in context with `tools/kanjictx.py`; 3 guesses listed in
    text.md). `tools/kss_script.py dump` -> `script/C3.tsv` (964 strings) + `script/C6.tsv` (493), all 0x614 ids, no
    unknown codes; `tools/tilemap_text.py dump` -> `script/tilemaps.tsv` (T1-T5, 16 entries). `tests/test_script.py`:
    every id roundtrips `encode(decode(words)) == words`, script files match the ROM, banks fully covered (4 orphan
    runs + C6 zero tail explained and checked for references), dump never clobbers English. Check: 27 passed.
  - Phase 3: `build.py` (build / `identity [--recompress]`) unpacks the dialogue banks C3/C6 + pointer table
    (`tools/kss_text.py`) and the 541 compressed blocks in `gfx/blocks.tsv` (`tools/gfx_blocks.py`), repacks them and
    fixes the header checksum: IDENTICAL. `tests/test_identity.py`.
  - Phases 1-2: recon (`docs/re/`), warp tool `tools/debug/warp.lua` + `warp_all.py` (123/123 scenes), save editor
    `tools/debug/save.py`, god mode `tools/lua/god.lua` (`docs/re/save.md`).
- **Next:**
  1. Phase 5 (`references/pipeline.md` §Marker, `platform-snes.md`): expand to 2 MB and relocate strings with 24-bit
     pointers (hooks at `C1:7270-728D`, name reader `C1:74F1`; `text.md` §Engine facts); font decision for the 16×16
     2bpp dialogue font (VWF or 8×16 half-width into the WRAM buffer `$7F:A000`); build a marker ROM (`[id]` + filler
     at full width), boot it, tour with the warp list, find non-text "strings", and measure every box variant (dialogue
     box 2 lines, names in menus/status/battle, battle messages, province card `{name}の闘い`, overworld labels).
  2. Small-font tilemap text (`script/tilemaps.tsv`): needs English small-font cells + map rewrite (G5/T1-T5).
  3. Leads: staff-roll line data around `C2:CA80` (`text.md` §Other text) for the credits redraw; graphics blocks that
     grow need relocation + load-table pointer rewrite (`gfx_blocks.pack` refuses now); story-progress flags unmapped;
     G14/T8 sources (`graphics.md` §Still open).
- **Open bugs:** none.
- **Waiting on the user:** GUI keyboard input in `tools/mesen/Mesen.exe` not checked (headless session); not blocking. Title logo 平安風雲伝 kept Japanese under D5 (no official English logo); say if an English subtitle is wanted.
