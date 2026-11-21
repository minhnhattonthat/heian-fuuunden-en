# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 2. Debug tool not started (phase 1 recon done 2026-11-21). Last build: none yet.
- **Done:**
  - Step 0 setup: MesenCE qa-1 in `tools/mesen/`, original ROM smoke-boots (`tools/routes/boot.txt`), Start input and Lua `L.log` checked, guard hook blocks the `sed -i` canary, pre-commit rejects a failing test, owner rulings D1-D8.
  - Phase 1 text recon (`docs/re/text.md`, verified): 16-bit codes = glyph index, control codes, 0x614-entry pointer table with the C3/C6 split, menu captions at `C1:9E7F`.
  - Phase 1 graphics recon: decompressor `C1:05CF` (raw / LZ / word-RLE) decoded by `tools/kss_comp.py`; every block chain enumerated (`tools/kss_blocks.py`); load tables A `C1:EDFD` and B `C1:EFA1` (`docs/re/compression.md`). Small font found at `C8:8954`. Static sweep of all compressed and raw banks plus menu tour: survey in `docs/re/graphics.md` (G1-G12 tile art, T1-T7 small-font tilemap text). ROM map updated.
  - Savestates: `work/states/opening_4500.mss` (opening dialogue), `work/states/play3_end.mss` (first free roam, a town; X opens the menu). Not in git; recreate with `tools/routes/newgame.txt` + `--mash 90 --mash-key a`.
- **Next (phase 2, `references/emulator-qa.md` §Debug tool):**
  1. Find story flags / map id / party data in RAM (`ramsearch.py`, `watch.lua`) and build `tools/debug/warp.lua` + `tools/debug/scenes.tsv`.
  2. Scenes the survey still needs shots of (graphics.md "phase 2" rows): first battle (G6 command buttons `C8:B282`, table B id 8 loaded at `C0:62CA`), the G7/G8 screens (table B ids 33-36 and 43; probably name entry / kana list; code `C1:E747` loads id 43), ending + credits (G9, table B id 12 from bank CB code), save messages T4/T5, any chapter card or game over.
  3. A forced-battle hook is the quickest way into battle: no encounter was reached by walking in the first town.
  4. `save.py` (SRAM editor) if the save format is simple; check the SRAM checksum.
- **Open bugs:** none.
- **Waiting on the user:** GUI keyboard input in `tools/mesen/Mesen.exe` not checked (headless session); not blocking. Title logo 平安風雲伝 kept Japanese under D5 (no official English logo); say if an English subtitle is wanted.
