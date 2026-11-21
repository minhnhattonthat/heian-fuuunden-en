# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 1. Research and recon in progress (text recon done; graphics-text survey incomplete). Last build: none yet.
- **Done:**
  - Step 0 setup: MesenCE qa-1 in `tools/mesen/`, original ROM smoke-boots (`tools/routes/boot.txt`), Start input and Lua `L.log` checked, guard hook blocks the `sed -i` canary, pre-commit rejects a failing test, owner rulings D1-D8.
  - Phase 1 text recon (`docs/re/text.md`, verified): 16-bit LE codes = glyph index; dialogue font 16×16 2bpp at file 0x90000; kana layout; control codes FF FB FE FD FC 56; 0x614-entry pointer table at C3:0000 with the C3/C6 bank split; both banks full; menu captions are BG3 tilemap words at `C1:9E7F`. Prior work: none usable (`docs/re/prior-work.md`). ROM map and free-space candidates: `docs/re/rom-map.md`.
  - Savestates: `work/states/opening_4500.mss` (opening dialogue), `work/states/play3_end.mss` (first free roam, field; X opens the menu). Not in git; recreate with `tools/routes/newgame.txt` + `--mash 90 --mash-key a`.
- **Next (finish phase 1):**
  1. Graphics-text survey (`docs/re/graphics.md` §Still to survey): reach a battle (walk out of town from `play3_end.mss`), shops/items/equipment/options, then list every tile-drawn label. Trace G3/G4 (file-select scroll kana) and G6 labels to their ROM source.
  2. Find the other tilemap-text tables like `C1:9E7F` (status labels, battle commands) by dumping BG3 and searching the map words.
  3. Locate the 8×16 small font source (compressed? `vramfind.py` found 299 tiles not raw) and the compression format if any.
  4. Then phase 2 (debug tool): story flags / scene ids for warps; mid-game cards, ending and credits go into the survey from there.
- **Open bugs:** none.
- **Waiting on the user:** GUI keyboard input in `tools/mesen/Mesen.exe` not checked (headless session); not blocking. Title logo 平安風雲伝 kept Japanese under D5 (no official English logo); say if an English subtitle is wanted.
