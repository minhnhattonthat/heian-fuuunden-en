# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 5. Engine spike and marker build in progress (VWF + relocation + two-line small names working; width
  gate nearly done: party-list widening and a few unreached labels left).
  Last build: `build/heian_en.sfc` 2026-11-22 sha1 616728730c67 (2 MB, Japanese text relocated, smoke ok); marker
  `build/heian_marker.sfc` sha1 28aa831507eab5e6 (smoke ok, 123/123 warp scenes ok, `work/qa/marker_warp`).
- **Done:**
  - Phase 5 (`docs/re/hooks.md`, `docs/re/windows.md`): ROM expanded to 2 MB; every table string relocated to
    `$D8-$DE` with a 24-bit `PTRS` table (`tools/insert.py`); VWF on both glyph paths, English digits for `{num}`;
    fonts `fonts/en16.png` (Pixel Operator) and `fonts/en8.png` (Pixel Operator 8), both CC0 (D9, D10).
  - **Small mode (D10)**: renderer 2 draws `{small}line 1{sbr}line 2` as two 8-px lines in one 16-px field
    (`VwfMenu`/`VwfDraw8`/`MenuEnd` in `asm/main.asm`); the dialogue skips `{small}` and shows `{sbr}` as a space.
    The build picks it per string (`insert.fit_field`, budgets per id range in `insert.FIELDS`); a name that fits
    neither form is a build error. Marker names show `[id]` + filler on two small lines. Verified in the item grid,
    status screen, battle jutsu/shikigami lists and overworld labels (`work/qa/stress_small`, `marker_warp`).
  - Width gate measured (windows.md): dialogue 176 px x 3 lines (160 on the line before `{page}`), battle
    prompts 176 x 1, menu popups 112, renderer-2 fields 48 px (items, status, jutsu, shikigami, squad and province
    labels), **party list 24 px (3 tiles)**. `tools/lua/r2log.lua` logs every renderer-2 call (caller, id, VRAM).
  - Phases 1-4: recon (`docs/re/`), warp tool + save editor + god mode, identity build, `tbl/jp.tbl` + `script/`.
  - Check: 33 passed (`tests/test_insert.py::test_fit_field` new).
- **Next:**
  1. Party list engine work (windows.md §Not measured yet): 4 tiles per slot (slot table `C1:A3CB`/`A3DB`, readers
     `C1:2BEA`/`3292`/`330B`, buffer step `C1:2C0C`, tilemap block `C8:939E` via gfx_blocks recompress) plus a
     narrow 8-px font (3-px letters) so 8-letter names fit 32 px; then set `FIELDS` 054-083 to the new budget.
  2. Remaining labels: squad screen proper, ports 1BD-1C4 and places 101-12C (find where they draw: r2log in a
     field map exit / boat scene), province card `{name}の闘い` (dialogue; confirm 176 in a later shot).
  3. Non-table Japanese: battle command labels こうげき/じゅつ, status labels, captions, help screen (graphics,
     phase 8; tilemap words or `LDA #tile` chains).
  4. Then the lint: per-line px against windows.md budgets (dialogue 176/160, 3 lines per page; fields via
     `fit_field`; `{name}` widths with the longest name), fill `max` in `script/*.tsv`; then phase 6.
  5. Leads kept: staff roll near `C2:CA80` (credits redraw), small-font tilemap text (`script/tilemaps.tsv`),
     graphics blocks that grow need relocation, story-progress flags unmapped, item inventory not mapped in the save
     (`--qa 000=...` stands in for items in the grid).
- **Open bugs:** none (party-list overflow is expected until Next 1; marker strings wider than a field spill into
  the neighbour's tiles by design).
- **Waiting on the user:** GUI keyboard input in `tools/mesen/Mesen.exe` not checked (headless session); not blocking. Title logo 平安風雲伝 kept Japanese under D5 (no official English logo); say if an English subtitle is wanted.
