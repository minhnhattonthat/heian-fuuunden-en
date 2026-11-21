# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 5. Engine spike and marker build in progress (VWF, relocation, small/narrow names and the party-list
  widening done; left: budgets for the renderer-2 screens no warp scene reaches, then the lint).
  Last build: `build/heian_en.sfc` 2026-11-22 sha1 8eb9b3e58340 (2 MB, smoke ok); marker `build/heian_marker.sfc`
  sha1 fb8741720fca (smoke ok; 123/123 warp scenes ok, `work/qa/marker_warp`).
- **Done:**
  - Phase 5 (`docs/re/hooks.md`, `docs/re/windows.md`): ROM expanded to 2 MB; every table string relocated to
    `$D8-$DE` with a 24-bit `PTRS` table (`tools/insert.py`); VWF on both glyph paths, English digits for `{num}`;
    fonts `fonts/en16.png`, `fonts/en8.png` (Pixel Operator, CC0) and `fonts/en_narrow.png` (own art,
    `tools/font_narrow.py`) (D9, D10, D11).
  - Small mode (D10): `{small}line 1{sbr}line 2` = two 8-px lines in one 16-px field; `{narrow}` = the same in the
    narrow font, last fallback in `insert.fit_field` (one-word names over 48 px: Sadamitsu, Yasumasa, Semimaru).
  - **Party list (D11)**: 8 slots of 5 tiles on one 8-px row, narrow font, 40 px (`PartyName` in `asm/main.asm`,
    slot table `C1:A3CB`, tilemaps `C8:939E`/`C8:9450` rewritten by `tools/gfx_edits.py`; `gfx_blocks.pack` can now
    move a grown block to `$DF:8000+`). Verified `work/qa/party/` (stress build `--qa 054=Sadamitsu --qa
    100=Yasumasa`). Build rule: party names (054-083) must fit 40 px narrow, letters only (`insert.party_fits`).
  - Width gate measured (windows.md): dialogue 176 px x 3 lines (160 on the line before `{page}`), battle prompts
    176 x 1, menu popups 112, renderer-2 fields 48 px, party list 40 px narrow. `tools/lua/r2log.lua` logs every
    renderer-2 call; `tools/lua/wramuse.lua` maps free WRAM (`$7E:1B25-1CFF`).
  - Phases 1-4: recon (`docs/re/`), warp tool + save editor + god mode, identity build, `tbl/jp.tbl` + `script/`.
  - Check: 35 passed (`test_party_fits`, `test_party_tilemaps` new).
- **Next:**
  1. Renderer-2 screens no warp scene reaches (table in windows.md §Not measured yet): places 101-111 (`C1:363A`,
     VRAM 6110), exit labels 115-12C (`C1:6910`), a second party-name screen (`C1:6011`, table `C1:E6CE`: check it
     gets the same narrow treatment or measure it), jutsu/shikigami outside battle (`C1:2E0E`, `C1:57C0`), battle
     windows `C5:1281`/`206A`/`12FF`/`132A`, ports 1BD-1C4 (caller not found), squad exchange screen (panel B,
     needs two squads). For each: find the trigger (mode/sub from the caller's code), add a scene to
     `tools/debug/scenes.tsv`, shoot the marker build, record the budget; else mark the budget "guess" in windows.md.
  2. Province card `{name}の闘い` (dialogue; confirm 176 in a `card_p*` shot).
  3. The lint: per-line px against windows.md budgets (dialogue 176/160, 3 lines per page; fields via `fit_field`;
     `{name}` widths with the longest name), fill `max` in `script/*.tsv`; then phase 6.
  4. Non-table Japanese (battle command labels, status labels, captions, help screen): graphics, phase 8.
  5. Leads kept: staff roll near `C2:CA80` (credits redraw), small-font tilemap text (`script/tilemaps.tsv`),
     story-progress flags unmapped, item inventory and squad roster not mapped in the save (`--qa ID=...` stands
     in for items and party names).
- **Open bugs:** none. Untranslated (Japanese) party names show only their top half in the party list until phase 6
  fills `en` (by design of the one-row slots).
- **Waiting on the user:** GUI keyboard input in `tools/mesen/Mesen.exe` not checked (headless session); not blocking. Title logo 平安風雲伝 kept Japanese under D5 (no official English logo); say if an English subtitle is wanted.
