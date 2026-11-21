# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 5. Engine spike and marker build in progress (VWF + relocation working in-game; width gate half done).
  Last build: `build/heian_en.sfc` 2026-11-22 (2 MB, Japanese text relocated, smoke ok); marker
  `build/heian_marker.sfc` (smoke ok, 38/38 warp scenes ok).
- **Done:**
  - Phase 5 so far (`docs/re/hooks.md`, `docs/re/windows.md`): ROM expanded to 2 MB; every table string relocated to
    `$D8-$DE` with a 24-bit `PTRS` table (`tools/insert.py`, hooks `C1:7270/74F1/754D`); VWF on both glyph paths
    (dialogue `C1:73A5`, renderer 2 `C1:75B8` + upload size `C1:7564`), English digits for `{num}` (`C1:7537`);
    font `fonts/en16.png` from Pixel Operator (CC0, D9), table `tbl/en.tbl` (code = 0x400 + ASCII). asar 1.91 in
    `tools/asar/` (gitignored; github.com/RPGHacker/asar/releases v1.91). `build.py marker [--qa ID=TEXT] [--out F]`.
    Torture line (all ASCII, double spaces, 176-px and 160-px lines, 3-line page) renders correctly
    (`work/qa/torture2`, route `tools/routes/newgame_pages.txt`). `tests/test_insert.py` (pointers reach strings,
    no bank crossing, marker lines fit, font/table agree, hooks assembled). Check: 32 passed.
  - Measured (windows.md): dialogue 176 px x 3 lines, 160 px on the line before `{page}` (▼ arrow erases x 160-175
    of line 3); battle turn / help prompts 176 px x 1; menu popups (28B, 243) 112 px; renderer-2 name fields (item,
    jutsu, shikigami grids, battle jutsu list, status equipment) 48 px.
  - Phases 1-4: recon (`docs/re/`), warp tool + save editor + god mode, identity build, `tbl/jp.tbl` + `script/` dump.
- **Next:**
  1. Finish the width gate (`docs/re/windows.md` §Not measured yet): squad list, portrait name plates / party list,
     province card `{name}の闘い` (warp `card_p*` with a later shot), overworld labels; check the end-of-string page
     arrow on line 3 too (if it shows, line 3 is 160 px on every final page).
  2. Renderer-2 fields are 48 px (~7 letters): engine work before translating (D4): find each field's tile reserve
     (callers of `C1:753B`, VRAM `$0C`, tilemaps), then a narrow second font for renderer 2 and/or wider fields.
     Longer names currently overflow into neighbouring fields' tiles (garbled rows in `marker_warp/menu_items`).
  3. Non-table Japanese seen in the marker build: battle command labels こうげき/じゅつ (find the tilemap words or
     `LDA #tile` chains), plus the known graphics text (status labels, captions, help screen; phase 8).
  4. Then the lint: per-line px against windows.md budgets (dialogue 176/160, 3 lines per page; names by field), and
     fill `max` in `script/*.tsv`; then phase 6.
  5. Leads kept: staff roll near `C2:CA80` (credits redraw), small-font tilemap text (`script/tilemaps.tsv`),
     graphics blocks that grow need relocation, story-progress flags unmapped.
- **Open bugs:** none (renderer-2 overflow is expected for marker-length names; fixed by the field work in Next 2).
- **Waiting on the user:** GUI keyboard input in `tools/mesen/Mesen.exe` not checked (headless session); not blocking. Title logo 平安風雲伝 kept Japanese under D5 (no official English logo); say if an English subtitle is wanted.
